"""
Exchange Module Models - Self-Contained Models for Exchange Operations
NVC Banking Platform - Exchange Module

This module contains all database models specific to exchange operations,
making the Exchange module fully self-contained and modular.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, Numeric, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import relationship
import enum
import uuid
import logging

from modules.core.extensions import db

logger = logging.getLogger(__name__)

# Exchange Enumerations
class ExchangeType(enum.Enum):
    """Types of exchange operations"""
    INTERNAL_EXCHANGE = "INTERNAL_EXCHANGE"  # Internal NVC platform exchanges
    EXTERNAL_EXCHANGE = "EXTERNAL_EXCHANGE"  # External exchanges via Binance/other providers
    FIAT_TO_DIGITAL = "FIAT_TO_DIGITAL"
    DIGITAL_TO_FIAT = "DIGITAL_TO_FIAT"
    DIGITAL_TO_DIGITAL = "DIGITAL_TO_DIGITAL"
    FIAT_TO_FIAT = "FIAT_TO_FIAT"

class ExchangeStatus(enum.Enum):
    """Exchange transaction statuses"""
    PENDING = "PENDING"
    QUOTE_REQUESTED = "QUOTE_REQUESTED"
    QUOTE_ACCEPTED = "QUOTE_ACCEPTED"
    PROCESSING = "PROCESSING"
    FIAT_LOCKED = "FIAT_LOCKED"
    DIGITAL_LOCKED = "DIGITAL_LOCKED"
    CONVERTING = "CONVERTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class ExchangeProvider(enum.Enum):
    """Exchange service providers"""
    INTERNAL_LIQUIDITY = "INTERNAL_LIQUIDITY"
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    KRAKEN = "KRAKEN"
    UNISWAP = "UNISWAP"
    CIRCLE = "CIRCLE"
    CHAINLINK = "CHAINLINK"

# Exchange Models
class ExchangeRate(db.Model):
    """
    Real-time exchange rates between fiat currencies and digital assets
    Updated regularly from multiple sources for accurate pricing
    """
    __tablename__ = 'exchange_rates'
    __table_args__ = (
        Index('idx_exchange_from_to', 'from_currency', 'to_currency'),
        Index('idx_exchange_timestamp', 'timestamp'),
        Index('idx_exchange_provider', 'provider'),
        UniqueConstraint('from_currency', 'to_currency', 'provider', 'timestamp', name='uq_exchange_rate'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    rate_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Currency pair
    from_currency = Column(String(10), nullable=False)  # USD, EUR, NVCT, BTC, etc.
    to_currency = Column(String(10), nullable=False)
    
    # Rate information
    exchange_rate = Column(Numeric(28, 18), nullable=False)
    bid_rate = Column(Numeric(28, 18))  # Buy rate
    ask_rate = Column(Numeric(28, 18))  # Sell rate
    spread_percentage = Column(Numeric(8, 4))
    
    # Provider and timing
    provider = Column(SQLEnum(ExchangeProvider), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Market data
    volume_24h = Column(Numeric(28, 18))
    price_change_24h = Column(Numeric(8, 4))
    market_cap = Column(Numeric(28, 2))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency}/{self.to_currency}: {self.exchange_rate}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'rate_uuid': self.rate_uuid,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': float(self.exchange_rate),
            'bid_rate': float(self.bid_rate) if self.bid_rate else None,
            'ask_rate': float(self.ask_rate) if self.ask_rate else None,
            'spread_percentage': float(self.spread_percentage) if self.spread_percentage else None,
            'provider': self.provider.value,
            'timestamp': self.timestamp.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'volume_24h': float(self.volume_24h) if self.volume_24h else None,
            'price_change_24h': float(self.price_change_24h) if self.price_change_24h else None,
            'market_cap': float(self.market_cap) if self.market_cap else None
        }
    
    def is_valid(self):
        """Check if rate is still valid"""
        if not self.valid_until:
            return True
        return datetime.utcnow() < self.valid_until


class ExchangeTransaction(db.Model):
    """
    Exchange transactions between fiat and digital assets
    Coordinates between banking accounts and digital asset accounts
    """
    __tablename__ = 'exchange_transactions'
    __table_args__ = (
        Index('idx_exchange_tx_status', 'status'),
        Index('idx_exchange_tx_type', 'exchange_type'),
        Index('idx_exchange_tx_date', 'created_at'),
        Index('idx_exchange_user', 'user_id'),
        UniqueConstraint('transaction_uuid', name='uq_exchange_transaction_uuid'),
        CheckConstraint('from_amount > 0', name='chk_positive_from_amount'),
        CheckConstraint('to_amount >= 0', name='chk_non_negative_to_amount'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    transaction_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # User and transaction type
    user_id = Column(Integer, nullable=False)  # Reference to User table
    exchange_type = Column(SQLEnum(ExchangeType), nullable=False)
    
    # Account references (flexible for internal/external)
    from_account_id = Column(Integer)  # Source account ID
    to_account_id = Column(Integer)    # Destination account ID
    from_account_type = Column(String(20))  # 'bank_account', 'digital_account', 'external'
    to_account_type = Column(String(20))    # 'bank_account', 'digital_account', 'external'
    
    # Exchange details
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    from_amount = Column(Numeric(28, 18), nullable=False)
    to_amount = Column(Numeric(28, 18))
    
    # Exchange rate information
    exchange_rate = Column(Numeric(28, 18))
    quoted_rate = Column(Numeric(28, 18))
    executed_rate = Column(Numeric(28, 18))
    rate_provider = Column(SQLEnum(ExchangeProvider))
    quote_expires_at = Column(DateTime)
    
    # Fees
    fee_amount = Column(Numeric(28, 18), default=Decimal('0'))
    fee_currency = Column(String(10))
    exchange_fee = Column(Numeric(28, 18), default=Decimal('0'))
    network_fee = Column(Numeric(28, 18), default=Decimal('0'))
    platform_fee = Column(Numeric(28, 18), default=Decimal('0'))
    
    # Status and timing
    status = Column(SQLEnum(ExchangeStatus), default=ExchangeStatus.PENDING)
    quote_requested_at = Column(DateTime)
    quote_accepted_at = Column(DateTime)
    processing_started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # External exchange data
    external_transaction_id = Column(String(100))  # Binance order ID, etc.
    external_order_data = Column(Text)  # JSON data from external provider
    
    # Additional data
    notes = Column(Text)
    error_message = Column(Text)
    exchange_metadata = Column(Text)  # JSON metadata
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExchangeTransaction {self.transaction_uuid}: {self.from_amount} {self.from_currency} → {self.to_currency}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'transaction_uuid': self.transaction_uuid,
            'exchange_type': self.exchange_type,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'from_amount': float(self.from_amount),
            'to_amount': float(self.to_amount) if self.to_amount else None,
            'exchange_rate': float(self.exchange_rate) if self.exchange_rate else None,
            'quoted_rate': float(self.quoted_rate) if self.quoted_rate else None,
            'executed_rate': float(self.executed_rate) if self.executed_rate else None,
            'fee_amount': float(self.fee_amount) if self.fee_amount else 0.0,
            'fee_currency': self.fee_currency,
            'status': self.status,
            'external_transaction_id': self.external_transaction_id,
            'quote_expires_at': self.quote_expires_at.isoformat() if self.quote_expires_at else None,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
    
    def calculate_total_cost(self):
        """Calculate total cost including all fees"""
        total = self.from_amount or Decimal('0')
        total += self.exchange_fee or Decimal('0')
        total += self.network_fee or Decimal('0')
        total += self.platform_fee or Decimal('0')
        return total
    
    def is_quote_valid(self):
        """Check if quote is still valid"""
        if not self.quote_expires_at:
            return False
        return datetime.utcnow() < self.quote_expires_at
    
    def can_execute(self):
        """Check if exchange can be executed"""
        return (
            self.status == ExchangeStatus.QUOTE_ACCEPTED and
            self.is_quote_valid() and
            self.quoted_rate is not None
        )


class LiquidityPool(db.Model):
    """
    Internal liquidity pools for seamless exchange operations
    Maintains reserves of both fiat and digital assets
    """
    __tablename__ = 'liquidity_pools'
    __table_args__ = (
        Index('idx_liquidity_currency', 'currency'),
        Index('idx_liquidity_pool_type', 'pool_type'),
        Index('idx_liquidity_active', 'is_active'),
        CheckConstraint('total_reserves >= 0', name='chk_non_negative_total_reserves'),
        CheckConstraint('available_reserves >= 0', name='chk_non_negative_available_reserves'),
        CheckConstraint('locked_reserves >= 0', name='chk_non_negative_locked_reserves'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    pool_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Pool details
    pool_name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)  # USD, NVCT, BTC, etc.
    pool_type = Column(String(20), default='INTERNAL')  # INTERNAL, EXTERNAL, HYBRID
    
    # Reserves and limits
    total_reserves = Column(Numeric(28, 18), default=Decimal('0'))
    available_reserves = Column(Numeric(28, 18), default=Decimal('0'))
    locked_reserves = Column(Numeric(28, 18), default=Decimal('0'))
    minimum_reserves = Column(Numeric(28, 18), default=Decimal('0'))
    maximum_reserves = Column(Numeric(28, 18))
    
    # Pool configuration
    is_active = Column(Boolean, default=True)
    auto_rebalance = Column(Boolean, default=True)
    rebalance_threshold = Column(Numeric(8, 4), default=Decimal('10.0'))  # Percentage
    
    # Connected accounts (flexible references)
    fiat_account_id = Column(Integer)
    digital_account_id = Column(Integer)
    
    # Statistics
    total_volume_24h = Column(Numeric(28, 18), default=Decimal('0'))
    transaction_count_24h = Column(Integer, default=0)
    last_rebalance_date = Column(DateTime)
    
    # Health metrics
    health_score = Column(Numeric(5, 2), default=Decimal('100.0'))  # 0-100%
    utilization_rate = Column(Numeric(5, 2), default=Decimal('0.0'))  # 0-100%
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LiquidityPool {self.currency}: {self.available_reserves} available>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'pool_uuid': self.pool_uuid,
            'pool_name': self.pool_name,
            'currency': self.currency,
            'pool_type': self.pool_type,
            'total_reserves': float(self.total_reserves),
            'available_reserves': float(self.available_reserves),
            'locked_reserves': float(self.locked_reserves),
            'minimum_reserves': float(self.minimum_reserves),
            'maximum_reserves': float(self.maximum_reserves) if self.maximum_reserves else None,
            'is_active': self.is_active,
            'auto_rebalance': self.auto_rebalance,
            'rebalance_threshold': float(self.rebalance_threshold),
            'total_volume_24h': float(self.total_volume_24h),
            'transaction_count_24h': self.transaction_count_24h,
            'health_score': float(self.health_score),
            'utilization_rate': float(self.utilization_rate),
            'last_rebalance_date': self.last_rebalance_date.isoformat() if self.last_rebalance_date else None,
            'created_at': self.created_at.isoformat()
        }
    
    def calculate_utilization(self):
        """Calculate current utilization rate"""
        if self.total_reserves == 0:
            return Decimal('0.0')
        utilized = self.total_reserves - self.available_reserves
        return (utilized / self.total_reserves) * 100
    
    def needs_rebalancing(self):
        """Check if pool needs rebalancing"""
        if not self.auto_rebalance:
            return False
        current_utilization = self.calculate_utilization()
        return current_utilization > self.rebalance_threshold
    
    def calculate_health_score(self):
        """Calculate pool health score based on various metrics"""
        score = Decimal('100.0')
        
        # Deduct points for high utilization
        utilization = self.calculate_utilization()
        if utilization > 90:
            score -= Decimal('30.0')
        elif utilization > 75:
            score -= Decimal('15.0')
        elif utilization > 50:
            score -= Decimal('5.0')
        
        # Deduct points if below minimum reserves
        if self.available_reserves < self.minimum_reserves:
            score -= Decimal('40.0')
        
        # Deduct points if inactive
        if not self.is_active:
            score -= Decimal('50.0')
        
        return max(score, Decimal('0.0'))


class ExchangeAlert(db.Model):
    """
    Rate alerts for exchange operations
    Users can set alerts for specific rate targets
    """
    __tablename__ = 'exchange_alerts'
    __table_args__ = (
        Index('idx_alert_user', 'user_id'),
        Index('idx_alert_active', 'is_active'),
        Index('idx_alert_currency_pair', 'from_currency', 'to_currency'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    alert_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # User and alert details
    user_id = Column(Integer, nullable=False)
    from_currency = Column(String(10), nullable=False)
    to_currency = Column(String(10), nullable=False)
    
    # Alert criteria
    alert_type = Column(String(10), nullable=False)  # 'above', 'below'
    target_rate = Column(Numeric(28, 18), nullable=False)
    current_rate = Column(Numeric(28, 18))
    
    # Status and notifications
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    notification_sent = Column(Boolean, default=False)
    
    # Alert configuration
    expires_at = Column(DateTime)
    repeat_alert = Column(Boolean, default=False)
    notification_methods = Column(String(100))  # 'email,sms,push'
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExchangeAlert {self.from_currency}/{self.to_currency} {self.alert_type} {self.target_rate}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'alert_uuid': self.alert_uuid,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'alert_type': self.alert_type,
            'target_rate': float(self.target_rate),
            'current_rate': float(self.current_rate) if self.current_rate else None,
            'is_active': self.is_active,
            'is_triggered': self.is_triggered,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def check_trigger(self, current_rate):
        """Check if alert should be triggered"""
        if not self.is_active or self.is_triggered:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        self.current_rate = current_rate
        
        if self.alert_type == 'above':
            return current_rate >= self.target_rate
        elif self.alert_type == 'below':
            return current_rate <= self.target_rate
        
        return False