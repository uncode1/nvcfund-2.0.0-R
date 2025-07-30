"""
Interest Rate Management Models
Self-contained database models for rate management with foreign key relationships
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# Import centralized database instance
from modules.core.extensions import db

class RateType(Enum):
    """Types of interest rates"""
    FEDERAL_FUNDS = "federal_funds"
    PRIME_RATE = "prime_rate"
    DISCOUNT_RATE = "discount_rate"
    TREASURY_YIELD = "treasury_yield"
    MORTGAGE_RATE = "mortgage_rate"
    PERSONAL_LOAN = "personal_loan"
    AUTO_LOAN = "auto_loan"
    BUSINESS_LOAN = "business_loan"
    DEPOSIT_RATE = "deposit_rate"
    CREDIT_CARD = "credit_card"
    MONEY_MARKET = "money_market"
    CERTIFICATE_DEPOSIT = "certificate_deposit"

class ProductCategory(Enum):
    """Product categories for rate classification"""
    FEDERAL_POLICY = "federal_policy"
    CONSUMER_LENDING = "consumer_lending"
    COMMERCIAL_LENDING = "commercial_lending"
    DEPOSIT_PRODUCTS = "deposit_products"
    CREDIT_PRODUCTS = "credit_products"
    INVESTMENT_PRODUCTS = "investment_products"

class ApprovalLevel(Enum):
    """Approval levels for rate changes"""
    TREASURY_OFFICER = "treasury_officer"
    ASSET_LIABILITY_MANAGER = "asset_liability_manager"
    CFO = "cfo"
    BOARD_MEMBER = "board_member"
    MONETARY_POLICY_COMMITTEE = "monetary_policy_committee"

class RateChangeStatus(Enum):
    """Status of rate change requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"

class InterestRateProduct(db.Model):
    """Interest rate products and their current rates"""
    __tablename__ = 'interest_rate_products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product identification
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    rate_type = Column(String(50), nullable=False)
    product_category = Column(String(50), nullable=False)
    
    # Current rate details
    current_rate = Column(Numeric(8, 6), nullable=False)  # Current effective rate
    base_rate = Column(Numeric(8, 6), nullable=False)     # Base rate component
    margin = Column(Numeric(8, 6), default=0.000000)     # Additional margin
    
    # Rate constraints
    minimum_rate = Column(Numeric(8, 6))
    maximum_rate = Column(Numeric(8, 6))
    rate_floor = Column(Numeric(8, 6))
    rate_ceiling = Column(Numeric(8, 6))
    
    # Product attributes
    term_months = Column(Integer)  # Product term in months
    credit_tier = Column(String(20))  # excellent, good, fair, poor
    balance_tier = Column(String(50))  # Balance requirements
    
    # Approval requirements
    required_approval_level = Column(String(50), nullable=False)
    maximum_change_allowed = Column(Numeric(8, 6), default=0.500000)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    is_promotional = Column(Boolean, default=False)
    promotional_end_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_rate_change = Column(DateTime)
    
    # Relationships
    rate_changes = relationship("RateChangeRequest", back_populates="product")
    rate_history = relationship("RateHistory", back_populates="product")
    
    def __repr__(self):
        return f"<InterestRateProduct {self.product_code}: {self.current_rate}%>"

