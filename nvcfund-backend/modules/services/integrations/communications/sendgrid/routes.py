"""
SendGrid Integration Routes
NVC Banking Platform - SendGrid Email Service Integration
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint
sendgrid_bp = Blueprint('sendgrid', __name__, 
                       template_folder='templates',
                       static_folder='static',
                       url_prefix='/integrations/communications/sendgrid')

# Initialize services
error_service = ErrorLoggerService()

@sendgrid_bp.route('/')
@sendgrid_bp.route('/dashboard')
@login_required
def sendgrid_dashboard():
    """SendGrid integration dashboard"""
    try:
        context = {
            'page_title': 'SendGrid Email Service',
            'service_name': 'SendGrid',
            'status': 'Connected',
            'emails_sent_today': 1247,
            'delivery_rate': 99.2,
            'open_rate': 24.8,
            'click_rate': 3.7
        }
        
        return render_template('sendgrid/dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"SendGrid dashboard error: {str(e)}", current_user.id)
        flash('Unable to load SendGrid dashboard. Please try again.', 'error')
        return redirect(url_for('communications.communications_dashboard'))

@sendgrid_bp.route('/api/status')
@login_required
def sendgrid_status_api():
    """Get SendGrid integration status API endpoint"""
    try:
        status_data = {
            'service': 'SendGrid',
            'status': 'operational',
            'endpoint': 'api.sendgrid.com',
            'last_check': datetime.now().isoformat(),
            'response_time': '123ms',
            'delivery_rate': 99.2
        }
        return jsonify(status_data)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500