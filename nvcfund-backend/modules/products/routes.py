"""
NVC Banking Platform - Products Module Routes
Centralized product management and integration system
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from modules.core.enterprise_logging import EnterpriseLogger
from modules.core.decorators import admin_required
import logging

# Create Products blueprint
products_bp = Blueprint('products', __name__, url_prefix='/products')

logger = logging.getLogger(__name__)

@products_bp.route('/')
@login_required
def main_dashboard():
    """Main products dashboard with overview of all banking products"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed products main dashboard")
        
        # Product categories and metrics
        product_categories = [
            {
                'name': 'Banking Products',
                'icon': 'fas fa-university',
                'color': 'primary',
                'count': 12,
                'active': 11,
                'description': 'Traditional banking products and accounts',
                'modules': ['accounts', 'banking', 'cards_payments'],
                'url': url_for('products.banking_products')
            },
            {
                'name': 'Investment Products',
                'icon': 'fas fa-chart-line',
                'color': 'success',
                'count': 8,
                'active': 7,
                'description': 'Investment and trading products',
                'modules': ['investments', 'trading', 'treasury'],
                'url': url_for('products.investment_products')
            },
            {
                'name': 'Digital Products',
                'icon': 'fas fa-laptop',
                'color': 'info',
                'count': 6,
                'active': 6,
                'description': 'Digital banking and fintech products',
                'modules': ['api', 'integrations', 'nvct_stablecoin'],
                'url': url_for('products.digital_products')
            },
            {
                'name': 'Insurance Products',
                'icon': 'fas fa-shield-alt',
                'color': 'warning',
                'count': 4,
                'active': 4,
                'description': 'Insurance and protection products',
                'modules': ['insurance'],
                'url': url_for('products.insurance_products')
            },
            {
                'name': 'Blockchain Products',
                'icon': 'fas fa-link',
                'color': 'dark',
                'count': 5,
                'active': 4,
                'description': 'Blockchain and cryptocurrency products',
                'modules': ['smart_contracts', 'blockchain_analytics'],
                'url': url_for('products.blockchain_products')
            },
            {
                'name': 'Institutional Products',
                'icon': 'fas fa-building',
                'color': 'secondary',
                'count': 3,
                'active': 3,
                'description': 'Enterprise and institutional banking products',
                'modules': ['institutional', 'sovereign'],
                'url': url_for('products.institutional_products')
            }
        ]
        
        # Calculate overall metrics
        total_products = sum(cat['count'] for cat in product_categories)
        active_products = sum(cat['active'] for cat in product_categories)
        product_uptime = round((active_products / total_products) * 100, 1) if total_products > 0 else 0
        
        dashboard_data = {
            'product_categories': product_categories,
            'total_products': total_products,
            'active_products': active_products,
            'product_uptime': product_uptime,
            'daily_transactions': 45680,
            'total_customers': 18547,
            'revenue_today': 847200
        }
        
        return render_template('products/dashboard.html', **dashboard_data)
        
    except Exception as e:
        logger.error(f"Error in products main dashboard: {str(e)}")
        flash('Unable to load products dashboard', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@products_bp.route('/banking-products')
@login_required
def banking_products():
    """Banking products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed banking products category")
        
        banking_modules = [
            {
                'name': 'Accounts Management',
                'icon': 'fas fa-user-circle',
                'color': 'primary',
                'status': 'Active',
                'description': 'Customer account management and operations',
                'daily_transactions': 8547,
                'success_rate': 99.2,
                'last_activity': '2 min ago',
                'url': '/accounts/'
            },
            {
                'name': 'Banking Operations',
                'icon': 'fas fa-exchange-alt',
                'color': 'success',
                'status': 'Active',
                'description': 'Core banking transactions and transfers',
                'daily_transactions': 12456,
                'success_rate': 98.7,
                'last_activity': '1 min ago',
                'url': '/banking/'
            },
            {
                'name': 'Cards & Payments',
                'icon': 'fas fa-credit-card',
                'color': 'info',
                'status': 'Active',
                'description': 'Card management and payment processing',
                'daily_transactions': 18547,
                'success_rate': 99.8,
                'last_activity': '30 sec ago',
                'url': '/cardspayments/'
            }
        ]
        
        category_data = {
            'category_name': 'Banking Products',
            'category_description': 'Traditional banking products and account management',
            'modules': banking_modules,
            'total_modules': len(banking_modules),
            'active_modules': len([m for m in banking_modules if m['status'] == 'Active']),
            'daily_transactions': sum(m['daily_transactions'] for m in banking_modules),
            'success_rate': round(sum(m['success_rate'] for m in banking_modules) / len(banking_modules), 1)
        }
        
        return render_template('products/banking_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in banking products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/investment-products')
@login_required
def investment_products():
    """Investment products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed investment products category")
        
        investment_modules = [
            {
                'name': 'Investments Portfolio',
                'icon': 'fas fa-chart-pie',
                'color': 'success',
                'status': 'Active',
                'description': 'Investment portfolio management and analysis',
                'daily_trades': 547,
                'success_rate': 97.4,
                'last_activity': '5 min ago',
                'url': '/investments/'
            },
            {
                'name': 'Trading Platform',
                'icon': 'fas fa-chart-line',
                'color': 'primary',
                'status': 'Active',
                'description': 'Advanced trading platform and market analysis',
                'daily_trades': 1245,
                'success_rate': 96.8,
                'last_activity': '1 min ago',
                'url': '/trading/'
            },
            {
                'name': 'Treasury Management',
                'icon': 'fas fa-coins',
                'color': 'warning',
                'status': 'Active',
                'description': 'Treasury operations and cash management',
                'daily_trades': 234,
                'success_rate': 99.1,
                'last_activity': '3 min ago',
                'url': '/treasury/'
            }
        ]
        
        category_data = {
            'category_name': 'Investment Products',
            'category_description': 'Investment and trading products for wealth management',
            'modules': investment_modules,
            'total_modules': len(investment_modules),
            'active_modules': len([m for m in investment_modules if m['status'] == 'Active']),
            'daily_trades': sum(m['daily_trades'] for m in investment_modules),
            'success_rate': round(sum(m['success_rate'] for m in investment_modules) / len(investment_modules), 1)
        }
        
        return render_template('products/investment_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in investment products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/digital-products')
@login_required
def digital_products():
    """Digital products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed digital products category")
        
        digital_modules = [
            {
                'name': 'API Gateway',
                'icon': 'fas fa-code',
                'color': 'info',
                'status': 'Active',
                'description': 'RESTful API services and integration',
                'daily_requests': 125647,
                'success_rate': 99.6,
                'last_activity': '15 sec ago',
                'url': '/api/'
            },
            {
                'name': 'External Integrations',
                'icon': 'fas fa-plug',
                'color': 'success',
                'status': 'Active',
                'description': 'Third-party service integrations',
                'daily_requests': 8547,
                'success_rate': 98.2,
                'last_activity': '2 min ago',
                'url': '/integrations/'
            },
            {
                'name': 'NVCT Stablecoin',
                'icon': 'fas fa-coins',
                'color': 'warning',
                'status': 'Active',
                'description': 'Digital stablecoin management platform',
                'daily_requests': 2456,
                'success_rate': 99.8,
                'last_activity': '1 min ago',
                'url': '/nvctstablecoin/'
            }
        ]
        
        category_data = {
            'category_name': 'Digital Products',
            'category_description': 'Digital banking and fintech solutions',
            'modules': digital_modules,
            'total_modules': len(digital_modules),
            'active_modules': len([m for m in digital_modules if m['status'] == 'Active']),
            'daily_requests': sum(m['daily_requests'] for m in digital_modules),
            'success_rate': round(sum(m['success_rate'] for m in digital_modules) / len(digital_modules), 1)
        }
        
        return render_template('products/digital_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in digital products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/insurance-products')
@login_required
def insurance_products():
    """Insurance products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed insurance products category")
        
        insurance_modules = [
            {
                'name': 'Insurance Services',
                'icon': 'fas fa-shield-alt',
                'color': 'warning',
                'status': 'Active',
                'description': 'Comprehensive insurance product management',
                'daily_policies': 147,
                'success_rate': 97.8,
                'last_activity': '8 min ago',
                'url': '/insurance/'
            }
        ]
        
        category_data = {
            'category_name': 'Insurance Products',
            'category_description': 'Insurance and protection products',
            'modules': insurance_modules,
            'total_modules': len(insurance_modules),
            'active_modules': len([m for m in insurance_modules if m['status'] == 'Active']),
            'daily_policies': sum(m['daily_policies'] for m in insurance_modules),
            'success_rate': round(sum(m['success_rate'] for m in insurance_modules) / len(insurance_modules), 1)
        }
        
        return render_template('products/insurance_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in insurance products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/blockchain-products')
@login_required
def blockchain_products():
    """Blockchain products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed blockchain products category")
        
        blockchain_modules = [
            {
                'name': 'Smart Contracts',
                'icon': 'fas fa-file-code',
                'color': 'dark',
                'status': 'Active',
                'description': 'Smart contract deployment and management',
                'daily_deployments': 23,
                'success_rate': 98.4,
                'last_activity': '12 min ago',
                'url': '/smartcontracts/'
            },
            {
                'name': 'Blockchain Analytics',
                'icon': 'fas fa-chart-area',
                'color': 'info',
                'status': 'Active',
                'description': 'Blockchain transaction analysis and monitoring',
                'daily_queries': 5647,
                'success_rate': 99.1,
                'last_activity': '4 min ago',
                'url': '/blockchainanalytics/'
            }
        ]
        
        category_data = {
            'category_name': 'Blockchain Products',
            'category_description': 'Blockchain and cryptocurrency products',
            'modules': blockchain_modules,
            'total_modules': len(blockchain_modules),
            'active_modules': len([m for m in blockchain_modules if m['status'] == 'Active']),
            'daily_operations': sum(m.get('daily_deployments', m.get('daily_queries', 0)) for m in blockchain_modules),
            'success_rate': round(sum(m['success_rate'] for m in blockchain_modules) / len(blockchain_modules), 1)
        }
        
        return render_template('products/blockchain_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in blockchain products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/institutional-products')
@login_required
def institutional_products():
    """Institutional products category dashboard"""
    try:
        logger.info(f"User {current_user.id if current_user.is_authenticated else 'anonymous'} accessed institutional products category")
        
        institutional_modules = [
            {
                'name': 'Institutional Banking',
                'icon': 'fas fa-building',
                'color': 'secondary',
                'status': 'Active',
                'description': 'Enterprise banking services for institutions',
                'daily_transactions': 847,
                'success_rate': 99.4,
                'last_activity': '6 min ago',
                'url': '/institutional/'
            },
            {
                'name': 'Sovereign Services',
                'icon': 'fas fa-landmark',
                'color': 'primary',
                'status': 'Active',
                'description': 'Government and sovereign banking services',
                'daily_transactions': 156,
                'success_rate': 98.9,
                'last_activity': '15 min ago',
                'url': '/sovereign/'
            }
        ]
        
        category_data = {
            'category_name': 'Institutional Products',
            'category_description': 'Enterprise and institutional banking products',
            'modules': institutional_modules,
            'total_modules': len(institutional_modules),
            'active_modules': len([m for m in institutional_modules if m['status'] == 'Active']),
            'daily_transactions': sum(m['daily_transactions'] for m in institutional_modules),
            'success_rate': round(sum(m['success_rate'] for m in institutional_modules) / len(institutional_modules), 1)
        }
        
        return render_template('products/institutional_products.html', **category_data)
        
    except Exception as e:
        logger.error(f"Error in institutional products dashboard: {str(e)}")
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/api/products-summary')
@login_required
def api_products_summary():
    """API endpoint for products summary data"""
    try:
        summary_data = {
            'total_products': 38,
            'active_products': 35,
            'product_uptime': 92.1,
            'daily_transactions': 45680,
            'categories': 6,
            'timestamp': '2025-07-08 17:15:00'
        }
        
        return jsonify(summary_data)
        
    except Exception as e:
        logger.error(f"Error in products API summary: {str(e)}")
        return jsonify({'error': 'Unable to load products summary'}), 500

# Missing routes referenced in templates
@products_bp.route('/analytics')
@login_required
def analytics():
    """Products analytics dashboard"""
    try:
        analytics_data = {
            'total_products': 45,
            'active_products': 42,
            'revenue_per_product': 125000.00,
            'customer_adoption': 78.5
        }
        return render_template('products/analytics.html',
                             analytics_data=analytics_data,
                             page_title='Products Analytics')
    except Exception as e:
        logger.error(f"Products analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/add-product')
@login_required
def add_product():
    """Add new product"""
    try:
        product_types = [
            {'id': 'banking', 'name': 'Banking Product'},
            {'id': 'investment', 'name': 'Investment Product'},
            {'id': 'insurance', 'name': 'Insurance Product'},
            {'id': 'trading', 'name': 'Trading Product'}
        ]
        return render_template('products/add_product.html',
                             product_types=product_types,
                             page_title='Add Product')
    except Exception as e:
        logger.error(f"Add product error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/activity-log')
@login_required
def activity_log():
    """Products activity log"""
    try:
        activity_data = {
            'recent_activities': [
                {'action': 'Product Created', 'product': 'Premium Savings', 'timestamp': '2025-01-15 10:30'},
                {'action': 'Product Updated', 'product': 'Investment Portfolio', 'timestamp': '2025-01-15 09:15'},
                {'action': 'Product Activated', 'product': 'Crypto Trading', 'timestamp': '2025-01-14 16:45'}
            ]
        }
        return render_template('products/activity_log.html',
                             activity_data=activity_data,
                             page_title='Activity Log')
    except Exception as e:
        logger.error(f"Activity log error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/banking-analytics')
@login_required
def banking_analytics():
    """Banking products analytics"""
    try:
        banking_data = {
            'total_banking_products': 15,
            'active_accounts': 12500,
            'total_deposits': 45600000.00,
            'loan_portfolio': 25400000.00
        }
        return render_template('products/banking_analytics.html',
                             banking_data=banking_data,
                             page_title='Banking Analytics')
    except Exception as e:
        logger.error(f"Banking analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('products.main_dashboard'))

@products_bp.route('/add-banking-product')
@login_required
def add_banking_product():
    """Add new banking product"""
    try:
        banking_product_types = [
            {'id': 'savings', 'name': 'Savings Account'},
            {'id': 'checking', 'name': 'Checking Account'},
            {'id': 'loan', 'name': 'Loan Product'},
            {'id': 'credit_card', 'name': 'Credit Card'}
        ]
        return render_template('products/add_banking_product.html',
                             banking_product_types=banking_product_types,
                             page_title='Add Banking Product')
    except Exception as e:
        logger.error(f"Add banking product error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('products.main_dashboard'))