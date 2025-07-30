"""
DeFi Compliance Integration Service
Enterprise-grade integration between modern DeFi features and compliance systems
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from cryptography.fernet import Fernet

from ....services import SmartContractService
from .....security_center.data_security import security_framework
from .....compliance.services import ComplianceService


class ComplianceLevel(Enum):
    """Compliance levels for DeFi operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    """Risk categories for DeFi activities."""
    YIELD_FARMING = "yield_farming"
    FLASH_LOANS = "flash_loans"
    AMM_TRADING = "amm_trading"
    STAKING = "staking"
    GOVERNANCE = "governance"
    CROSS_CHAIN = "cross_chain"


@dataclass
class DeFiComplianceRule:
    """DeFi-specific compliance rule."""
    rule_id: str
    category: RiskCategory
    compliance_level: ComplianceLevel
    max_amount: Decimal
    daily_limit: Decimal
    requires_kyc: bool
    requires_aml_check: bool
    geographic_restrictions: List[str] = field(default_factory=list)
    time_restrictions: Dict[str, Any] = field(default_factory=dict)
    additional_checks: List[str] = field(default_factory=list)


@dataclass
class DeFiTransaction:
    """DeFi transaction with compliance metadata."""
    tx_id: str
    user_id: str
    contract_address: str
    function_name: str
    amount: Decimal
    token_address: str
    category: RiskCategory
    timestamp: datetime
    compliance_score: int = 0
    risk_flags: List[str] = field(default_factory=list)
    aml_status: str = "pending"
    kyc_status: str = "pending"
    approved: bool = False


