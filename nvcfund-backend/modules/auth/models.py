"""
Authentication Models
Self-contained models for user management, KYC, and authentication
"""

import logging
from datetime import datetime, timezone
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

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Enhanced user roles for comprehensive banking operations"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TREASURY_OFFICER = "treasury_officer"
    SOVEREIGN_BANKER = "sovereign_banker"
    CENTRAL_BANK_GOVERNOR = "central_bank_governor"
    ASSET_LIABILITY_MANAGER = "asset_liability_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    RISK_MANAGER = "risk_manager"
    INSTITUTIONAL_BANKER = "institutional_banker"
    CORRESPONDENT_BANKER = "correspondent_banker"
    BRANCH_MANAGER = "branch_manager"
    CUSTOMER_SERVICE = "customer_service"
    BUSINESS_USER = "business_user"
    STANDARD_USER = "standard_user"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, UserRole):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __hash__(self):
        return hash(self.value)
    
    @property
    def display_name(self):
        """Return a human-readable display name for the role"""
        return self.value.replace('_', ' ').title()
    
    @classmethod
    def get_privileged_roles(cls):
        """Return list of privileged administrative roles"""
        return [
            cls.SUPER_ADMIN, cls.ADMIN, cls.TREASURY_OFFICER,
            cls.SOVEREIGN_BANKER, cls.CENTRAL_BANK_GOVERNOR,
            cls.ASSET_LIABILITY_MANAGER, cls.COMPLIANCE_OFFICER,
            cls.RISK_MANAGER, cls.INSTITUTIONAL_BANKER
        ]
    
    @classmethod
    def get_admin_roles(cls):
        """Return list of admin-level roles"""
        return [cls.SUPER_ADMIN, cls.ADMIN]
    
    @classmethod
    def get_treasury_roles(cls):
        """Return list of treasury-related roles"""
        return [cls.TREASURY_OFFICER, cls.ASSET_LIABILITY_MANAGER]

class AccountType(Enum):
    """Account types for different customer segments"""
    INDIVIDUAL = "individual"
    BUSINESS_CLIENT = "business_client"
    PARTNER_PROGRAM = "partner_program"
    CENTRAL_BANK = "central_bank"
    SOVEREIGN_ENTITY = "sovereign_entity"
    ISLAMIC_BANKING = "islamic_banking"

