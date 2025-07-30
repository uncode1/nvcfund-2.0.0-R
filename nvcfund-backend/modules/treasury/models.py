"""
Treasury Operations Models
Self-contained models for $30T treasury operations and NVCT stablecoin management
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

class TreasuryOperationType(Enum):
    """Types of treasury operations"""
    NVCT_MINTING = "nvct_minting"
    NVCT_BURNING = "nvct_burning"
    ASSET_BACKING = "asset_backing"
    LIQUIDITY_MANAGEMENT = "liquidity_management"
    MONETARY_POLICY = "monetary_policy"
    RESERVE_MANAGEMENT = "reserve_management"
    YIELD_CURVE_MANAGEMENT = "yield_curve_management"
    FOREIGN_EXCHANGE = "foreign_exchange"
    DEBT_ISSUANCE = "debt_issuance"
    COLLATERAL_MANAGEMENT = "collateral_management"

class AssetClass(Enum):
    """Asset classes for treasury portfolio"""
    US_TREASURY_BONDS = "us_treasury_bonds"
    CORPORATE_BONDS = "corporate_bonds"
    REAL_ESTATE = "real_estate"
    GOLD_RESERVES = "gold_reserves"
    COMMODITY_RESERVES = "commodity_reserves"
    FOREIGN_CURRENCY = "foreign_currency"
    CRYPTOCURRENCY = "cryptocurrency"
    EQUITY_SECURITIES = "equity_securities"
    MONEY_MARKET = "money_market"
    DERIVATIVES = "derivatives"

class TreasuryTransactionStatus(Enum):
    """Treasury transaction status"""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDER_REVIEW = "under_review"

class NVCTSupplyOperation(Base):
    """NVCT stablecoin supply management operations"""
    __tablename__ = 'nvct_supply_operations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Operation details
    operation_type = Column(String(50), nullable=False)  # minting, burning
    amount = Column(Numeric(24, 2), nullable=False)  # NVCT amount
    operation_reason = Column(String(200), nullable=False)
    
    # Authorization
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    authorization_level = Column(String(50), nullable=False)  # treasury_officer, board, emergency
    
    # Supply metrics
    supply_before = Column(Numeric(24, 2), nullable=False)
    supply_after = Column(Numeric(24, 2), nullable=False)
    daily_limit_used = Column(Numeric(24, 2), default=0.00)
    monthly_limit_used = Column(Numeric(24, 2), default=0.00)
    
    # Asset backing verification
    backing_ratio_before = Column(Numeric(8, 4), nullable=False)  # Percentage
    backing_ratio_after = Column(Numeric(8, 4), nullable=False)
    required_backing_increase = Column(Numeric(24, 2))
    
    # Network deployment
    blockchain_networks = Column(JSONB)  # List of networks (BSC, Polygon, etc.)
    transaction_hashes = Column(JSONB)  # Network-specific tx hashes
    
    # Status and execution
    status = Column(String(20), default=TreasuryTransactionStatus.PENDING.value)
    execution_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Risk and compliance
    risk_assessment = Column(String(20))  # low, medium, high, critical
    compliance_approval = Column(Boolean, default=False)
    regulatory_notification = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    authorizer = relationship("User", foreign_keys=[authorized_by])
    
    def calculate_new_backing_ratio(self, total_assets: Decimal) -> Decimal:
        """Calculate backing ratio after operation"""
        if self.supply_after > 0:
            return (total_assets / self.supply_after) * 100
        return Decimal('0.00')
    
    def __repr__(self):
        return f"<NVCTSupplyOperation {self.operation_type}: {self.amount} NVCT>"

class AssetBackingPortfolio(Base):
    """Asset backing portfolio for NVCT stablecoin"""
    __tablename__ = 'asset_backing_portfolio'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Asset identification
    asset_id = Column(String(100), unique=True, nullable=False)
    asset_name = Column(String(200), nullable=False)
    asset_class = Column(String(50), nullable=False)  # AssetClass enum
    
    # Financial details
    face_value = Column(Numeric(24, 2), nullable=False)
    market_value = Column(Numeric(24, 2), nullable=False)
    book_value = Column(Numeric(24, 2), nullable=False)
    
    # Portfolio allocation
    portfolio_weight = Column(Numeric(8, 4), nullable=False)  # Percentage
    target_weight = Column(Numeric(8, 4), nullable=False)
    rebalancing_threshold = Column(Numeric(8, 4), default=5.0000)  # Threshold for rebalancing
    
    # Asset characteristics
    maturity_date = Column(DateTime)
    coupon_rate = Column(Numeric(8, 6))  # For bonds
    credit_rating = Column(String(20))  # AAA, AA+, etc.
    
    # Geographic and sector allocation
    geographic_region = Column(String(100))
    sector_classification = Column(String(100))
    currency = Column(String(3), default='USD')
    
    # Risk metrics
    duration = Column(Numeric(8, 4))  # For bonds
    beta = Column(Numeric(8, 6))  # For equities
    volatility = Column(Numeric(8, 4))  # Historical volatility
    
    # Custodial information
    custodian = Column(String(200))
    custodial_account = Column(String(100))
    physical_location = Column(String(200))  # For physical assets
    
    # Valuation and pricing
    last_valuation_date = Column(DateTime, nullable=False)
    valuation_method = Column(String(50))  # market, model, cost
    price_source = Column(String(100))
    
    # Status and compliance
    is_active = Column(Boolean, default=True)
    is_encumbered = Column(Boolean, default=False)
    regulatory_compliant = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("AssetTransaction", back_populates="asset")
    valuations = relationship("AssetValuation", back_populates="asset")
    
    def calculate_yield(self) -> Optional[Decimal]:
        """Calculate current yield for income-generating assets"""
        if self.coupon_rate and self.market_value:
            annual_income = self.face_value * (self.coupon_rate / 100)
            return (annual_income / self.market_value) * 100
        return None
    
    def __repr__(self):
        return f"<AssetBackingPortfolio {self.asset_id}: {self.market_value} USD>"

class AssetTransaction(Base):
    """Transactions for asset backing portfolio"""
    __tablename__ = 'asset_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction details
    asset_id = Column(UUID(as_uuid=True), ForeignKey('asset_backing_portfolio.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # buy, sell, rebalance, valuation_adjustment
    
    # Financial details
    quantity = Column(Numeric(24, 8), nullable=False)
    price_per_unit = Column(Numeric(18, 8), nullable=False)
    total_amount = Column(Numeric(24, 2), nullable=False)
    fees_and_charges = Column(Numeric(18, 2), default=0.00)
    
    # Transaction metadata
    counterparty = Column(String(200))
    execution_venue = Column(String(200))
    settlement_date = Column(DateTime, nullable=False)
    
    # Authorization
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    authorization_level = Column(String(50), nullable=False)
    
    # Portfolio impact
    portfolio_weight_impact = Column(Numeric(8, 4))
    backing_ratio_impact = Column(Numeric(8, 4))
    
    # Status
    status = Column(String(20), default=TreasuryTransactionStatus.PENDING.value)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    asset = relationship("AssetBackingPortfolio", back_populates="transactions")
    authorizer = relationship("User", foreign_keys=[authorized_by])
    
    def __repr__(self):
        return f"<AssetTransaction {self.transaction_type}: {self.total_amount} USD>"

class AssetValuation(Base):
    """Asset valuation records for portfolio management"""
    __tablename__ = 'asset_valuations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Valuation details
    asset_id = Column(UUID(as_uuid=True), ForeignKey('asset_backing_portfolio.id'), nullable=False)
    valuation_date = Column(DateTime, nullable=False)
    
    # Valuation amounts
    market_value = Column(Numeric(24, 2), nullable=False)
    book_value = Column(Numeric(24, 2), nullable=False)
    fair_value = Column(Numeric(24, 2))
    
    # Valuation methodology
    valuation_method = Column(String(50), nullable=False)  # mark_to_market, model, cost
    price_source = Column(String(100), nullable=False)
    valuation_model = Column(String(100))
    
    # Market data
    market_price = Column(Numeric(18, 8))
    bid_price = Column(Numeric(18, 8))
    ask_price = Column(Numeric(18, 8))
    volume = Column(Numeric(24, 2))
    
    # Valuation adjustments
    liquidity_adjustment = Column(Numeric(8, 4), default=0.0000)
    credit_adjustment = Column(Numeric(8, 4), default=0.0000)
    model_adjustment = Column(Numeric(8, 4), default=0.0000)
    
    # Quality indicators
    confidence_level = Column(String(20))  # high, medium, low
    data_staleness_hours = Column(Integer, default=0)
    
    # Auditing
    valued_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewed_by = Column(Integer, ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship("AssetBackingPortfolio", back_populates="valuations")
    valuer = relationship("User", foreign_keys=[valued_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<AssetValuation {self.valuation_date}: {self.market_value} USD>"

class TreasuryLiquidityPosition(Base):
    """Daily liquidity positions and management"""
    __tablename__ = 'treasury_liquidity_positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Position details
    position_date = Column(DateTime, nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Cash positions
    opening_balance = Column(Numeric(24, 2), nullable=False)
    closing_balance = Column(Numeric(24, 2), nullable=False)
    intraday_peak = Column(Numeric(24, 2))
    intraday_trough = Column(Numeric(24, 2))
    
    # Liquidity sources
    deposit_inflows = Column(Numeric(24, 2), default=0.00)
    deposit_outflows = Column(Numeric(24, 2), default=0.00)
    lending_inflows = Column(Numeric(24, 2), default=0.00)
    lending_outflows = Column(Numeric(24, 2), default=0.00)
    
    # Central bank operations
    fed_funds_borrowed = Column(Numeric(24, 2), default=0.00)
    fed_funds_lent = Column(Numeric(24, 2), default=0.00)
    discount_window_usage = Column(Numeric(24, 2), default=0.00)
    
    # Liquidity metrics
    liquidity_coverage_ratio = Column(Numeric(8, 4))
    net_stable_funding_ratio = Column(Numeric(8, 4))
    liquidity_risk_score = Column(Integer)  # 1-100 scale
    
    # Stress testing
    stress_test_shortfall = Column(Numeric(24, 2))
    emergency_liquidity_available = Column(Numeric(24, 2))
    
    # Management actions
    liquidity_actions_taken = Column(JSONB)  # List of actions
    cost_of_liquidity = Column(Numeric(8, 6))  # Weighted average cost
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TreasuryLiquidityPosition {self.position_date}: {self.closing_balance} {self.currency}>"

class MonetaryPolicyOperation(Base):
    """Monetary policy operations and Federal Reserve interactions"""
    __tablename__ = 'monetary_policy_operations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Operation details
    operation_type = Column(String(50), nullable=False)  # open_market, discount_window, reserve_requirement
    operation_direction = Column(String(20), nullable=False)  # tightening, easing, neutral
    
    # Financial details
    notional_amount = Column(Numeric(24, 2), nullable=False)
    execution_rate = Column(Numeric(8, 6), nullable=False)
    maturity_date = Column(DateTime)
    
    # Federal Reserve interaction
    fed_facility = Column(String(100))  # Primary_Credit, Seasonal_Credit, etc.
    fed_reference_number = Column(String(100))
    collateral_provided = Column(Numeric(24, 2))
    
    # Policy context
    fomc_meeting_date = Column(DateTime)
    policy_statement_reference = Column(String(200))
    economic_justification = Column(Text)
    
    # Market impact
    fed_funds_rate_impact = Column(Numeric(8, 6))
    yield_curve_impact = Column(JSONB)  # Impact across maturities
    market_reaction = Column(Text)
    
    # Authorization and execution
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    executed_by = Column(Integer, ForeignKey('users.id'))
    
    # Status and timing
    status = Column(String(20), default=TreasuryTransactionStatus.PENDING.value)
    execution_time = Column(DateTime)
    settlement_time = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    authorizer = relationship("User", foreign_keys=[authorized_by])
    executor = relationship("User", foreign_keys=[executed_by])
    
    def __repr__(self):
        return f"<MonetaryPolicyOperation {self.operation_type}: {self.notional_amount} USD>"

class TreasuryRiskMetrics(Base):
    """Daily treasury risk metrics and monitoring"""
    __tablename__ = 'treasury_risk_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Risk measurement date
    measurement_date = Column(DateTime, nullable=False)
    
    # Portfolio risk metrics
    portfolio_var_1day = Column(Numeric(24, 2))  # 1-day Value at Risk
    portfolio_var_10day = Column(Numeric(24, 2))  # 10-day Value at Risk
    expected_shortfall = Column(Numeric(24, 2))  # Conditional VaR
    
    # Interest rate risk
    duration = Column(Numeric(8, 4))
    convexity = Column(Numeric(8, 4))
    key_rate_durations = Column(JSONB)  # Duration by key rates
    
    # Credit risk
    credit_var = Column(Numeric(24, 2))
    credit_concentration = Column(Numeric(8, 4))  # Herfindahl index
    default_probability = Column(Numeric(8, 6))
    
    # Liquidity risk
    liquidity_adjusted_var = Column(Numeric(24, 2))
    funding_gap = Column(Numeric(24, 2))
    liquidity_stress_loss = Column(Numeric(24, 2))
    
    # Operational risk
    operational_var = Column(Numeric(24, 2))
    cyber_risk_score = Column(Integer)  # 1-100 scale
    
    # Risk limits utilization
    var_limit_utilization = Column(Numeric(8, 4))  # Percentage of limit used
    concentration_limit_breaches = Column(Integer)
    stress_test_breaches = Column(Integer)
    
    # Risk-adjusted returns
    sharpe_ratio = Column(Numeric(8, 6))
    sortino_ratio = Column(Numeric(8, 6))
    risk_adjusted_return = Column(Numeric(8, 6))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TreasuryRiskMetrics {self.measurement_date}: VaR {self.portfolio_var_1day}>"

# Create indexes for optimal query performance
Index('idx_nvct_supply_operations_type', NVCTSupplyOperation.operation_type)
Index('idx_nvct_supply_operations_status', NVCTSupplyOperation.status)
Index('idx_nvct_supply_operations_date', NVCTSupplyOperation.created_at)
Index('idx_asset_backing_portfolio_class', AssetBackingPortfolio.asset_class)
Index('idx_asset_backing_portfolio_active', AssetBackingPortfolio.is_active)
Index('idx_asset_transactions_asset_id', AssetTransaction.asset_id)
Index('idx_asset_transactions_type', AssetTransaction.transaction_type)
Index('idx_asset_valuations_asset_id', AssetValuation.asset_id)
Index('idx_asset_valuations_date', AssetValuation.valuation_date)
Index('idx_liquidity_positions_date', TreasuryLiquidityPosition.position_date)
Index('idx_liquidity_positions_currency', TreasuryLiquidityPosition.currency)
Index('idx_monetary_policy_operations_type', MonetaryPolicyOperation.operation_type)
Index('idx_monetary_policy_operations_status', MonetaryPolicyOperation.status)
Index('idx_treasury_risk_metrics_date', TreasuryRiskMetrics.measurement_date)