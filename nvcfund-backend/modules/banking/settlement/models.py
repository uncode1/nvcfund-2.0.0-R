"""
Settlement Models
Self-contained models for payment settlement, SWIFT operations, and clearing systems
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

from modules.core.database import Base

class SettlementType(Enum):
    """Types of settlement operations"""
    RTGS = "rtgs"  # Real-Time Gross Settlement
    ACH = "ach"    # Automated Clearing House
    SWIFT = "swift" # SWIFT Network
    FEDWIRE = "fedwire" # Federal Reserve Wire Network
    CHIPS = "chips" # Clearing House Interbank Payments System
    SEPA = "sepa"  # Single Euro Payments Area
    TARGET2 = "target2" # Trans-European Automated Real-time Gross settlement Express Transfer system

class SettlementStatus(Enum):
    """Settlement transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SETTLED = "settled"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class SettlementTransaction(Base):
    """Core settlement transaction records"""
    __tablename__ = 'settlement_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction identification
    transaction_reference = Column(String(100), unique=True, nullable=False)
    settlement_type = Column(String(20), nullable=False)  # SettlementType
    
    # Financial details
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Parties involved
    sender_institution = Column(String(11))  # BIC code
    sender_account = Column(String(34))      # IBAN or account number
    sender_name = Column(String(200))
    
    receiver_institution = Column(String(11))  # BIC code
    receiver_account = Column(String(34))       # IBAN or account number
    receiver_name = Column(String(200))
    
    # Settlement details
    value_date = Column(DateTime, nullable=False)
    settlement_date = Column(DateTime)
    priority = Column(String(20), default='normal')  # high, normal, low
    
    # Network-specific details
    swift_message_type = Column(String(10))  # MT103, MT202, etc.
    swift_uetr = Column(String(36))          # Unique End-to-End Transaction Reference
    fedwire_imad = Column(String(20))        # Input Message Accountability Data
    chips_uid = Column(String(16))           # CHIPS Universal Identifier
    
    # Status and processing
    status = Column(String(20), default=SettlementStatus.PENDING.value)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Error handling
    error_code = Column(String(20))
    error_description = Column(Text)
    return_reason = Column(String(200))
    
    # Compliance and regulatory
    aml_status = Column(String(20), default='pending')
    sanctions_screening = Column(String(20), default='pending')
    regulatory_reporting = Column(Boolean, default=False)
    
    # Fees and charges
    settlement_fee = Column(Numeric(10, 4), default=0.0000)
    correspondent_charges = Column(Numeric(10, 4), default=0.0000)
    total_charges = Column(Numeric(10, 4), default=0.0000)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    swift_messages = relationship("SwiftMessage", back_populates="settlement_transaction")
    
    def __repr__(self):
        return f"<SettlementTransaction {self.transaction_reference}: {self.amount} {self.currency}>"

class SwiftMessage(Base):
    """SWIFT message processing and tracking"""
    __tablename__ = 'swift_messages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Message identification
    settlement_transaction_id = Column(UUID(as_uuid=True), ForeignKey('settlement_transactions.id'), nullable=False)
    message_type = Column(String(10), nullable=False)  # MT103, MT202, MT910, etc.
    swift_reference = Column(String(16), nullable=False)
    
    # Message routing
    sender_bic = Column(String(11), nullable=False)
    receiver_bic = Column(String(11), nullable=False)
    message_priority = Column(String(1), default='N')  # U (Urgent), N (Normal), S (System)
    
    # Message content
    message_text = Column(Text, nullable=False)
    structured_data = Column(JSONB)  # Parsed message fields
    
    # Network details
    session_number = Column(String(4))
    sequence_number = Column(String(6))
    input_time = Column(DateTime)
    output_time = Column(DateTime)
    
    # Processing status
    message_status = Column(String(20), default='created')  # created, sent, acknowledged, delivered, failed
    network_delivery_status = Column(String(20))
    
    # Acknowledgments and responses
    ack_received = Column(Boolean, default=False)
    ack_timestamp = Column(DateTime)
    nack_reason = Column(String(200))
    
    # Response messages
    response_message_type = Column(String(10))  # MT910, MT900, etc.
    response_received = Column(Boolean, default=False)
    response_timestamp = Column(DateTime)
    
    # Error handling
    error_code = Column(String(10))
    error_description = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    settlement_transaction = relationship("SettlementTransaction", back_populates="swift_messages")
    
    def __repr__(self):
        return f"<SwiftMessage {self.message_type}: {self.swift_reference}>"

