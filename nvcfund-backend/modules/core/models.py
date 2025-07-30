"""
Core Database Models for NVC Banking Platform
Reusable models with proper relationships to avoid conflicts
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import UUID, JSONB, JSON
from flask_login import UserMixin

from .extensions import db

# === BASE MIXINS FOR REUSABILITY ===

class TimestampMixin:
    """Reusable timestamp mixin"""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditMixin:
    """Reusable audit trail mixin"""
    @declared_attr
    def created_by(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)

# === FORM SUBMISSION TRACKING ===

class FormSubmissionStatus(Enum):
    """Form submission status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class FormSubmission(TimestampMixin, db.Model):
    """Track all form submissions across the banking platform"""
    __tablename__ = 'form_submissions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    submission_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Form metadata
    form_type = Column(String(100), nullable=False)
    module_name = Column(String(50), nullable=False)
    
    # User tracking with proper relationship
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_ip = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Security
    csrf_token = Column(String(128), nullable=False)
    session_id = Column(String(128), nullable=False)
    
    # Form data (encrypted in production)
    form_data = Column(Text, nullable=False)
    
    # Processing status
    status = Column(String(20), nullable=False, default=FormSubmissionStatus.PENDING.value)
    error_message = Column(Text, nullable=True)
    
    # Processing timestamps
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Audit trail
    processing_notes = Column(Text, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="form_submissions")
    approved_by_user = relationship("User", foreign_keys=[approved_by], backref="approved_submissions")
    
    def __repr__(self):
        return f'<FormSubmission {self.submission_id}: {self.form_type}>'

# === BANKING MODELS ===
# Banking models moved to modules.banking.models for better organization

# === TREASURY OPERATIONS ===

class TreasuryOperation(TimestampMixin, AuditMixin, db.Model):
    """Treasury operations and settings"""
    __tablename__ = 'treasury_operations'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    operation_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Operation details
    operation_type = Column(String(50), nullable=False)
    operation_data = Column(Text, nullable=False)
    
    # Form submission reference with proper relationship
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=False)
    
    # Authorization with proper relationship
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    authorization_level = Column(String(20), nullable=False)
    
    # Status
    status = Column(String(20), nullable=False, default='pending_approval')
    
    # Processing timestamps
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)
    
    # Relationships
    form_submission = relationship("FormSubmission", backref="treasury_operations")
    authorized_by_user = relationship("User", foreign_keys=[authorized_by], backref="authorized_treasury_operations")
    
    def __repr__(self):
        return f'<TreasuryOperation {self.operation_id}: {self.operation_type}>'

# === AUDIT TRAIL ===

class AuditLog(db.Model):
    """Comprehensive audit logging for all form submissions and transactions"""
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Event details
    event_type = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=False)
    
    # User and session with proper relationships
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(128), nullable=False)
    user_ip = Column(String(45), nullable=False)
    
    # Related records with proper relationships
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    
    # Additional data
    additional_data = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="audit_logs")
    form_submission = relationship("FormSubmission", backref="audit_logs")
    # Transaction relationship will be set by banking module to avoid circular imports
    
    def __repr__(self):
        return f'<AuditLog {self.log_id}: {self.event_type}>'

# === API KEY MANAGEMENT ===

class APIKeyStore(TimestampMixin, db.Model):
    """Secure storage for external API credentials"""
    __tablename__ = 'api_key_store'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100), nullable=False, index=True)
    encrypted_api_key = Column(Text, nullable=True)
    encrypted_secret_key = Column(Text, nullable=True)
    key_alias = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f'<APIKeyStore {self.service_name}:{self.key_alias}>'

# === ADDITIONAL MODELS FOR COMPATIBILITY ===

# Account alias for backwards compatibility - will be set by banking module
Account = None

