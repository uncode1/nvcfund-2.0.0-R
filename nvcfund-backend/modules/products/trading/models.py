"""
Trading Platform Models
Comprehensive models for securities, FX, commodities, derivatives, and portfolio management
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

class AssetClass(Enum):
    """Asset class categories"""
    EQUITIES = "equities"
    FIXED_INCOME = "fixed_income"
    FOREIGN_EXCHANGE = "foreign_exchange"
    COMMODITIES = "commodities"
    DERIVATIVES = "derivatives"
    ALTERNATIVES = "alternatives"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"

class InstrumentType(Enum):
    """Financial instrument types"""
    # Equities
    COMMON_STOCK = "common_stock"
    PREFERRED_STOCK = "preferred_stock"
    ETF = "etf"
    ADR = "adr"
    
    # Fixed Income
    GOVERNMENT_BOND = "government_bond"
    CORPORATE_BOND = "corporate_bond"
    MUNICIPAL_BOND = "municipal_bond"
    TREASURY_BILL = "treasury_bill"
    
    # FX
    SPOT_FX = "spot_fx"
    FX_FORWARD = "fx_forward"
    FX_SWAP = "fx_swap"
    
    # Commodities
    PRECIOUS_METALS = "precious_metals"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    INDUSTRIAL_METALS = "industrial_metals"
    
    # Derivatives
    FUTURES = "futures"
    OPTIONS = "options"
    SWAPS = "swaps"
    CFDS = "cfds"

class OrderType(Enum):
    """Trading order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"

class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    COVER = "cover"

