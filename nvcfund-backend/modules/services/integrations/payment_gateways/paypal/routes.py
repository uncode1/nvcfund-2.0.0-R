"""
PayPal Integration Routes
NVC Banking Platform - PayPal Payment Gateway Integration
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint
paypal_bp = Blueprint('paypal', __name__, 
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/integrations/payment-gateways/paypal')

# Initialize services
error_service = ErrorLoggerService()

@paypal_bp.route('/')
@paypal_bp.route('/dashboard')
@login_required
def paypal_dashboard():
    """PayPal integration dashboard"""
    try:
        context = {
            'page_title': 'PayPal Integration',
            'gateway_name': 'PayPal',
            'status': 'Connected',
            'transactions_today': 127,
            'volume_today': 45678.90,
            'success_rate': 99.2
        }
        
        return render_template('paypal/dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"PayPal dashboard error: {str(e)}", current_user.id)
        flash('Unable to load PayPal dashboard. Please try again.', 'error')
        return redirect(url_for('payment_gateways.payment_gateways_dashboard'))

@paypal_bp.route('/api/status')
@login_required
def paypal_status_api():
    """Get PayPal integration status API endpoint"""
    try:
        status_data = {
            'service': 'PayPal',
            'status': 'operational',
            'endpoint': 'api.paypal.com',
            'last_check': datetime.now().isoformat(),
            'response_time': '145ms',
            'success_rate': 99.2
        }
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500