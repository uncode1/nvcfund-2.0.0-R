"""
Communications Integration Routes
NVC Banking Platform - Communication Services Integration Management
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint with unique name to avoid conflicts
communications_integration_bp = Blueprint('communications_integration', __name__, 
                             template_folder='templates',
                             static_folder='static',
                             url_prefix='/integrations/communications')

# Initialize services
error_service = ErrorLoggerService()

@communications_integration_bp.route('/')
@communications_integration_bp.route('/dashboard')
@login_required
def communications_dashboard():
    """Communications integration dashboard"""
    try:
        context = {
            'page_title': 'Communications Integration',
            'total_services': 3,
            'active_services': 3,
            'emails_sent_today': 1247,
            'sms_sent_today': 567,
            'push_notifications_today': 2890
        }
        
        return render_template('communications/dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Communications dashboard error: {str(e)}", current_user.id)
        flash('Unable to load communications dashboard. Please try again.', 'error')
        return redirect(url_for('integrations.integrations_dashboard'))

# Redirect routes to individual communication service sub-modules
@communications_integration_bp.route('/sendgrid')
@login_required
def sendgrid_redirect():
    """Redirect to SendGrid sub-module"""
    return redirect('/integrations/communications/sendgrid/')

@communications_integration_bp.route('/twilio')
@login_required
def twilio_redirect():
    """Redirect to Twilio sub-module"""
    return redirect('/integrations/communications/twilio/')

@communications_integration_bp.route('/push-notifications')
@login_required
def push_notifications_redirect():
    """Redirect to Push Notifications sub-module"""
    return redirect('/integrations/communications/push-notifications/')