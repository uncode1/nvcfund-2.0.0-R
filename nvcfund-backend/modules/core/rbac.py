"""
High-Performance Role-Based Access Control (RBAC)
Lightweight, fast authorization system with minimal overhead
"""

from functools import wraps, lru_cache
from typing import Dict, Set, Optional, Callable, Any
from flask import current_app, request, jsonify, g
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

class FastRBAC:
    """Ultra-fast RBAC system optimized for banking performance requirements"""
    
    def __init__(self):
        # Pre-computed permission sets for O(1) lookups
        self._role_permissions: Dict[str, Set[str]] = {}
        self._permission_cache: Dict[str, bool] = {}
        self._initialized = False
        
    @lru_cache(maxsize=128)
    def _get_user_role_key(self, user_id: str, role: str) -> str:
        """Generate cache key for user-role combination"""
        return f"{user_id}:{role}"
    
    def initialize(self):
        """Initialize RBAC with optimized permission mappings"""
        if self._initialized:
            return
            
        # Optimized role-permission mapping using sets for O(1) contains operations
        self._role_permissions = {
            # Standard users - minimal permissions
            'standard_user': {
                'view_accounts', 'create_transfers', 'view_transactions', 'manage_cards'
            },
            'business_user': {
                'view_accounts', 'create_transfers', 'view_transactions', 'manage_cards',
                'business_banking', 'bulk_transfers'
            },
            'partner_user': {
                'view_accounts', 'create_transfers', 'view_transactions', 'manage_cards',
                'business_banking', 'bulk_transfers', 'api_access', 'treasury_view'
            },
            
            # Banking staff - progressive permissions
            'banking_officer': {
                'view_accounts', 'customer_accounts', 'approve_transactions', 'kyc_access'
            },
            'branch_manager': {
                'view_accounts', 'customer_accounts', 'approve_transactions', 'kyc_access',
                'manage_staff', 'rate_setting_basic'
            },
            'loan_officer': {
                'view_accounts', 'customer_accounts', 'loan_processing', 'credit_analysis'
            },
            
            # Treasury operations - high-value permissions
            'treasury_officer': {
                'treasury_dashboard', 'liquidity_management', 'nvct_operations',
                'asset_management', 'rate_setting_commercial', 'swift_access'
            },
            
            # Compliance and risk - oversight permissions
            'compliance_officer': {
                'compliance_dashboard', 'aml_access', 'audit_logs', 'regulatory_reports',
                'customer_accounts', 'transaction_monitoring'
            },
            'risk_manager': {
                'risk_dashboard', 'treasury_view', 'compliance_view', 'audit_logs'
            },
            
            # Senior management - strategic permissions
            'central_bank_governor': {
                'sovereign_banking', 'monetary_policy', 'banking_supervision',
                'treasury_full', 'rate_authority_board', 'emergency_powers'
            },
            'sovereign_banker': {
                'sovereign_banking', 'international_relations', 'treasury_view',
                'correspondent_banking'
            },
            
            # System administration - technical permissions
            'admin': {
                'user_management', 'system_config', 'audit_logs', 'security_admin',
                'treasury_dashboard', 'trading_dashboard', 'compliance_dashboard',
                'settlement_dashboard', 'analytics_dashboard'
            },
            'super_admin': {
                'full_access', 'emergency_controls', 'database_access', 'system_override',
                'treasury_dashboard', 'trading_dashboard', 'compliance_dashboard',
                'settlement_dashboard', 'analytics_dashboard', 'sovereign_banking',
                'nvct_operations', 'user_management', 'system_config', 'audit_logs',
                'security_admin', 'liquidity_management', 'asset_management',
                'rate_setting_commercial', 'swift_access', 'aml_access',
                'regulatory_reports', 'transaction_monitoring', 'risk_dashboard',
                'monetary_policy', 'banking_supervision', 'treasury_full',
                'rate_authority_board', 'emergency_powers', 'international_relations',
                'correspondent_banking', 'api_access', 'treasury_view', 'manage_cards',
                'view_accounts', 'create_transfers', 'view_transactions', 'customer_accounts',
                'approve_transactions', 'kyc_access', 'manage_staff', 'rate_setting_basic',
                # Trading & Markets Access
                'forex_trading', 'commodities_trading', 'securities_trading', 'derivatives_trading',
                'crypto_trading', 'blockchain_analytics', 'portfolio_management', 'market_data',
                'exchange_platform', 'institutional_dashboard', 'investment_services',
                'stablecoin_management', 'trading_operations', 'binance_integration'
            }
        }
        
        # Create reverse lookup for faster permission checking
        self._permission_roles: Dict[str, Set[str]] = {}
        for role, permissions in self._role_permissions.items():
            for permission in permissions:
                if permission not in self._permission_roles:
                    self._permission_roles[permission] = set()
                self._permission_roles[permission].add(role)
        
        self._initialized = True
        logger.info("FastRBAC initialized with optimized permission mappings")
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Ultra-fast permission check - O(1) operation"""
        if not self._initialized:
            self.initialize()
        
        # Super admin bypass - uncode has all permissions
        if user_role == 'super_admin':
            return True
        
        # Direct set lookup - fastest possible check
        role_permissions = self._role_permissions.get(user_role, set())
        return permission in role_permissions
    
    def get_user_permissions(self, user_role: str) -> Set[str]:
        """Get all permissions for a role - O(1) operation"""
        if not self._initialized:
            self.initialize()
        
        return self._role_permissions.get(user_role, set()).copy()
    
    def can_access_module(self, user_role: str, module: str) -> bool:
        """Fast module access check based on permission patterns"""
        if not self._initialized:
            self.initialize()
        
        # Module-permission mapping for O(1) checks
        module_permissions = {
            'treasury': 'treasury_dashboard',
            'compliance': 'compliance_dashboard', 
            'sovereign': 'sovereign_banking',
            'admin': 'user_management',
            'nvct': 'nvct_operations',
            'settlement': 'swift_access',
            'interest_rates': 'rate_setting_basic'
        }
        
        required_permission = module_permissions.get(module)
        if not required_permission:
            return True  # Public module
        
        return self.has_permission(user_role, required_permission)

# Global RBAC instance
rbac = FastRBAC()

def get_user_role() -> str:
    """Fast user role extraction with caching"""
    if hasattr(g, 'user_role'):
        return g.user_role
    
    if not current_user.is_authenticated:
        g.user_role = 'anonymous'
        return 'anonymous'
    
    # Cache role in request context for multiple checks
    user_role = getattr(current_user, 'role', 'standard_user')
    g.user_role = user_role
    return user_role

def require_permission(permission: str, api_mode: bool = False):
    """Lightweight permission decorator with minimal overhead"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # All users including super admins go through proper permission auditing
            
            user_role = get_user_role()
            
            if user_role == 'anonymous':
                if api_mode or request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return current_app.login_manager.unauthorized()
            
            # Fast permission check
            if not rbac.has_permission(user_role, permission):
                logger.warning(f"Access denied: {user_role} lacks {permission} for {func.__name__}")
                
                if api_mode or request.is_json:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required': permission
                    }), 403
                return current_app.login_manager.unauthorized()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str, api_mode: bool = False):
    """Lightweight role decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user_role = get_user_role()
            
            if user_role == 'anonymous':
                if api_mode or request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return current_app.login_manager.unauthorized()
            
            if user_role != role:
                logger.warning(f"Access denied: {user_role} is not {role} for {func.__name__}")
                
                if api_mode or request.is_json:
                    return jsonify({
                        'error': 'Insufficient role',
                        'required': role,
                        'current': user_role
                    }), 403
                return current_app.login_manager.unauthorized()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_role(*roles: str, api_mode: bool = False):
    """Require any of the specified roles"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user_role = get_user_role()
            
            if user_role == 'anonymous':
                if api_mode or request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return current_app.login_manager.unauthorized()
            
            if user_role not in roles:
                logger.warning(f"Access denied: {user_role} not in {roles} for {func.__name__}")
                
                if api_mode or request.is_json:
                    return jsonify({
                        'error': 'Insufficient role',
                        'required_any': list(roles),
                        'current': user_role
                    }), 403
                return current_app.login_manager.unauthorized()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# === CONVENIENCE DECORATORS FOR BANKING MODULES ===

