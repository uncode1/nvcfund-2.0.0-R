"""
Insurance Services Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService

# Create module blueprint
insurance_bp = Blueprint('insurance', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/insurance')

# Initialize services
error_service = ErrorLoggerService()

@insurance_bp.route('/')
@login_required
def main_dashboard():
    """Insurance Services main dashboard"""
    try:
        return render_template('insurance/insurance_dashboard.html',
                             user=current_user,
                             page_title='Insurance Services Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@insurance_bp.route('/overview')
@login_required  
def overview():
    """Insurance Services overview page"""
    try:
        return render_template('insurance/insurance_overview.html',
                             user=current_user,
                             page_title='Insurance Services Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/policy-management')
@login_required
def policy_management():
    """Insurance policy management"""
    try:
        return render_template('insurance/insurance_policy_management.html',
                             user=current_user,
                             page_title='Policy Management')
    except Exception as e:
        error_service.log_error("POLICY_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/settings')
@login_required
def settings():
    """Insurance Services settings page"""
    try:
        return render_template('insurance/insurance_settings.html',
                             user=current_user,
                             page_title='Insurance Services Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

# Drill-down routes for detailed views
@insurance_bp.route('/policies/active')
@login_required
def active_policies():
    """Active policies drill-down view"""
    try:
        return render_template('insurance/active_policies.html',
                             user=current_user,
                             page_title='Active Policies')
    except Exception as e:
        error_service.log_error("ACTIVE_POLICIES_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/claims/management')
@login_required
def claims_management():
    """Claims management drill-down view"""
    try:
        return render_template('insurance/claims_management.html',
                             user=current_user,
                             page_title='Claims Management')
    except Exception as e:
        error_service.log_error("CLAIMS_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/premiums/analysis')
@login_required
def premiums_analysis():
    """Premiums analysis drill-down view"""
    try:
        return render_template('insurance/premiums_analysis.html',
                             user=current_user,
                             page_title='Premiums Analysis')
    except Exception as e:
        error_service.log_error("PREMIUMS_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/coverage/details')
@login_required
def coverage_details():
    """Coverage details drill-down view"""
    try:
        return render_template('insurance/coverage_details.html',
                             user=current_user,
                             page_title='Coverage Details')
    except Exception as e:
        error_service.log_error("COVERAGE_DETAILS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

@insurance_bp.route('/products/<product_type>')
@login_required
def product_details(product_type):
    """Product-specific drill-down view"""
    try:
        return render_template('insurance/product_details.html',
                             user=current_user,
                             product_type=product_type,
                             page_title=f'{product_type.title()} Insurance Details')
    except Exception as e:
        error_service.log_error("PRODUCT_DETAILS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('insurance.main_dashboard'))

# Module health check
@insurance_bp.route('/api/health')
def health_check():
    """Insurance Services health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Insurance Services",
        "version": "1.0.0",
        "routes_active": 19
    })