class CorrespondentBank(Base):
    """Correspondent banking relationships and accounts"""
    __tablename__ = 'correspondent_banks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Bank identification
    bank_name = Column(String(200), nullable=False)
    bic_code = Column(String(11), unique=True, nullable=False)
    country_code = Column(String(2), nullable=False)
    
    # Contact information
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    
    # Account details
    nostro_account = Column(String(34))  # Our account with them
    vostro_account = Column(String(34))  # Their account with us
    
    # Relationship details
    relationship_type = Column(String(50))  # correspondent, agent, clearing
    currencies_supported = Column(ARRAY(String(3)))
    daily_settlement_limit = Column(Numeric(18, 2))
    
    # Operational status
    is_active = Column(Boolean, default=True)
    relationship_start_date = Column(DateTime)
    last_settlement_date = Column(DateTime)
    
    # Risk and compliance
    risk_rating = Column(String(20))  # low, medium, high
    compliance_status = Column(String(20), default='compliant')
    last_due_diligence = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Settlement statistics
    total_settlements_ytd = Column(Integer, default=0)
    total_volume_ytd = Column(Numeric(24, 2), default=0.00)
    average_settlement_time = Column(Integer)  # in minutes
    
    # Fees and charges
    standard_fee = Column(Numeric(10, 4), default=0.0000)
    priority_fee = Column(Numeric(10, 4), default=0.0000)
    investigation_fee = Column(Numeric(10, 4), default=0.0000)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CorrespondentBank {self.bank_name}: {self.bic_code}>"

class LiquidityPosition(Base):
    """Daily liquidity positions for settlement operations"""
    __tablename__ = 'liquidity_positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Position details
    position_date = Column(DateTime, nullable=False)
    currency = Column(String(3), nullable=False)
    account_type = Column(String(50), nullable=False)  # settlement, nostro, operational
    
    # Balance information
    opening_balance = Column(Numeric(18, 2), nullable=False)
    closing_balance = Column(Numeric(18, 2), nullable=False)
    intraday_peak = Column(Numeric(18, 2))
    intraday_low = Column(Numeric(18, 2))
    
    # Settlement flows
    incoming_settlements = Column(Numeric(18, 2), default=0.00)
    outgoing_settlements = Column(Numeric(18, 2), default=0.00)
    net_settlement_flow = Column(Numeric(18, 2), default=0.00)
    
    # Funding operations
    funding_received = Column(Numeric(18, 2), default=0.00)
    funding_provided = Column(Numeric(18, 2), default=0.00)
    overnight_funding = Column(Numeric(18, 2), default=0.00)
    
    # Liquidity metrics
    liquidity_coverage_ratio = Column(Numeric(8, 4))
    available_liquidity = Column(Numeric(18, 2))
    committed_liquidity = Column(Numeric(18, 2))
    stressed_liquidity_requirement = Column(Numeric(18, 2))
    
    # Operational limits
    minimum_balance_requirement = Column(Numeric(18, 2))
    maximum_exposure_limit = Column(Numeric(18, 2))
    early_warning_threshold = Column(Numeric(18, 2))
    
    # Risk indicators
    liquidity_risk_score = Column(Integer)  # 1-100 scale
    concentration_risk = Column(Numeric(8, 4))
    funding_risk = Column(String(20))  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LiquidityPosition {self.position_date}: {self.closing_balance} {self.currency}>"