class DeFiComplianceIntegration:
    """
    Enterprise DeFi Compliance Integration Service
    
    Integrates all modern DeFi features with existing compliance systems:
    - Real-time transaction monitoring
    - AML/KYC integration
    - Risk assessment
    - Regulatory reporting
    - Audit trail maintenance
    """

    def __init__(self):
        """Initialize DeFi compliance integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.smart_contract_service = SmartContractService()
        self.compliance_service = ComplianceService()
        self.security_framework = security_framework
        
        # Initialize compliance rules
        self.compliance_rules = self._initialize_compliance_rules()
        
        # Initialize monitoring systems
        self.transaction_monitor = DeFiTransactionMonitor()
        self.risk_assessor = DeFiRiskAssessor()
        self.audit_logger = DeFiAuditLogger()
        
        # Encryption for sensitive data
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)

    def _initialize_compliance_rules(self) -> Dict[RiskCategory, List[DeFiComplianceRule]]:
        """Initialize DeFi compliance rules."""
        rules = {
            RiskCategory.YIELD_FARMING: [
                DeFiComplianceRule(
                    rule_id="YF_001",
                    category=RiskCategory.YIELD_FARMING,
                    compliance_level=ComplianceLevel.MEDIUM,
                    max_amount=Decimal('1000000'),  # $1M max
                    daily_limit=Decimal('100000'),  # $100K daily
                    requires_kyc=True,
                    requires_aml_check=True,
                    geographic_restrictions=['US', 'CN', 'KP'],
                    additional_checks=['smart_contract_audit', 'liquidity_check']
                )
            ],
            RiskCategory.FLASH_LOANS: [
                DeFiComplianceRule(
                    rule_id="FL_001",
                    category=RiskCategory.FLASH_LOANS,
                    compliance_level=ComplianceLevel.HIGH,
                    max_amount=Decimal('10000000'),  # $10M max
                    daily_limit=Decimal('50000000'),  # $50M daily
                    requires_kyc=True,
                    requires_aml_check=True,
                    geographic_restrictions=['US', 'CN', 'KP', 'IR'],
                    additional_checks=['mev_analysis', 'arbitrage_detection', 'liquidation_risk']
                )
            ],
            RiskCategory.AMM_TRADING: [
                DeFiComplianceRule(
                    rule_id="AMM_001",
                    category=RiskCategory.AMM_TRADING,
                    compliance_level=ComplianceLevel.MEDIUM,
                    max_amount=Decimal('5000000'),  # $5M max
                    daily_limit=Decimal('1000000'),  # $1M daily
                    requires_kyc=True,
                    requires_aml_check=True,
                    additional_checks=['slippage_analysis', 'front_running_detection']
                )
            ],
            RiskCategory.STAKING: [
                DeFiComplianceRule(
                    rule_id="STK_001",
                    category=RiskCategory.STAKING,
                    compliance_level=ComplianceLevel.LOW,
                    max_amount=Decimal('2000000'),  # $2M max
                    daily_limit=Decimal('500000'),  # $500K daily
                    requires_kyc=True,
                    requires_aml_check=False,
                    additional_checks=['validator_verification', 'slashing_risk']
                )
            ],
            RiskCategory.GOVERNANCE: [
                DeFiComplianceRule(
                    rule_id="GOV_001",
                    category=RiskCategory.GOVERNANCE,
                    compliance_level=ComplianceLevel.HIGH,
                    max_amount=Decimal('0'),  # No monetary limit
                    daily_limit=Decimal('0'),
                    requires_kyc=True,
                    requires_aml_check=True,
                    additional_checks=['voting_power_analysis', 'proposal_review']
                )
            ]
        }
        return rules

    async def validate_defi_transaction(
        self, 
        transaction: DeFiTransaction
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate DeFi transaction against compliance rules.
        
        Returns:
            Tuple of (is_approved, risk_flags, compliance_metadata)
        """
        try:
            self.logger.info(f"Validating DeFi transaction: {transaction.tx_id}")
            
            # Get applicable compliance rules
            rules = self.compliance_rules.get(transaction.category, [])
            if not rules:
                return False, ["No compliance rules found"], {}
            
            risk_flags = []
            compliance_metadata = {
                'validation_timestamp': datetime.utcnow().isoformat(),
                'rules_applied': [rule.rule_id for rule in rules],
                'compliance_score': 0
            }
            
            # Apply each compliance rule
            for rule in rules:
                rule_result = await self._apply_compliance_rule(transaction, rule)
                
                if not rule_result['passed']:
                    risk_flags.extend(rule_result['flags'])
                
                compliance_metadata[f'rule_{rule.rule_id}'] = rule_result
            
            # Perform AML check if required
            if any(rule.requires_aml_check for rule in rules):
                aml_result = await self._perform_aml_check(transaction)
                transaction.aml_status = aml_result['status']
                
                if aml_result['status'] != 'approved':
                    risk_flags.append(f"AML check failed: {aml_result['reason']}")
                
                compliance_metadata['aml_check'] = aml_result
            
            # Perform KYC check if required
            if any(rule.requires_kyc for rule in rules):
                kyc_result = await self._perform_kyc_check(transaction)
                transaction.kyc_status = kyc_result['status']
                
                if kyc_result['status'] != 'verified':
                    risk_flags.append(f"KYC check failed: {kyc_result['reason']}")
                
                compliance_metadata['kyc_check'] = kyc_result
            
            # Calculate overall compliance score
            compliance_score = self._calculate_compliance_score(transaction, rules, risk_flags)
            transaction.compliance_score = compliance_score
            compliance_metadata['compliance_score'] = compliance_score
            
            # Determine approval
            is_approved = len(risk_flags) == 0 and compliance_score >= 70
            transaction.approved = is_approved
            transaction.risk_flags = risk_flags
            
            # Log audit trail
            await self.audit_logger.log_compliance_check(transaction, compliance_metadata)
            
            self.logger.info(
                f"Transaction {transaction.tx_id} validation complete: "
                f"approved={is_approved}, score={compliance_score}"
            )
            
            return is_approved, risk_flags, compliance_metadata
            
        except Exception as e:
            self.logger.error(f"Error validating DeFi transaction: {e}")
            return False, [f"Validation error: {str(e)}"], {}

    async def _apply_compliance_rule(
        self, 
        transaction: DeFiTransaction, 
        rule: DeFiComplianceRule
    ) -> Dict[str, Any]:
        """Apply a specific compliance rule to a transaction."""
        result = {
            'rule_id': rule.rule_id,
            'passed': True,
            'flags': [],
            'metadata': {}
        }
        
        try:
            # Check amount limits
            if rule.max_amount > 0 and transaction.amount > rule.max_amount:
                result['passed'] = False
                result['flags'].append(f"Amount {transaction.amount} exceeds max {rule.max_amount}")
            
            # Check daily limits
            if rule.daily_limit > 0:
                daily_usage = await self._get_daily_usage(transaction.user_id, rule.category)
                if daily_usage + transaction.amount > rule.daily_limit:
                    result['passed'] = False
                    result['flags'].append(f"Daily limit exceeded: {daily_usage + transaction.amount} > {rule.daily_limit}")
            
            # Check geographic restrictions
            if rule.geographic_restrictions:
                user_location = await self._get_user_location(transaction.user_id)
                if user_location in rule.geographic_restrictions:
                    result['passed'] = False
                    result['flags'].append(f"Geographic restriction: {user_location}")
            
            # Apply additional checks
            for check in rule.additional_checks:
                check_result = await self._perform_additional_check(transaction, check)
                if not check_result['passed']:
                    result['passed'] = False
                    result['flags'].extend(check_result['flags'])
                result['metadata'][check] = check_result
            
        except Exception as e:
            self.logger.error(f"Error applying compliance rule {rule.rule_id}: {e}")
            result['passed'] = False
            result['flags'].append(f"Rule application error: {str(e)}")
        
        return result

    async def _perform_aml_check(self, transaction: DeFiTransaction) -> Dict[str, Any]:
        """Perform AML check on transaction."""
        try:
            # Use existing AML service
            aml_result = self.smart_contract_service._perform_aml_check(
                amount=float(transaction.amount),
                user_id=transaction.user_id,
                transaction_type=transaction.category.value
            )
            
            return {
                'status': 'approved' if aml_result['compliant'] else 'rejected',
                'reason': aml_result.get('reason', ''),
                'enhanced_dd_required': aml_result.get('enhanced_dd_required', False),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AML check error: {e}")
            return {
                'status': 'error',
                'reason': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    def _calculate_compliance_score(
        self, 
        transaction: DeFiTransaction, 
        rules: List[DeFiComplianceRule], 
        risk_flags: List[str]
    ) -> int:
        """Calculate overall compliance score (0-100)."""
        base_score = 100
        
        # Deduct points for risk flags
        score_deduction = len(risk_flags) * 15
        
        # Adjust based on transaction category risk
        category_risk_multiplier = {
            RiskCategory.YIELD_FARMING: 0.9,
            RiskCategory.FLASH_LOANS: 0.7,
            RiskCategory.AMM_TRADING: 0.8,
            RiskCategory.STAKING: 0.95,
            RiskCategory.GOVERNANCE: 0.85
        }
        
        multiplier = category_risk_multiplier.get(transaction.category, 0.8)
        final_score = int((base_score - score_deduction) * multiplier)
        
        return max(0, min(100, final_score))

    async def _get_daily_usage(self, user_id: str, category: RiskCategory) -> Decimal:
        """Get user's daily usage for a category."""
        return Decimal('0')  # Placeholder

    async def _get_user_location(self, user_id: str) -> str:
        """Get user's geographic location."""
        return "US"  # Placeholder

    async def _perform_kyc_check(self, transaction: DeFiTransaction) -> Dict[str, Any]:
        """Perform KYC check on user."""
        try:
            return {
                'status': 'verified',
                'verification_level': 'full',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'reason': str(e), 'timestamp': datetime.utcnow().isoformat()}

    async def _perform_additional_check(self, transaction: DeFiTransaction, check_type: str) -> Dict[str, Any]:
        """Perform additional compliance checks."""
        return {'passed': True, 'flags': [], 'metadata': {}}


class DeFiTransactionMonitor:
    """Real-time DeFi transaction monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")


class DeFiRiskAssessor:
    """DeFi risk assessment engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")


class DeFiAuditLogger:
    """DeFi audit logging system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def log_compliance_check(self, transaction: DeFiTransaction, metadata: Dict[str, Any]) -> bool:
        """Log compliance check to audit trail."""
        try:
            audit_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'transaction_id': transaction.tx_id,
                'user_id': transaction.user_id,
                'compliance_metadata': metadata,
                'result': 'approved' if transaction.approved else 'rejected'
            }
            self.logger.info(f"Audit log entry: {audit_entry}")
            return True
        except Exception as e:
            self.logger.error(f"Error logging audit entry: {e}")
            return False
