"""
NVCT Stablecoin Models
Self-contained models for $30T NVCT stablecoin operations and multi-network management
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

class NVCTOperationType(Enum):
    """Types of NVCT operations"""
    MINTING = "minting"
    BURNING = "burning"
    CROSS_CHAIN_BRIDGE = "cross_chain_bridge"
    COLLATERAL_DEPOSIT = "collateral_deposit"
    COLLATERAL_WITHDRAWAL = "collateral_withdrawal"
    GOVERNANCE_PROPOSAL = "governance_proposal"
    EMERGENCY_PAUSE = "emergency_pause"
    RESERVE_REBALANCING = "reserve_rebalancing"

class BlockchainNetwork(Enum):
    """Supported blockchain networks"""
    BSC = "bsc"
    POLYGON = "polygon"
    ETHEREUM = "ethereum"
    FANTOM = "fantom"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"

class NVCTTransactionStatus(Enum):
    """NVCT transaction status"""
    PENDING = "pending"
    INITIATED = "initiated"
    CONFIRMING = "confirming"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NVCTSupplyManagement(Base):
    """NVCT stablecoin supply management and tracking"""
    __tablename__ = 'nvct_supply_management'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Supply tracking
    total_supply = Column(Numeric(24, 2), nullable=False, default=30000000000000.00)  # $30T target
    circulating_supply = Column(Numeric(24, 2), nullable=False, default=0.00)
    
    # Network distribution
    bsc_supply = Column(Numeric(24, 2), default=0.00)
    polygon_supply = Column(Numeric(24, 2), default=0.00)
    ethereum_supply = Column(Numeric(24, 2), default=0.00)
    fantom_supply = Column(Numeric(24, 2), default=0.00)
    other_networks_supply = Column(Numeric(24, 2), default=0.00)
    
    # Collateral backing
    total_collateral_usd = Column(Numeric(24, 2), nullable=False)
    collateralization_ratio = Column(Numeric(8, 4), nullable=False)  # Target: 189% (56.7T/30T)
    
    # Asset backing breakdown
    us_treasury_backing = Column(Numeric(24, 2), default=0.00)
    corporate_bonds_backing = Column(Numeric(24, 2), default=0.00)
    real_estate_backing = Column(Numeric(24, 2), default=0.00)
    gold_backing = Column(Numeric(24, 2), default=0.00)
    commodity_backing = Column(Numeric(24, 2), default=0.00)
    cash_equivalents_backing = Column(Numeric(24, 2), default=0.00)
    
    # Operational limits
    daily_mint_limit = Column(Numeric(24, 2), default=500000000.00)  # $500M daily
    daily_burn_limit = Column(Numeric(24, 2), default=100000000.00)  # $100M daily
    emergency_pause_active = Column(Boolean, default=False)
    
    # Market metrics
    peg_stability_score = Column(Numeric(6, 4), default=99.9900)  # Target: 99.99%
    volume_24h = Column(Numeric(24, 2), default=0.00)
    market_cap_ranking = Column(Integer)
    
    # Governance and control
    governance_threshold = Column(Numeric(8, 4), default=67.0000)  # 67% supermajority
    treasury_multisig_threshold = Column(Integer, default=5)  # 5 of 7 signatures
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    operations = relationship("NVCTOperation", back_populates="supply_management")
    bridge_transactions = relationship("NVCTBridgeTransaction", back_populates="supply_management")
    
    def calculate_backing_ratio(self) -> Decimal:
        """Calculate current backing ratio"""
        if self.circulating_supply > 0:
            return (self.total_collateral_usd / self.circulating_supply) * 100
        return Decimal('0.00')
    
    def get_network_distribution(self) -> Dict[str, Decimal]:
        """Get supply distribution across networks"""
        return {
            'bsc': self.bsc_supply,
            'polygon': self.polygon_supply,
            'ethereum': self.ethereum_supply,
            'fantom': self.fantom_supply,
            'other': self.other_networks_supply
        }
    
    def __repr__(self):
        return f"<NVCTSupplyManagement Supply: {self.circulating_supply}, Collateral: {self.total_collateral_usd}>"

class NVCTOperation(Base):
    """NVCT operational transactions and minting/burning operations"""
    __tablename__ = 'nvct_operations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Operation details
    supply_management_id = Column(UUID(as_uuid=True), ForeignKey('nvct_supply_management.id'), nullable=False)
    operation_type = Column(String(50), nullable=False)  # NVCTOperationType
    
    # Transaction details
    amount = Column(Numeric(24, 2), nullable=False)
    target_network = Column(String(20), nullable=False)  # BlockchainNetwork
    
    # Blockchain execution
    transaction_hash = Column(String(66))  # Ethereum tx hash
    block_number = Column(Integer)
    gas_used = Column(Integer)
    gas_price_gwei = Column(Numeric(18, 9))
    
    # Authorization and compliance
    authorized_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    authorization_level = Column(String(50), nullable=False)  # treasury_officer, board, emergency
    compliance_verified = Column(Boolean, default=False)
    
    # Financial tracking
    usd_equivalent = Column(Numeric(24, 2), nullable=False)
    exchange_rate_used = Column(Numeric(18, 8), default=1.00000000)  # NVCT/USD rate
    fee_amount = Column(Numeric(18, 8), default=0.00000000)
    
    # Collateral requirements
    collateral_required = Column(Numeric(24, 2))
    collateral_posted = Column(Numeric(24, 2))
    collateral_sources = Column(JSONB)  # List of collateral sources
    
    # Operational context
    operation_reason = Column(String(200), nullable=False)
    market_conditions = Column(Text)
    risk_assessment = Column(String(20))  # low, medium, high, critical
    
    # Status and execution
    status = Column(String(20), default=NVCTTransactionStatus.PENDING.value)
    initiated_at = Column(DateTime)
    completed_at = Column(DateTime)
    failed_reason = Column(Text)
    
    # Supply impact
    supply_before = Column(Numeric(24, 2), nullable=False)
    supply_after = Column(Numeric(24, 2), nullable=False)
    backing_ratio_impact = Column(Numeric(8, 4))
    
    # Regulatory compliance
    regulatory_approval = Column(Boolean, default=False)
    aml_cleared = Column(Boolean, default=False)
    ofac_cleared = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supply_management = relationship("NVCTSupplyManagement", back_populates="operations")
    authorizer = relationship("User", foreign_keys=[authorized_by])
    
    def validate_operation_limits(self) -> bool:
        """Validate operation against daily limits"""
        # This would check against daily operation limits
        return True
    
    def __repr__(self):
        return f"<NVCTOperation {self.operation_type}: {self.amount} NVCT>"

class NVCTBridgeTransaction(Base):
    """Cross-chain bridge transactions for NVCT"""
    __tablename__ = 'nvct_bridge_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Bridge operation details
    supply_management_id = Column(UUID(as_uuid=True), ForeignKey('nvct_supply_management.id'), nullable=False)
    bridge_direction = Column(String(20), nullable=False)  # lock_and_mint, burn_and_unlock
    
    # Source and destination
    source_network = Column(String(20), nullable=False)  # BlockchainNetwork
    destination_network = Column(String(20), nullable=False)  # BlockchainNetwork
    
    # Transaction amounts
    amount = Column(Numeric(24, 2), nullable=False)
    bridge_fee = Column(Numeric(18, 8), default=0.00000000)
    network_fee_source = Column(Numeric(18, 8))
    network_fee_destination = Column(Numeric(18, 8))
    
    # User details
    user_address_source = Column(String(42), nullable=False)  # Ethereum address
    user_address_destination = Column(String(42), nullable=False)
    
    # Transaction hashes
    source_tx_hash = Column(String(66))
    destination_tx_hash = Column(String(66))
    lock_tx_hash = Column(String(66))  # For lock operations
    unlock_tx_hash = Column(String(66))  # For unlock operations
    
    # Bridge validation
    source_confirmations = Column(Integer, default=0)
    required_confirmations = Column(Integer, default=12)
    validator_signatures = Column(JSONB)  # List of validator signatures
    
    # Status tracking
    status = Column(String(20), default=NVCTTransactionStatus.PENDING.value)
    source_status = Column(String(20), default='pending')
    destination_status = Column(String(20), default='pending')
    
    # Timing
    initiated_at = Column(DateTime, nullable=False)
    source_confirmed_at = Column(DateTime)
    destination_executed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Error handling
    failed_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supply_management = relationship("NVCTSupplyManagement", back_populates="bridge_transactions")
    
    def is_bridge_complete(self) -> bool:
        """Check if bridge transaction is complete"""
        return (self.status == NVCTTransactionStatus.CONFIRMED.value and 
                self.source_confirmations >= self.required_confirmations and
                self.destination_tx_hash is not None)
    
    def __repr__(self):
        return f"<NVCTBridgeTransaction {self.source_network}->{self.destination_network}: {self.amount}>"

class NVCTGovernance(Base):
    """NVCT governance proposals and voting"""
    __tablename__ = 'nvct_governance'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Proposal details
    proposal_id = Column(String(50), unique=True, nullable=False)
    proposal_title = Column(String(200), nullable=False)
    proposal_description = Column(Text, nullable=False)
    proposal_type = Column(String(50), nullable=False)  # parameter_change, upgrade, emergency
    
    # Proposer information
    proposed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    proposer_stake = Column(Numeric(24, 2), nullable=False)
    
    # Proposal parameters
    target_parameter = Column(String(100))  # Parameter being changed
    current_value = Column(String(200))
    proposed_value = Column(String(200))
    
    # Smart contract details
    target_contract = Column(String(42))  # Contract address
    function_call = Column(Text)  # Encoded function call
    
    # Voting mechanics
    voting_start = Column(DateTime, nullable=False)
    voting_end = Column(DateTime, nullable=False)
    minimum_quorum = Column(Numeric(8, 4), default=33.0000)  # 33% quorum
    approval_threshold = Column(Numeric(8, 4), default=67.0000)  # 67% approval
    
    # Voting results
    votes_for = Column(Numeric(24, 2), default=0.00)
    votes_against = Column(Numeric(24, 2), default=0.00)
    votes_abstain = Column(Numeric(24, 2), default=0.00)
    total_votes = Column(Numeric(24, 2), default=0.00)
    
    # Participation metrics
    unique_voters = Column(Integer, default=0)
    voter_turnout_percent = Column(Numeric(8, 4), default=0.0000)
    
    # Execution details
    proposal_status = Column(String(20), default='active')  # active, passed, failed, executed, cancelled
    execution_eta = Column(DateTime)  # Estimated execution time
    executed_at = Column(DateTime)
    execution_tx_hash = Column(String(66))
    
    # Risk assessment
    impact_assessment = Column(Text)
    security_review_status = Column(String(20))  # pending, approved, rejected
    technical_review_status = Column(String(20))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    proposer = relationship("User", foreign_keys=[proposed_by])
    votes = relationship("NVCTGovernanceVote", back_populates="proposal")
    
    def calculate_approval_rate(self) -> Decimal:
        """Calculate current approval rate"""
        if self.total_votes > 0:
            return (self.votes_for / self.total_votes) * 100
        return Decimal('0.00')
    
    def meets_quorum(self, total_supply: Decimal) -> bool:
        """Check if proposal meets minimum quorum"""
        if total_supply > 0:
            participation_rate = (self.total_votes / total_supply) * 100
            return participation_rate >= self.minimum_quorum
        return False
    
    def __repr__(self):
        return f"<NVCTGovernance {self.proposal_id}: {self.proposal_status}>"

class NVCTGovernanceVote(Base):
    """Individual governance votes"""
    __tablename__ = 'nvct_governance_votes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Vote details
    proposal_id = Column(UUID(as_uuid=True), ForeignKey('nvct_governance.id'), nullable=False)
    voter_address = Column(String(42), nullable=False)  # Voter's wallet address
    
    # Vote choice and weight
    vote_choice = Column(String(20), nullable=False)  # for, against, abstain
    voting_power = Column(Numeric(24, 2), nullable=False)  # NVCT tokens held
    
    # Vote validation
    signature = Column(String(132))  # Cryptographic signature
    message_hash = Column(String(66))
    block_number = Column(Integer)
    
    # Timestamps
    voted_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    proposal = relationship("NVCTGovernance", back_populates="votes")
    
    def __repr__(self):
        return f"<NVCTGovernanceVote {self.vote_choice}: {self.voting_power}>"

class NVCTMarketData(Base):
    """NVCT market data and price tracking"""
    __tablename__ = 'nvct_market_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Price data
    timestamp = Column(DateTime, nullable=False)
    price_usd = Column(Numeric(18, 8), nullable=False)
    price_deviation = Column(Numeric(8, 6))  # Deviation from $1.00 peg
    
    # Volume data
    volume_24h = Column(Numeric(24, 2), default=0.00)
    volume_7d = Column(Numeric(24, 2), default=0.00)
    volume_30d = Column(Numeric(24, 2), default=0.00)
    
    # Market metrics
    market_cap = Column(Numeric(24, 2))
    market_cap_rank = Column(Integer)
    dominance_percentage = Column(Numeric(8, 4))
    
    # Trading data by exchange
    trading_pairs = Column(JSONB)  # List of trading pairs
    exchange_volumes = Column(JSONB)  # Volume by exchange
    liquidity_pools = Column(JSONB)  # DeFi liquidity data
    
    # Stability metrics
    volatility_24h = Column(Numeric(8, 6))
    volatility_7d = Column(Numeric(8, 6))
    volatility_30d = Column(Numeric(8, 6))
    
    # Network activity
    active_addresses = Column(Integer)
    transaction_count_24h = Column(Integer)
    unique_holders = Column(Integer)
    
    # DeFi integration metrics
    total_value_locked = Column(Numeric(24, 2))
    defi_protocols = Column(JSONB)  # List of integrated protocols
    yield_opportunities = Column(JSONB)  # Available yield options
    
    # Arbitrage and peg maintenance
    arbitrage_opportunities = Column(JSONB)  # Cross-exchange arbitrage
    peg_maintenance_actions = Column(JSONB)  # Automated peg maintenance
    
    # Data sources
    data_sources = Column(JSONB)  # List of price feed sources
    data_quality_score = Column(Integer)  # 1-100 quality score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def is_within_peg_range(self, tolerance: Decimal = Decimal('0.005')) -> bool:
        """Check if price is within acceptable peg range"""
        target_price = Decimal('1.00')
        deviation = abs(self.price_usd - target_price)
        return deviation <= tolerance
    
    def __repr__(self):
        return f"<NVCTMarketData {self.timestamp}: ${self.price_usd}>"

class NVCTAuditLog(Base):
    """Comprehensive audit logging for NVCT operations"""
    __tablename__ = 'nvct_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    event_category = Column(String(50), nullable=False)  # operation, governance, security, maintenance
    
    # User and authorization
    user_id = Column(Integer, ForeignKey('users.id'))
    user_role = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Operation details
    operation_id = Column(UUID(as_uuid=True))  # Reference to related operation
    before_state = Column(JSONB)  # State before operation
    after_state = Column(JSONB)  # State after operation
    
    # Transaction details
    transaction_hash = Column(String(66))
    block_number = Column(Integer)
    network = Column(String(20))
    
    # Financial impact
    amount_involved = Column(Numeric(24, 2))
    currency = Column(String(10))
    fee_paid = Column(Numeric(18, 8))
    
    # Security and compliance
    security_level = Column(String(20))  # routine, elevated, critical
    compliance_flags = Column(JSONB)  # Compliance considerations
    risk_score = Column(Integer)  # 1-100 risk score
    
    # Event description and context
    event_description = Column(Text, nullable=False)
    technical_details = Column(JSONB)
    error_details = Column(Text)
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<NVCTAuditLog {self.event_type}: {self.event_timestamp}>"

# Create indexes for optimal query performance
Index('idx_nvct_supply_management_last_updated', NVCTSupplyManagement.last_updated)
Index('idx_nvct_operations_operation_type', NVCTOperation.operation_type)
Index('idx_nvct_operations_status', NVCTOperation.status)
Index('idx_nvct_operations_authorized_by', NVCTOperation.authorized_by)
Index('idx_nvct_operations_created_at', NVCTOperation.created_at)
Index('idx_nvct_bridge_transactions_status', NVCTBridgeTransaction.status)
Index('idx_nvct_bridge_transactions_source_network', NVCTBridgeTransaction.source_network)
Index('idx_nvct_bridge_transactions_destination_network', NVCTBridgeTransaction.destination_network)
Index('idx_nvct_governance_proposal_status', NVCTGovernance.proposal_status)
Index('idx_nvct_governance_voting_end', NVCTGovernance.voting_end)
Index('idx_nvct_governance_votes_proposal_id', NVCTGovernanceVote.proposal_id)
Index('idx_nvct_governance_votes_voter_address', NVCTGovernanceVote.voter_address)
Index('idx_nvct_market_data_timestamp', NVCTMarketData.timestamp)
Index('idx_nvct_market_data_price_usd', NVCTMarketData.price_usd)
Index('idx_nvct_audit_logs_event_type', NVCTAuditLog.event_type)
Index('idx_nvct_audit_logs_event_timestamp', NVCTAuditLog.event_timestamp)
Index('idx_nvct_audit_logs_user_id', NVCTAuditLog.user_id)