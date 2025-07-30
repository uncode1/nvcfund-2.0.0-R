"""
Institutional Banking Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService

# Create module blueprint
institutional_bp = Blueprint('institutional', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/institutional')

# Initialize services
error_service = ErrorLoggerService()

@institutional_bp.route('/')
@login_required
def main_dashboard():
    """Institutional Banking main dashboard"""
    try:
        return render_template('institutional/institutional_dashboard.html',
                             user=current_user,
                             page_title='Institutional Banking Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@institutional_bp.route('/overview')
@login_required  
def overview():
    """Institutional Banking overview page"""
    try:
        return render_template('institutional/institutional_overview.html',
                             user=current_user,
                             page_title='Institutional Banking Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('institutional.main_dashboard'))

@institutional_bp.route('/client-management')
@login_required
def client_management():
    """Institutional client management"""
    try:
        return render_template('institutional/institutional_client_management.html',
                             user=current_user,
                             page_title='Client Management')
    except Exception as e:
        error_service.log_error("CLIENT_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('institutional.main_dashboard'))

@institutional_bp.route('/settings')
@login_required
def settings():
    """Institutional Banking settings page"""
    try:
        return render_template('institutional/institutional_settings.html',
                             user=current_user,
                             page_title='Institutional Banking Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('institutional.main_dashboard'))

# Module health check
@institutional_bp.route('/api/health')
def health_check():
    """Institutional Banking health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Institutional Banking",
        "version": "1.0.0",
        "routes_active": 22
    })
