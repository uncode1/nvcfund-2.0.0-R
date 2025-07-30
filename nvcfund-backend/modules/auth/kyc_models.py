"""
KYC Models for Plaid Identity Verification Integration
Database models for storing KYC verification data
"""

from modules.core.extensions import db
from datetime import datetime
from sqlalchemy import Enum as SQLEnum
import enum

class KYCStatus(enum.Enum):
    """KYC verification status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    INCOMPLETE = "incomplete"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class RiskLevel(enum.Enum):
    """Risk level enumeration for KYC results"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PlaidKYCVerification(db.Model):
    """
    Store Plaid Identity Verification data
    """
    __tablename__ = 'plaid_kyc_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Plaid verification details
    plaid_verification_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    client_user_id = db.Column(db.String(255), nullable=False, index=True)
    template_id = db.Column(db.String(255), nullable=True)
    
    # Verification status and timestamps
    status = db.Column(SQLEnum(KYCStatus), default=KYCStatus.PENDING, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Verification results
    overall_score = db.Column(db.Float, nullable=True)
    risk_level = db.Column(SQLEnum(RiskLevel), nullable=True)
    
    # Step verification flags
    document_verified = db.Column(db.Boolean, default=False, nullable=False)
    kyc_passed = db.Column(db.Boolean, default=False, nullable=False)
    selfie_verified = db.Column(db.Boolean, default=False, nullable=False)
    data_sources_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # URLs and metadata
    shareable_url = db.Column(db.Text, nullable=True)
    link_token = db.Column(db.Text, nullable=True)
    link_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Raw response data (JSON)
    plaid_response_data = db.Column(db.JSON, nullable=True)
    
    # Compliance and audit
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='plaid_kyc_verifications')
    
    def __repr__(self):
        return f'<PlaidKYCVerification {self.plaid_verification_id}: {self.status.value}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plaid_verification_id': self.plaid_verification_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'overall_score': self.overall_score,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'document_verified': self.document_verified,
            'kyc_passed': self.kyc_passed,
            'selfie_verified': self.selfie_verified,
            'data_sources_verified': self.data_sources_verified,
            'shareable_url': self.shareable_url,
            'is_complete': self.is_complete(),
            'is_approved': self.is_approved()
        }
    
    def is_complete(self):
        """Check if verification is complete"""
        return self.status in [KYCStatus.SUCCESS, KYCStatus.FAILED, KYCStatus.EXPIRED, KYCStatus.CANCELLED]
    
    def is_approved(self):
        """Check if verification passed"""
        return self.status == KYCStatus.SUCCESS and self.kyc_passed
    
    def update_from_plaid_data(self, plaid_data):
        """Update model with data from Plaid API response"""
        if not plaid_data.get('success'):
            return False
        
        summary = plaid_data.get('summary', {})
        
        # Update basic fields
        self.status = KYCStatus(summary.get('status', 'pending'))
        self.overall_score = summary.get('overall_score')
        if summary.get('risk_level'):
            self.risk_level = RiskLevel(summary.get('risk_level'))
        
        # Update verification flags
        self.document_verified = summary.get('document_verified', False)
        self.kyc_passed = summary.get('kyc_passed', False)
        self.selfie_verified = summary.get('selfie_verified', False)
        self.data_sources_verified = summary.get('data_sources_verified', False)
        
        # Update timestamps
        if summary.get('created_at'):
            self.started_at = datetime.fromisoformat(summary['created_at'].replace('Z', '+00:00'))
        if summary.get('completed_at'):
            self.completed_at = datetime.fromisoformat(summary['completed_at'].replace('Z', '+00:00'))
        
        # Store full response data
        self.plaid_response_data = plaid_data
        self.updated_at = datetime.utcnow()
        
        return True

class KYCDocument(db.Model):
    """
    Store individual KYC document verification results
    """
    __tablename__ = 'kyc_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    kyc_verification_id = db.Column(db.Integer, db.ForeignKey('plaid_kyc_verifications.id'), nullable=False)
    
    # Document details
    document_type = db.Column(db.String(100), nullable=False)  # passport, driver_license, etc.
    document_status = db.Column(db.String(50), nullable=False)  # success, failed, pending
    document_country = db.Column(db.String(2), nullable=True)  # ISO country code
    
    # Extracted data
    extracted_name = db.Column(db.String(255), nullable=True)
    extracted_date_of_birth = db.Column(db.Date, nullable=True)
    extracted_address = db.Column(db.Text, nullable=True)
    extracted_document_number = db.Column(db.String(100), nullable=True)
    extracted_expiry_date = db.Column(db.Date, nullable=True)
    
    # Verification results
    authenticity_score = db.Column(db.Float, nullable=True)
    image_quality_score = db.Column(db.Float, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    plaid_document_data = db.Column(db.JSON, nullable=True)
    
    # Relationship
    kyc_verification = db.relationship('PlaidKYCVerification', backref='documents')
    
    def __repr__(self):
        return f'<KYCDocument {self.document_type}: {self.document_status}>'

class KYCComplianceAction(db.Model):
    """
    Store compliance actions taken based on KYC results
    """
    __tablename__ = 'kyc_compliance_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    kyc_verification_id = db.Column(db.Integer, db.ForeignKey('plaid_kyc_verifications.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Action details
    action_type = db.Column(db.String(100), nullable=False)  # approve, reject, request_additional, flag_review
    action_reason = db.Column(db.Text, nullable=True)
    automated = db.Column(db.Boolean, default=True, nullable=False)
    
    # Staff details (if manual action)
    staff_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    staff_comments = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    kyc_verification = db.relationship('PlaidKYCVerification', backref='compliance_actions')
    user = db.relationship('User', foreign_keys=[user_id], backref='kyc_compliance_actions')
    staff_user = db.relationship('User', foreign_keys=[staff_user_id], backref='kyc_staff_actions')
    
    def __repr__(self):
        return f'<KYCComplianceAction {self.action_type}: {self.automated}>'

class KYCAuditLog(db.Model):
    """
    Audit log for all KYC-related activities
    """
    __tablename__ = 'kyc_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    kyc_verification_id = db.Column(db.Integer, db.ForeignKey('plaid_kyc_verifications.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Event details
    event_type = db.Column(db.String(100), nullable=False)  # verification_started, status_updated, etc.
    event_description = db.Column(db.Text, nullable=False)
    event_data = db.Column(db.JSON, nullable=True)
    
    # Context
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    kyc_verification = db.relationship('PlaidKYCVerification', backref='audit_logs')
    user = db.relationship('User', backref='kyc_audit_logs')
    
    def __repr__(self):
        return f'<KYCAuditLog {self.event_type}: {self.created_at}>'
    
    @staticmethod
    def log_event(user_id, event_type, event_description, 
                  kyc_verification_id=None, event_data=None, 
                  ip_address=None, user_agent=None, session_id=None):
        """
        Create an audit log entry
        """
        log_entry = KYCAuditLog(
            user_id=user_id,
            event_type=event_type,
            event_description=event_description,
            kyc_verification_id=kyc_verification_id,
            event_data=event_data,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        db.session.add(log_entry)
        try:
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            raise e