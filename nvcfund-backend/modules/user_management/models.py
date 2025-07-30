"""
User Management Models
Self-contained models for user accounts, profiles, preferences, and account management
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import uuid

from modules.core.extensions import db
from ..auth.models import UserRole  # Import UserRole from authoritative source

class AccountType(Enum):
    """Account types for users"""
    INDIVIDUAL_ACCOUNT = "individual_account"
    BUSINESS_CLIENT = "business_client"
    PARTNER_PROGRAM = "partner_program"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    CLOSED = "closed"

class UserProfile(db.Model):
    """Enhanced user profile with comprehensive banking features"""
    __tablename__ = 'user_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User identification
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(DateTime)
    
    # Contact information
    phone_number = Column(String(20), unique=True)
    secondary_phone = Column(String(20))
    address_line_1 = Column(String(200))
    address_line_2 = Column(String(200))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default='United States')
    
    # Account management
    account_type = Column(String(50), default=AccountType.INDIVIDUAL_ACCOUNT.value)
    user_role = Column(String(50), default=UserRole.STANDARD_USER.value)
    status = Column(String(20), default=UserStatus.ACTIVE.value)
    
    # Security and verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    kyc_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    
    # Profile metadata
    profile_picture_url = Column(String(500))
    time_zone = Column(String(50), default='UTC')
    preferred_language = Column(String(10), default='en')
    preferred_currency = Column(String(3), default='USD')
    
    # Account settings
    marketing_emails_enabled = Column(Boolean, default=True)
    security_notifications_enabled = Column(Boolean, default=True)
    transaction_notifications_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    last_activity_at = Column(DateTime)
    
    # Additional profile data (JSON)
    additional_info = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index('idx_user_profile_email', 'email'),
        Index('idx_user_profile_username', 'username'),
        Index('idx_user_profile_phone', 'phone_number'),
        Index('idx_user_profile_status', 'status'),
    )
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_display_name(self) -> str:
        """Get name for display purposes"""
        return self.get_full_name() or self.username
    
    def get_formatted_phone(self) -> str:
        """Get formatted phone number"""
        if not self.phone_number:
            return ""
        # Simple US phone formatting
        digits = ''.join(filter(str.isdigit, self.phone_number))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return self.phone_number
    
    def get_address_string(self) -> str:
        """Get formatted address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state_province} {self.postal_code}" if self.city and self.state_province else None,
            self.country
        ]
        return ", ".join(filter(None, address_parts))
    
    def is_verified(self) -> bool:
        """Check if user is fully verified"""
        return self.email_verified and self.phone_verified and self.kyc_verified
    
    def can_access_feature(self, feature: str) -> bool:
        """Check if user can access specific features based on account type"""
        feature_access = {
            AccountType.INDIVIDUAL_ACCOUNT.value: ['basic_banking', 'transfers', 'payments'],
            AccountType.BUSINESS_CLIENT.value: ['basic_banking', 'transfers', 'payments', 'business_accounts', 'api_access'],
            AccountType.PARTNER_PROGRAM.value: ['all_features']
        }
        
        allowed_features = feature_access.get(self.account_type, [])
        return feature in allowed_features or 'all_features' in allowed_features
    
    def __repr__(self):
        return f"<UserProfile {self.get_full_name()}>"

class UserDocument(db.Model):
    """User documents for KYC and identity verification"""
    __tablename__ = 'user_documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User association
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Document information
    document_type = Column(String(50), nullable=False)  # passport, driver_license, utility_bill, etc.
    document_number = Column(String(100))
    issuing_authority = Column(String(200))
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Document status
    verification_status = Column(String(20), default='pending')  # pending, verified, rejected, expired
    verification_date = Column(DateTime)
    verification_notes = Column(Text)
    
    # File information
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(50))
    
    # Security and metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_from_ip = Column(String(45))
    document_hash = Column(String(128))  # For integrity verification
    
    # Relationships
    user = relationship("User", back_populates="documents")
    
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    def __repr__(self):
        return f"<UserDocument {self.document_type} for User {self.user_id}>"

class UserSession(db.Model):
    """User session tracking for security and analytics"""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User association
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Session information
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    session_token = Column(String(500))
    
    # Session metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_fingerprint = Column(String(255))
    location = Column(String(200))
    
    # Session status
    is_active = Column(Boolean, default=True)
    login_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime)
    
    # Security flags
    is_suspicious = Column(Boolean, default=False)
    security_score = Column(Numeric(5, 2), default=100.00)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired"""
        if not self.is_active or self.logout_time:
            return True
        
        if self.last_activity:
            expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
            return datetime.utcnow() > expiry_time
        
        return False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserSession {self.session_id} for User {self.user_id}>"

class UserPreference(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User association
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Display preferences
    theme = Column(String(20), default='light')  # light, dark, auto
    language = Column(String(10), default='en')
    time_zone = Column(String(50), default='UTC')
    currency = Column(String(3), default='USD')
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    
    # Security preferences
    two_factor_enabled = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=30)  # minutes
    login_alerts = Column(Boolean, default=True)
    
    # Banking preferences
    default_account_id = Column(String(50))
    transaction_limit_alerts = Column(Boolean, default=True)
    monthly_statement_delivery = Column(String(20), default='email')  # email, mail, both
    
    # Dashboard preferences
    dashboard_layout = Column(JSONB, default=dict)
    favorite_features = Column(ARRAY(String), default=list)
    quick_actions = Column(ARRAY(String), default=list)
    
    # Privacy preferences
    data_sharing_consent = Column(Boolean, default=False)
    analytics_tracking = Column(Boolean, default=True)
    
    # Additional preferences (JSON)
    custom_settings = Column(JSONB, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences", uselist=False)
    
    def get_preference(self, key: str, default=None):
        """Get a custom preference value"""
        return self.custom_settings.get(key, default)
    
    def set_preference(self, key: str, value):
        """Set a custom preference value"""
        if not self.custom_settings:
            self.custom_settings = {}
        self.custom_settings[key] = value
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserPreference for User {self.user_id}>"

class SupportTicket(db.Model):
    """Support tickets for user assistance"""
    __tablename__ = 'support_tickets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User association
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Ticket information
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50))  # account, technical, billing, general
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Status tracking
    status = Column(String(20), default='open')  # open, in_progress, resolved, closed
    assigned_agent_id = Column(Integer, ForeignKey('users.id'))
    
    # Resolution information
    resolution = Column(Text)
    resolution_date = Column(DateTime)
    satisfaction_rating = Column(Integer)  # 1-5 scale
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
    
    def __repr__(self):
        return f"<SupportTicket {self.ticket_number}: {self.subject}>"