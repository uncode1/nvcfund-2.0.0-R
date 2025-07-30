"""
Banking Models
Core banking account models and transaction types for the banking module
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

from modules.core.extensions import db

class BankAccountType(Enum):
    """Bank account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    INVESTMENT = "investment"
    MONEY_MARKET = "money_market"
    CERTIFICATE_DEPOSIT = "certificate_deposit"

class BankAccountStatus(Enum):
    """Bank account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"
    PENDING_APPROVAL = "pending_approval"

class TransactionType(Enum):
    """Transaction types for banking operations"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    REFUND = "refund"
    REVERSAL = "reversal"
    ADJUSTMENT = "adjustment"

class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"

class BankAccount(db.Model):
    """Bank accounts owned by users"""
    __tablename__ = 'bank_accounts'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    
    # Account identification
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    account_type = Column(String(50), nullable=False)  # checking, savings, business, investment
    account_name = Column(String(200), nullable=False)
    
    # Account holder - references core User model
    account_holder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Account status
    status = Column(String(20), default='active')  # active, inactive, frozen, closed
    opening_date = Column(DateTime, default=datetime.utcnow)
    closing_date = Column(DateTime)
    
    # Financial details
    currency = Column(String(3), default='USD')
    current_balance = Column(Numeric(18, 2), default=0.00)
    available_balance = Column(Numeric(18, 2), default=0.00)
    pending_balance = Column(Numeric(18, 2), default=0.00)
    
    # Account limits and controls
    daily_withdrawal_limit = Column(Numeric(18, 2), default=1000.00)
    daily_transfer_limit = Column(Numeric(18, 2), default=5000.00)
    overdraft_limit = Column(Numeric(18, 2), default=0.00)
    minimum_balance = Column(Numeric(18, 2), default=0.00)
    
    # Interest and fees
    interest_rate = Column(Numeric(8, 4), default=0.0000)
    monthly_fee = Column(Numeric(8, 2), default=0.00)
    overdraft_fee = Column(Numeric(8, 2), default=35.00)
    
    # Digital features
    online_banking_enabled = Column(Boolean, default=True)
    mobile_banking_enabled = Column(Boolean, default=True)
    card_access_enabled = Column(Boolean, default=True)
    wire_transfer_enabled = Column(Boolean, default=False)
    
    # Risk and compliance
    fraud_monitoring_enabled = Column(Boolean, default=True)
    large_transaction_alerts = Column(Boolean, default=True)
    foreign_transaction_alerts = Column(Boolean, default=True)
    
    # Account metadata
    branch_code = Column(String(10))
    routing_number = Column(String(20))
    swift_code = Column(String(20))
    iban = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime)
    
    # Relationship to User model
    account_holder = relationship("User", backref="banking_accounts")
    
    def __repr__(self):
        return f"<BankAccount {self.account_number} - {self.account_type}>"

# Set the Account alias in core models to avoid circular imports
from ..core import models as core_models
core_models.Account = BankAccount

class Transaction(db.Model):
    """Banking transaction model"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Transaction details
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')

    # Account information
    account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    from_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)
    to_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=True)

    # External accounts
    external_account_number = Column(String(50), nullable=True)
    routing_number = Column(String(20), nullable=True)

    # Processing
    status = Column(String(20), nullable=False, default=TransactionStatus.PENDING.value)
    reference_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)

    # User tracking
    initiated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Processing timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    initiated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Additional transaction metadata
    merchant_name = Column(String(100), nullable=True)
    merchant_category = Column(String(50), nullable=True)
    location = Column(String(200), nullable=True)
    channel = Column(String(20), nullable=True)  # ATM, online, mobile, branch
    fee_amount = Column(Numeric(10, 2), nullable=True)
    fee_description = Column(String(100), nullable=True)

    # Relationships
    account = relationship("BankAccount", foreign_keys=[account_id], backref="transactions")
    from_account = relationship("BankAccount", foreign_keys=[from_account_id])
    to_account = relationship("BankAccount", foreign_keys=[to_account_id])
    initiated_by_user = relationship("User", foreign_keys=[initiated_by], backref="initiated_transactions")

    # Indexes
    __table_args__ = (
        Index('idx_transaction_account', 'account_id'),
        Index('idx_transaction_type', 'transaction_type'),
        Index('idx_transaction_status', 'status'),
        Index('idx_transaction_created', 'created_at'),
        Index('idx_transaction_reference', 'reference_number'),
    )

    def __repr__(self):
        return f'<Transaction {self.transaction_id}: {self.transaction_type} ${self.amount}>'

class DigitalAssetAccount(db.Model):
    """Digital asset accounts for cryptocurrency and tokens"""
    __tablename__ = 'digital_asset_accounts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Account identification
    account_holder_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    asset_symbol = Column(String(10), nullable=False)  # BTC, ETH, NVCT, etc.
    asset_name = Column(String(100), nullable=False)
    network = Column(String(50), nullable=False)  # ethereum, polygon, bsc, etc.
    
    # Wallet information
    wallet_address = Column(String(255), nullable=False, unique=True)
    public_key = Column(Text)
    
    # Account status
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime)
    
    # Balance information
    balance = Column(Numeric(36, 18), default=0.000000000000000000)
    pending_balance = Column(Numeric(36, 18), default=0.000000000000000000)
    
    # Account features
    staking_enabled = Column(Boolean, default=False)
    trading_enabled = Column(Boolean, default=True)
    transfer_enabled = Column(Boolean, default=True)
    
    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_digital_account_holder', 'account_holder_id'),
        Index('idx_digital_wallet_address', 'wallet_address'),
        Index('idx_digital_asset_symbol', 'asset_symbol'),
    )
    
    def __repr__(self):
        return f"<DigitalAssetAccount {self.asset_symbol} - {self.wallet_address[:10]}...>"

class DigitalAssetTransaction(db.Model):
    """Digital asset transaction records"""
    __tablename__ = 'digital_asset_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction identification
    transaction_hash = Column(String(255), unique=True, nullable=False)
    block_number = Column(Integer)
    block_hash = Column(String(255))
    
    # Account and network
    account_id = Column(UUID(as_uuid=True), ForeignKey('digital_asset_accounts.id'), nullable=False)
    network = Column(String(50), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # send, receive, stake, unstake, swap
    amount = Column(Numeric(36, 18), nullable=False)
    gas_fee = Column(Numeric(36, 18), default=0.000000000000000000)
    
    # Addresses
    from_address = Column(String(255))
    to_address = Column(String(255))
    
    # Status and timing
    status = Column(String(20), default='pending')
    confirmations = Column(Integer, default=0)
    required_confirmations = Column(Integer, default=12)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_digital_tx_hash', 'transaction_hash'),
        Index('idx_digital_tx_account', 'account_id'),
        Index('idx_digital_tx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<DigitalAssetTransaction {self.transaction_hash[:10]}... - {self.amount}>"