class KYCStatus(Enum):
    """KYC verification status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REQUIRES_UPDATE = "requires_update"

class User(UserMixin, db.Model):
    """Enhanced user model with comprehensive banking roles"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    # Store role as string in database, but work with Enum in Python
    _role = Column('role', String(50), nullable=False, default=UserRole.STANDARD_USER.value)
    account_type = Column(String(50), nullable=False, default=AccountType.INDIVIDUAL.value)
    
    # Profile information - matching actual database schema
    first_name = Column(String(200))
    last_name = Column(String(200))
    middle_name = Column(String(200))
    phone_number = Column(String(20))
    date_of_birth = Column(DateTime)
    nationality = Column(String(100))
    
    # Address information
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Additional verification fields
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    kyc_status = Column(String(20), default='pending')  # pending, in_review, approved, rejected, expired
    
    # User metrics
    login_count = Column(Integer, default=0)
    credit_score = Column(Integer)
    risk_rating = Column(String(20))
    customer_since = Column(DateTime)
    last_transaction_date = Column(DateTime)
    locked_until = Column(DateTime)
    user_uuid = Column(String(255))
    permissions = Column(Text)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Authentication metadata
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime)
    account_locked_until = Column(DateTime)
    
    # Session management  
    last_activity = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships within auth module
    kyc_records = relationship("KYCVerification", back_populates="user", foreign_keys="KYCVerification.user_id")
    session_logs = relationship("UserSessionLog", back_populates="user")
    
    # Cross-module relationships - handled via core models
    # These relationships are defined in core models to avoid circular imports
    # trading_accounts = relationship("TradingAccount", back_populates="user")
    
    @property
    def role(self):
        """Convert string from DB to UserRole Enum object"""
        try:
            return UserRole(self._role)
        except ValueError:
            # Fallback to STANDARD_USER if invalid role in database
            return UserRole.STANDARD_USER

    @role.setter
    def role(self, role_enum):
        """Set role using UserRole Enum object or string"""
        if isinstance(role_enum, UserRole):
            self._role = role_enum.value
        elif isinstance(role_enum, str):
            # Validate the string is a valid role
            try:
                role_obj = UserRole(role_enum)
                self._role = role_obj.value
            except ValueError:
                raise ValueError(f"Invalid role: {role_enum}. Must be a valid UserRole.")
        else:
            raise ValueError("Role must be a UserRole Enum member or valid string")
    
    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check password against hash - supports multiple hash formats"""
        # Handle scrypt format password hashes (existing database format)
        if self.password_hash.startswith('scrypt:'):
            try:
                # Parse scrypt format: scrypt:n:r:p$salt$hash
                parts = self.password_hash.split('$')
                if len(parts) >= 3:
                    from hashlib import scrypt
                    import base64
                    
                    # Extract parameters from format like 'scrypt:32768:8:1'
                    scrypt_header = parts[0]  # scrypt:32768:8:1
                    salt_b64 = parts[1]       # base64 encoded salt
                    stored_hash_b64 = parts[2]  # base64 encoded hash
                    
                    # Parse scrypt parameters
                    scrypt_params = scrypt_header.split(':')
                    if len(scrypt_params) == 4 and scrypt_params[0] == 'scrypt':
                        n = int(scrypt_params[1])
                        r = int(scrypt_params[2])
                        p = int(scrypt_params[3])
                        
                        # Decode salt and stored hash
                        salt = base64.b64decode(salt_b64.encode('ascii'))
                        stored_hash = base64.b64decode(stored_hash_b64.encode('ascii'))
                        
                        # Compute hash for provided password
                        computed_hash = scrypt(
                            password.encode('utf-8'),
                            salt=salt,
                            n=n,
                            r=r,
                            p=p,
                            dklen=len(stored_hash)
                        )
                        
                        # Compare hashes securely
                        import hmac
                        return hmac.compare_digest(stored_hash, computed_hash)
                        
            except (ValueError, TypeError, ImportError) as e:
                logger.warning(f"Error processing scrypt password hash: {e}")
                return False
        
        # Fall back to standard Werkzeug password check for modern hashes
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has specific role"""
        return self.role == role
    
    def is_privileged_user(self) -> bool:
        """Check if user has privileged access"""
        return self.role in UserRole.get_privileged_roles()
    
    def get_session_timeout(self) -> int:
        """Get role-based session timeout"""
        timeouts = {
            UserRole.SUPER_ADMIN: 10,
            UserRole.ADMIN: 10,
            UserRole.TREASURY_OFFICER: 12,
            UserRole.ASSET_LIABILITY_MANAGER: 12,
            UserRole.COMPLIANCE_OFFICER: 12,
            UserRole.SOVEREIGN_BANKER: 15,
            UserRole.CENTRAL_BANK_GOVERNOR: 15,
        }
        return timeouts.get(self.role, 15)  # Default 15 minutes
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def __repr__(self):
        return f"<User {self.username}: {self.role}>"

class KYCVerification(db.Model):
    """KYC verification records and compliance tracking"""
    __tablename__ = 'kyc_verifications'
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # KYC status and level
    verification_level = Column(String(20), nullable=False)  # basic, enhanced, enhanced_dd
    status = Column(String(20), default='pending')
    
    # Personal information verification
    identity_document_type = Column(String(50))  # passport, drivers_license, national_id
    identity_document_number = Column(String(100))
    identity_document_expiry = Column(DateTime)
    identity_verified = Column(Boolean, default=False)
    
    # Address verification
    proof_of_address_type = Column(String(50))  # utility_bill, bank_statement, lease
    address_verified = Column(Boolean, default=False)
    
    # Enhanced verification (for business and partner accounts)
    business_registration_number = Column(String(100))
    tax_identification_number = Column(String(50))
    business_license_number = Column(String(100))
    business_verified = Column(Boolean, default=False)
    
    # Financial verification
    income_verification_type = Column(String(50))
    income_amount = Column(Numeric(18, 2))
    source_of_funds = Column(String(200))
    financial_verified = Column(Boolean, default=False)
    
    # Compliance and risk assessment
    risk_score = Column(Integer)  # 1-100 scale
    risk_category = Column(String(20))  # low, medium, high
    sanctions_check_passed = Column(Boolean, default=False)
    pep_check_passed = Column(Boolean, default=False)  # Politically Exposed Person
    
    # Verification metadata
    verified_by = Column(Integer, ForeignKey('users.id'))
    verification_notes = Column(Text)
    compliance_officer_notes = Column(Text)
    
    # Document tracking
    documents_uploaded = Column(JSONB)  # List of document types uploaded
    documents_verified = Column(JSONB)  # List of verified documents
    
    # Dates
    verification_date = Column(DateTime)
    expiry_date = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="kyc_records", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by], post_update=True)
    
    def is_verification_current(self) -> bool:
        """Check if KYC verification is still current"""
        if self.expiry_date:
            return datetime.utcnow() < self.expiry_date
        return True
    
    def requires_renewal(self) -> bool:
        """Check if KYC requires renewal"""
        if self.next_review_date:
            return datetime.utcnow() >= self.next_review_date
        return False
    
    def __repr__(self):
        return f"<KYCVerification {self.user_id}: {self.status}>"