class RateChangeRequest(db.Model):
    """Rate change requests with approval workflow"""
    __tablename__ = 'rate_change_requests'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request details
    product_id = Column(UUID(as_uuid=True), ForeignKey('interest_rate_products.id'), nullable=False)
    requested_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Rate change details
    current_rate = Column(Numeric(8, 6), nullable=False)
    requested_rate = Column(Numeric(8, 6), nullable=False)
    rate_change_amount = Column(Numeric(8, 6), nullable=False)
    rate_change_percentage = Column(Numeric(8, 6), nullable=False)
    
    # Request metadata
    justification = Column(Text, nullable=False)
    market_analysis = Column(Text)
    competitive_analysis = Column(Text)
    profitability_impact = Column(Text)
    customer_impact = Column(Text)
    
    # Effective dates
    requested_effective_date = Column(DateTime, nullable=False)
    approved_effective_date = Column(DateTime)
    
    # Request type and urgency
    change_type = Column(String(50), nullable=False)  # regular, promotional, emergency
    urgency_level = Column(String(20), default='normal')  # low, normal, high, emergency
    
    # Approval workflow
    required_approval_level = Column(String(50), nullable=False)
    current_approval_level = Column(String(50))
    status = Column(String(20), default=RateChangeStatus.PENDING.value)
    
    # Fed policy correlation
    fed_policy_correlation = Column(String(50))
    market_condition_factor = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("InterestRateProduct", back_populates="rate_changes")
    requester = relationship("User", foreign_keys=[requested_by])
    approvals = relationship("RateChangeApproval", back_populates="request")
    
    @validates('requested_rate')
    def validate_requested_rate(self, key, value):
        """Validate requested rate is within acceptable bounds"""
        if value < 0:
            raise ValueError("Interest rate cannot be negative")
        if value > 50:
            raise ValueError("Interest rate cannot exceed 50%")
        return value
    
    def __repr__(self):
        return f"<RateChangeRequest {self.id}: {self.current_rate}% → {self.requested_rate}%>"

class RateChangeApproval(db.Model):
    """Approval records for rate change requests"""
    __tablename__ = 'rate_change_approvals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Approval details
    request_id = Column(UUID(as_uuid=True), ForeignKey('rate_change_requests.id'), nullable=False)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Approval decision
    approval_action = Column(String(20), nullable=False)  # approve, reject, request_revision
    approval_level = Column(String(50), nullable=False)
    approval_authority = Column(Numeric(8, 6), nullable=False)  # Max change authority
    
    # Approval metadata
    approval_notes = Column(Text, nullable=False)
    conditions = Column(Text)
    risk_assessment = Column(String(20))  # low, medium, high, very_high
    
    # Approval dates
    approval_date = Column(DateTime, default=datetime.utcnow)
    effective_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    request = relationship("RateChangeRequest", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_id])
    
    def __repr__(self):
        return f"<RateChangeApproval {self.approval_action}: {self.approval_level}>"

class RateHistory(db.Model):
    """Historical rate changes for audit and analysis"""
    __tablename__ = 'rate_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product and rate details
    product_id = Column(UUID(as_uuid=True), ForeignKey('interest_rate_products.id'), nullable=False)
    product_code = Column(String(50), nullable=False)  # Denormalized for performance
    
    # Rate change details
    previous_rate = Column(Numeric(8, 6), nullable=False)
    new_rate = Column(Numeric(8, 6), nullable=False)
    rate_change_amount = Column(Numeric(8, 6), nullable=False)
    rate_change_percentage = Column(Numeric(8, 6), nullable=False)
    
    # Change metadata
    change_reason = Column(String(100))
    change_type = Column(String(50))  # manual, automatic, policy_driven
    change_source = Column(String(50))  # fed_policy, market_condition, competitive
    
    # Approval details
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_level = Column(String(50))
    
    # Effective dates
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    
    # Market context
    fed_funds_rate = Column(Numeric(8, 6))  # Fed funds rate at time of change
    prime_rate = Column(Numeric(8, 6))      # Prime rate at time of change
    treasury_10_year = Column(Numeric(8, 6))  # 10-year treasury at time of change
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("InterestRateProduct", back_populates="rate_history")
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<RateHistory {self.product_code}: {self.previous_rate}% → {self.new_rate}%>"

class RateAuthorityMatrix(db.Model):
    """Authority matrix for rate changes by user role"""
    __tablename__ = 'rate_authority_matrix'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authority details
    user_role = Column(String(50), nullable=False)
    approval_level = Column(String(50), nullable=False)
    
    # Authority limits
    maximum_rate_change = Column(Numeric(8, 6), nullable=False)
    maximum_absolute_rate = Column(Numeric(8, 6))
    
    # Product restrictions
    allowed_product_categories = Column(JSONB)  # List of allowed categories
    restricted_products = Column(JSONB)         # List of restricted products
    
    # Additional constraints
    requires_dual_approval = Column(Boolean, default=False)
    emergency_authority = Column(Boolean, default=False)
    
    # Effective dates
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RateAuthorityMatrix {self.user_role}: {self.maximum_rate_change}%>"

