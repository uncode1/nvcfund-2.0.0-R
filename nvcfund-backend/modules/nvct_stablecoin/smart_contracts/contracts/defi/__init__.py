"""
DeFi Smart Contracts Module
Enterprise-grade decentralized finance smart contracts and compliance integration
"""

# Import DeFi compliance integration components
from .defi_compliance_integration import (
    DeFiComplianceIntegration,
    DeFiTransaction,
    RiskCategory,
    ComplianceLevel,
    DeFiComplianceRule,
    DeFiTransactionMonitor,
    DeFiRiskAssessor,
    DeFiAuditLogger
)

# Export all DeFi components for easy importing
__all__ = [
    # Core compliance classes
    'DeFiComplianceIntegration',
    'DeFiTransaction',
    'RiskCategory', 
    'ComplianceLevel',
    'DeFiComplianceRule',
    
    # Monitoring and assessment classes
    'DeFiTransactionMonitor',
    'DeFiRiskAssessor', 
    'DeFiAuditLogger',
]

# Module metadata
__version__ = "2.0.0"
__author__ = "NVC Banking Platform"
__description__ = "Enterprise DeFi smart contracts with compliance integration"

# Contract file mappings for easy reference
DEFI_CONTRACTS = {
    'yield_farming': 'YieldFarmingProtocol.sol',
    'flash_loans': 'FlashLoanProtocol.sol',
    'amm': 'ConcentratedLiquidityAMM.sol',
    'staking': 'AdvancedStaking.sol'
}

# Template mappings
DEFI_TEMPLATES = {
    'dashboard': 'templates/defi_dashboard.html',
    'yield_farming': 'templates/yield_farming.html',
    'flash_loans': 'templates/flash_loans.html',
    'amm_trading': 'templates/amm_trading.html',
    'staking': 'templates/staking.html',
    'governance': 'templates/governance.html'
}
