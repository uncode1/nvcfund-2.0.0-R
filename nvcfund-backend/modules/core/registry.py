"""
Module Registry - Central management for all banking platform modules
Enables hot-swappable feature management with zero downtime
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app, has_request_context
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """Central registry for all banking platform modules"""
    
    def __init__(self):
        self.active_modules: Dict[str, Any] = {}
        self.decommissioned_modules: Dict[str, Any] = {}
        self.feature_flags: Dict[str, Dict] = {}
        self.navbar_configs: Dict[str, List] = {}
        self._initialize_feature_flags()
    
    def _initialize_feature_flags(self):
        """Initialize feature flags for all modules"""
        self.feature_flags = {
            # Dashboard Module (Pilot Test)
            'dashboard': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'treasury_officer', 'admin', 'sovereign_banker'],
                'priority': 1,
                'health_check': '/api/v1/dashboard/health',
                'description': 'Main dashboard and user overview'
            },
            
            # Core Banking Features
            'accounts_management': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'admin'],
                'priority': 1,
                'health_check': '/api/v1/accounts/health',
                'description': 'Account management and operations'
            },
            'payment_transfers': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'admin'],
                'priority': 1,
                'health_check': '/api/v1/transfers/health',
                'description': 'Payment and transfer operations'
            },
            'cards_services': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'admin'],
                'priority': 1,
                'health_check': '/api/v1/cards/health',
                'description': 'Card management and services'
            },
            
            # Treasury Operations
            'treasury_operations': {
                'enabled': True,
                'roles': ['treasury_officer', 'admin', 'sovereign_banker'],
                'priority': 2,
                'health_check': '/api/v1/treasury/health',
                'description': 'Treasury and liquidity management'
            },
            'nvct_stablecoin': {
                'enabled': True,
                'roles': ['treasury_officer', 'admin'],
                'priority': 2,
                'health_check': '/api/v1/treasury/nvct/health',
                'description': 'NVCT stablecoin operations (30T supply)'
            },
            
            # BlockchainSettle Integration
            'blockchain_settlement': {
                'enabled': True,
                'roles': ['settlement_operator', 'treasury_officer', 'admin'],
                'priority': 3,
                'health_check': '/api/v1/settlement/health',
                'description': 'Blockchain settlement engine'
            },
            'smart_contracts': {
                'enabled': True,
                'roles': ['settlement_operator', 'admin'],
                'priority': 3,
                'health_check': '/api/v1/contracts/health',
                'description': 'Smart contract management'
            },
            
            # Sovereign Banking
            'central_banking': {
                'enabled': True,
                'roles': ['central_banker', 'sovereign_banker', 'admin'],
                'priority': 4,
                'health_check': '/api/v1/central-bank/health',
                'description': 'Central banking operations'
            },
            'federal_reserve': {
                'enabled': True,
                'roles': ['central_banker', 'admin'],
                'priority': 4,
                'health_check': '/api/v1/fed-reserve/health',
                'description': 'Federal Reserve integration'
            },
            
            # Settlement Infrastructure
            'swift_operations': {
                'enabled': True,
                'roles': ['swift_operator', 'settlement_operator', 'admin'],
                'priority': 5,
                'health_check': '/api/v1/swift/health',
                'description': 'SWIFT messaging and operations'
            },
            'rtgs_settlement': {
                'enabled': True,
                'roles': ['settlement_operator', 'admin'],
                'priority': 5,
                'health_check': '/api/v1/rtgs/health',
                'description': 'Real-time gross settlement'
            },
            
            # Compliance & Risk
            'compliance_kyc': {
                'enabled': True,
                'roles': ['compliance_officer', 'admin'],
                'priority': 6,
                'health_check': '/api/v1/compliance/health',
                'description': 'KYC/AML compliance'
            },
            'risk_management': {
                'enabled': True,
                'roles': ['risk_officer', 'admin'],
                'priority': 6,
                'health_check': '/api/v1/risk/health',
                'description': 'Risk assessment and management'
            },
            'interest_rate_management': {
                'enabled': True,
                'roles': ['treasury_officer', 'asset_liability_manager', 'chief_financial_officer', 'board_of_directors', 'monetary_policy_committee', 'admin'],
                'priority': 3,
                'health_check': '/interest_rate_management/api/health',
                'description': 'Comprehensive interest rate setting and control for all banking products'
            },
            'trading': {
                'enabled': True,
                'roles': ['business_user', 'institutional_banker', 'treasury_officer', 'admin'],
                'priority': 4,
                'health_check': '/trading/api/health',
                'description': 'Advanced trading platform with multi-asset support, risk management, and algorithmic trading'
            },
            
            # Public Services Module
            'public': {
                'enabled': True,
                'roles': ['all'],  # Public access
                'priority': 1,
                'health_check': '/public/api/health',
                'description': 'Public-facing pages, contact forms, and documentation'
            },
            
            # Administrative
            'admin_panel': {
                'enabled': True,
                'roles': ['admin'],
                'priority': 7,
                'health_check': '/api/v1/admin/health',
                'description': 'Administrative functions'
            },
            
            # External Integrations
            'binance_integration': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'institutional', 'treasury_officer', 'admin'],
                'priority': 6,
                'health_check': '/binance/api/health',
                'description': 'OAuth 2.0 integration with Binance APIs for secure trading'
            },
            
            # Exchange Module
            'exchange': {
                'enabled': True,
                'roles': ['standard', 'premium', 'business', 'institutional', 'treasury_officer', 'admin'],
                'priority': 5,
                'health_check': '/exchange/api/health',
                'description': 'Complete exchange operations with internal and external trading capabilities'
            },
            
            # API Module
            'api': {
                'enabled': True,
                'roles': ['all'],
                'priority': 1,
                'health_check': '/api/v1/health',
                'description': 'Unified API system consolidating all legacy API routes'
            }
        }
    
    def register_module(self, module_name: str, blueprint, config: Dict, app_instance=None):
        """Register a module with the platform"""
        try:
            if self.is_module_enabled(module_name):
                self.active_modules[module_name] = {
                    'blueprint': blueprint,
                    'config': config,
                    'status': 'active',
                    'registered_at': datetime.now(),
                    'health_endpoint': config.get('health_check'),
                    'version': config.get('version', '1.0.0')
                }
                
                # Store blueprint for later registration
                if not hasattr(self, 'pending_blueprints'):
                    self.pending_blueprints = []
                
                self.pending_blueprints.append({
                    'blueprint': blueprint,
                    'module_name': module_name
                })
                
                logger.info(f"Module '{module_name}' registered successfully (blueprint queued)")
                return True
            else:
                logger.warning(f"Module '{module_name}' not enabled - skipping registration")
                return False
        except Exception as e:
            logger.error(f"Failed to register module '{module_name}': {e}")
            import traceback
            logger.error(f"Registration error details: {traceback.format_exc()}")
            return False
    
    def register_all_blueprints(self, app):
        """Register all pending blueprints with the Flask app"""
        if hasattr(self, 'pending_blueprints'):
            for blueprint_info in self.pending_blueprints:
                try:
                    app.register_blueprint(blueprint_info['blueprint'])
                    logger.info(f"Blueprint for module '{blueprint_info['module_name']}' registered with Flask")
                except Exception as e:
                    logger.error(f"Failed to register blueprint for '{blueprint_info['module_name']}': {e}")
            
            # Clear pending blueprints after registration
            self.pending_blueprints = []
    
    def decommission_module(self, module_name: str, reason: str = "Manual decommission"):
        """Safely decommission a module"""
        if module_name in self.active_modules:
            module = self.active_modules.pop(module_name)
            module['decommissioned_at'] = datetime.now()
            module['reason'] = reason
            module['status'] = 'decommissioned'
            self.decommissioned_modules[module_name] = module
            logger.info(f"Module '{module_name}' decommissioned: {reason}")
            return True
        return False
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if module is enabled"""
        flags = self.feature_flags.get(module_name, {})
        return flags.get('enabled', False)
    
    def has_module_access(self, module_name: str, user_role: str = None) -> bool:
        """Check if user has access to module"""
        if not self.is_module_enabled(module_name):
            return False
        
        # Get user role from current_user if not provided
        if user_role is None and has_request_context():
            try:
                user_role = getattr(current_user, 'role', 'standard')
            except:
                user_role = 'standard'
        
        feature_config = self.feature_flags.get(module_name, {})
        allowed_roles = feature_config.get('roles', [])
        
        return user_role in allowed_roles
    
    def get_user_modules(self, user_role: str) -> List[str]:
        """Get list of modules available to user role"""
        available = []
        for module_name, config in self.feature_flags.items():
            if (config.get('enabled', False) and 
                user_role in config.get('roles', [])):
                available.append(module_name)
        return available
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules"""
        return {
            'active_modules': len(self.active_modules),
            'decommissioned_modules': len(self.decommissioned_modules),
            'total_features': len(self.feature_flags),
            'enabled_features': sum(1 for f in self.feature_flags.values() if f.get('enabled')),
            'modules': {
                name: {
                    'status': module['status'],
                    'version': module.get('version', 'unknown'),
                    'registered_at': module['registered_at'].isoformat() if isinstance(module['registered_at'], datetime) else str(module['registered_at'])
                }
                for name, module in self.active_modules.items()
            }
        }
    
    def enable_feature(self, feature_name: str) -> bool:
        """Enable a feature flag"""
        if feature_name in self.feature_flags:
            self.feature_flags[feature_name]['enabled'] = True
            logger.info(f"Feature '{feature_name}' enabled")
            return True
        return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a feature flag"""
        if feature_name in self.feature_flags:
            self.feature_flags[feature_name]['enabled'] = False
            logger.info(f"Feature '{feature_name}' disabled")
            return True
        return False

# Global registry instance
module_registry = ModuleRegistry()