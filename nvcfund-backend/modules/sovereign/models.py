"""
Sovereign Banking Models
Self-contained models for central banking operations and sovereign debt management
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

class SovereignOperationType(Enum):
    """Types of sovereign banking operations"""
    MONETARY_POLICY = "monetary_policy"
    DEBT_ISSUANCE = "debt_issuance"
    RESERVE_MANAGEMENT = "reserve_management"
    FOREIGN_EXCHANGE = "foreign_exchange"
    BANKING_SUPERVISION = "banking_supervision"
    REGULATORY_ACTION = "regulatory_action"
    EMERGENCY_LENDING = "emergency_lending"
    PAYMENT_SYSTEM = "payment_system"

class DebtInstrumentType(Enum):
    """Types of sovereign debt instruments"""
    TREASURY_BILL = "treasury_bill"
    TREASURY_NOTE = "treasury_note"
    TREASURY_BOND = "treasury_bond"
    TREASURY_STRIP = "treasury_strip"
    INFLATION_PROTECTED = "inflation_protected"
    FOREIGN_CURRENCY_BOND = "foreign_currency_bond"
    FLOATING_RATE_NOTE = "floating_rate_note"
    ZERO_COUPON_BOND = "zero_coupon_bond"

class CreditRating(Enum):
    """Sovereign credit ratings"""
    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    BB_MINUS = "BB-"

class SovereignDebtPortfolio(Base):
    """Sovereign debt portfolio management"""
    __tablename__ = 'sovereign_debt_portfolio'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Debt instrument identification
    instrument_id = Column(String(50), unique=True, nullable=False)
    cusip = Column(String(9), unique=True)  # CUSIP identifier
    isin = Column(String(12), unique=True)  # ISIN identifier
    
    # Instrument details
    instrument_type = Column(String(50), nullable=False)  # DebtInstrumentType
    series_designation = Column(String(50))  # Series A, B, etc.
    
    # Financial terms
    face_value = Column(Numeric(24, 2), nullable=False)
    outstanding_amount = Column(Numeric(24, 2), nullable=False)
    issue_price = Column(Numeric(12, 6), nullable=False)  # Price per 100
    current_price = Column(Numeric(12, 6))
    
    # Interest terms
    coupon_rate = Column(Numeric(8, 6))  # Annual coupon rate
    payment_frequency = Column(Integer)  # Payments per year
    accrued_interest = Column(Numeric(18, 2), default=0.00)
    
    # Maturity and duration
    issue_date = Column(DateTime, nullable=False)
    maturity_date = Column(DateTime, nullable=False)
    first_payment_date = Column(DateTime)
    last_payment_date = Column(DateTime)
    
    # Yield and performance
    yield_to_maturity = Column(Numeric(8, 6))
    current_yield = Column(Numeric(8, 6))
    duration = Column(Numeric(8, 4))
    modified_duration = Column(Numeric(8, 4))
    convexity = Column(Numeric(8, 4))
    
    # Market information
    benchmark_spread = Column(Numeric(8, 6))  # Spread over benchmark
    credit_spread = Column(Numeric(8, 6))
    liquidity_score = Column(Integer)  # 1-100 scale
    
    # Portfolio allocation
    portfolio_weight = Column(Numeric(8, 4))  # Percentage of portfolio
    strategic_allocation = Column(Numeric(8, 4))  # Target allocation
    
    # Risk metrics
    credit_rating = Column(String(10))  # CreditRating enum
    probability_of_default = Column(Numeric(8, 6))
    loss_given_default = Column(Numeric(8, 4))
    
    # Currency and geographic
    currency = Column(String(3), default='USD')
    issuing_country = Column(String(50))
    
    # Status and flags
    is_active = Column(Boolean, default=True)
    is_callable = Column(Boolean, default=False)
    is_inflation_protected = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("SovereignDebtTransaction", back_populates="instrument")
    payments = relationship("SovereignDebtPayment", back_populates="instrument")
    
    def calculate_annual_debt_service(self) -> Decimal:
        """Calculate annual debt service requirements"""
        if self.coupon_rate and self.outstanding_amount and self.payment_frequency:
            return (self.outstanding_amount * self.coupon_rate / 100) + (self.outstanding_amount / self.years_to_maturity())
        return Decimal('0.00')
    
    def years_to_maturity(self) -> float:
        """Calculate years to maturity"""
        days_to_maturity = (self.maturity_date - datetime.utcnow()).days
        return max(0, days_to_maturity / 365.25)
    
    def __repr__(self):
        return f"<SovereignDebtPortfolio {self.instrument_id}: {self.outstanding_amount}>"

class SovereignDebtTransaction(Base):
    """Sovereign debt issuance and trading transactions"""
    __tablename__ = 'sovereign_debt_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction details
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('sovereign_debt_portfolio.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # issuance, buyback, exchange, auction
    
    # Financial details
    principal_amount = Column(Numeric(24, 2), nullable=False)
    transaction_price = Column(Numeric(12, 6), nullable=False)
    accrued_interest = Column(Numeric(18, 2), default=0.00)
    total_consideration = Column(Numeric(24, 2), nullable=False)
    
    # Transaction execution
    execution_date = Column(DateTime, nullable=False)
    settlement_date = Column(DateTime, nullable=False)
    value_date = Column(DateTime)
    
    # Market context
    benchmark_yield = Column(Numeric(8, 6))  # 10Y Treasury at execution
    credit_spread_at_execution = Column(Numeric(8, 6))
    market_conditions = Column(String(200))
    
    # Auction details (for primary issuance)
    auction_type = Column(String(50))  # competitive, non-competitive
    bid_to_cover_ratio = Column(Numeric(8, 4))
    number_of_bidders = Column(Integer)
    allocation_amount = Column(Numeric(24, 2))
    
    # Counterparty information
    counterparty_type = Column(String(50))  # primary_dealer, institutional, central_bank
    counterparty_name = Column(String(200))
    dealer_fee = Column(Numeric(18, 2), default=0.00)
    
    # Authorization and processing
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    processed_by = Column(Integer, ForeignKey('users.id'))
    
    # Impact analysis
    debt_to_gdp_impact = Column(Numeric(8, 4))
    interest_expense_impact = Column(Numeric(24, 2))
    duration_impact = Column(Numeric(8, 4))
    
    # Status
    status = Column(String(20), default='pending')  # pending, executed, settled, failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instrument = relationship("SovereignDebtPortfolio", back_populates="transactions")
    authorizer = relationship("User", foreign_keys=[authorized_by])
    processor = relationship("User", foreign_keys=[processed_by])
    
    def __repr__(self):
        return f"<SovereignDebtTransaction {self.transaction_type}: {self.principal_amount}>"

class SovereignDebtPayment(Base):
    """Sovereign debt service payments"""
    __tablename__ = 'sovereign_debt_payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Payment details
    instrument_id = Column(UUID(as_uuid=True), ForeignKey('sovereign_debt_portfolio.id'), nullable=False)
    payment_type = Column(String(50), nullable=False)  # coupon, principal, final
    
    # Payment amounts
    scheduled_amount = Column(Numeric(24, 2), nullable=False)
    actual_amount = Column(Numeric(24, 2))
    principal_portion = Column(Numeric(24, 2), default=0.00)
    interest_portion = Column(Numeric(24, 2), default=0.00)
    
    # Payment dates
    scheduled_date = Column(DateTime, nullable=False)
    actual_payment_date = Column(DateTime)
    
    # Payment execution
    payment_method = Column(String(50))  # wire_transfer, book_entry, physical_delivery
    paying_agent = Column(String(200))
    confirmation_number = Column(String(100))
    
    # Status and tracking
    payment_status = Column(String(20), default='scheduled')  # scheduled, executed, failed, cancelled
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instrument = relationship("SovereignDebtPortfolio", back_populates="payments")
    
    def __repr__(self):
        return f"<SovereignDebtPayment {self.payment_type}: {self.scheduled_amount}>"

class InternationalReserves(Base):
    """International reserves management"""
    __tablename__ = 'international_reserves'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reserve position date
    position_date = Column(DateTime, nullable=False)
    
    # Foreign currency reserves
    usd_reserves = Column(Numeric(24, 2), default=0.00)
    eur_reserves = Column(Numeric(24, 2), default=0.00)
    jpy_reserves = Column(Numeric(24, 2), default=0.00)
    gbp_reserves = Column(Numeric(24, 2), default=0.00)
    cny_reserves = Column(Numeric(24, 2), default=0.00)
    other_currency_reserves = Column(Numeric(24, 2), default=0.00)
    
    # Gold reserves
    gold_ounces = Column(Numeric(18, 6), default=0.000000)
    gold_market_value = Column(Numeric(24, 2), default=0.00)
    gold_average_cost = Column(Numeric(12, 6))
    
    # Special Drawing Rights (SDR)
    sdr_holdings = Column(Numeric(24, 2), default=0.00)
    sdr_allocation = Column(Numeric(24, 2), default=0.00)
    imf_reserve_position = Column(Numeric(24, 2), default=0.00)
    
    # Reserve composition
    total_reserves = Column(Numeric(24, 2), nullable=False)
    currency_composition = Column(JSONB)  # Breakdown by currency
    maturity_profile = Column(JSONB)  # Breakdown by maturity
    
    # Investment allocation
    government_securities = Column(Numeric(24, 2), default=0.00)
    supranational_securities = Column(Numeric(24, 2), default=0.00)
    bank_deposits = Column(Numeric(24, 2), default=0.00)
    money_market_instruments = Column(Numeric(24, 2), default=0.00)
    
    # Risk metrics
    duration = Column(Numeric(8, 4))
    credit_rating_distribution = Column(JSONB)
    currency_var = Column(Numeric(24, 2))  # Currency Value at Risk
    
    # Liquidity metrics
    liquid_reserves_ratio = Column(Numeric(8, 4))  # Percentage
    reserve_adequacy_ratio = Column(Numeric(8, 4))  # Months of imports
    
    # Performance metrics
    total_return_ytd = Column(Numeric(8, 6))
    benchmark_return = Column(Numeric(8, 6))
    excess_return = Column(Numeric(8, 6))
    
    # Operational metrics
    managed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    custodian_banks = Column(JSONB)  # List of custodian banks
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = relationship("User", foreign_keys=[managed_by])
    
    def calculate_reserve_coverage(self, monthly_imports: Decimal) -> Decimal:
        """Calculate import coverage in months"""
        if monthly_imports > 0:
            return self.total_reserves / monthly_imports
        return Decimal('0.00')
    
    def __repr__(self):
        return f"<InternationalReserves {self.position_date}: {self.total_reserves}>"

class CentralBankPolicy(Base):
    """Central bank monetary policy decisions and implementation"""
    __tablename__ = 'central_bank_policy'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Policy meeting details
    meeting_date = Column(DateTime, nullable=False)
    meeting_type = Column(String(50), nullable=False)  # regular, emergency, interim
    policy_effective_date = Column(DateTime, nullable=False)
    
    # Interest rate decisions
    policy_rate = Column(Numeric(8, 6), nullable=False)  # Main policy rate
    policy_rate_change = Column(Numeric(8, 6), default=0.000000)
    discount_rate = Column(Numeric(8, 6))
    reserve_requirement_ratio = Column(Numeric(8, 4))
    
    # Policy stance and forward guidance
    policy_stance = Column(String(50))  # hawkish, dovish, neutral, data_dependent
    forward_guidance = Column(Text)
    next_meeting_guidance = Column(Text)
    
    # Economic assessment
    inflation_outlook = Column(Numeric(8, 4))  # Projected inflation
    growth_outlook = Column(Numeric(8, 4))  # Projected GDP growth
    unemployment_outlook = Column(Numeric(8, 4))  # Projected unemployment
    
    # Policy tools and operations
    quantitative_easing_amount = Column(Numeric(24, 2), default=0.00)
    asset_purchase_programs = Column(JSONB)  # List of purchase programs
    lending_facilities = Column(JSONB)  # Available facilities
    
    # Market impact assessment
    market_reaction = Column(Text)
    yield_curve_impact = Column(JSONB)  # Impact across maturities
    fx_rate_impact = Column(Numeric(8, 6))
    equity_market_impact = Column(Numeric(8, 4))
    
    # Communication
    policy_statement = Column(Text, nullable=False)
    press_conference_summary = Column(Text)
    governor_speech_highlights = Column(Text)
    
    # Voting and dissent
    committee_votes_for = Column(Integer)
    committee_votes_against = Column(Integer)
    dissenting_opinions = Column(Text)
    
    # Implementation details
    policy_implemented_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    implementation_status = Column(String(20), default='pending')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    implementer = relationship("User", foreign_keys=[policy_implemented_by])
    
    def __repr__(self):
        return f"<CentralBankPolicy {self.meeting_date}: {self.policy_rate}%>"

class BankingSupervision(Base):
    """Banking supervision and regulatory oversight"""
    __tablename__ = 'banking_supervision'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Supervised institution
    bank_id = Column(String(50), nullable=False)  # Bank charter number
    bank_name = Column(String(200), nullable=False)
    bank_type = Column(String(50), nullable=False)  # commercial, savings, credit_union
    
    # Supervisory assessment
    examination_date = Column(DateTime, nullable=False)
    examination_type = Column(String(50))  # full_scope, targeted, follow_up
    
    # CAMELS ratings
    capital_adequacy = Column(Integer, nullable=False)  # 1-5 scale
    asset_quality = Column(Integer, nullable=False)
    management = Column(Integer, nullable=False)
    earnings = Column(Integer, nullable=False)
    liquidity = Column(Integer, nullable=False)
    sensitivity_to_market_risk = Column(Integer, nullable=False)
    composite_rating = Column(Integer, nullable=False)
    
    # Financial metrics
    tier1_capital_ratio = Column(Numeric(8, 4), nullable=False)
    total_capital_ratio = Column(Numeric(8, 4), nullable=False)
    leverage_ratio = Column(Numeric(8, 4), nullable=False)
    liquidity_coverage_ratio = Column(Numeric(8, 4))
    net_stable_funding_ratio = Column(Numeric(8, 4))
    
    # Asset quality indicators
    npl_ratio = Column(Numeric(8, 4))  # Non-performing loans ratio
    charge_off_rate = Column(Numeric(8, 4))
    provision_coverage_ratio = Column(Numeric(8, 4))
    classified_assets_ratio = Column(Numeric(8, 4))
    
    # Profitability metrics
    return_on_assets = Column(Numeric(8, 6))
    return_on_equity = Column(Numeric(8, 6))
    net_interest_margin = Column(Numeric(8, 6))
    efficiency_ratio = Column(Numeric(8, 4))
    
    # Risk assessment
    credit_risk_score = Column(Integer)  # 1-100 scale
    operational_risk_score = Column(Integer)
    market_risk_score = Column(Integer)
    liquidity_risk_score = Column(Integer)
    
    # Regulatory actions
    enforcement_actions = Column(JSONB)  # List of enforcement actions
    corrective_measures = Column(JSONB)  # Required corrective measures
    examination_findings = Column(Text)
    management_response = Column(Text)
    
    # Supervisory contact
    supervised_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    next_examination_date = Column(DateTime)
    
    # Status
    supervisory_status = Column(String(50))  # satisfactory, fair, unsatisfactory
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supervisor = relationship("User", foreign_keys=[supervised_by])
    
    def calculate_prompt_corrective_action_category(self) -> str:
        """Calculate PCA category based on capital ratios"""
        if self.tier1_capital_ratio >= 10.0 and self.total_capital_ratio >= 10.0:
            return "well_capitalized"
        elif self.tier1_capital_ratio >= 8.0 and self.total_capital_ratio >= 10.0:
            return "adequately_capitalized"
        elif self.tier1_capital_ratio >= 6.0 and self.total_capital_ratio >= 8.0:
            return "undercapitalized"
        elif self.tier1_capital_ratio >= 4.0 and self.total_capital_ratio >= 6.0:
            return "significantly_undercapitalized"
        else:
            return "critically_undercapitalized"
    
    def __repr__(self):
        return f"<BankingSupervision {self.bank_name}: CAMELS {self.composite_rating}>"

class ForeignExchangeOperation(Base):
    """Foreign exchange operations and interventions"""
    __tablename__ = 'foreign_exchange_operations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Operation details
    operation_type = Column(String(50), nullable=False)  # intervention, reserve_management, commercial
    operation_direction = Column(String(20), nullable=False)  # buy_domestic, sell_domestic, neutral
    
    # Currency details
    base_currency = Column(String(3), nullable=False)
    quote_currency = Column(String(3), nullable=False)
    currency_pair = Column(String(7), nullable=False)  # EURUSD, GBPUSD, etc.
    
    # Transaction details
    notional_amount = Column(Numeric(24, 2), nullable=False)
    exchange_rate = Column(Numeric(12, 8), nullable=False)
    settlement_amount = Column(Numeric(24, 2), nullable=False)
    
    # Market context
    market_rate_before = Column(Numeric(12, 8))
    market_rate_after = Column(Numeric(12, 8))
    volatility_before = Column(Numeric(8, 6))
    volatility_after = Column(Numeric(8, 6))
    
    # Intervention rationale
    intervention_objective = Column(String(200))
    market_conditions = Column(Text)
    policy_coordination = Column(Boolean, default=False)
    
    # Execution details
    execution_method = Column(String(50))  # direct, through_dealers, auction
    counterparties = Column(JSONB)  # List of counterparties
    execution_timeframe = Column(String(50))  # immediate, over_time, conditional
    
    # Impact assessment
    market_impact = Column(Numeric(8, 6))  # Basis points
    effectiveness_score = Column(Integer)  # 1-100 scale
    unintended_consequences = Column(Text)
    
    # Authorization and oversight
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    coordination_level = Column(String(50))  # unilateral, coordinated, g7, g20
    
    # Settlement details
    settlement_date = Column(DateTime, nullable=False)
    settlement_status = Column(String(20), default='pending')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    authorizer = relationship("User", foreign_keys=[authorized_by])
    
    def __repr__(self):
        return f"<ForeignExchangeOperation {self.currency_pair}: {self.notional_amount}>"

# Create indexes for optimal query performance
Index('idx_sovereign_debt_portfolio_instrument_type', SovereignDebtPortfolio.instrument_type)
Index('idx_sovereign_debt_portfolio_maturity_date', SovereignDebtPortfolio.maturity_date)
Index('idx_sovereign_debt_portfolio_credit_rating', SovereignDebtPortfolio.credit_rating)
Index('idx_sovereign_debt_transactions_instrument_id', SovereignDebtTransaction.instrument_id)
Index('idx_sovereign_debt_transactions_type', SovereignDebtTransaction.transaction_type)
Index('idx_sovereign_debt_payments_instrument_id', SovereignDebtPayment.instrument_id)
Index('idx_sovereign_debt_payments_scheduled_date', SovereignDebtPayment.scheduled_date)
Index('idx_international_reserves_position_date', InternationalReserves.position_date)
Index('idx_central_bank_policy_meeting_date', CentralBankPolicy.meeting_date)
Index('idx_central_bank_policy_effective_date', CentralBankPolicy.policy_effective_date)
Index('idx_banking_supervision_bank_id', BankingSupervision.bank_id)
Index('idx_banking_supervision_examination_date', BankingSupervision.examination_date)
Index('idx_banking_supervision_composite_rating', BankingSupervision.composite_rating)
Index('idx_fx_operations_currency_pair', ForeignExchangeOperation.currency_pair)
Index('idx_fx_operations_operation_type', ForeignExchangeOperation.operation_type)