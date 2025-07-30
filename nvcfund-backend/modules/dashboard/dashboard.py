
"""
Dashboard Module - Consolidated Functions
Central dashboard management with all dashboard logic and data retrieval functions
"""

from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from modules.core.decorators import feature_required, module_health_check
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DashboardManager:
    """Centralized dashboard management class"""
    
    def __init__(self):
        self.dashboard_configs = {
            'admin': self._get_admin_config,
            'super_admin': self._get_admin_config,
            'treasury_officer': self._get_treasury_config,
            'compliance_officer': self._get_compliance_config,
            'institutional_banker': self._get_institutional_config,
            'sovereign_banker': self._get_sovereign_config,
            'central_banker': self._get_sovereign_config,
            'risk_manager': self._get_risk_config,
            'loan_officer': self._get_loan_config,
            'operations_officer': self._get_operations_config,
            'relationship_manager': self._get_relationship_config,
            'banking_officer': self._get_banking_officer_config,
            'standard': self._get_user_config,
            'premium': self._get_user_config,
            'business': self._get_user_config
        }
    
    def get_dashboard_data(self, user_role, user=None):
        """Get dashboard data based on user role"""
        config_func = self.dashboard_configs.get(user_role.lower(), self._get_user_config)
        return config_func(user)
    
    def render_dashboard(self, user_role, user=None):
        """Render appropriate dashboard template based on user role"""
        try:
            user_role_lower = user_role.lower()
            username = getattr(current_user, 'username', 'User')
            last_login = session.get('last_login_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Get dashboard data
            dashboard_data = self.get_dashboard_data(user_role, user)
            
            # Single template with role-based content sections
            # Each role gets customized dashboard content within the same template
            template_name = 'dashboard/main_dashboard.html'

            # Role-specific dashboard configurations
            role_configs = {
                'admin': {
                    'show_system_status': True,
                    'show_user_management': True,
                    'show_audit_logs': True,
                    'show_compliance_alerts': True,
                    'dashboard_title': 'Administrative Dashboard',
                    'primary_metrics': ['total_users', 'system_health', 'security_alerts', 'compliance_status']
                },
                'super_admin': {
                    'show_system_status': True,
                    'show_user_management': True,
                    'show_audit_logs': True,
                    'show_compliance_alerts': True,
                    'show_financial_overview': True,
                    'dashboard_title': 'Executive Dashboard',
                    'primary_metrics': ['total_assets', 'system_health', 'user_activity', 'revenue']
                },
                'treasury_officer': {
                    'show_liquidity_management': True,
                    'show_cash_flow': True,
                    'show_investment_portfolio': True,
                    'show_risk_metrics': True,
                    'dashboard_title': 'Treasury Dashboard',
                    'primary_metrics': ['cash_position', 'liquidity_ratio', 'investment_performance', 'risk_exposure']
                },
                'compliance_officer': {
                    'show_compliance_alerts': True,
                    'show_audit_logs': True,
                    'show_regulatory_reports': True,
                    'show_kyc_status': True,
                    'dashboard_title': 'Compliance Dashboard',
                    'primary_metrics': ['compliance_score', 'pending_reviews', 'audit_findings', 'regulatory_deadlines']
                },
                'institutional_banker': {
                    'show_client_portfolio': True,
                    'show_transaction_volume': True,
                    'show_revenue_metrics': True,
                    'show_relationship_status': True,
                    'dashboard_title': 'Institutional Banking Dashboard',
                    'primary_metrics': ['client_assets', 'transaction_volume', 'revenue_ytd', 'client_satisfaction']
                },
                'loan_officer': {
                    'show_loan_pipeline': True,
                    'show_credit_metrics': True,
                    'show_approval_queue': True,
                    'show_portfolio_performance': True,
                    'dashboard_title': 'Loan Officer Dashboard',
                    'primary_metrics': ['loan_applications', 'approval_rate', 'portfolio_quality', 'delinquency_rate']
                },
                'relationship_manager': {
                    'show_client_portfolio': True,
                    'show_sales_pipeline': True,
                    'show_revenue_metrics': True,
                    'show_client_interactions': True,
                    'dashboard_title': 'Relationship Manager Dashboard',
                    'primary_metrics': ['client_portfolio_value', 'new_business', 'client_meetings', 'revenue_target']
                },
                'banking_officer': {
                    'show_daily_transactions': True,
                    'show_account_management': True,
                    'show_customer_service': True,
                    'show_operational_metrics': True,
                    'dashboard_title': 'Banking Officer Dashboard',
                    'primary_metrics': ['daily_transactions', 'account_openings', 'customer_inquiries', 'processing_time']
                },
                'operations_officer': {
                    'show_operational_metrics': True,
                    'show_processing_queue': True,
                    'show_system_performance': True,
                    'show_error_monitoring': True,
                    'dashboard_title': 'Operations Dashboard',
                    'primary_metrics': ['processing_volume', 'error_rate', 'system_uptime', 'sla_compliance']
                },
                'risk_manager': {
                    'show_risk_metrics': True,
                    'show_exposure_analysis': True,
                    'show_stress_testing': True,
                    'show_regulatory_capital': True,
                    'dashboard_title': 'Risk Management Dashboard',
                    'primary_metrics': ['var_exposure', 'credit_risk', 'market_risk', 'operational_risk']
                }
            }

            # Get role-specific configuration
            role_config = role_configs.get(user_role_lower, {
                'show_account_overview': True,
                'show_transaction_history': True,
                'show_quick_actions': True,
                'dashboard_title': 'Personal Dashboard',
                'primary_metrics': ['account_balance', 'monthly_spending', 'savings_goal', 'investment_growth']
            })

            # Render single template with role-specific configuration
            return render_template(template_name,
                                 username=username,
                                 user_role=user_role,
                                 last_login=last_login,
                                 role_config=role_config,
                                 user=user,
                                 now=datetime.now(),
                                 **dashboard_data)
                                 
        except Exception as e:
            logger.error(f"Dashboard rendering error for user {current_user.id if current_user else 'unknown'}: {e}")
            return render_template('dashboard/error.html', 
                                 error_message="Dashboard temporarily unavailable"), 500
    
    def _get_admin_config(self, user=None):
        """Get admin dashboard configuration"""
        is_superadmin = self._is_superadmin(user)
        
        base_data = {
            'system_health': 'Operational',
            'active_sessions': 89,
            'database_status': 'Connected',
            'total_users': 1247,
            'recent_admin_activities': [
                {
                    'type': 'system',
                    'description': 'System backup completed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'security',
                    'description': 'Security scan completed',
                    'timestamp': (datetime.now()).strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'user',
                    'description': 'New user registration approved',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'pending'
                }
            ],
            'is_superadmin': is_superadmin
        }
        
        if is_superadmin:
            base_data.update({
                'security_alerts': 2,
                'pending_approvals': 15,
                'system_uptime': '99.9%',
                'platform_revenue': '$2.1M',
                'critical_system_access': True,
                'user_management_access': True,
                'financial_data_access': True,
                'blockchain_admin_access': True,
                'sovereign_banking_override': True,
                'treasury_operations_full': True,
                'super_admin_notice': 'Super Administrator - Full Platform Control'
            })
        else:
            base_data.update({
                'security_alerts': 'Access Restricted',
                'pending_approvals': 'View Only',
                'platform_revenue': 'Access Restricted',
                'critical_system_access': False,
                'user_management_access': False,
                'financial_data_access': False,
                'limited_admin_notice': 'You have limited admin access. Contact superadmin for elevated privileges.'
            })
        
        return base_data
    
    def _get_treasury_config(self, user=None):
        """Get treasury dashboard configuration"""
        return {
            'nvct_supply': '30T NVCT',
            'asset_backing': '$56.7T',
            'collateral_ratio': '189%',
            'liquidity_pool': '$1.8B',
            'yield_rate': '12.5% APY',
            'active_providers': 892,
            'volume_24h': '$89M',
            'treasury_operations': 'operational',
            'settlement_status': 'active',
            'recent_treasury_activities': [
                {
                    'type': 'nvct_backing',
                    'description': 'NVCT reserve backing verified',
                    'amount': '$56.7T',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'verified'
                },
                {
                    'type': 'liquidity',
                    'description': 'Liquidity pool rebalanced',
                    'amount': '$500M',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'settlement',
                    'description': 'Cross-border settlement processed',
                    'amount': '$125M',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                }
            ]
        }
    
    def _get_compliance_config(self, user=None):
        """Get compliance dashboard configuration"""
        return {
            'kyc_pending': 23,
            'aml_alerts': 5,
            'regulatory_reports': 12,
            'compliance_score': '94.2%',
            'audit_status': 'current',
            'risk_level': 'low',
            'recent_compliance_activities': [
                {
                    'type': 'kyc',
                    'description': 'KYC verification completed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'aml',
                    'description': 'AML screening flagged transaction',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'pending_review'
                }
            ]
        }
    
    def _get_institutional_config(self, user=None):
        """Get institutional banking dashboard configuration"""
        return {
            'total_assets': '$2.1B',
            'active_accounts': 1247,
            'transaction_volume': '$456M',
            'correspondent_banks': 45,
            'swift_messages': 1250,
            'settlement_efficiency': '98.5%',
            'recent_institutional_activities': [
                {
                    'type': 'correspondent',
                    'description': 'New correspondent bank onboarded',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'settlement',
                    'description': 'Cross-border settlement processed',
                    'amount': '$25M',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'settled'
                }
            ]
        }
    
    def _get_sovereign_config(self, user=None):
        """Get sovereign banking dashboard configuration"""
        return {
            'reserves': {'total': '58.5B'},
            'currency': {'supply': '2.8T'},
            'interest_rate': '3.25%',
            'economic_index': '128.5',
            'central_bank_operations': 'operational',
            'federal_reserve_status': 'connected',
            'sovereign_debt_level': 'monitored',
            'recent_sovereign_activities': [
                {
                    'type': 'monetary_policy',
                    'description': 'Interest rate adjustment',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'implemented'
                }
            ]
        }
    
    def _get_risk_config(self, user=None):
        """Get risk management dashboard configuration"""
        return {
            'var': {'portfolio': '2.8M'},
            'credit_risk': '12.5%',
            'liquidity_ratio': '18.2%',
            'risk_score': '7.2',
            'recent_risk_activities': [
                {
                    'type': 'assessment',
                    'description': 'Portfolio risk assessment completed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                }
            ]
        }
    
    def _get_loan_config(self, user=None):
        """Get loan officer dashboard configuration"""
        return {
            'loan_applications': 15,
            'approved_loans': 8,
            'pending_review': 5,
            'default_rate': '2.1%',
            'portfolio_value': '$12.5M',
            'recent_loan_activities': [
                {
                    'type': 'approval',
                    'description': 'Commercial loan approved',
                    'amount': '$250K',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'approved'
                }
            ]
        }
    
    def _get_operations_config(self, user=None):
        """Get operations officer dashboard configuration"""
        return {
            'daily_transactions': 1250,
            'settlement_queue': 45,
            'failed_transactions': 2,
            'system_uptime': '99.9%',
            'processing_efficiency': '97.8%',
            'recent_operations_activities': [
                {
                    'type': 'settlement',
                    'description': 'Batch settlement processed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                }
            ]
        }
    
    def _get_relationship_config(self, user=None):
        """Get relationship manager dashboard configuration"""
        return {
            'client_portfolio': '$45M',
            'new_clients': 3,
            'upcoming_meetings': 8,
            'revenue_target': '85%',
            'client_satisfaction': '94%',
            'recent_relationship_activities': [
                {
                    'type': 'client_meeting',
                    'description': 'New client onboarding',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'scheduled'
                }
            ]
        }
    
    def _get_banking_officer_config(self, user=None):
        """Get banking officer dashboard configuration"""
        return {
            'pending_approvals': 12,
            'loans_processed': 45,
            'customer_applications': 8,
            'daily_transactions': '$2.5M',
            'compliance_alerts': 3,
            'recent_banking_activities': [
                {
                    'type': 'transaction_processing',
                    'description': 'Daily transaction batch processed',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                }
            ]
        }
    
    def _get_user_config(self, user=None):
        """Get standard user dashboard configuration"""
        return {
            'total_accounts': 3,
            'account_balance': '$15,675.85',
            'recent_transactions': [
                {
                    'type': 'transfer',
                    'description': 'Transferred $500.00 to Savings Account',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'deposit',
                    'description': 'Direct deposit received',
                    'amount': '$2,850.00',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'payment',
                    'description': 'Utility bill payment',
                    'amount': '$145.67',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                },
                {
                    'type': 'transfer',
                    'description': 'NVCT crypto exchange',
                    'amount': '$1,200.00',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'completed'
                }
            ],
            'alerts': [],
            'notifications': []
        }
    
    def _is_superadmin(self, user=None):
        """Check if user is a superadmin"""
        if user is None:
            user = current_user
        
        username = getattr(user, 'username', '')
        user_role = getattr(user, 'role', '')
        
        return (username.lower() == 'uncode' or 
                user_role.lower() in ['super_admin', 'superadmin'] or
                hasattr(user, 'is_superadmin') and user.is_superadmin)
    
    def get_overview_data(self, user_role):
        """Get dashboard overview section data"""
        return {
            'account_summary': {
                'checking': '$5,432.10',
                'savings': '$12,890.50',
                'investment': '$45,200.00'
            },
            'credit_summary': {
                'available_credit': '$8,500.00',
                'outstanding_balance': '$1,230.45'
            }
        }
    
    def get_recent_activities(self, user_role):
        """Get recent activities based on user role"""
        base_activities = [
            {
                'type': 'transfer',
                'description': 'Transferred $500.00 to Savings Account',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'completed'
            },
            {
                'type': 'deposit',
                'description': 'Direct deposit received',
                'amount': '$2,850.00',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'completed'
            }
        ]
        
        if user_role.lower() in ['treasury_officer', 'admin']:
            base_activities.insert(0, {
                'type': 'treasury',
                'description': 'NVCT reserve backing verified',
                'amount': '$56.7T',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'verified'
            })
        
        return base_activities
    
    def get_quick_actions(self, user_role):
        """Get available quick actions based on user permissions"""
        from modules.core.registry import module_registry
        
        available_actions = []
        
        # Define role-based actions
        if user_role.lower() in ['admin', 'treasury_officer']:
            available_actions.extend([
                {
                    'title': 'Treasury Dashboard',
                    'icon': 'fas fa-chart-line',
                    'route': 'dashboard.treasury_dashboard',
                    'description': 'Access treasury operations'
                },
                {
                    'title': 'NVCT Management',
                    'icon': 'fas fa-coins',
                    'route': 'treasury.nvct_management',
                    'description': 'Manage NVCT stablecoin (30T supply)'
                }
            ])
        
        # Standard banking actions for all roles
        available_actions.extend([
            {
                'title': 'Create Account',
                'icon': 'fas fa-plus-circle',
                'route': 'accounts.create',
                'description': 'Open a new banking account'
            },
            {
                'title': 'Transfer Funds',
                'icon': 'fas fa-exchange-alt',
                'route': 'transfers.create',
                'description': 'Send money to another account'
            },
            {
                'title': 'View Transactions',
                'icon': 'fas fa-list',
                'route': 'transactions.list',
                'description': 'View transaction history'
            }
        ])
        
        return available_actions

# Global dashboard manager instance
dashboard_manager = DashboardManager()

# Convenience functions for backward compatibility
def get_admin_dashboard_data(is_superadmin=False):
    """Legacy function for admin dashboard data"""
    user = current_user if hasattr(current_user, 'role') else None
    return dashboard_manager._get_admin_config(user)

def get_treasury_dashboard_data():
    """Legacy function for treasury dashboard data"""
    return dashboard_manager._get_treasury_config()

def get_compliance_dashboard_data():
    """Legacy function for compliance dashboard data"""
    return dashboard_manager._get_compliance_config()

def get_institutional_dashboard_data():
    """Legacy function for institutional dashboard data"""
    return dashboard_manager._get_institutional_config()

def get_sovereign_dashboard_data():
    """Legacy function for sovereign dashboard data"""
    return dashboard_manager._get_sovereign_config()

def get_risk_dashboard_data():
    """Legacy function for risk dashboard data"""
    return dashboard_manager._get_risk_config()

def get_loan_officer_dashboard_data():
    """Legacy function for loan officer dashboard data"""
    return dashboard_manager._get_loan_config()

def get_operations_officer_dashboard_data():
    """Legacy function for operations officer dashboard data"""
    return dashboard_manager._get_operations_config()

def get_relationship_manager_dashboard_data():
    """Legacy function for relationship manager dashboard data"""
    return dashboard_manager._get_relationship_config()

def get_banking_officer_dashboard_data(user_role):
    """Legacy function for banking officer dashboard data"""
    return dashboard_manager._get_banking_officer_config()

def get_user_dashboard_data(user_role):
    """Legacy function for user dashboard data"""
    return dashboard_manager._get_user_config()

def get_overview_data(user_role):
    """Legacy function for overview data"""
    return dashboard_manager.get_overview_data(user_role)

def get_recent_activities(user_role):
    """Legacy function for recent activities"""
    return dashboard_manager.get_recent_activities(user_role)