class UserSessionLog(db.Model):
    """User session tracking for security and audit"""
    __tablename__ = 'user_session_logs'
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Session details
    session_id = Column(String(255), unique=True, nullable=False)
    login_timestamp = Column(DateTime, nullable=False)
    logout_timestamp = Column(DateTime)
    session_duration_minutes = Column(Integer)
    
    # Login details
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    login_method = Column(String(50))  # password, sso, api_key
    
    # Session status
    login_successful = Column(Boolean, default=True)
    logout_reason = Column(String(50))  # user_logout, timeout, forced_logout, system_shutdown
    
    # Security context
    device_fingerprint = Column(String(255))
    geolocation = Column(JSONB)  # {country, city, lat, lon}
    is_suspicious_activity = Column(Boolean, default=False)
    security_flags = Column(JSONB)  # JSON array of security flags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="session_logs")
    
    def calculate_session_duration(self):
        """Calculate session duration if logout timestamp exists"""
        if self.logout_timestamp:
            duration = self.logout_timestamp - self.login_timestamp
            self.session_duration_minutes = int(duration.total_seconds() / 60)
    
    def __repr__(self):
        return f"<UserSessionLog {self.user_id}: {self.login_timestamp}>"

class ComplianceAction(db.Model):
    """Compliance actions and regulatory requirements"""
    __tablename__ = 'compliance_actions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # kyc_review, aml_check, sanctions_screening
    action_category = Column(String(50), nullable=False)  # routine, triggered, regulatory
    
    # Action trigger
    trigger_reason = Column(String(200))
    trigger_event = Column(String(100))
    automatic_trigger = Column(Boolean, default=False)
    
    # Action status
    status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    
    # Assignment and workflow
    assigned_to = Column(Integer, ForeignKey('users.id'))
    assigned_date = Column(DateTime)
    completed_by = Column(Integer, ForeignKey('users.id'))
    completion_date = Column(DateTime)
    
    # Action details
    action_description = Column(Text)
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Regulatory requirements
    regulatory_requirement = Column(String(100))  # BSA, AML, KYC, PATRIOT_ACT
    compliance_deadline = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    completer = relationship("User", foreign_keys=[completed_by])
    
    def is_overdue(self) -> bool:
        """Check if compliance action is overdue"""
        if self.compliance_deadline and self.status not in ['completed']:
            return datetime.utcnow() > self.compliance_deadline
        return False
    
    def __repr__(self):
        return f"<ComplianceAction {self.action_type}: {self.status}>"

class RolePermission(db.Model):
    """Role-based permissions for fine-grained access control"""
    __tablename__ = 'role_permissions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Role and permission details
    user_role = Column(String(50), nullable=False)
    permission_category = Column(String(50), nullable=False)  # banking, admin, treasury, etc.
    permission_name = Column(String(100), nullable=False)
    
    # Permission scope
    can_read = Column(Boolean, default=False)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)
    
    # Additional constraints
    resource_constraints = Column(JSONB)  # Additional permission constraints
    amount_limits = Column(JSONB)  # Financial limits by permission
    
    # Effective dates
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RolePermission {self.user_role}: {self.permission_name}>"

# Create indexes for optimal query performance
Index('idx_users_username', User.username)
Index('idx_users_email', User.email)
Index('idx_users_role', User._role)
Index('idx_users_account_type', User.account_type)
Index('idx_users_kyc_status', User.kyc_status)
Index('idx_kyc_verifications_user_id', KYCVerification.user_id)
Index('idx_kyc_verifications_status', KYCVerification.status)
Index('idx_kyc_verifications_verification_level', KYCVerification.verification_level)
Index('idx_user_session_logs_user_id', UserSessionLog.user_id)
Index('idx_user_session_logs_session_id', UserSessionLog.session_id)
Index('idx_user_session_logs_login_timestamp', UserSessionLog.login_timestamp)
Index('idx_compliance_actions_user_id', ComplianceAction.user_id)
Index('idx_compliance_actions_status', ComplianceAction.status)
Index('idx_compliance_actions_assigned_to', ComplianceAction.assigned_to)
Index('idx_role_permissions_user_role', RolePermission.user_role)
Index('idx_role_permissions_permission_category', RolePermission.permission_category)