class FederalRateTracking(db.Model):
    """Track federal rates and policy changes"""
    __tablename__ = 'federal_rate_tracking'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Federal rate details
    federal_funds_rate = Column(Numeric(8, 6), nullable=False)
    discount_rate = Column(Numeric(8, 6), nullable=False)
    prime_rate = Column(Numeric(8, 6), nullable=False)
    
    # Treasury yields
    treasury_3_month = Column(Numeric(8, 6))
    treasury_6_month = Column(Numeric(8, 6))
    treasury_1_year = Column(Numeric(8, 6))
    treasury_2_year = Column(Numeric(8, 6))
    treasury_5_year = Column(Numeric(8, 6))
    treasury_10_year = Column(Numeric(8, 6))
    treasury_30_year = Column(Numeric(8, 6))
    
    # SOFR rates
    sofr_overnight = Column(Numeric(8, 6))
    sofr_30_day = Column(Numeric(8, 6))
    sofr_90_day = Column(Numeric(8, 6))
    
    # Policy context
    fomc_meeting_date = Column(DateTime)
    policy_stance = Column(String(50))  # hawkish, dovish, neutral
    policy_statement = Column(Text)
    
    # Market indicators
    inflation_rate = Column(Numeric(8, 6))
    unemployment_rate = Column(Numeric(8, 6))
    gdp_growth = Column(Numeric(8, 6))
    
    # Timestamps
    effective_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FederalRateTracking {self.effective_date}: Fed {self.federal_funds_rate}%>"

class CompetitorRateMonitoring(db.Model):
    """Monitor competitor rates for market positioning"""
    __tablename__ = 'competitor_rate_monitoring'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Competitor details
    competitor_name = Column(String(200), nullable=False)
    competitor_type = Column(String(50))  # bank, credit_union, fintech
    market_tier = Column(String(20))  # tier_1, tier_2, regional, local
    
    # Rate details
    product_type = Column(String(50), nullable=False)
    competitor_rate = Column(Numeric(8, 6), nullable=False)
    our_rate = Column(Numeric(8, 6), nullable=False)
    rate_differential = Column(Numeric(8, 6), nullable=False)
    
    # Additional terms
    minimum_balance = Column(Numeric(18, 2))
    promotional_rate = Column(Boolean, default=False)
    promotional_period = Column(Integer)  # Days
    
    # Competitive position
    market_position = Column(String(20))  # leading, competitive, lagging
    recommended_action = Column(String(50))
    
    # Data collection
    data_source = Column(String(100))
    collection_method = Column(String(50))  # web_scraping, manual, api
    
    # Timestamps
    rate_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompetitorRateMonitoring {self.competitor_name}: {self.competitor_rate}%>"

# Create indexes for optimal query performance
Index('idx_interest_rate_products_code', InterestRateProduct.product_code)
Index('idx_interest_rate_products_category', InterestRateProduct.product_category)
Index('idx_interest_rate_products_rate_type', InterestRateProduct.rate_type)
Index('idx_rate_change_requests_product_id', RateChangeRequest.product_id)
Index('idx_rate_change_requests_requested_by', RateChangeRequest.requested_by)
Index('idx_rate_change_requests_status', RateChangeRequest.status)
Index('idx_rate_change_requests_created_at', RateChangeRequest.created_at)
Index('idx_rate_change_approvals_request_id', RateChangeApproval.request_id)
Index('idx_rate_change_approvals_approver_id', RateChangeApproval.approver_id)
Index('idx_rate_history_product_id', RateHistory.product_id)
Index('idx_rate_history_effective_from', RateHistory.effective_from)
Index('idx_rate_history_product_code', RateHistory.product_code)
Index('idx_federal_rate_tracking_effective_date', FederalRateTracking.effective_date)
Index('idx_competitor_rate_monitoring_competitor_name', CompetitorRateMonitoring.competitor_name)
Index('idx_competitor_rate_monitoring_product_type', CompetitorRateMonitoring.product_type)
Index('idx_competitor_rate_monitoring_rate_date', CompetitorRateMonitoring.rate_date)