# Add indexes for performance
Index('idx_form_submissions_user_id', FormSubmission.user_id)
Index('idx_form_submissions_status', FormSubmission.status)
Index('idx_form_submissions_submitted_at', FormSubmission.submitted_at)
Index('idx_audit_logs_user_id', AuditLog.user_id)
Index('idx_audit_logs_created_at', AuditLog.created_at)

class SecurityEventLog(db.Model):
    """Security-specific events requiring immediate attention"""
    __tablename__ = 'security_event_logs'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False)  # login_failure, mfa_bypass_attempt, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    event_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class TransactionAuditLog(db.Model):
    """Financial transaction audit trail"""
    __tablename__ = 'transaction_audit_logs'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    event_type = Column(String(50), nullable=False)  # created, modified, cancelled, completed
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class ApiAccessLog(db.Model):
    """API access logging for security monitoring"""
    __tablename__ = 'api_access_logs'
    
    id = Column(Integer, primary_key=True)
    request_id = Column(String(36), nullable=False)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class SystemLogs(db.Model):
    """Comprehensive system logs table for all application events"""
    __tablename__ = 'system_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Log categorization
    category = Column(String(50), nullable=False)  # security_reports, banking, compliance, etc.
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    event_type = Column(String(100), nullable=False)
    
    # Content and context
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # User and session context
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(128), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # System context
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    process_id = Column(Integer, nullable=True)
    thread_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='system_logs')
    
    def __repr__(self):
        return f'<SystemLog {self.log_id}: {self.category}/{self.event_type}>'

class SecurityLogs(db.Model):
    """Dedicated security events logging"""
    __tablename__ = 'security_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Security event details
    event_type = Column(String(100), nullable=False)  # login_attempt, failed_auth, suspicious_activity
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), nullable=False)  # SUCCESS, FAILURE, BLOCKED
    
    # Event context
    description = Column(Text, nullable=False)
    risk_score = Column(Integer, default=0)
    
    # User and session
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    target_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(128), nullable=True)
    
    # Network context
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    
    # Additional metadata
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], backref='security_events')
    target_user = relationship('User', foreign_keys=[target_user_id])

class TransactionLogs(db.Model):
    """Transaction-specific logging"""
    __tablename__ = 'transaction_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Transaction reference
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    transaction_reference = Column(String(100), nullable=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # initiated, processing, completed, failed
    status = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default='USD')
    
    # Accounts involved
    from_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)
    to_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)
    
    # Processing details
    processing_time_ms = Column(Integer, nullable=True)
    error_code = Column(String(20), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Audit trail
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    transaction = relationship('Transaction', backref='logs')
    user = relationship('User', backref='transaction_logs')
    from_account = relationship('BankAccount', foreign_keys=[from_account_id])
    to_account = relationship('BankAccount', foreign_keys=[to_account_id])

class ComplianceLogs(db.Model):
    """AML, KYC, and regulatory compliance logging"""
    __tablename__ = 'compliance_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Compliance event details
    compliance_type = Column(String(50), nullable=False)  # AML, KYC, SANCTIONS, REPORTING
    event_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    
    # Subject details
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=True)
    
    # Compliance data
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH
    flags_triggered = Column(JSON, nullable=True)
    verification_result = Column(String(50), nullable=True)
    
    # Regulatory context
    regulation = Column(String(100), nullable=True)  # BSA, PATRIOT_ACT, etc.
    reporting_required = Column(Boolean, default=False)
    
    # Details and metadata
    description = Column(Text, nullable=False)
    compliance_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='compliance_logs')
    transaction = relationship('Transaction', backref='compliance_logs')

class ApiLogs(db.Model):
    """API access and integration logging"""
    __tablename__ = 'api_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Request details
    method = Column(String(10), nullable=False)
    endpoint = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    
    # Timing and performance
    response_time_ms = Column(Integer, nullable=True)
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # User context
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    api_key_id = Column(String(100), nullable=True)
    
    # Network context
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Metadata
    request_headers = Column(JSON, nullable=True)
    request_params = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', backref='api_logs')