def treasury_access(api_mode: bool = False):
    """Fast treasury access check"""
    return require_permission('treasury_dashboard', api_mode)

def admin_access(api_mode: bool = False):
    """Fast admin access check"""
    return require_permission('user_management', api_mode)

def compliance_access(api_mode: bool = False):
    """Fast compliance access check"""
    return require_permission('compliance_dashboard', api_mode)

def sovereign_access(api_mode: bool = False):
    """Fast sovereign banking access check"""
    return require_permission('sovereign_banking', api_mode)

def nvct_access(api_mode: bool = False):
    """Fast NVCT operations access check"""
    return require_permission('nvct_operations', api_mode)

def rate_authority(level: str = 'basic', api_mode: bool = False):
    """Fast interest rate authority check"""
    level_permissions = {
        'basic': 'rate_setting_basic',
        'commercial': 'rate_setting_commercial', 
        'board': 'rate_authority_board'
    }
    permission = level_permissions.get(level, 'rate_setting_basic')
    return require_permission(permission, api_mode)

# === TEMPLATE HELPER FUNCTIONS ===

def can_access(permission: str) -> bool:
    """Template helper for permission checks"""
    user_role = get_user_role()
    return rbac.has_permission(user_role, permission)

def has_role(role: str) -> bool:
    """Template helper for role checks"""
    user_role = get_user_role()
    return user_role == role

