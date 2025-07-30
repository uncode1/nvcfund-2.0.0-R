"""
Utils Module Services - Self-contained utility services
Provides navbar context and error logging services
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any
from flask_login import current_user

class NavbarContextService:
    """
    Self-contained navbar context service
    Provides consistent navbar structure for all templates
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_navbar_context(self) -> Dict[str, Any]:
        """
        Generate complete navbar context for templates
        Returns a properly structured context that templates expect
        """
        try:

            # Base navigation items that all users see
            base_navigation = {
                'dashboard': {
                    'title': 'Dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'items': self._get_dashboard_items()
                },
                'help_support': {
                    'title': 'Help & Support',
                    'icon': 'fas fa-life-ring',
                    'items': self._get_help_support_items()
                }
            }
            
            # User-specific navigation based on role
            user_navigation = self._get_user_navigation()

            # Defensive check: ensure all navigation items are lists, not method references
            # Check base navigation first
            for section_key, section in base_navigation.items():
                if callable(section.get('items')):
                    self.logger.warning(f"Base navigation section '{section_key}' has callable items, converting to list")
                    section['items'] = section['items']()
                elif not isinstance(section.get('items'), list):
                    self.logger.warning(f"Base navigation section '{section_key}' has non-list items: {type(section.get('items'))}")
                    section['items'] = []

            # Check user navigation
            for section_key, section in user_navigation.items():
                items = section.get('items')
                if callable(items):
                    self.logger.warning(f"User navigation section '{section_key}' has callable items: {items}, converting to list")
                    try:
                        section['items'] = items()
                    except Exception as e:
                        self.logger.error(f"Failed to call method for user navigation section '{section_key}': {e}")
                        section['items'] = []
                elif not isinstance(items, list):
                    self.logger.warning(f"User navigation section '{section_key}' has non-list items: {type(items)} - {items}")
                    section['items'] = []

            # Final validation before returning context
            context = {
                'base_navigation': base_navigation,
                'user_navigation': user_navigation,
                'current_user': current_user if current_user.is_authenticated else None
            }

            # Deep validation of all navigation items
            for nav_type, navigation in [('base', base_navigation), ('user', user_navigation)]:
                for section_key, section in navigation.items():
                    items = section.get('items')
                    if callable(items):
                        self.logger.error(f"CRITICAL: {nav_type} navigation section '{section_key}' still has callable items after defensive checks: {items}")
                        section['items'] = []
                    elif not isinstance(items, list):
                        self.logger.error(f"CRITICAL: {nav_type} navigation section '{section_key}' has non-list items: {type(items)} - {items}")
                        section['items'] = []

            return context
            
        except Exception as e:
            self.logger.error(f"Error generating navbar context: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._get_fallback_context()
    
    def _get_dashboard_items(self) -> List[Dict[str, str]]:
        """Get dashboard dropdown items"""
        return [
            {'title': 'Main Dashboard', 'route': '/dashboard/', 'icon': 'fas fa-home'},
            {'title': 'Overview', 'route': '/dashboard/overview', 'icon': 'fas fa-chart-line'},
            {'title': 'Quick Actions', 'route': '/dashboard/quick-actions', 'icon': 'fas fa-bolt'},
            {'title': 'Recent Activity', 'route': '/dashboard/recent-activity', 'icon': 'fas fa-history'}
        ]
    
    def _get_help_support_items(self) -> List[Dict[str, str]]:
        """Get help & support dropdown items"""
        return [
            {'title': 'Documentation', 'route': '/documentation', 'icon': 'fas fa-book'},
            {'title': 'Contact Support', 'route': '/contact', 'icon': 'fas fa-envelope'},
            {'title': 'FAQ', 'route': '/faq', 'icon': 'fas fa-question-circle'},
            {'title': 'Live Chat', 'route': '/chat/', 'icon': 'fas fa-comments'}
        ]
    
    def _get_user_navigation(self) -> Dict[str, Any]:
        """Get RBAC-controlled user-specific navigation showcasing accessible features"""

        if not current_user.is_authenticated:
            print("DEBUG: User not authenticated, returning empty dict")
            return {}

        user_role = getattr(current_user, 'role', None)
        if user_role and hasattr(user_role, 'value'):
            role_value = user_role.value
        else:
            role_value = 'standard'

        navigation = {}

        # Core Banking & Accounts (Available to most authenticated users)
        if self._has_permission('can_view_accounts'):
            banking_items = self._get_rbac_banking_items()
            if callable(banking_items):
                banking_items = banking_items()
            navigation['banking'] = {
                'title': 'Banking',
                'icon': 'fas fa-university',
                'items': banking_items
            }

        if self._has_permission('can_access_accounts'):
            accounts_items = self._get_rbac_accounts_items()
            if callable(accounts_items):
                print(f"ERROR: accounts_items is callable: {accounts_items}")
                accounts_items = accounts_items()
            navigation['accounts'] = {
                'title': 'Account Management',
                'icon': 'fas fa-credit-card',
                'items': accounts_items
            }

        # Products & Services (Comprehensive product suite)
        if self._has_permission('can_access_products'):
            navigation['products'] = {
                'title': 'Products',
                'icon': 'fas fa-box-open',
                'items': self._get_rbac_products_items()
            }

        # Cards & Payments
        if self._has_permission('can_access_cards_payments'):
            navigation['cards_payments'] = {
                'title': 'Cards & Payments',
                'icon': 'fas fa-credit-card',
                'items': self._get_rbac_cards_payments_items()
            }

        # Insurance Services
        if self._has_permission('can_access_insurance'):
            navigation['insurance'] = {
                'title': 'Insurance',
                'icon': 'fas fa-umbrella',
                'items': self._get_rbac_insurance_items()
            }

        # Investment Services
        if self._has_permission('can_access_investments'):
            navigation['investments'] = {
                'title': 'Investments',
                'icon': 'fas fa-chart-line',
                'items': self._get_rbac_investments_items()
            }

        # Islamic Banking
        if self._has_permission('can_access_islamic_banking'):
            navigation['islamic_banking'] = {
                'title': 'Islamic Banking',
                'icon': 'fas fa-mosque',
                'items': self._get_rbac_islamic_banking_items()
            }

        # Trading Platform
        if self._has_permission('can_access_trading'):
            navigation['trading'] = {
                'title': 'Trading',
                'icon': 'fas fa-chart-bar',
                'items': self._get_rbac_trading_items()
            }

        # Crypto & DeFi (Available to users with crypto permissions)
        if self._has_permission('can_access_crypto'):
            navigation['crypto'] = {
                'title': 'Crypto & DeFi',
                'icon': 'fab fa-bitcoin',
                'items': self._get_rbac_crypto_items()
            }

        # NVCT Stablecoin
        if self._has_permission('can_access_nvct_operations'):
            navigation['nvct_stablecoin'] = {
                'title': 'NVCT Stablecoin',
                'icon': 'fas fa-coins',
                'items': self._get_rbac_nvct_items()
            }

        # Exchange Services
        if self._has_permission('can_access_exchange'):
            navigation['exchange'] = {
                'title': 'Exchange',
                'icon': 'fas fa-exchange-alt',
                'items': self._get_rbac_exchange_items()
            }

        # Treasury Operations (Treasury officers and above)
        if self._has_permission('can_access_treasury'):
            navigation['treasury'] = {
                'title': 'Treasury Operations',
                'icon': 'fas fa-coins',
                'items': self._get_rbac_treasury_items()
            }

        # Sovereign Banking (Central bank and sovereign roles)
        if self._has_permission('can_access_sovereign_banking'):
            navigation['sovereign'] = {
                'title': 'Sovereign Banking',
                'icon': 'fas fa-university',
                'items': self._get_rbac_sovereign_items()
            }

        # Compliance & Risk (Compliance officers and risk managers)
        if self._has_permission('can_access_compliance'):
            navigation['compliance'] = {
                'title': 'Compliance & Risk',
                'icon': 'fas fa-balance-scale',
                'items': self._get_rbac_compliance_items()
            }

        # Administration (Admin and Super Admin only)
        if self._has_permission('can_access_admin_dashboard'):
            navigation['admin_management'] = {
                'title': 'Administration',
                'icon': 'fas fa-shield-alt',
                'items': self._get_rbac_admin_items()
            }

        # User Management
        if self._has_permission('can_manage_users'):
            navigation['user_management'] = {
                'title': 'User Management',
                'icon': 'fas fa-users',
                'items': self._get_rbac_user_management_items()
            }

        # Security Center (Admin and Security roles)
        if self._has_permission('can_access_security_center'):
            navigation['security_center'] = {
                'title': 'Security Center',
                'icon': 'fas fa-lock',
                'items': self._get_rbac_security_items()
            }

        # Analytics & Reports (Available to managers and above)
        if self._has_permission('can_access_analytics'):
            navigation['analytics'] = {
                'title': 'Analytics & Reports',
                'icon': 'fas fa-chart-line',
                'items': self._get_rbac_analytics_items()
            }

        # Services & Integrations (Available to most users)
        if self._has_permission('can_access_services'):
            navigation['services'] = {
                'title': 'Services',
                'icon': 'fas fa-cogs',
                'items': self._get_rbac_services_items()
            }

        # Communications
        if self._has_permission('can_access_communications'):
            navigation['communications'] = {
                'title': 'Communications',
                'icon': 'fas fa-envelope',
                'items': self._get_rbac_communications_items()
            }

        # Multi-Factor Authentication
        if self._has_permission('can_access_mfa'):
            navigation['mfa'] = {
                'title': 'Multi-Factor Auth',
                'icon': 'fas fa-key',
                'items': self._get_rbac_mfa_items()
            }

        # API Services
        if self._has_permission('can_access_api_services'):
            navigation['api'] = {
                'title': 'API Services',
                'icon': 'fas fa-code',
                'items': self._get_rbac_api_items()
            }

        # Integrations
        if self._has_permission('can_access_integrations'):
            navigation['integrations'] = {
                'title': 'Integrations',
                'icon': 'fas fa-plug',
                'items': self._get_rbac_integrations_items()
            }

        # Final defensive check: ensure all navigation items are lists, not method references
        for section_key, section in navigation.items():
            items = section.get('items')
            if callable(items):
                self.logger.warning(f"Navigation section '{section_key}' has callable items, converting to list")
                try:
                    section['items'] = items()
                except Exception as e:
                    self.logger.error(f"Failed to call method for section '{section_key}': {e}")
                    section['items'] = []
            elif not isinstance(items, list):
                self.logger.warning(f"Navigation section '{section_key}' has non-list items: {type(items)}")
                section['items'] = []

        return navigation if navigation else self._get_enhanced_default_navigation()

    def _has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission using comprehensive RBAC"""
        if not current_user.is_authenticated:
            return False

        # Comprehensive RBAC permission mappings for all discovered modules
        RBAC_PERMISSIONS = {
            # Core Banking Operations
            'can_view_accounts': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'treasury_officer', 'sovereign_banker', 'compliance_officer', 'admin', 'super_admin'],
            'can_initiate_transfer': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'treasury_officer', 'sovereign_banker', 'admin', 'super_admin'],
            'can_view_all_transactions': ['branch_manager', 'treasury_officer', 'compliance_officer', 'admin', 'super_admin'],

            # Core Account Management
            'can_access_accounts': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'treasury_officer', 'sovereign_banker', 'compliance_officer', 'admin', 'super_admin'],

            # Products & Services Access
            'can_access_products': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'treasury_officer', 'sovereign_banker', 'admin', 'super_admin'],
            'can_access_cards_payments': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_insurance': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_investments': ['standard_user', 'business_user', 'investment_advisor', 'branch_manager', 'admin', 'super_admin'],
            'can_access_islamic_banking': ['standard_user', 'business_user', 'islamic_banking_officer', 'branch_manager', 'admin', 'super_admin'],
            'can_access_trading': ['standard_user', 'business_user', 'investment_advisor', 'trader', 'admin', 'super_admin'],

            # Crypto & DeFi Operations
            'can_access_crypto': ['standard_user', 'business_user', 'treasury_officer', 'admin', 'super_admin'],
            'can_access_nvct_operations': ['treasury_officer', 'sovereign_banker', 'central_bank_governor', 'admin', 'super_admin'],
            'can_access_defi_protocols': ['treasury_officer', 'admin', 'super_admin'],
            'can_manage_smart_contracts': ['treasury_officer', 'admin', 'super_admin'],
            'can_access_exchange': ['standard_user', 'business_user', 'treasury_officer', 'trader', 'admin', 'super_admin'],

            # Administrative Functions
            'can_access_admin_dashboard': ['admin', 'super_admin'],
            'can_manage_users': ['admin', 'super_admin'],
            'can_view_system_logs': ['admin', 'super_admin'],
            'can_modify_system_settings': ['super_admin'],
            'can_access_branch_management': ['branch_manager', 'admin', 'super_admin'],

            # Security Center
            'can_access_security_center': ['admin', 'super_admin'],
            'can_view_security_logs': ['admin', 'super_admin'],
            'can_manage_security_settings': ['super_admin'],
            'can_access_threat_monitoring': ['admin', 'super_admin'],
            'can_manage_incident_response': ['admin', 'super_admin'],

            # Treasury Operations
            'can_access_treasury': ['treasury_officer', 'asset_liability_manager', 'admin', 'super_admin'],
            'can_manage_liquidity': ['treasury_officer', 'asset_liability_manager'],
            'can_manage_interest_rates': ['treasury_officer', 'asset_liability_manager'],
            'can_access_risk_management': ['treasury_officer', 'risk_manager', 'admin', 'super_admin'],

            # Sovereign Banking
            'can_access_sovereign_banking': ['sovereign_banker', 'central_bank_governor', 'super_admin'],
            'can_manage_monetary_policy': ['central_bank_governor', 'super_admin'],
            'can_access_foreign_exchange': ['sovereign_banker', 'central_bank_governor', 'treasury_officer', 'super_admin'],
            'can_manage_reserves': ['central_bank_governor', 'super_admin'],

            # Compliance & Risk
            'can_access_compliance': ['compliance_officer', 'risk_manager', 'admin', 'super_admin'],
            'can_manage_kyc': ['compliance_officer', 'admin', 'super_admin'],
            'can_access_aml': ['compliance_officer', 'admin', 'super_admin'],
            'can_manage_regulatory_reporting': ['compliance_officer', 'admin', 'super_admin'],

            # Analytics & Reporting
            'can_access_analytics': ['branch_manager', 'treasury_officer', 'compliance_officer', 'admin', 'super_admin'],
            'can_view_executive_reports': ['branch_manager', 'admin', 'super_admin'],
            'can_access_financial_analytics': ['treasury_officer', 'admin', 'super_admin'],

            # Services & Integrations
            'can_access_services': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_communications': ['customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_mfa': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_api_services': ['admin', 'super_admin'],
            'can_access_integrations': ['admin', 'super_admin'],

            # Customer Support
            'can_access_live_chat': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_manage_support_tickets': ['customer_service', 'branch_manager', 'admin', 'super_admin'],
            'can_access_knowledge_base': ['standard_user', 'business_user', 'customer_service', 'branch_manager', 'admin', 'super_admin'],

            # Institutional Banking
            'can_access_institutional': ['institutional_banker', 'correspondent_banker', 'admin', 'super_admin'],
            'can_manage_correspondent_banks': ['correspondent_banker', 'super_admin'],
            'can_access_wholesale_banking': ['institutional_banker', 'admin', 'super_admin']
        }

        # Get user role as string
        user_role = getattr(current_user, 'role', None)
        if user_role:
            if hasattr(user_role, 'value'):
                role_str = user_role.value.lower()
            elif hasattr(user_role, 'name'):
                role_str = user_role.name.lower()
            else:
                role_str = str(user_role).lower()
        else:
            role_str = 'standard_user'

        # Check if user role has permission
        allowed_roles = RBAC_PERMISSIONS.get(permission, [])
        return role_str in allowed_roles

    def _get_tier_one_navigation_items(self) -> List[Dict[str, str]]:
        """Tier one features navigation items"""
        return [
            {'title': 'Accounts', 'route': '/accounts/', 'icon': 'fas fa-university'},
            {'title': 'Treasury', 'route': '/treasury/', 'icon': 'fas fa-coins'},
            {'title': 'Settlement', 'route': '/settlement/', 'icon': 'fas fa-handshake'},
            {'title': 'Compliance', 'route': '/compliance/', 'icon': 'fas fa-shield-alt'},
            {'title': 'Institutional', 'route': '/institutional/', 'icon': 'fas fa-building'},
            {'title': 'Cards & Payments', 'route': '/cards_payments/', 'icon': 'fas fa-credit-card'},
            {'title': 'Investments', 'route': '/investments/', 'icon': 'fas fa-chart-line'},
            {'title': 'Insurance', 'route': '/insurance/', 'icon': 'fas fa-umbrella'}
        ]

    def _get_comprehensive_banking_items(self) -> List[Dict[str, str]]:
        """Comprehensive banking features showcasing full platform capabilities"""
        return [
            {'title': 'Banking Dashboard', 'route': '/banking/', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'Account Management', 'route': '/accounts/', 'icon': 'fas fa-university'},
            {'title': 'Money Transfers', 'route': '/banking/transfers', 'icon': 'fas fa-exchange-alt'},
            {'title': 'Payment Gateway', 'route': '/banking/payment-gateway-transfer', 'icon': 'fas fa-credit-card'},
            {'title': 'Bill Payments', 'route': '/banking/bill-payment', 'icon': 'fas fa-money-bill-wave'},
            {'title': 'Transaction History', 'route': '/banking/history', 'icon': 'fas fa-history'},
            {'title': 'Account Statements', 'route': '/banking/statements', 'icon': 'fas fa-file-alt'},
            {'title': 'Cards Management', 'route': '/banking/cards', 'icon': 'fas fa-credit-card'},
            {'title': 'Security Center', 'route': '/banking/security', 'icon': 'fas fa-shield-alt'}
        ]

    def _get_products_items(self) -> List[Dict[str, str]]:
        """Product offerings across all categories"""
        return [
            {'title': 'Cards & Payments', 'route': '/products/cards-payments/', 'icon': 'fas fa-credit-card'},
            {'title': 'Investment Services', 'route': '/products/investments/', 'icon': 'fas fa-chart-line'},
            {'title': 'Trading Platform', 'route': '/products/trading/', 'icon': 'fas fa-chart-candlestick'},
            {'title': 'Insurance Services', 'route': '/products/insurance/', 'icon': 'fas fa-umbrella'},
            {'title': 'Islamic Banking', 'route': '/products/islamic-banking/', 'icon': 'fas fa-mosque'},
            {'title': 'Halal Investments', 'route': '/products/islamic-banking/halal-investments', 'icon': 'fas fa-hand-holding-heart'}
        ]

    def _get_crypto_defi_items(self) -> List[Dict[str, str]]:
        """Cryptocurrency and DeFi features"""
        return [
            {'title': 'NVCT Stablecoin', 'route': '/nvct/', 'icon': 'fas fa-coins'},
            {'title': 'Crypto Wallets', 'route': '/nvct/wallets', 'icon': 'fas fa-wallet'},
            {'title': 'DeFi Protocols', 'route': '/nvct/defi', 'icon': 'fas fa-network-wired'},
            {'title': 'Yield Farming', 'route': '/nvct/yield-farming', 'icon': 'fas fa-seedling'},
            {'title': 'Cross-Chain Bridge', 'route': '/nvct/bridge', 'icon': 'fas fa-bridge'},
            {'title': 'Blockchain Analytics', 'route': '/services/integrations/blockchain/', 'icon': 'fas fa-cube'},
            {'title': 'Smart Contracts', 'route': '/nvct/smart-contracts', 'icon': 'fas fa-file-contract'}
        ]

    def _get_comprehensive_services_items(self) -> List[Dict[str, str]]:
        """Comprehensive services showcasing integrations and communications"""
        return [
            {'title': 'Live Chat Support', 'route': '/chat/', 'icon': 'fas fa-comments'},
            {'title': 'Communications', 'route': '/services/communications/', 'icon': 'fas fa-envelope'},
            {'title': 'API Services', 'route': '/services/api/', 'icon': 'fas fa-code'},
            {'title': 'Analytics Dashboard', 'route': '/services/analytics/', 'icon': 'fas fa-chart-bar'},
            {'title': 'Exchange Services', 'route': '/services/exchange/', 'icon': 'fas fa-exchange-alt'},
            {'title': 'MFA Security', 'route': '/services/mfa/', 'icon': 'fas fa-mobile-alt'},
            {'title': 'Integrations Hub', 'route': '/services/integrations/', 'icon': 'fas fa-plug'}
        ]
    
    def _get_comprehensive_admin_items(self) -> List[Dict[str, str]]:
        """Comprehensive admin navigation showcasing full platform management"""
        return [
            {'title': 'Admin Dashboard', 'route': '/admin-management/', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'User Management', 'route': '/user-management/', 'icon': 'fas fa-users'},
            {'title': 'Branch Management', 'route': '/admin-management/branch-management', 'icon': 'fas fa-building'},
            {'title': 'Branch Reports', 'route': '/admin-management/branch-reports', 'icon': 'fas fa-chart-bar'},
            {'title': 'System Settings', 'route': '/admin-management/system-settings', 'icon': 'fas fa-cog'},
            {'title': 'Teller Operations', 'route': '/admin-management/teller-operations', 'icon': 'fas fa-cash-register'},
            {'title': 'Maintenance Mode', 'route': '/admin-management/maintenance', 'icon': 'fas fa-tools'},
            {'title': 'Backup Management', 'route': '/admin-management/backups', 'icon': 'fas fa-database'}
        ]

    def _get_security_center_items(self) -> List[Dict[str, str]]:
        """Security center navigation items"""
        return [
            {'title': 'Security Dashboard', 'route': '/security-center/', 'icon': 'fas fa-shield-alt'},
            {'title': 'Threat Monitoring', 'route': '/security-center/threat-monitoring', 'icon': 'fas fa-eye'},
            {'title': 'Incident Response', 'route': '/security-center/incident-response', 'icon': 'fas fa-exclamation-triangle'},
            {'title': 'Fraud Detection', 'route': '/security-center/fraud-detection-aml', 'icon': 'fas fa-search'},
            {'title': 'Blocked Attacks', 'route': '/security-center/blocked-attacks', 'icon': 'fas fa-ban'},
            {'title': 'WAF Management', 'route': '/security-center/waf-management', 'icon': 'fas fa-firewall'},
            {'title': 'XDR Dashboard', 'route': '/security-center/xdr-dashboard', 'icon': 'fas fa-radar'}
        ]

    def _get_analytics_reports_items(self) -> List[Dict[str, str]]:
        """Analytics and reporting navigation items"""
        return [
            {'title': 'Analytics Dashboard', 'route': '/services/analytics/', 'icon': 'fas fa-chart-line'},
            {'title': 'Financial Analytics', 'route': '/services/analytics/financial', 'icon': 'fas fa-dollar-sign'},
            {'title': 'Executive Reports', 'route': '/services/analytics/executive', 'icon': 'fas fa-briefcase'},
            {'title': 'Reports Center', 'route': '/services/analytics/reports', 'icon': 'fas fa-file-alt'},
            {'title': 'Compliance Reports', 'route': '/compliance/regulatory-reporting', 'icon': 'fas fa-balance-scale'},
            {'title': 'Risk Assessment', 'route': '/compliance/risk-management', 'icon': 'fas fa-exclamation-triangle'}
        ]

    def _get_system_management_items(self) -> List[Dict[str, str]]:
        """System management navigation items"""
        return [
            {'title': 'Log Viewer', 'route': '/admin-management/log-viewer', 'icon': 'fas fa-file-alt'},
            {'title': 'Logs Dashboard', 'route': '/admin-management/logs-dashboard', 'icon': 'fas fa-chart-bar'},
            {'title': 'System Health', 'route': '/admin/system/health', 'icon': 'fas fa-heartbeat'},
            {'title': 'Performance Monitor', 'route': '/admin/system/monitoring', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'Database Admin', 'route': '/admin/database', 'icon': 'fas fa-database'},
            {'title': 'API Management', 'route': '/services/api/', 'icon': 'fas fa-code'}
        ]
    
    def _get_comprehensive_treasury_items(self) -> List[Dict[str, str]]:
        """Comprehensive treasury operations navigation"""
        return [
            {'title': 'Treasury Dashboard', 'route': '/treasury/', 'icon': 'fas fa-tachometer-alt'},
            {'title': 'Interest Rates', 'route': '/treasury/interest-rates/', 'icon': 'fas fa-percentage'},
            {'title': 'Liquidity Management', 'route': '/treasury/liquidity', 'icon': 'fas fa-water'},
            {'title': 'Asset Management', 'route': '/treasury/assets', 'icon': 'fas fa-briefcase'},
            {'title': 'Risk Management', 'route': '/treasury/risk', 'icon': 'fas fa-exclamation-triangle'},
            {'title': 'Treasury Reports', 'route': '/treasury/reports', 'icon': 'fas fa-file-alt'}
        ]

    def _get_nvct_stablecoin_items(self) -> List[Dict[str, str]]:
        """NVCT Stablecoin specific navigation"""
        return [
            {'title': 'NVCT Dashboard', 'route': '/nvct/', 'icon': 'fas fa-coins'},
            {'title': 'Supply Management', 'route': '/nvct/supply', 'icon': 'fas fa-cogs'},
            {'title': 'Asset Backing', 'route': '/nvct/assets', 'icon': 'fas fa-vault'},
            {'title': 'Network Management', 'route': '/nvct/networks', 'icon': 'fas fa-network-wired'},
            {'title': 'Cross-Chain Bridge', 'route': '/nvct/bridge', 'icon': 'fas fa-bridge'},
            {'title': 'DeFi Protocols', 'route': '/nvct/defi', 'icon': 'fas fa-network-wired'},
            {'title': 'Smart Contracts', 'route': '/nvct/smart-contracts', 'icon': 'fas fa-file-contract'},
            {'title': 'Governance', 'route': '/nvct/governance', 'icon': 'fas fa-vote-yea'},
            {'title': 'Analytics', 'route': '/nvct/analytics', 'icon': 'fas fa-chart-line'}
        ]

    def _get_comprehensive_sovereign_items(self) -> List[Dict[str, str]]:
        """Comprehensive sovereign banking navigation"""
        return [
            {'title': 'Sovereign Dashboard', 'route': '/sovereign/', 'icon': 'fas fa-university'},
            {'title': 'Central Banking', 'route': '/sovereign/central-bank', 'icon': 'fas fa-landmark'},
            {'title': 'Monetary Policy', 'route': '/sovereign/monetary-policy', 'icon': 'fas fa-percentage'},
            {'title': 'Sovereign Debt', 'route': '/sovereign/sovereign-debt', 'icon': 'fas fa-chart-pie'},
            {'title': 'Foreign Exchange', 'route': '/sovereign/foreign-exchange', 'icon': 'fas fa-exchange-alt'},
            {'title': 'International Reserves', 'route': '/sovereign/reserves', 'icon': 'fas fa-coins'},
            {'title': 'Banking Regulation', 'route': '/sovereign/regulatory', 'icon': 'fas fa-shield-alt'},
            {'title': 'Loan Registry', 'route': '/sovereign/loan-registry', 'icon': 'fas fa-book'},
            {'title': 'Economic Indicators', 'route': '/sovereign/economic-indicators', 'icon': 'fas fa-chart-line'}
        ]

    def _get_compliance_risk_items(self) -> List[Dict[str, str]]:
        """Compliance and risk management navigation"""
        return [
            {'title': 'Compliance Dashboard', 'route': '/compliance/', 'icon': 'fas fa-balance-scale'},
            {'title': 'Risk Management', 'route': '/compliance/risk-management', 'icon': 'fas fa-exclamation-triangle'},
            {'title': 'Regulatory Reporting', 'route': '/compliance/regulatory-reporting', 'icon': 'fas fa-file-alt'},
            {'title': 'Compliance Framework', 'route': '/compliance/compliance-framework', 'icon': 'fas fa-sitemap'},
            {'title': 'Violations Tracking', 'route': '/compliance/compliance-violations', 'icon': 'fas fa-exclamation-circle'},
            {'title': 'Assessment Tools', 'route': '/compliance/compliance-assessment', 'icon': 'fas fa-clipboard-check'}
        ]

    def _get_security_monitoring_items(self) -> List[Dict[str, str]]:
        """Security monitoring navigation for compliance officers"""
        return [
            {'title': 'Security Overview', 'route': '/security-center/', 'icon': 'fas fa-shield-alt'},
            {'title': 'Threat Analysis', 'route': '/security-center/threats-analysis', 'icon': 'fas fa-search'},
            {'title': 'Vulnerability Assessment', 'route': '/security-center/vulnerabilities-assessment', 'icon': 'fas fa-bug'},
            {'title': 'Incident Management', 'route': '/security-center/incidents-management', 'icon': 'fas fa-exclamation-triangle'},
            {'title': 'Investigation Tools', 'route': '/security-center/investigation-tools', 'icon': 'fas fa-search-plus'}
        ]
    
    def _get_enhanced_default_navigation(self) -> Dict[str, Any]:
        """Enhanced default navigation showcasing platform capabilities"""
        return {
            'banking': {
                'title': 'Banking',
                'icon': 'fas fa-university',
                'items': [
                    {'title': 'Dashboard', 'route': '/dashboard/', 'icon': 'fas fa-tachometer-alt'},
                    {'title': 'Account Overview', 'route': '/accounts/', 'icon': 'fas fa-wallet'},
                    {'title': 'Transfers', 'route': '/banking/transfers', 'icon': 'fas fa-exchange-alt'},
                    {'title': 'Transaction History', 'route': '/banking/history', 'icon': 'fas fa-history'}
                ]
            },
            'services': {
                'title': 'Services',
                'icon': 'fas fa-cogs',
                'items': [
                    {'title': 'Live Chat Support', 'route': '/chat/', 'icon': 'fas fa-comments'},
                    {'title': 'User Profile', 'route': '/user-management/', 'icon': 'fas fa-user'},
                    {'title': 'Settings', 'route': '/settings', 'icon': 'fas fa-cog'},
                    {'title': 'Help Center', 'route': '/public/faq', 'icon': 'fas fa-question-circle'}
                ]
            }
        }
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """Fallback context when errors occur"""
        return {
            'base_navigation': {
                'dashboard': {
                    'title': 'Dashboard',
                    'icon': 'fas fa-tachometer-alt',
                    'items': []
                },
                'help_support': {
                    'title': 'Help',
                    'icon': 'fas fa-life-ring',
                    'items': []
                }
            },
            'user_navigation': {},
            'current_user': None
        }

    # RBAC-Controlled Navigation Methods
    def _get_rbac_banking_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled banking navigation items"""
        items = []
        if self._has_permission('can_view_accounts'):
            items.append({'title': 'Accounts', 'route': '/accounts/', 'icon': 'fas fa-university'})
        if self._has_permission('can_initiate_transfer'):
            items.append({'title': 'Transfers', 'route': '/banking/transfers/', 'icon': 'fas fa-exchange-alt'})
        if self._has_permission('can_view_all_transactions'):
            items.append({'title': 'Transaction History', 'route': '/banking/transactions/', 'icon': 'fas fa-history'})
        return items

    def _get_rbac_products_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled products navigation items"""
        items = []
        if self._has_permission('can_access_cards_payments'):
            items.append({'title': 'Cards & Payments', 'route': '/products/cards_payments/', 'icon': 'fas fa-credit-card'})
        if self._has_permission('can_access_insurance'):
            items.append({'title': 'Insurance', 'route': '/products/insurance/', 'icon': 'fas fa-umbrella'})
        if self._has_permission('can_access_investments'):
            items.append({'title': 'Investments', 'route': '/products/investments/', 'icon': 'fas fa-chart-line'})
        if self._has_permission('can_access_islamic_banking'):
            items.append({'title': 'Islamic Banking', 'route': '/products/islamic_banking/', 'icon': 'fas fa-mosque'})
        if self._has_permission('can_access_trading'):
            items.append({'title': 'Trading', 'route': '/products/trading/', 'icon': 'fas fa-chart-bar'})
        return items

    def _get_rbac_crypto_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled crypto navigation items"""
        items = []
        if self._has_permission('can_access_nvct_operations'):
            items.append({'title': 'NVCT Stablecoin', 'route': '/nvct-stablecoin/', 'icon': 'fas fa-coins'})
        if self._has_permission('can_access_defi_protocols'):
            items.append({'title': 'DeFi Protocols', 'route': '/crypto/defi/', 'icon': 'fab fa-ethereum'})
        if self._has_permission('can_manage_smart_contracts'):
            items.append({'title': 'Smart Contracts', 'route': '/crypto/contracts/', 'icon': 'fas fa-file-contract'})
        return items

    def _get_rbac_admin_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled admin navigation items"""
        items = []
        if self._has_permission('can_manage_users'):
            items.append({'title': 'User Management', 'route': '/user-management/', 'icon': 'fas fa-users'})
        if self._has_permission('can_access_branch_management'):
            items.append({'title': 'Branch Management', 'route': '/admin-management/branches/', 'icon': 'fas fa-building'})
        if self._has_permission('can_view_system_logs'):
            items.append({'title': 'System Logs', 'route': '/admin-management/logs/', 'icon': 'fas fa-file-alt'})
        if self._has_permission('can_modify_system_settings'):
            items.append({'title': 'System Settings', 'route': '/admin-management/settings/', 'icon': 'fas fa-cogs'})
        return items

    def _get_rbac_security_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled security navigation items"""
        items = []
        if self._has_permission('can_view_security_logs'):
            items.append({'title': 'Security Logs', 'route': '/security-center/logs/', 'icon': 'fas fa-shield-alt'})
        if self._has_permission('can_access_threat_monitoring'):
            items.append({'title': 'Threat Monitoring', 'route': '/security-center/threats/', 'icon': 'fas fa-eye'})
        if self._has_permission('can_manage_incident_response'):
            items.append({'title': 'Incident Response', 'route': '/security-center/incidents/', 'icon': 'fas fa-exclamation-triangle'})
        return items

    def _get_rbac_treasury_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled treasury navigation items"""
        items = []
        if self._has_permission('can_manage_liquidity'):
            items.append({'title': 'Liquidity Management', 'route': '/treasury/liquidity/', 'icon': 'fas fa-water'})
        if self._has_permission('can_manage_interest_rates'):
            items.append({'title': 'Interest Rates', 'route': '/treasury/rates/', 'icon': 'fas fa-percentage'})
        if self._has_permission('can_access_risk_management'):
            items.append({'title': 'Risk Management', 'route': '/treasury/risk/', 'icon': 'fas fa-shield-alt'})
        return items

    def _get_rbac_sovereign_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled sovereign banking navigation items"""
        items = []
        if self._has_permission('can_manage_monetary_policy'):
            items.append({'title': 'Monetary Policy', 'route': '/sovereign/monetary/', 'icon': 'fas fa-university'})
        if self._has_permission('can_access_foreign_exchange'):
            items.append({'title': 'Foreign Exchange', 'route': '/sovereign/forex/', 'icon': 'fas fa-globe'})
        if self._has_permission('can_manage_reserves'):
            items.append({'title': 'Reserve Management', 'route': '/sovereign/reserves/', 'icon': 'fas fa-vault'})
        return items

    def _get_rbac_compliance_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled compliance navigation items"""
        items = []
        if self._has_permission('can_manage_kyc'):
            items.append({'title': 'KYC Management', 'route': '/compliance/kyc/', 'icon': 'fas fa-id-card'})
        if self._has_permission('can_access_aml'):
            items.append({'title': 'AML Monitoring', 'route': '/compliance/aml/', 'icon': 'fas fa-search'})
        if self._has_permission('can_manage_regulatory_reporting'):
            items.append({'title': 'Regulatory Reports', 'route': '/compliance/reports/', 'icon': 'fas fa-file-alt'})
        return items

    def _get_rbac_analytics_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled analytics navigation items"""
        items = []
        if self._has_permission('can_view_executive_reports'):
            items.append({'title': 'Executive Reports', 'route': '/analytics/executive/', 'icon': 'fas fa-chart-pie'})
        if self._has_permission('can_access_financial_analytics'):
            items.append({'title': 'Financial Analytics', 'route': '/analytics/financial/', 'icon': 'fas fa-chart-line'})
        return items

    def _get_rbac_services_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled services navigation items"""
        items = []
        if self._has_permission('can_access_communications'):
            items.append({'title': 'Communications', 'route': '/services/communications/', 'icon': 'fas fa-envelope'})
        if self._has_permission('can_access_api_services'):
            items.append({'title': 'API Services', 'route': '/services/api/', 'icon': 'fas fa-code'})
        if self._has_permission('can_access_integrations'):
            items.append({'title': 'Integrations', 'route': '/services/integrations/', 'icon': 'fas fa-plug'})
        if self._has_permission('can_access_live_chat'):
            items.append({'title': 'Live Chat', 'route': '/chat/', 'icon': 'fas fa-comments'})
        return items

    # Additional RBAC Navigation Methods for Comprehensive Feature Set
    def _get_rbac_accounts_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled accounts navigation items"""
        items = []
        if self._has_permission('can_view_accounts'):
            items.append({'title': 'Account Overview', 'route': '/accounts/', 'icon': 'fas fa-eye'})
        if self._has_permission('can_manage_accounts'):
            items.append({'title': 'Account Management', 'route': '/accounts/manage/', 'icon': 'fas fa-cogs'})
        return items

    def _get_rbac_cards_payments_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled cards & payments navigation items"""
        items = []
        if self._has_permission('can_access_cards_payments'):
            items.append({'title': 'Card Management', 'route': '/products/cards_payments/', 'icon': 'fas fa-credit-card'})
            items.append({'title': 'Payment Processing', 'route': '/products/cards_payments/payments/', 'icon': 'fas fa-money-bill-wave'})
            items.append({'title': 'Transaction History', 'route': '/products/cards_payments/transactions/', 'icon': 'fas fa-history'})
        return items

    def _get_rbac_insurance_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled insurance navigation items"""
        items = []
        if self._has_permission('can_access_insurance'):
            items.append({'title': 'Insurance Products', 'route': '/products/insurance/', 'icon': 'fas fa-shield-alt'})
            items.append({'title': 'Policy Management', 'route': '/products/insurance/policies/', 'icon': 'fas fa-file-contract'})
            items.append({'title': 'Claims Processing', 'route': '/products/insurance/claims/', 'icon': 'fas fa-clipboard-check'})
        return items

    def _get_rbac_investments_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled investments navigation items"""
        items = []
        if self._has_permission('can_access_investments'):
            items.append({'title': 'Investment Portfolio', 'route': '/products/investments/', 'icon': 'fas fa-chart-pie'})
            items.append({'title': 'Market Analysis', 'route': '/products/investments/analysis/', 'icon': 'fas fa-chart-line'})
            items.append({'title': 'Investment Products', 'route': '/products/investments/products/', 'icon': 'fas fa-box'})
        return items

    def _get_rbac_islamic_banking_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled Islamic banking navigation items"""
        items = []
        if self._has_permission('can_access_islamic_banking'):
            items.append({'title': 'Sharia Products', 'route': '/products/islamic_banking/', 'icon': 'fas fa-mosque'})
            items.append({'title': 'Sukuk Management', 'route': '/products/islamic_banking/sukuk/', 'icon': 'fas fa-certificate'})
            items.append({'title': 'Halal Investments', 'route': '/products/islamic_banking/investments/', 'icon': 'fas fa-hand-holding-usd'})
        return items

    def _get_rbac_trading_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled trading navigation items"""
        items = []
        if self._has_permission('can_access_trading'):
            items.append({'title': 'Trading Platform', 'route': '/products/trading/', 'icon': 'fas fa-chart-bar'})
            items.append({'title': 'Market Data', 'route': '/products/trading/market/', 'icon': 'fas fa-chart-line'})
            items.append({'title': 'Order Management', 'route': '/products/trading/orders/', 'icon': 'fas fa-list'})
        return items

    def _get_rbac_nvct_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled NVCT stablecoin navigation items"""
        items = []
        if self._has_permission('can_access_nvct_operations'):
            items.append({'title': 'NVCT Dashboard', 'route': '/nvct-stablecoin/', 'icon': 'fas fa-tachometer-alt'})
            items.append({'title': 'Mint/Burn Operations', 'route': '/nvct-stablecoin/operations/', 'icon': 'fas fa-coins'})
            items.append({'title': 'Smart Contracts', 'route': '/nvct-stablecoin/contracts/', 'icon': 'fas fa-file-contract'})
        return items

    def _get_rbac_exchange_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled exchange navigation items"""
        items = []
        if self._has_permission('can_access_exchange'):
            items.append({'title': 'Exchange Dashboard', 'route': '/services/exchange/', 'icon': 'fas fa-exchange-alt'})
            items.append({'title': 'Order Book', 'route': '/services/exchange/orderbook/', 'icon': 'fas fa-book'})
            items.append({'title': 'Trading Pairs', 'route': '/services/exchange/pairs/', 'icon': 'fas fa-link'})
        return items

    def _get_rbac_user_management_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled user management navigation items"""
        items = []
        if self._has_permission('can_manage_users'):
            items.append({'title': 'User Directory', 'route': '/user-management/', 'icon': 'fas fa-users'})
            items.append({'title': 'Role Management', 'route': '/user-management/roles/', 'icon': 'fas fa-user-tag'})
            items.append({'title': 'Permissions', 'route': '/user-management/permissions/', 'icon': 'fas fa-key'})
        return items

    def _get_rbac_communications_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled communications navigation items"""
        items = []
        if self._has_permission('can_access_communications'):
            items.append({'title': 'Message Center', 'route': '/services/communications/', 'icon': 'fas fa-envelope'})
            items.append({'title': 'Email Templates', 'route': '/services/communications/templates/', 'icon': 'fas fa-file-alt'})
            items.append({'title': 'Notifications', 'route': '/services/communications/notifications/', 'icon': 'fas fa-bell'})
        return items

    def _get_rbac_mfa_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled MFA navigation items"""
        items = []
        if self._has_permission('can_access_mfa'):
            items.append({'title': 'MFA Settings', 'route': '/services/mfa/', 'icon': 'fas fa-key'})
            items.append({'title': 'Authentication Methods', 'route': '/services/mfa/methods/', 'icon': 'fas fa-mobile-alt'})
            items.append({'title': 'Security Tokens', 'route': '/services/mfa/tokens/', 'icon': 'fas fa-shield-alt'})
        return items

    def _get_rbac_api_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled API services navigation items"""
        items = []
        if self._has_permission('can_access_api_services'):
            items.append({'title': 'API Dashboard', 'route': '/services/api/', 'icon': 'fas fa-code'})
            items.append({'title': 'API Keys', 'route': '/services/api/keys/', 'icon': 'fas fa-key'})
            items.append({'title': 'API Documentation', 'route': '/services/api/docs/', 'icon': 'fas fa-book'})
        return items

    def _get_rbac_integrations_items(self) -> List[Dict[str, str]]:
        """RBAC-controlled integrations navigation items"""
        items = []
        if self._has_permission('can_access_integrations'):
            items.append({'title': 'Integration Hub', 'route': '/services/integrations/', 'icon': 'fas fa-plug'})
            items.append({'title': 'Payment Gateways', 'route': '/services/integrations/payments/', 'icon': 'fas fa-credit-card'})
            items.append({'title': 'Blockchain Services', 'route': '/services/integrations/blockchain/', 'icon': 'fas fa-link'})
            items.append({'title': 'Financial Data', 'route': '/services/integrations/financial/', 'icon': 'fas fa-chart-line'})
        return items


class ErrorLoggerService:
    """
    Self-contained error logging service
    Provides banking-grade error logging and monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_dir = os.path.join(os.getcwd(), 'logs', 'errors')
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure error log directory exists"""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create error log directory: {e}")
    
    def log_error(self, error_type: str, message: str, details: Dict[str, Any] = None):
        """
        Log error with banking compliance standards
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'error_type': error_type,
                'message': message,
                'details': details or {},
                'user_id': getattr(current_user, 'id', 'anonymous') if current_user.is_authenticated else 'anonymous'
            }
            
            # Log to file
            log_file = os.path.join(self.log_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log')
            with open(log_file, 'a') as f:
                f.write(f"{timestamp} - {error_type}: {message}\n")
                if details:
                    f.write(f"Details: {details}\n")
                f.write("---\n")
            
            # Log to application logger
            self.logger.error(f"{error_type}: {message}", extra={'details': details})
            
        except Exception as e:
            # Fallback logging
            self.logger.error(f"Error logging failed: {e}")
    
    def log_security_event(self, event_type: str, message: str, user_id: str = None):
        """Log security-related events"""
        self.log_error(
            error_type=f"SECURITY_{event_type}",
            message=message,
            details={
                'user_id': user_id or getattr(current_user, 'id', 'anonymous'),
                'timestamp': datetime.now().isoformat(),
                'event_category': 'security'
            }
        )
    
    def log_template_error(self, template_name: str, error: Exception):
        """Log template rendering errors"""
        self.log_error(
            error_type="TEMPLATE_ERROR",
            message=f"Template rendering failed: {template_name}",
            details={
                'template': template_name,
                'exception': str(error),
                'exception_type': type(error).__name__
            }
        )
    
    def log_auth_error(self, auth_type: str, message: str, user_id: str = None):
        """Log authentication errors"""
        self.log_error(
            error_type=f"AUTH_{auth_type}",
            message=message,
            details={
                'user_id': user_id,
                'auth_category': auth_type.lower(),
                'timestamp': datetime.now().isoformat()
            }
        )

class BankingLogger:
    """
    Banking Logger Service for WebSocket handlers and real-time operations
    Provides structured logging for banking platform events
    """
    
    def __init__(self, module_name="banking_platform"):
        self.logger = logging.getLogger(module_name)
        self.module_name = module_name
    
    def log_info(self, message: str, extra_data: Dict = None):
        """Log informational messages"""
        try:
            if extra_data:
                self.logger.info(f"{message} | Data: {extra_data}")
            else:
                self.logger.info(message)
        except Exception as e:
            self.logger.error(f"Failed to log info message: {str(e)}")
    
    def log_error(self, error_type: str, message: str, extra_data: Dict = None):
        """Log error messages with context"""
        try:
            error_msg = f"[{error_type}] {message}"
            if extra_data:
                error_msg += f" | Context: {extra_data}"
            self.logger.error(error_msg)
        except Exception as e:
            self.logger.error(f"Failed to log error: {str(e)}")
    
    def log_warning(self, message: str, extra_data: Dict = None):
        """Log warning messages"""
        try:
            if extra_data:
                self.logger.warning(f"{message} | Data: {extra_data}")
            else:
                self.logger.warning(message)
        except Exception as e:
            self.logger.error(f"Failed to log warning: {str(e)}")
    
    def log_debug(self, message: str, extra_data: Dict = None):
        """Log debug messages"""
        try:
            if extra_data:
                self.logger.debug(f"{message} | Data: {extra_data}")
            else:
                self.logger.debug(message)
        except Exception as e:
            self.logger.error(f"Failed to log debug message: {str(e)}")
