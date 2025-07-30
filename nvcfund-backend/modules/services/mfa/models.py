"""
MFA Models
NVC Banking Platform - Multi-Factor Authentication Database Models

This module defines the database models for MFA functionality:
- MFA configuration per user
- Backup codes for account recovery
- MFA audit logs for security tracking
"""

from modules.core.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import Index, UUID
import secrets
import string
import uuid


class MFAConfiguration(db.Model):
    """
    Multi-Factor Authentication configuration for users
    Stores TOTP secrets, backup codes, and MFA preferences
    """
    __tablename__ = 'mfa_configurations'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # TOTP Configuration
    totp_secret = db.Column(db.String(255), nullable=True)  # Base32 encoded TOTP secret
    totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    totp_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Backup Configuration
    backup_codes_generated = db.Column(db.Boolean, default=False, nullable=False)
    backup_codes_count = db.Column(db.Integer, default=0, nullable=False)
    
    # MFA Enforcement
    is_enforced = db.Column(db.Boolean, default=False, nullable=False)  # Admin can enforce MFA
    setup_required = db.Column(db.Boolean, default=False, nullable=False)  # User must set up MFA
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='mfa_config', lazy=True)
    backup_codes = db.relationship('MFABackupCode', backref='mfa_config', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('MFAAuditLog', backref='mfa_config', lazy=True)
    
    def __repr__(self):
        return f'<MFAConfiguration {self.user_id}: TOTP={self.totp_enabled}>'
    
    def generate_backup_codes(self, count=10):
        """Generate new backup codes for the user"""
        # Remove existing backup codes
        for code in self.backup_codes:
            db.session.delete(code)
        
        # Generate new codes
        backup_codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            backup_code = MFABackupCode(
                mfa_config_id=self.id,
                code_hash=code,  # In production, hash this
                is_used=False
            )
            backup_codes.append(backup_code)
            db.session.add(backup_code)
        
        self.backup_codes_generated = True
        self.backup_codes_count = count
        db.session.commit()
        
        return [code.code_hash for code in backup_codes]  # Return plain codes for display
    
    def verify_backup_code(self, code):
        """Verify a backup code and mark it as used"""
        backup_code = MFABackupCode.query.filter_by(
            mfa_config_id=self.id,
            code_hash=code,  # In production, hash the input code
            is_used=False
        ).first()
        
        if backup_code:
            backup_code.is_used = True
            backup_code.used_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def get_unused_backup_codes_count(self):
        """Get count of unused backup codes"""
        return MFABackupCode.query.filter_by(
            mfa_config_id=self.id,
            is_used=False
        ).count()


class MFABackupCode(db.Model):
    """
    Backup codes for MFA recovery
    Each code can only be used once
    """
    __tablename__ = 'mfa_backup_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    mfa_config_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mfa_configurations.id'), nullable=False)
    
    code_hash = db.Column(db.String(255), nullable=False)  # Hashed backup code
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<MFABackupCode {self.id}: Used={self.is_used}>'


class MFAAuditLog(db.Model):
    """
    Audit log for MFA operations
    Tracks all MFA-related activities for security monitoring
    """
    __tablename__ = 'mfa_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    mfa_config_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mfa_configurations.id'), nullable=False)
    
    # Event Details
    event_type = db.Column(db.String(100), nullable=False)  # 'setup', 'verify', 'disable', 'backup_used'
    event_description = db.Column(db.Text, nullable=True)
    event_result = db.Column(db.String(50), nullable=False)  # 'success', 'failure', 'error'
    
    # Request Context
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    
    # Metadata
    additional_data = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<MFAAuditLog {self.event_type}: {self.event_result}>'
    
    @staticmethod
    def log_event(mfa_config_id, event_type, event_description, event_result, 
                  ip_address=None, user_agent=None, session_id=None, additional_data=None):
        """Create a new audit log entry"""
        log_entry = MFAAuditLog(
            mfa_config_id=mfa_config_id,
            event_type=event_type,
            event_description=event_description,
            event_result=event_result,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            additional_data=additional_data
        )
        db.session.add(log_entry)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Log to application logger if database logging fails
            import logging
            logging.error(f"Failed to create MFA audit log: {str(e)}")


# Database indexes for performance
Index('idx_mfa_config_user_id', MFAConfiguration.user_id)
Index('idx_mfa_backup_codes_config_id', MFABackupCode.mfa_config_id)
Index('idx_mfa_backup_codes_used', MFABackupCode.is_used)
Index('idx_mfa_audit_logs_config_id', MFAAuditLog.mfa_config_id)
Index('idx_mfa_audit_logs_event_type', MFAAuditLog.event_type)
Index('idx_mfa_audit_logs_created_at', MFAAuditLog.created_at)