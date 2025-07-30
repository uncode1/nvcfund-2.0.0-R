"""
Smart Contracts Module - Enterprise DeFi 2.0 Implementation
Enterprise-grade blockchain smart contract management and deployment system
with modern DeFi features, advanced security, and compliance frameworks

Features:
- Yield Farming & Advanced Staking
- AMM with Concentrated Liquidity
- Flash Loan Capabilities
- MEV Protection
- Upgradeable Contract Patterns
- Advanced Governance (Quadratic Voting)
- Emergency Controls & Circuit Breakers
- Account Abstraction (ERC-4337)
- Gasless Transactions
- Zero-Knowledge Integration
- Latest ERC Standards
- Formal Verification Integration
"""

# Import all contract components for easy access at the top level
from .contracts import (
    # DeFi components
    DeFiComplianceIntegration,
    DeFiTransaction,
    RiskCategory,
    ComplianceLevel,
    DeFiComplianceRule,
    DeFiTransactionMonitor,
    DeFiRiskAssessor,
    DeFiAuditLogger,

    # Contract and template mappings
    DEFI_CONTRACTS,
    DEFI_TEMPLATES,
    MODULES
)

# Export everything at the smart_contracts level for easy importing
__all__ = [
    # DeFi components
    'DeFiComplianceIntegration',
    'DeFiTransaction',
    'RiskCategory',
    'ComplianceLevel',
    'DeFiComplianceRule',
    'DeFiTransactionMonitor',
    'DeFiRiskAssessor',
    'DeFiAuditLogger',

    # Mappings
    'DEFI_CONTRACTS',
    'DEFI_TEMPLATES',
    'MODULES',

    # Blueprint
    'smart_contracts_bp',
]

__version__ = "2.0.0"
__author__ = "NVC Banking Platform"
__description__ = "Enterprise smart contracts with hierarchical organization"

from .routes import smart_contracts_bp