class SettlementLimit(Base):
    """Settlement limits and controls"""
    __tablename__ = 'settlement_limits'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Limit identification
    limit_type = Column(String(50), nullable=False)  # daily, transaction, counterparty, currency
    limit_name = Column(String(200), nullable=False)
    
    # Scope and applicability
    currency = Column(String(3))
    counterparty_bic = Column(String(11))
    settlement_type = Column(String(20))
    
    # Limit values
    limit_amount = Column(Numeric(18, 2), nullable=False)
    utilized_amount = Column(Numeric(18, 2), default=0.00)
    available_amount = Column(Numeric(18, 2))
    
    # Threshold management
    warning_threshold = Column(Numeric(8, 4), default=80.0000)  # 80% warning
    breach_threshold = Column(Numeric(8, 4), default=95.0000)   # 95% breach
    
    # Time-based controls
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    reset_frequency = Column(String(20))  # daily, monthly, annual
    last_reset_date = Column(DateTime)
    
    # Status and monitoring
    is_active = Column(Boolean, default=True)
    breached = Column(Boolean, default=False)
    breach_count = Column(Integer, default=0)
    last_breach_date = Column(DateTime)
    
    # Authorization requirements
    override_required = Column(Boolean, default=False)
    authorized_by = Column(Integer, ForeignKey('users.id'))
    authorization_expiry = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    authorizer = relationship("User", foreign_keys=[authorized_by])
    
    def calculate_utilization_percentage(self) -> Decimal:
        """Calculate current utilization percentage"""
        if self.limit_amount > 0:
            return (self.utilized_amount / self.limit_amount) * 100
        return Decimal('0.00')
    
    def is_warning_breached(self) -> bool:
        """Check if warning threshold is breached"""
        return self.calculate_utilization_percentage() >= self.warning_threshold
    
    def is_limit_breached(self) -> bool:
        """Check if limit is breached"""
        return self.calculate_utilization_percentage() >= self.breach_threshold
    
    def __repr__(self):
        return f"<SettlementLimit {self.limit_name}: {self.utilized_amount}/{self.limit_amount}>"

class SettlementReconciliation(Base):
    """Settlement reconciliation and exception management"""
    __tablename__ = 'settlement_reconciliations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reconciliation details
    reconciliation_date = Column(DateTime, nullable=False)
    reconciliation_type = Column(String(50), nullable=False)  # daily, intraday, month_end
    
    # Scope
    currency = Column(String(3), nullable=False)
    account_identifier = Column(String(50))
    counterparty_bic = Column(String(11))
    
    # Reconciliation results
    expected_balance = Column(Numeric(18, 2), nullable=False)
    actual_balance = Column(Numeric(18, 2), nullable=False)
    difference = Column(Numeric(18, 2), nullable=False)
    
    # Transaction counts
    expected_transaction_count = Column(Integer)
    actual_transaction_count = Column(Integer)
    unmatched_transactions = Column(Integer, default=0)
    
    # Status and resolution
    reconciliation_status = Column(String(20), default='pending')  # pending, matched, unmatched, resolved
    exception_count = Column(Integer, default=0)
    resolution_notes = Column(Text)
    
    # Investigation details
    investigated_by = Column(Integer, ForeignKey('users.id'))
    investigation_start = Column(DateTime)
    investigation_completion = Column(DateTime)
    
    # Approval and sign-off
    approved_by = Column(Integer, ForeignKey('users.id'))
    approval_date = Column(DateTime)
    management_review_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investigator = relationship("User", foreign_keys=[investigated_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<SettlementReconciliation {self.reconciliation_date}: {self.difference} {self.currency}>"

# Create indexes for optimal query performance
Index('idx_settlement_transactions_reference', SettlementTransaction.transaction_reference)
Index('idx_settlement_transactions_status', SettlementTransaction.status)
Index('idx_settlement_transactions_value_date', SettlementTransaction.value_date)
Index('idx_settlement_transactions_currency', SettlementTransaction.currency)
Index('idx_swift_messages_message_type', SwiftMessage.message_type)
Index('idx_swift_messages_swift_reference', SwiftMessage.swift_reference)
Index('idx_swift_messages_status', SwiftMessage.message_status)
Index('idx_correspondent_banks_bic_code', CorrespondentBank.bic_code)
Index('idx_correspondent_banks_active', CorrespondentBank.is_active)
Index('idx_liquidity_positions_date_currency', LiquidityPosition.position_date, LiquidityPosition.currency)
Index('idx_settlement_limits_type', SettlementLimit.limit_type)
Index('idx_settlement_limits_active', SettlementLimit.is_active)
Index('idx_settlement_reconciliations_date', SettlementReconciliation.reconciliation_date)
Index('idx_settlement_reconciliations_status', SettlementReconciliation.reconciliation_status)