
"""
Dashboard Navigation Manager
Handles all dashboard-related navigation and menu building
Self-contained within the dashboard package
"""

from flask_login import current_user
from ..auth.models import UserRole

class DashboardNavigation:
    """Self-contained dashboard navigation manager"""
    
    @staticmethod
    def get_dashboard_nav_items(user_role=None):
        """Get navigation items specific to dashboard functionality"""
        if not user_role and current_user.is_authenticated:
            user_role = current_user.role
            
        nav_items = []
        
        # Role-specific dashboard navigation
        if user_role == UserRole.ADMIN.value:
            nav_items.extend([
                {'name': 'Admin Dashboard', 'url': '/dashboard/admin', 'icon': 'fas fa-crown'},
                {'name': 'System Health', 'url': '/admin/system/health', 'icon': 'fas fa-heartbeat'},
                {'name': 'Security Monitor', 'url': '/admin/security/dpi_dashboard', 'icon': 'fas fa-shield-alt'}
            ])
            
        elif user_role == UserRole.TREASURY_OFFICER.value:
            nav_items.extend([
                {'name': 'Treasury Dashboard', 'url': '/dashboard/treasury', 'icon': 'fas fa-university'},
                {'name': 'Liquidity Management', 'url': '/treasury/liquidity/dashboard', 'icon': 'fas fa-chart-line'},
                {'name': 'Settlement Operations', 'url': '/treasury/settlement_dashboard', 'icon': 'fas fa-exchange-alt'}
            ])
            
        elif user_role == UserRole.COMPLIANCE_OFFICER.value:
            nav_items.extend([
                {'name': 'Compliance Dashboard', 'url': '/dashboard/compliance', 'icon': 'fas fa-balance-scale'},
                {'name': 'AML Monitoring', 'url': '/admin/compliance/aml_monitoring', 'icon': 'fas fa-search'},
                {'name': 'Audit Reports', 'url': '/compliance/audit/reports', 'icon': 'fas fa-file-alt'}
            ])
            
        elif user_role == UserRole.INSTITUTIONAL_BANKER.value:
            nav_items.extend([
                {'name': 'Institutional Dashboard', 'url': '/dashboard/institutional', 'icon': 'fas fa-building'},
                {'name': 'Correspondent Banking', 'url': '/institutional/correspondent_banking', 'icon': 'fas fa-handshake'},
                {'name': 'SWIFT Operations', 'url': '/institutional/swift_dashboard', 'icon': 'fas fa-globe'}
            ])
            
        elif user_role == UserRole.SOVEREIGN_BANKER.value:
            nav_items.extend([
                {'name': 'Sovereign Dashboard', 'url': '/dashboard/sovereign', 'icon': 'fas fa-flag'},
                {'name': 'Asset Management', 'url': '/sovereign/asset-management', 'icon': 'fas fa-chart-pie'},
                {'name': 'Diplomatic Relations', 'url': '/sovereign/diplomatic-relations', 'icon': 'fas fa-globe-americas'}
            ])
            
        else:  # Regular users
            nav_items.extend([
                {'name': 'My Dashboard', 'url': '/dashboard', 'icon': 'fas fa-home'},
                {'name': 'Account Overview', 'url': '/banking/accounts', 'icon': 'fas fa-credit-card'},
                {'name': 'Transaction History', 'url': '/banking/transactions', 'icon': 'fas fa-history'}
            ])
            
        return nav_items
    
    @staticmethod
    def get_dashboard_sidebar_items(user_role=None):
        """Get sidebar items for dashboard pages"""
        if not user_role and current_user.is_authenticated:
            user_role = current_user.role
            
        sidebar_items = {
            'quick_actions': [],
            'recent_items': [],
            'notifications': []
        }
        
        # Role-specific quick actions
        if user_role == UserRole.ADMIN.value:
            sidebar_items['quick_actions'] = [
                {'name': 'System Status', 'url': '/admin/system/health', 'icon': 'fas fa-heartbeat'},
                {'name': 'User Management', 'url': '/admin/tools/dashboard', 'icon': 'fas fa-users'},
                {'name': 'Security Alerts', 'url': '/admin/security/threat_intelligence', 'icon': 'fas fa-exclamation-triangle'}
            ]
            
        elif user_role == UserRole.TREASURY_OFFICER.value:
            sidebar_items['quick_actions'] = [
                {'name': 'New Settlement', 'url': '/blockchain/create_settlement', 'icon': 'fas fa-plus'},
                {'name': 'Liquidity Check', 'url': '/treasury/liquidity/monitoring', 'icon': 'fas fa-chart-bar'},
                {'name': 'Fund Transfer', 'url': '/treasury/funding/new_capital_injection', 'icon': 'fas fa-exchange-alt'}
            ]
            
        return sidebar_items
    
    @staticmethod
    def build_breadcrumb_nav(current_page, user_role=None):
        """Build breadcrumb navigation for dashboard pages"""
        breadcrumbs = [{'name': 'Home', 'url': '/'}]
        
        if 'dashboard' in current_page:
            breadcrumbs.append({'name': 'Dashboard', 'url': '/dashboard'})
            
            if user_role == UserRole.ADMIN.value and 'admin' in current_page:
                breadcrumbs.append({'name': 'Admin Dashboard', 'url': '/dashboard/admin'})
            elif user_role == UserRole.TREASURY_OFFICER.value and 'treasury' in current_page:
                breadcrumbs.append({'name': 'Treasury Dashboard', 'url': '/dashboard/treasury'})
            elif user_role == UserRole.COMPLIANCE_OFFICER.value and 'compliance' in current_page:
                breadcrumbs.append({'name': 'Compliance Dashboard', 'url': '/dashboard/compliance'})
                
        return breadcrumbs
