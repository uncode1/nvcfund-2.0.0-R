"""
Treasury Operations Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from ..core.form_decorators import treasury_form, process_form, require_post_data
from ..core.form_processor import form_processor

# Create module blueprint
treasury_bp = Blueprint('treasury', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/treasury')

# Initialize services
error_service = ErrorLoggerService()

@treasury_bp.route('/')
@login_required
def main_dashboard():
    """Treasury Operations main dashboard"""
    try:
        return render_template('treasury/treasury_dashboard.html',
                             user=current_user,
                             page_title='Treasury Operations Dashboard')
    except Exception as e:
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/dashboard')
@treasury_bp.route('/overview')
@login_required  
def overview():
    """Treasury Operations overview page"""
    try:
        return render_template('treasury/treasury_overview.html',
                             user=current_user,
                             page_title='Treasury Operations Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/cash-management')
@login_required
def cash_management():
    """Cash management and liquidity overview"""
    try:
        return render_template('treasury/treasury_overview.html',
                             user=current_user,
                             page_title='Cash Management')
    except Exception as e:
        error_service.log_error("CASH_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/securities')
@login_required
def securities():
    """Government securities portfolio"""
    try:
        return render_template('treasury/treasury_overview.html',
                             user=current_user,
                             page_title='Government Securities')
    except Exception as e:
        error_service.log_error("SECURITIES_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/cash-flow')
@login_required
def cash_flow():
    """Cash flow management and forecasting"""
    try:
        return render_template('treasury/cash_flow.html',
                             user=current_user,
                             page_title='Cash Flow Management')
    except Exception as e:
        error_service.log_error("CASH_FLOW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/alm')
@login_required
def asset_liability_management():
    """Asset Liability Management dashboard"""
    try:
        return render_template('treasury/alm_dashboard.html',
                             user=current_user,
                             page_title='Asset Liability Management')
    except Exception as e:
        error_service.log_error("ALM_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/money-market')
@login_required
def money_market():
    """Money market operations"""
    try:
        return render_template('treasury/money_market.html',
                             user=current_user,
                             page_title='Money Market Operations')
    except Exception as e:
        error_service.log_error("MONEY_MARKET_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/fx-operations')
@login_required
def fx_operations():
    """Foreign exchange operations"""
    try:
        return render_template('treasury/fx_operations.html',
                             user=current_user,
                             page_title='Foreign Exchange Operations')
    except Exception as e:
        error_service.log_error("FX_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/risk-management')
@login_required
def risk_management():
    """Treasury risk management dashboard"""
    try:
        return render_template('treasury/risk_management.html',
                             user=current_user,
                             page_title='Treasury Risk Management')
    except Exception as e:
        error_service.log_error("RISK_MGMT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@treasury_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@treasury_form('treasury_settings')
def settings():
    """Treasury Operations settings page with form processing"""
    try:
        if request.method == 'POST':
            # Form processing is handled by the decorator
            flash('Treasury settings updated successfully', 'success')
            return redirect(url_for('treasury.settings'))
        
        return render_template('treasury/treasury_settings.html',
                             user=current_user,
                             page_title='Treasury Operations Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

# Drill-down routes for detailed views
@treasury_bp.route('/cash-flow/analysis')
@login_required
def cash_flow_analysis():
    """Cash flow analysis drill-down view"""
    try:
        return render_template('treasury/cash_flow_analysis.html',
                             user=current_user,
                             page_title='Cash Flow Analysis')
    except Exception as e:
        error_service.log_error("CASH_FLOW_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

@treasury_bp.route('/liquidity/management')
@login_required
def liquidity_management():
    """Liquidity management drill-down view"""
    try:
        return render_template('treasury/liquidity_management.html',
                             user=current_user,
                             page_title='Liquidity Management')
    except Exception as e:
        error_service.log_error("LIQUIDITY_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

@treasury_bp.route('/investment/portfolio')
@login_required
def investment_portfolio():
    """Investment portfolio drill-down view"""
    try:
        return render_template('treasury/investment_portfolio.html',
                             user=current_user,
                             page_title='Investment Portfolio')
    except Exception as e:
        error_service.log_error("INVESTMENT_PORTFOLIO_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

@treasury_bp.route('/risk/assessment')
@login_required
def risk_assessment():
    """Risk assessment drill-down view"""
    try:
        return render_template('treasury/risk_assessment.html',
                             user=current_user,
                             page_title='Risk Assessment')
    except Exception as e:
        error_service.log_error("RISK_ASSESSMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

# Missing routes referenced in templates
@treasury_bp.route('/treasury-overview')
@login_required
def treasury_overview():
    """Treasury overview dashboard"""
    try:
        overview_data = {
            'total_assets': 45670000000.00,
            'liquid_assets': 12500000000.00,
            'investment_portfolio': 25000000000.00,
            'cash_reserves': 8170000000.00,
            'asset_allocation': [
                {'type': 'Government Bonds', 'amount': 20000000000.00, 'percentage': 44},
                {'type': 'Corporate Bonds', 'amount': 15000000000.00, 'percentage': 33},
                {'type': 'Cash Equivalents', 'amount': 10670000000.00, 'percentage': 23}
            ]
        }
        return render_template('treasury/treasury_overview.html',
                             overview_data=overview_data,
                             page_title='Treasury Overview')
    except Exception as e:
        error_service.log_error("TREASURY_OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

@treasury_bp.route('/interest-rate-management')
@login_required
def interest_rate_management():
    """Interest rate management dashboard"""
    try:
        rate_data = {
            'current_base_rate': 5.25,
            'fed_funds_rate': 5.50,
            'prime_rate': 8.50,
            'treasury_yield_10y': 4.25,
            'rate_changes': [
                {'date': '2025-01-10', 'rate': 5.25, 'change': 0.25, 'direction': 'up'},
                {'date': '2024-12-15', 'rate': 5.00, 'change': 0.25, 'direction': 'up'},
                {'date': '2024-11-10', 'rate': 4.75, 'change': 0.00, 'direction': 'stable'}
            ]
        }
        return render_template('treasury/interest_rate_management.html',
                             rate_data=rate_data,
                             page_title='Interest Rate Management')
    except Exception as e:
        error_service.log_error("INTEREST_RATE_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('treasury.main_dashboard'))

# Module health check
@treasury_bp.route('/api/health')
def health_check():
    """Treasury Operations health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Treasury Operations",
        "version": "1.0.0",
        "routes_active": 29
    })
