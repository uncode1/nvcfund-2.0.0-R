"""
Smart Contract Implementations
Enterprise-grade Solidity contracts with modern DeFi 2.0 features and hierarchical organization
"""

# Import all DeFi components for easy access
from .defi import (
    DeFiComplianceIntegration,
    DeFiTransaction,
    RiskCategory,
    ComplianceLevel,
    DeFiComplianceRule,
    DeFiTransactionMonitor,
    DeFiRiskAssessor,
    DeFiAuditLogger,
    DEFI_CONTRACTS,
    DEFI_TEMPLATES
)

# Export everything at the contracts level for easy importing
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

    # Contract and template mappings
    'DEFI_CONTRACTS',
    'DEFI_TEMPLATES',
]

# Module organization
MODULES = {
    'defi': 'DeFi 2.0 smart contracts and compliance',
    'governance': 'Governance and voting contracts',
    'security': 'Security and protection contracts',
    'standards': 'Standard implementations and integrations'
}

__version__ = "2.0.0"
__author__ = "NVC Banking Platform"
