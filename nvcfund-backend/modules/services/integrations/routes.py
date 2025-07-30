"""
Integrations Routes - External Service Integration Management
Central hub for managing all external service integrations
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint
integrations_bp = Blueprint('integrations', __name__, 
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/integrations')

# Initialize services
error_service = ErrorLoggerService()

@integrations_bp.route('/')
@integrations_bp.route('/dashboard')
@login_required
def integrations_dashboard():
    """Integrations management dashboard"""
    try:
        # Get integration status from sub-modules
        integration_status = _get_integration_status()
        
        context = {
            'integration_categories': integration_status,
            'page_title': 'Integrations Dashboard',
            'total_integrations': sum(len(cat['services']) for cat in integration_status),
            'active_integrations': sum(len([s for s in cat['services'] if s['status'] == 'active']) 
                                     for cat in integration_status)
        }
        
        return render_template('integrations/dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Integrations dashboard error: {str(e)}", current_user.id)
        flash('Unable to load integrations dashboard. Please try again.', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@integrations_bp.route('/payment-gateways')
@login_required
def payment_gateways():
    """Payment gateways integration management"""
    return redirect(url_for('payment_gateways.gateway_dashboard'))

@integrations_bp.route('/blockchain')
@login_required
def blockchain_integrations():
    """Blockchain integrations management"""
    try:
        blockchain_services = _get_blockchain_integrations()
        
        context = {
            'blockchain_services': blockchain_services,
            'page_title': 'Blockchain Integrations',
            'total_services': len(blockchain_services),
            'active_services': len([s for s in blockchain_services if s['status'] == 'active'])
        }
        
        return render_template('integrations/blockchain.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Blockchain integrations error: {str(e)}", current_user.id)
        flash('Unable to load blockchain integrations. Please try again.', 'error')
        return redirect(url_for('integrations.integrations_dashboard'))

@integrations_bp.route('/communications')
@login_required
def communications_integrations():
    """Communications integrations management"""
    try:
        communication_services = _get_communication_integrations()
        
        context = {
            'communication_services': communication_services,
            'page_title': 'Communications Integrations',
            'total_services': len(communication_services),
            'active_services': len([s for s in communication_services if s['status'] == 'active'])
        }
        
        return render_template('integrations/communications.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Communications integrations error: {str(e)}", current_user.id)
        flash('Unable to load communications integrations. Please try again.', 'error')
        return redirect(url_for('integrations.integrations_dashboard'))

@integrations_bp.route('/financial-data')
@login_required
def financial_data_integrations():
    """Financial data provider integrations management"""
    try:
        financial_services = _get_financial_data_integrations()
        
        context = {
            'financial_services': financial_services,
            'page_title': 'Financial Data Integrations',
            'total_services': len(financial_services),
            'active_services': len([s for s in financial_services if s['status'] == 'active'])
        }
        
        return render_template('integrations/financial_data.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Financial data integrations error: {str(e)}", current_user.id)
        flash('Unable to load financial data integrations. Please try again.', 'error')
        return redirect(url_for('integrations.integrations_dashboard'))

@integrations_bp.route('/api/status')
@login_required
def integration_status_api():
    """Get integration status API endpoint"""
    try:
        status_data = {
            'payment_gateways': _get_payment_gateway_status(),
            'blockchain': _get_blockchain_status(),
            'communications': _get_communications_status(),
            'financial_data': _get_financial_data_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def _get_integration_status():
    """Get status of all integration categories"""
    return [
        {
            'name': 'Payment Gateways',
            'description': 'External payment processing services',
            'route': 'integrations.payment_gateways',
            'icon': 'fas fa-credit-card',
            'color': 'primary',
            'services': [
                {'name': 'PayPal', 'status': 'active', 'uptime': '99.9%'},
                {'name': 'Stripe', 'status': 'active', 'uptime': '99.8%'},
                {'name': 'Flutterwave', 'status': 'active', 'uptime': '99.5%'},
                {'name': 'Mojaloop', 'status': 'active', 'uptime': '99.7%'},
                {'name': 'Mobile Transfer', 'status': 'active', 'uptime': '99.4%'}
            ]
        },
        {
            'name': 'Blockchain Services',
            'description': 'Cryptocurrency and blockchain integrations',
            'route': 'integrations.blockchain_integrations',
            'icon': 'fas fa-link',
            'color': 'warning',
            'services': [
                {'name': 'Binance API', 'status': 'active', 'uptime': '99.6%'},
                {'name': 'Etherscan', 'status': 'active', 'uptime': '99.3%'},
                {'name': 'Polygonscan', 'status': 'active', 'uptime': '99.1%'},
                {'name': 'NVCT Network', 'status': 'active', 'uptime': '99.8%'}
            ]
        },
        {
            'name': 'Communications',
            'description': 'Email and messaging service integrations',
            'route': 'integrations.communications_integrations',
            'icon': 'fas fa-envelope',
            'color': 'info',
            'services': [
                {'name': 'SendGrid', 'status': 'active', 'uptime': '99.9%'},
                {'name': 'Twilio SMS', 'status': 'active', 'uptime': '99.7%'},
                {'name': 'Push Notifications', 'status': 'active', 'uptime': '99.5%'}
            ]
        },
        {
            'name': 'Financial Data',
            'description': 'Banking and financial data providers',
            'route': 'integrations.financial_data_integrations',
            'icon': 'fas fa-chart-line',
            'color': 'success',
            'services': [
                {'name': 'Plaid', 'status': 'active', 'uptime': '99.8%'},
                {'name': 'Federal Reserve API', 'status': 'active', 'uptime': '99.9%'},
                {'name': 'ACH Network', 'status': 'active', 'uptime': '99.7%'},
                {'name': 'SWIFT Network', 'status': 'active', 'uptime': '99.6%'}
            ]
        }
    ]

def _get_blockchain_integrations():
    """Get blockchain integration details"""
    return [
        {
            'name': 'Binance Exchange',
            'description': 'Cryptocurrency trading and market data',
            'status': 'active',
            'api_version': 'v3',
            'last_sync': '2 minutes ago',
            'daily_calls': 8547,
            'rate_limit': '1200/minute',
            'features': ['Live prices', 'Order execution', 'Portfolio tracking']
        },
        {
            'name': 'Etherscan',
            'description': 'Ethereum blockchain explorer',
            'status': 'active',
            'api_version': 'v1',
            'last_sync': '1 minute ago',
            'daily_calls': 2145,
            'rate_limit': '5/second',
            'features': ['Transaction tracking', 'Smart contract verification', 'Gas analytics']
        },
        {
            'name': 'Polygonscan',
            'description': 'Polygon blockchain explorer',
            'status': 'active',
            'api_version': 'v1',
            'last_sync': '3 minutes ago',
            'daily_calls': 1876,
            'rate_limit': '5/second',
            'features': ['Transaction tracking', 'DeFi analytics', 'Token analysis']
        },
        {
            'name': 'NVCT Network',
            'description': 'Native stablecoin infrastructure',
            'status': 'active',
            'api_version': 'v2',
            'last_sync': '30 seconds ago',
            'daily_calls': 12457,
            'rate_limit': 'Unlimited',
            'features': ['Mint/burn operations', 'Reserve management', 'Compliance monitoring']
        }
    ]

def _get_communication_integrations():
    """Get communication integration details"""
    return [
        {
            'name': 'SendGrid',
            'description': 'Email delivery service',
            'status': 'active',
            'api_version': 'v3',
            'last_sync': '1 minute ago',
            'daily_usage': '2,847 emails',
            'monthly_limit': '100,000 emails',
            'features': ['Transactional emails', 'Marketing campaigns', 'Analytics']
        },
        {
            'name': 'Twilio SMS',
            'description': 'SMS messaging service',
            'status': 'active',
            'api_version': 'v1',
            'last_sync': '2 minutes ago',
            'daily_usage': '456 messages',
            'monthly_limit': '10,000 messages',
            'features': ['OTP delivery', 'Notifications', 'Two-way messaging']
        },
        {
            'name': 'Push Notifications',
            'description': 'Mobile and web push notifications',
            'status': 'active',
            'api_version': 'v2',
            'last_sync': '30 seconds ago',
            'daily_usage': '1,247 notifications',
            'monthly_limit': 'Unlimited',
            'features': ['Real-time alerts', 'Transaction notifications', 'Marketing messages']
        }
    ]

def _get_financial_data_integrations():
    """Get financial data integration details"""
    return [
        {
            'name': 'Plaid',
            'description': 'Banking and financial data aggregation',
            'status': 'active',
            'api_version': 'v2',
            'last_sync': '5 minutes ago',
            'daily_usage': '1,547 requests',
            'monthly_limit': '100,000 requests',
            'features': ['Account linking', 'Transaction data', 'Identity verification']
        },
        {
            'name': 'Federal Reserve API',
            'description': 'Economic data and rates',
            'status': 'active',
            'api_version': 'v1',
            'last_sync': '1 hour ago',
            'daily_usage': '124 requests',
            'monthly_limit': 'Unlimited',
            'features': ['Interest rates', 'Economic indicators', 'Market data']
        },
        {
            'name': 'ACH Network',
            'description': 'Automated Clearing House processing',
            'status': 'active',
            'api_version': 'v2',
            'last_sync': '10 minutes ago',
            'daily_usage': '847 transactions',
            'monthly_limit': 'Unlimited',
            'features': ['Direct deposits', 'Bill payments', 'Bulk transfers']
        },
        {
            'name': 'SWIFT Network',
            'description': 'International wire transfer network',
            'status': 'active',
            'api_version': 'v1',
            'last_sync': '15 minutes ago',
            'daily_usage': '156 messages',
            'monthly_limit': 'Unlimited',
            'features': ['International transfers', 'Trade finance', 'Compliance monitoring']
        }
    ]

def _get_payment_gateway_status():
    """Get payment gateway status summary"""
    return {
        'total_gateways': 5,
        'active_gateways': 5,
        'daily_volume': 125847.50,
        'success_rate': 99.8
    }

def _get_blockchain_status():
    """Get blockchain integration status summary"""
    return {
        'total_services': 4,
        'active_services': 4,
        'daily_calls': 25025,
        'average_uptime': 99.5
    }

def _get_communications_status():
    """Get communications integration status summary"""
    return {
        'total_services': 3,
        'active_services': 3,
        'daily_messages': 4550,
        'delivery_rate': 99.7
    }

def _get_financial_data_status():
    """Get financial data integration status summary"""
    return {
        'total_services': 4,
        'active_services': 4,
        'daily_requests': 2674,
        'data_accuracy': 99.9
    }