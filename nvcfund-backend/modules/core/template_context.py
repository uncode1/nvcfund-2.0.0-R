"""
Template Context Processors
Enterprise-grade template context management for role-based navigation
"""

from flask import current_app, request, g
from flask_login import current_user
from modules.core.navigation_utils import get_user_nav_items
from modules.auth.models import UserRole
# from modules.core.rbac import is_view_only_mode  # Temporarily disabled
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_template_context(app):
    """Register template context processors with the Flask app"""
    @app.context_processor
    def inject_role_navigation():
        """
        Inject role-based navigation variables into all templates
        Dynamic role parsing - no hardcoded values
        """
        context = {}
        try:
            # Safe check for current_user existence and authentication
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                nav_context = get_user_nav_items(current_user)
                nav_items = nav_context.get('nav_items', [])
                # Defensive: ensure nav_items is always a list
                if isinstance(nav_items, str):
                    nav_items = []
                context.update({
                    'user_nav_items': nav_context.get('dropdowns', {}),
                    'nav_items': nav_items,
                    'user_role_enum': current_user.role if hasattr(current_user, 'role') else UserRole.STANDARD_USER,
                    'is_view_only_mode': False  # Temporarily disabled
                })
            else:
                # Default context for non-authenticated users
                context.update({
                    'user_nav_items': {},
                    'nav_items': [],
                    'user_role_enum': None,
                    'is_view_only_mode': False
                })
        except Exception as e:
            logger.error(f"Error injecting role navigation: {e}")
            context.update({
                'user_nav_items': {},
                'nav_items': [],
                'user_role_enum': None,
                'is_view_only_mode': False
            })
        return context
    
    @app.context_processor
    def inject_request_context():
        """
        Inject safe request context variables into templates
        """
        context = {}
        try:
            # Safely get request context
            if hasattr(request, 'endpoint') and request.endpoint:
                context['current_endpoint'] = request.endpoint
            else:
                context['current_endpoint'] = None
                
            if hasattr(request, 'path') and request.path:
                context['current_path'] = request.path
            else:
                context['current_path'] = None
                
        except Exception as e:
            logger.error(f"Error injecting request context: {e}")
            context.update({
                'current_endpoint': None,
                'current_path': None
            })
        return context
    
    @app.context_processor
    def inject_rbac_functions():
        """
        Inject RBAC permission checking functions into templates
        Following enterprise best practices for secure template rendering
        """
        def check_permission(permission_string):
            """
            Check if current user has specific permission
            Enterprise-grade permission checking for template conditionals
            """
            if not current_user or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return False
            
            # Define role-permission mappings following banking security standards
            ROLES_FOR_PERMISSION = {
                # Banking Operations
                'can_view_accounts': [UserRole.STANDARD_USER, UserRole.BUSINESS_USER, UserRole.CUSTOMER_SERVICE, 
                                     UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_initiate_transfer': [UserRole.STANDARD_USER, UserRole.BUSINESS_USER, UserRole.CUSTOMER_SERVICE,
                                        UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_all_transactions': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Administrative Functions
                'can_access_admin_dashboard': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_users': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_system_logs': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_modify_system_settings': [UserRole.SUPER_ADMIN],
                
                # Treasury Operations
                'can_access_treasury': [UserRole.TREASURY_OFFICER, UserRole.ASSET_LIABILITY_MANAGER, 
                                       UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_liquidity': [UserRole.TREASURY_OFFICER, UserRole.ASSET_LIABILITY_MANAGER],
                'can_access_nvct_operations': [UserRole.TREASURY_OFFICER, UserRole.SOVEREIGN_BANKER,
                                              UserRole.CENTRAL_BANK_GOVERNOR, UserRole.SUPER_ADMIN],
                
                # Sovereign Banking
                'can_access_sovereign_banking': [UserRole.SOVEREIGN_BANKER, UserRole.CENTRAL_BANK_GOVERNOR, 
                                               UserRole.SUPER_ADMIN],
                'can_manage_monetary_policy': [UserRole.CENTRAL_BANK_GOVERNOR, UserRole.SUPER_ADMIN],
                
                # Compliance & Risk
                'can_access_compliance': [UserRole.COMPLIANCE_OFFICER, UserRole.RISK_MANAGER, 
                                        UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_kyc': [UserRole.COMPLIANCE_OFFICER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_access_risk_management': [UserRole.RISK_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Branch Operations & Customer Service
                'can_access_branch_management': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_customer_service': [UserRole.CUSTOMER_SERVICE, UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_handle_customer_issues': [UserRole.CUSTOMER_SERVICE, UserRole.BRANCH_MANAGER],
                'can_approve_branch_transactions': [UserRole.BRANCH_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Institutional Banking
                'can_access_institutional': [UserRole.INSTITUTIONAL_BANKER, UserRole.CORRESPONDENT_BANKER,
                                           UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_correspondent_banks': [UserRole.CORRESPONDENT_BANKER, UserRole.SUPER_ADMIN],
                'can_access_wholesale_banking': [UserRole.INSTITUTIONAL_BANKER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Asset Liability Management
                'can_access_alm': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.TREASURY_OFFICER, UserRole.SUPER_ADMIN],
                'can_manage_interest_rates': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.TREASURY_OFFICER],
                'can_access_balance_sheet': [UserRole.ASSET_LIABILITY_MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN],
                
                # Security Center
                'can_access_security_center': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_view_security_logs': [UserRole.ADMIN, UserRole.SUPER_ADMIN],
                'can_manage_security_settings': [UserRole.SUPER_ADMIN]
            }
            
            # Check if the user's current role is allowed for this permission
            allowed_roles = ROLES_FOR_PERMISSION.get(permission_string, [])
            return current_user.role in allowed_roles
        
        def has_role(role):
            """Check if current user has specific role"""
            if not current_user or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return False
            return current_user.role == role
        
        def is_privileged_user():
            """Check if user has privileged access"""
            if not current_user or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return False
            return current_user.is_privileged_user()
        
        def can_access_module(module_name):
            """Check if user can access specific banking module"""
            if not current_user or not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                return False
            
            module_permissions = {
                'admin_management': 'can_access_admin_dashboard',
                'security_center': 'can_access_security_center', 
                'treasury': 'can_access_treasury',
                'sovereign': 'can_access_sovereign_banking',
                'compliance': 'can_access_compliance',
                'institutional': 'can_access_institutional',
                'nvct_stablecoin': 'can_access_nvct_operations'
            }
            
            required_permission = module_permissions.get(module_name)
            if required_permission:
                return check_permission(required_permission)
            return False
        
        return {
            'check_permission': check_permission,
            'has_role': has_role,
            'is_privileged_user': is_privileged_user,
            'can_access_module': can_access_module,
            'get_role_navigation': get_user_nav_items,
            'get_role_display': lambda user: user.role.name if user.role else 'Guest',
            'UserRole': UserRole  # Make UserRole enum available in templates
        }
    
    @app.context_processor
    def inject_common_variables():
        """
        Inject common template variables
        Explicitly provide current_user since Flask-Login's automatic injection isn't working
        """
        try:
            from flask_login import current_user
            return {
                'now': datetime.now(),
                'current_year': datetime.now().year,
                'current_user': current_user
            }
        except Exception as e:
            # Fallback if Flask-Login is not available
            return {
                'now': datetime.now(),
                'current_year': datetime.now().year,
                'current_user': None
            }