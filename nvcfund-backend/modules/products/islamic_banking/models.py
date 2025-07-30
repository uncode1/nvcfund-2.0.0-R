"""
Islamic Banking Models
Self-contained models for Sharia-compliant banking with foreign key relationships
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from modules.core.database import Base

class ShariaProductType(Enum):
    """Types of Sharia-compliant products"""
    MURABAHA = "murabaha"  # Cost-plus financing
    IJARA = "ijara"        # Leasing
    MUSHARAKA = "musharaka"  # Partnership
    MUDARABA = "mudaraba"    # Profit-sharing
    SUKUK = "sukuk"          # Islamic bonds
    ISTISNA = "istisna"      # Manufacturing finance
    SALAM = "salam"          # Forward sale
    TAKAFUL = "takaful"      # Islamic insurance
    QARD_HASSAN = "qard_hassan"  # Benevolent loan
    WAKALA = "wakala"        # Agency

class ShariaComplianceStatus(Enum):
    """Sharia compliance verification status"""
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    SHARIA_APPROVED = "sharia_approved"
    SHARIA_REJECTED = "sharia_rejected"
    REQUIRES_MODIFICATION = "requires_modification"
    EXPIRED = "expired"

class AssetBacking(Enum):
    """Types of asset backing for Islamic products"""
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    RECEIVABLES = "receivables"
    INFRASTRUCTURE = "infrastructure"
    MIXED_ASSETS = "mixed_assets"

class IslamicBankingProduct(Base):
    """Islamic banking products and their Sharia compliance details"""
    __tablename__ = 'islamic_banking_products'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Product identification
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False)  # ShariaProductType enum
    
    # Sharia structure details
    sharia_structure = Column(String(100), nullable=False)
    underlying_principle = Column(String(100))  # Sale, lease, partnership, etc.
    asset_backing = Column(String(50), nullable=False)  # AssetBacking enum
    
    # Financial details
    principal_amount = Column(Numeric(18, 2), nullable=False)
    profit_rate = Column(Numeric(8, 6), nullable=False)  # Sharia-compliant profit rate
    actual_profit_rate = Column(Numeric(8, 6))  # Current effective rate
    
    # Term and maturity
    term_months = Column(Integer, nullable=False)
    maturity_date = Column(DateTime)
    
    # Asset details
    asset_description = Column(Text)
    asset_value = Column(Numeric(18, 2))
    asset_ownership_percentage = Column(Numeric(5, 2))  # Bank's ownership %
    
    # Sharia compliance
    sharia_compliance_status = Column(String(50), default=ShariaComplianceStatus.PENDING_REVIEW.value)
    sharia_board_approval_date = Column(DateTime)
    sharia_board_member = Column(String(200))
    sharia_certificate_number = Column(String(100))
    
    # Compliance notes and conditions
    sharia_compliance_notes = Column(Text)
    compliance_conditions = Column(JSONB)  # List of compliance conditions
    
    # Risk assessment
    risk_category = Column(String(20), default='medium')  # low, medium, high
    risk_factors = Column(JSONB)  # List of risk factors
    
    # Product status
    is_active = Column(Boolean, default=True)
    is_shariah_compliant = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("IslamicTransaction", back_populates="product")
    compliance_reviews = relationship("ShariaComplianceReview", back_populates="product")
    
    def calculate_total_return(self) -> Decimal:
        """Calculate total return based on profit rate and term"""
        if self.principal_amount and self.profit_rate and self.term_months:
            monthly_rate = self.profit_rate / 12 / 100
            return self.principal_amount * (1 + monthly_rate * self.term_months)
        return Decimal('0.00')
    
    def __repr__(self):
        return f"<IslamicBankingProduct {self.product_code}: {self.product_type}>"

class MurabahaContract(Base):
    """Murabaha (cost-plus financing) contracts"""
    __tablename__ = 'murabaha_contracts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contract details
    contract_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Asset details
    asset_description = Column(Text, nullable=False)
    asset_cost = Column(Numeric(18, 2), nullable=False)  # Bank's purchase cost
    markup_amount = Column(Numeric(18, 2), nullable=False)  # Profit markup
    selling_price = Column(Numeric(18, 2), nullable=False)  # Total selling price
    
    # Payment terms
    payment_schedule = Column(String(50), nullable=False)  # monthly, quarterly, etc.
    number_of_installments = Column(Integer, nullable=False)
    installment_amount = Column(Numeric(18, 2), nullable=False)
    
    # Contract dates
    contract_date = Column(DateTime, nullable=False)
    asset_delivery_date = Column(DateTime)
    first_payment_date = Column(DateTime, nullable=False)
    final_payment_date = Column(DateTime, nullable=False)
    
    # Asset ownership
    asset_purchased_by_bank = Column(Boolean, default=False)
    asset_delivered_to_customer = Column(Boolean, default=False)
    ownership_transfer_date = Column(DateTime)
    
    # Contract status
    contract_status = Column(String(20), default='active')  # active, completed, defaulted
    outstanding_balance = Column(Numeric(18, 2))
    
    # Sharia compliance
    sharia_approved = Column(Boolean, default=False)
    purchase_order_provided = Column(Boolean, default=False)
    asset_inspection_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - using string reference to avoid circular imports
    customer = relationship("User", foreign_keys=[customer_id])
    payments = relationship("MurabahaPayment", back_populates="contract")
    
    def __repr__(self):
        return f"<MurabahaContract {self.contract_number}: {self.selling_price}>"

class MurabahaPayment(Base):
    """Payment records for Murabaha contracts"""
    __tablename__ = 'murabaha_payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Payment details
    contract_id = Column(UUID(as_uuid=True), ForeignKey('murabaha_contracts.id'), nullable=False)
    payment_number = Column(Integer, nullable=False)  # Installment number
    
    # Payment amounts
    scheduled_amount = Column(Numeric(18, 2), nullable=False)
    paid_amount = Column(Numeric(18, 2))
    principal_portion = Column(Numeric(18, 2))
    profit_portion = Column(Numeric(18, 2))
    
    # Payment dates
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    
    # Payment status
    payment_status = Column(String(20), default='pending')  # pending, paid, overdue, waived
    days_overdue = Column(Integer, default=0)
    
    # Late payment handling (Sharia-compliant)
    charity_amount = Column(Numeric(18, 2), default=0.00)  # Late payment charity
    charity_paid = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = relationship("MurabahaContract", back_populates="payments")
    
    def calculate_days_overdue(self):
        """Calculate days overdue if payment is late"""
        if self.payment_status == 'overdue' and not self.payment_date:
            self.days_overdue = (datetime.utcnow().date() - self.due_date.date()).days
        else:
            self.days_overdue = 0
    
    def __repr__(self):
        return f"<MurabahaPayment {self.payment_number}: {self.scheduled_amount}>"

class SukukInvestment(Base):
    """Sukuk (Islamic bonds) investments and tracking"""
    __tablename__ = 'sukuk_investments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Sukuk identification
    sukuk_id = Column(String(50), unique=True, nullable=False)
    sukuk_name = Column(String(200), nullable=False)
    issuer_name = Column(String(200), nullable=False)
    
    # Investment details
    face_value = Column(Numeric(18, 2), nullable=False)
    issue_price = Column(Numeric(18, 2), nullable=False)
    current_value = Column(Numeric(18, 2))
    
    # Profit distribution
    expected_profit_rate = Column(Numeric(8, 6), nullable=False)
    profit_distribution_frequency = Column(String(20))  # monthly, quarterly, semi-annual
    
    # Sukuk structure
    sukuk_structure = Column(String(50), nullable=False)  # ijara, murabaha, musharaka
    underlying_assets = Column(Text, nullable=False)
    asset_pool_value = Column(Numeric(18, 2))
    
    # Dates
    issue_date = Column(DateTime, nullable=False)
    maturity_date = Column(DateTime, nullable=False)
    next_profit_payment_date = Column(DateTime)
    
    # Investment status
    investment_status = Column(String(20), default='active')  # active, matured, sold
    
    # Sharia compliance
    sharia_board_certified = Column(Boolean, default=False)
    ongoing_sharia_monitoring = Column(Boolean, default=True)
    
    # Performance tracking
    total_profit_received = Column(Numeric(18, 2), default=0.00)
    yield_to_maturity = Column(Numeric(8, 6))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profit_payments = relationship("SukukProfitPayment", back_populates="sukuk")
    
    def __repr__(self):
        return f"<SukukInvestment {self.sukuk_id}: {self.face_value}>"

class SukukProfitPayment(Base):
    """Profit payment records for Sukuk investments"""
    __tablename__ = 'sukuk_profit_payments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Payment details
    sukuk_id = Column(UUID(as_uuid=True), ForeignKey('sukuk_investments.id'), nullable=False)
    payment_period = Column(String(50), nullable=False)  # Q1-2025, etc.
    
    # Payment amounts
    expected_amount = Column(Numeric(18, 2), nullable=False)
    actual_amount = Column(Numeric(18, 2))
    profit_rate_applied = Column(Numeric(8, 6))
    
    # Payment dates
    expected_payment_date = Column(DateTime, nullable=False)
    actual_payment_date = Column(DateTime)
    
    # Payment status
    payment_status = Column(String(20), default='pending')  # pending, received, delayed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sukuk = relationship("SukukInvestment", back_populates="profit_payments")
    
    def __repr__(self):
        return f"<SukukProfitPayment {self.payment_period}: {self.expected_amount}>"

class ShariaComplianceReview(Base):
    """Sharia compliance review records"""
    __tablename__ = 'sharia_compliance_reviews'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Review details
    product_id = Column(UUID(as_uuid=True), ForeignKey('islamic_banking_products.id'), nullable=False)
    review_type = Column(String(50), nullable=False)  # initial, periodic, special
    
    # Review team
    sharia_scholar = Column(String(200), nullable=False)
    review_committee = Column(JSONB)  # List of committee members
    
    # Review findings
    compliance_status = Column(String(50), nullable=False)
    compliance_score = Column(Integer)  # 1-100 scale
    findings = Column(Text)
    recommendations = Column(Text)
    
    # Compliance issues
    violations_found = Column(Boolean, default=False)
    violation_severity = Column(String(20))  # minor, major, critical
    violation_details = Column(Text)
    
    # Corrective actions
    corrective_actions_required = Column(Boolean, default=False)
    corrective_actions = Column(JSONB)  # List of required actions
    corrective_actions_deadline = Column(DateTime)
    
    # Review outcome
    recommendation = Column(String(50))  # approve, reject, modify, conditional_approval
    conditions = Column(JSONB)  # List of approval conditions
    
    # Review dates
    review_start_date = Column(DateTime, nullable=False)
    review_completion_date = Column(DateTime)
    next_review_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("IslamicBankingProduct", back_populates="compliance_reviews")
    
    def is_review_overdue(self) -> bool:
        """Check if review is overdue"""
        if self.next_review_date:
            return datetime.utcnow() > self.next_review_date
        return False
    
    def __repr__(self):
        return f"<ShariaComplianceReview {self.product_id}: {self.compliance_status}>"

class IslamicTransaction(Base):
    """Transaction records for Islamic banking products"""
    __tablename__ = 'islamic_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction details
    product_id = Column(UUID(as_uuid=True), ForeignKey('islamic_banking_products.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Transaction information
    transaction_type = Column(String(50), nullable=False)  # financing, payment, profit_distribution
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default='USD')
    
    # Islamic compliance
    sharia_compliant = Column(Boolean, default=True)
    compliance_verification_method = Column(String(100))
    
    # Transaction metadata
    description = Column(Text)
    reference_number = Column(String(50), unique=True, nullable=False)
    
    # Status and processing
    status = Column(String(20), default='pending')  # pending, completed, failed, cancelled
    processing_date = Column(DateTime)
    settlement_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("IslamicBankingProduct", back_populates="transactions")
    customer = relationship("User", foreign_keys=[customer_id])
    
    def __repr__(self):
        return f"<IslamicTransaction {self.reference_number}: {self.amount}>"

class ZakatCalculation(Base):
    """Zakat calculation and distribution records"""
    __tablename__ = 'zakat_calculations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Customer details
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    calculation_year = Column(Integer, nullable=False)
    
    # Wealth categories
    cash_and_savings = Column(Numeric(18, 2), default=0.00)
    gold_and_silver = Column(Numeric(18, 2), default=0.00)
    business_assets = Column(Numeric(18, 2), default=0.00)
    investment_assets = Column(Numeric(18, 2), default=0.00)
    other_assets = Column(Numeric(18, 2), default=0.00)
    
    # Liabilities
    outstanding_debts = Column(Numeric(18, 2), default=0.00)
    immediate_expenses = Column(Numeric(18, 2), default=0.00)
    
    # Calculation details
    total_zakatable_wealth = Column(Numeric(18, 2), nullable=False)
    nisab_threshold = Column(Numeric(18, 2), nullable=False)  # Current nisab value
    zakat_rate = Column(Numeric(5, 4), default=2.5000)  # 2.5%
    
    # Zakat amount
    zakat_due = Column(Numeric(18, 2), nullable=False)
    zakat_paid = Column(Numeric(18, 2), default=0.00)
    zakat_outstanding = Column(Numeric(18, 2), nullable=False)
    
    # Payment details
    payment_method = Column(String(50))  # direct_donation, bank_distribution, manual
    distribution_preference = Column(JSONB)  # Preferred charity categories
    
    # Status
    calculation_status = Column(String(20), default='calculated')  # calculated, paid, overdue
    
    # Timestamps
    calculation_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    distributions = relationship("ZakatDistribution", back_populates="calculation")
    
    def is_eligible_for_zakat(self) -> bool:
        """Check if wealth exceeds nisab threshold"""
        return self.total_zakatable_wealth >= self.nisab_threshold
    
    def __repr__(self):
        return f"<ZakatCalculation {self.customer_id}: {self.zakat_due}>"

class ZakatDistribution(Base):
    """Zakat distribution records to beneficiaries"""
    __tablename__ = 'zakat_distributions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Distribution details
    calculation_id = Column(UUID(as_uuid=True), ForeignKey('zakat_calculations.id'), nullable=False)
    
    # Beneficiary information
    beneficiary_category = Column(String(50), nullable=False)  # poor, needy, travelers, etc.
    beneficiary_organization = Column(String(200))
    
    # Distribution amount
    amount_distributed = Column(Numeric(18, 2), nullable=False)
    distribution_method = Column(String(50))  # direct_transfer, charity_organization
    
    # Geographic distribution
    distribution_location = Column(String(200))
    local_distribution = Column(Boolean, default=True)
    
    # Distribution tracking
    distribution_date = Column(DateTime, nullable=False)
    confirmation_received = Column(Boolean, default=False)
    receipt_number = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    calculation = relationship("ZakatCalculation", back_populates="distributions")
    
    def __repr__(self):
        return f"<ZakatDistribution {self.beneficiary_category}: {self.amount_distributed}>"

# Create indexes for optimal query performance
Index('idx_islamic_banking_products_code', IslamicBankingProduct.product_code)
Index('idx_islamic_banking_products_type', IslamicBankingProduct.product_type)
Index('idx_islamic_banking_products_compliance_status', IslamicBankingProduct.sharia_compliance_status)
Index('idx_murabaha_contracts_customer_id', MurabahaContract.customer_id)
Index('idx_murabaha_contracts_contract_number', MurabahaContract.contract_number)
Index('idx_murabaha_contracts_status', MurabahaContract.contract_status)
Index('idx_murabaha_payments_contract_id', MurabahaPayment.contract_id)
Index('idx_murabaha_payments_due_date', MurabahaPayment.due_date)
Index('idx_sukuk_investments_sukuk_id', SukukInvestment.sukuk_id)
Index('idx_sukuk_investments_status', SukukInvestment.investment_status)
Index('idx_sharia_compliance_reviews_product_id', ShariaComplianceReview.product_id)
Index('idx_islamic_transactions_product_id', IslamicTransaction.product_id)
Index('idx_islamic_transactions_customer_id', IslamicTransaction.customer_id)
Index('idx_zakat_calculations_customer_id', ZakatCalculation.customer_id)
Index('idx_zakat_calculations_year', ZakatCalculation.calculation_year)
Index('idx_zakat_distributions_calculation_id', ZakatDistribution.calculation_id)