class OrderStatus(Enum):
    """Order execution status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"

class TradingInstrument(Base):
    """Financial instruments available for trading"""
    __tablename__ = 'trading_instruments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    asset_class = Column(String(50), nullable=False)
    instrument_type = Column(String(50), nullable=False)
    
    # Market Data
    exchange = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    current_price = Column(Numeric(20, 8), nullable=True)
    bid_price = Column(Numeric(20, 8), nullable=True)
    ask_price = Column(Numeric(20, 8), nullable=True)
    last_update = Column(DateTime(timezone=True), nullable=True)
    
    # Contract Specifications
    contract_size = Column(Numeric(20, 8), default=1)
    tick_size = Column(Numeric(20, 8), default=0.01)
    minimum_quantity = Column(Numeric(20, 8), default=1)
    maximum_quantity = Column(Numeric(20, 8), nullable=True)
    
    # Trading Parameters
    margin_requirement = Column(Numeric(5, 4), default=0.1)  # 10% default
    is_tradeable = Column(Boolean, default=True)
    is_shortable = Column(Boolean, default=True)
    
    # Risk Parameters
    volatility = Column(Numeric(8, 6), nullable=True)
    beta = Column(Numeric(8, 6), nullable=True)
    risk_level = Column(String(20), default='moderate')
    
    # Market Information
    sector = Column(String(100), nullable=True)
    country = Column(String(50), nullable=True)
    rating = Column(String(10), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    trades = relationship("Trade", back_populates="instrument")
    positions = relationship("Position", back_populates="instrument")
    orders = relationship("TradingOrder", back_populates="instrument")
    
    __table_args__ = (
        Index('idx_instrument_symbol', 'symbol'),
        Index('idx_instrument_asset_class', 'asset_class'),
        Index('idx_instrument_exchange', 'exchange'),
    )

class TradingAccount(Base):
    """Trading accounts for different strategies and risk profiles"""
    __tablename__ = 'trading_accounts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(20), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Account Details
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # individual, business, institutional
    base_currency = Column(String(3), nullable=False, default='USD')
    
    # Balances
    cash_balance = Column(Numeric(20, 2), default=0)
    available_balance = Column(Numeric(20, 2), default=0)
    margin_used = Column(Numeric(20, 2), default=0)
    margin_available = Column(Numeric(20, 2), default=0)
    equity_value = Column(Numeric(20, 2), default=0)
    total_value = Column(Numeric(20, 2), default=0)
    
    # Risk Management
    max_leverage = Column(Numeric(8, 2), default=1.0)
    risk_tolerance = Column(String(20), default='moderate')
    max_position_size = Column(Numeric(20, 2), nullable=True)
    max_daily_loss = Column(Numeric(20, 2), nullable=True)
    
    # Trading Permissions
    can_trade_equities = Column(Boolean, default=True)
    can_trade_forex = Column(Boolean, default=False)
    can_trade_commodities = Column(Boolean, default=False)
    can_trade_derivatives = Column(Boolean, default=False)
    can_short_sell = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_frozen = Column(Boolean, default=False)
    freeze_reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Relationships  
    # user = relationship("User", back_populates="trading_accounts")  # Commented to avoid circular imports
    positions = relationship("Position", back_populates="account")
    orders = relationship("TradingOrder", back_populates="account")
    trades = relationship("Trade", back_populates="account")
    portfolios = relationship("Portfolio", back_populates="account")

class TradingOrder(Base):
    """Trading orders with comprehensive execution tracking"""
    __tablename__ = 'trading_orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String(50), nullable=False, unique=True, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey('trading_accounts.id'), nullable=False)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('trading_instruments.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Order Details
    order_type = Column(String(20), nullable=False)
    order_side = Column(String(10), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=True)
    stop_price = Column(Numeric(20, 8), nullable=True)
    
    # Execution Details
    filled_quantity = Column(Numeric(20, 8), default=0)
    remaining_quantity = Column(Numeric(20, 8), nullable=False)
    average_fill_price = Column(Numeric(20, 8), nullable=True)
    total_commission = Column(Numeric(20, 8), default=0)
    
    # Status and Timing
    status = Column(String(20), default='pending')
    submitted_at = Column(DateTime(timezone=True), default=datetime.now)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Risk Management
    estimated_margin = Column(Numeric(20, 2), nullable=True)
    risk_score = Column(Numeric(5, 2), nullable=True)
    
    # Advanced Order Parameters
    time_in_force = Column(String(10), default='DAY')  # DAY, GTC, IOC, FOK
    execution_instructions = Column(JSONB, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="orders")
    instrument = relationship("TradingInstrument", back_populates="orders")
    # user = relationship("User", back_populates="trading_orders")  # Commented to avoid circular imports
    trades = relationship("Trade", back_populates="order")
    
    __table_args__ = (
        Index('idx_order_account', 'account_id'),
        Index('idx_order_instrument', 'instrument_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_submitted', 'submitted_at'),
    )

class Trade(Base):
    """Executed trades with full transaction details"""
    __tablename__ = 'trades'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(String(50), nullable=False, unique=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey('trading_orders.id'), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('trading_accounts.id'), nullable=False)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('trading_instruments.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Trade Execution Details
    side = Column(String(10), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    total_value = Column(Numeric(20, 2), nullable=False)
    
    # Costs and Fees
    commission = Column(Numeric(20, 8), default=0)
    exchange_fees = Column(Numeric(20, 8), default=0)
    regulatory_fees = Column(Numeric(20, 8), default=0)
    total_fees = Column(Numeric(20, 8), default=0)
    net_amount = Column(Numeric(20, 2), nullable=False)
    
    # Settlement
    trade_date = Column(DateTime(timezone=True), default=datetime.now)
    settlement_date = Column(DateTime(timezone=True), nullable=False)
    is_settled = Column(Boolean, default=False)
    
    # Counterparty Information
    counterparty = Column(String(100), nullable=True)
    exchange = Column(String(50), nullable=False)
    clearing_house = Column(String(100), nullable=True)
    
    # Risk and P&L
    market_value_change = Column(Numeric(20, 2), default=0)
    unrealized_pnl = Column(Numeric(20, 2), default=0)
    realized_pnl = Column(Numeric(20, 2), default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    order = relationship("TradingOrder", back_populates="trades")
    account = relationship("TradingAccount", back_populates="trades")
    instrument = relationship("TradingInstrument", back_populates="trades")
    # user = relationship("User", back_populates="trades")  # Commented to avoid circular imports
    
    __table_args__ = (
        Index('idx_trade_account', 'account_id'),
        Index('idx_trade_instrument', 'instrument_id'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_trade_settlement', 'settlement_date'),
    )

class Position(Base):
    """Current and historical trading positions"""
    __tablename__ = 'positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('trading_accounts.id'), nullable=False)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('trading_instruments.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Position Details
    quantity = Column(Numeric(20, 8), nullable=False)
    average_cost = Column(Numeric(20, 8), nullable=False)
    total_cost = Column(Numeric(20, 2), nullable=False)
    current_price = Column(Numeric(20, 8), nullable=True)
    market_value = Column(Numeric(20, 2), nullable=True)
    
    # P&L Calculation
    unrealized_pnl = Column(Numeric(20, 2), default=0)
    unrealized_pnl_percent = Column(Numeric(8, 4), default=0)
    realized_pnl = Column(Numeric(20, 2), default=0)
    total_pnl = Column(Numeric(20, 2), default=0)
    
    # Risk Metrics
    position_value = Column(Numeric(20, 2), nullable=False)
    margin_requirement = Column(Numeric(20, 2), default=0)
    var_1day = Column(Numeric(20, 2), nullable=True)  # Value at Risk
    var_5day = Column(Numeric(20, 2), nullable=True)
    
    # Position Management
    is_long = Column(Boolean, nullable=False)
    is_short = Column(Boolean, default=False)
    is_hedged = Column(Boolean, default=False)
    hedge_ratio = Column(Numeric(8, 4), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True), default=datetime.now)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    last_price_update = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="positions")
    instrument = relationship("TradingInstrument", back_populates="positions")
    # user = relationship("User", back_populates="positions")  # Commented to avoid circular imports
    
    __table_args__ = (
        Index('idx_position_account', 'account_id'),
        Index('idx_position_instrument', 'instrument_id'),
        Index('idx_position_active', 'is_active'),
        Index('idx_position_opened', 'opened_at'),
    )

class Portfolio(Base):
    """Portfolio management and analysis"""
    __tablename__ = 'portfolios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_name = Column(String(100), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey('trading_accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Portfolio Composition
    total_value = Column(Numeric(20, 2), default=0)
    cash_value = Column(Numeric(20, 2), default=0)
    securities_value = Column(Numeric(20, 2), default=0)
    margin_value = Column(Numeric(20, 2), default=0)
    
    # Performance Metrics
    total_return = Column(Numeric(20, 2), default=0)
    total_return_percent = Column(Numeric(8, 4), default=0)
    day_change = Column(Numeric(20, 2), default=0)
    day_change_percent = Column(Numeric(8, 4), default=0)
    
    # Risk Analytics
    portfolio_beta = Column(Numeric(8, 6), nullable=True)
    portfolio_volatility = Column(Numeric(8, 6), nullable=True)
    sharpe_ratio = Column(Numeric(8, 4), nullable=True)
    max_drawdown = Column(Numeric(8, 4), nullable=True)
    var_95 = Column(Numeric(20, 2), nullable=True)
    
    # Allocation Analysis
    equity_allocation = Column(Numeric(5, 4), default=0)
    fixed_income_allocation = Column(Numeric(5, 4), default=0)
    commodity_allocation = Column(Numeric(5, 4), default=0)
    cash_allocation = Column(Numeric(5, 4), default=0)
    
    # Benchmarks
    benchmark_index = Column(String(50), nullable=True)
    alpha = Column(Numeric(8, 4), nullable=True)
    tracking_error = Column(Numeric(8, 4), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
    last_rebalance = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    account = relationship("TradingAccount", back_populates="portfolios")
    # user = relationship("User", back_populates="portfolios")  # Commented to avoid circular imports

class RiskMetrics(Base):
    """Real-time risk monitoring and metrics"""
    __tablename__ = 'risk_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('trading_accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Portfolio Risk Metrics
    total_exposure = Column(Numeric(20, 2), nullable=False)
    net_exposure = Column(Numeric(20, 2), nullable=False)
    gross_exposure = Column(Numeric(20, 2), nullable=False)
    leverage_ratio = Column(Numeric(8, 2), nullable=False)
    
    # Value at Risk
    var_1day_95 = Column(Numeric(20, 2), nullable=True)
    var_1day_99 = Column(Numeric(20, 2), nullable=True)
    var_10day_95 = Column(Numeric(20, 2), nullable=True)
    expected_shortfall = Column(Numeric(20, 2), nullable=True)
    
    # Concentration Risk
    largest_position_percent = Column(Numeric(5, 4), nullable=True)
    top_5_positions_percent = Column(Numeric(5, 4), nullable=True)
    sector_concentration = Column(JSONB, nullable=True)
    currency_exposure = Column(JSONB, nullable=True)
    
    # Risk Limits
    risk_limit_utilization = Column(Numeric(5, 4), nullable=True)
    margin_utilization = Column(Numeric(5, 4), nullable=True)
    is_risk_limit_breached = Column(Boolean, default=False)
    breach_details = Column(JSONB, nullable=True)
    
    # Market Risk
    correlation_risk = Column(Numeric(8, 6), nullable=True)
    duration_risk = Column(Numeric(8, 4), nullable=True)
    convexity_risk = Column(Numeric(8, 6), nullable=True)
    
    # Stress Testing
    stress_test_results = Column(JSONB, nullable=True)
    scenario_analysis = Column(JSONB, nullable=True)
    
    # Metadata
    calculation_date = Column(DateTime(timezone=True), default=datetime.now)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    
    # Relationships
    account = relationship("TradingAccount")
    
    __table_args__ = (
        Index('idx_risk_account', 'account_id'),
        Index('idx_risk_date', 'calculation_date'),
    )

class MarketData(Base):
    """Real-time and historical market data"""
    __tablename__ = 'market_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('trading_instruments.id'), nullable=False)
    
    # Price Data
    open_price = Column(Numeric(20, 8), nullable=True)
    high_price = Column(Numeric(20, 8), nullable=True)
    low_price = Column(Numeric(20, 8), nullable=True)
    close_price = Column(Numeric(20, 8), nullable=True)
    current_price = Column(Numeric(20, 8), nullable=True)
    
    # Volume and Interest
    volume = Column(Numeric(20, 0), default=0)
    volume_weighted_price = Column(Numeric(20, 8), nullable=True)
    open_interest = Column(Numeric(20, 0), nullable=True)
    
    # Bid/Ask Data
    bid_price = Column(Numeric(20, 8), nullable=True)
    ask_price = Column(Numeric(20, 8), nullable=True)
    bid_size = Column(Numeric(20, 0), nullable=True)
    ask_size = Column(Numeric(20, 0), nullable=True)
    spread = Column(Numeric(20, 8), nullable=True)
    
    # Market Statistics
    price_change = Column(Numeric(20, 8), default=0)
    price_change_percent = Column(Numeric(8, 4), default=0)
    volatility_30d = Column(Numeric(8, 6), nullable=True)
    average_volume_30d = Column(Numeric(20, 0), nullable=True)
    
    # Technical Indicators
    rsi_14 = Column(Numeric(8, 4), nullable=True)
    moving_avg_20 = Column(Numeric(20, 8), nullable=True)
    moving_avg_50 = Column(Numeric(20, 8), nullable=True)
    bollinger_upper = Column(Numeric(20, 8), nullable=True)
    bollinger_lower = Column(Numeric(20, 8), nullable=True)
    
    # Timestamps
    market_date = Column(DateTime(timezone=True), nullable=False)
    last_update = Column(DateTime(timezone=True), default=datetime.now)
    
    # Data Quality
    data_source = Column(String(50), nullable=False)
    is_real_time = Column(Boolean, default=True)
    delay_minutes = Column(Integer, default=0)
    
    # Relationships
    instrument = relationship("TradingInstrument")
    
    __table_args__ = (
        Index('idx_market_data_instrument', 'instrument_id'),
        Index('idx_market_data_date', 'market_date'),
        Index('idx_market_data_update', 'last_update'),
    )