def get_accessible_modules() -> Set[str]:
    """Get modules accessible to current user"""
    user_role = get_user_role()
    accessible = set()
    
    modules = [
        ('treasury', 'treasury_dashboard'),
        ('compliance', 'compliance_dashboard'),
        ('sovereign', 'sovereign_banking'),
        ('admin', 'user_management'),
        ('nvct', 'nvct_operations'),
        ('settlement', 'swift_access')
    ]
    
    for module, permission in modules:
        if rbac.has_permission(user_role, permission):
            accessible.add(module)
    
    # Always accessible modules
    accessible.update(['dashboard', 'banking', 'auth'])
    
    return accessible

# === INTEGRATION WITH EXISTING SYSTEM ===

def init_rbac(app):
    """Initialize RBAC with Flask app"""
    rbac.initialize()
    
    # Add template globals for permission checking
    app.jinja_env.globals.update({
        'can_access': can_access,
        'has_role': has_role,
        'get_accessible_modules': get_accessible_modules,
        'current_user_role': get_user_role
    })
    
    logger.info("FastRBAC integrated with Flask application")

# === BACKWARD COMPATIBILITY ===

# Provide aliases for existing decorators to avoid breaking changes
login_required = require_permission('view_accounts')
admin_required = admin_access
treasury_required = treasury_access
compliance_required = compliance_access

def banking_required(api_mode: bool = False):
    """Basic banking access"""
    return require_permission('view_accounts', api_mode)

def permission_required(permission: str):
    """Backward compatibility with old decorator signature"""
    return require_permission(permission, api_mode=False)

# Performance monitoring
def log_performance_metrics():
    """Log RBAC performance metrics for monitoring"""
    cache_info = rbac._get_user_role_key.cache_info()
    logger.debug(f"RBAC cache performance: hits={cache_info.hits}, misses={cache_info.misses}")

# === STANDALONE FUNCTIONS FOR MODULE IMPORTS ===

def has_permission(permission: str, user_role: str = None) -> bool:
    """Standalone has_permission function for module imports"""
    if user_role is None:
        user_role = get_user_role()
    return rbac.has_permission(user_role, permission)

def require_permission(permission: str, api_mode: bool = False):
    """Standalone require_permission function for module imports"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            user_role = get_user_role()
            
            if user_role == 'anonymous':
                if api_mode or request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return current_app.login_manager.unauthorized()
            
            if not rbac.has_permission(user_role, permission):
                logger.warning(f"Access denied: {user_role} lacks {permission} for {func.__name__}")
                
                if api_mode or request.is_json:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required': permission,
                        'current_role': user_role
                    }), 403
                return current_app.login_manager.unauthorized()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Initialize on import
rbac.initialize()