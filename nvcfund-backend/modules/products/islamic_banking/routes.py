"""
Islamic Banking Routes
Comprehensive Sharia-compliant banking endpoints and interfaces
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import IslamicBankingService
from modules.utils.services import ErrorLoggerService
import logging

# Initialize services
islamic_banking_service = IslamicBankingService()
error_logger = ErrorLoggerService()
logger = logging.getLogger(__name__)

# Create blueprint with hyphenated URL for professional banking appearance
islamic_banking_bp = Blueprint('islamic_banking', __name__, 
                              url_prefix='/islamic-banking',
                              template_folder='templates',
                              static_folder='static')

# Create legacy redirect blueprint for underscore URL
islamic_banking_legacy_bp = Blueprint('islamic_banking_legacy', __name__, 
                              url_prefix='/islamic_banking',
                              template_folder='templates',
                              static_folder='static')

# Create legacy redirect blueprint for hyphenated URL
islamic_banking_hyphen_bp = Blueprint('islamic_banking_hyphen', __name__, 
                              url_prefix='/islamic-banking',
                              template_folder='templates',
                              static_folder='static')

@islamic_banking_bp.route('/')
@islamic_banking_hyphen_bp.route('/')
@login_required
def main_dashboard():
    """Islamic Banking main dashboard"""
    try:
        # Get comprehensive Islamic banking data
        products_data = islamic_banking_service.get_islamic_products_overview()
        compliance_data = islamic_banking_service.get_sharia_compliance_dashboard()
        
        return render_template('islamic_banking/islamic_banking_dashboard.html',
                             products_data=products_data,
                             compliance_data=compliance_data)
    except Exception as e:
        error_logger.log_error("islamic_banking_dashboard_error", str(e))
        flash("Unable to load Islamic banking dashboard", "error")
        return redirect(url_for('public.index'))

@islamic_banking_bp.route('/products')
@login_required
def islamic_products():
    """Islamic banking products overview"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        
        return render_template('islamic_banking/islamic_products.html',
                             products_data=products_data)
    except Exception as e:
        error_logger.log_error("islamic_products_error", str(e))
        flash("Unable to load Islamic products", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/murabaha')
@login_required
def murabaha_financing():
    """Murabaha financing management"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        murabaha_data = products_data['financing_products']['murabaha']
        
        return render_template('islamic_banking/islamic_murabaha.html',
                             murabaha_data=murabaha_data)
    except Exception as e:
        error_logger.log_error("murabaha_financing_error", str(e))
        flash("Unable to load Murabaha financing", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/sharia-compliance')
@login_required
def sharia_compliance():
    """Sharia compliance monitoring dashboard"""
    try:
        compliance_data = islamic_banking_service.get_sharia_compliance_dashboard()
        
        return render_template('islamic_banking/sharia_compliance.html',
                             compliance_data=compliance_data,
                             user=current_user,
                             page_title='Sharia Compliance')
    except Exception as e:
        error_logger.log_error("sharia_compliance_error", str(e))
        flash("Unable to load Sharia compliance dashboard", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/ijara')
@login_required
def ijara_leasing():
    """Ijara leasing management"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        ijara_data = products_data['financing_products']['ijara']
        
        return render_template('islamic_banking/islamic_ijara.html',
                             ijara_data=ijara_data)
    except Exception as e:
        error_logger.log_error("ijara_leasing_error", str(e))
        flash("Unable to load Ijara leasing", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/sukuk')
@login_required
def sukuk_management():
    """Sukuk (Islamic bonds) management"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        sukuk_data = products_data['investment_products']['sukuk']
        
        return render_template('islamic_banking/islamic_sukuk.html',
                             sukuk_data=sukuk_data)
    except Exception as e:
        error_logger.log_error("sukuk_management_error", str(e))
        flash("Unable to load Sukuk management", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/profit_sharing')
@login_required
def profit_sharing():
    """Profit and loss sharing dashboard"""
    try:
        pls_data = islamic_banking_service.get_profit_loss_sharing_dashboard()
        
        return render_template('islamic_banking/islamic_profit_sharing.html',
                             pls_data=pls_data)
    except Exception as e:
        error_logger.log_error("profit_sharing_error", str(e))
        flash("Unable to load profit sharing dashboard", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/halal_investments')
@login_required
def halal_investments():
    """Halal investment screening and portfolio management"""
    try:
        investment_data = islamic_banking_service.get_halal_investment_screening()
        
        return render_template('islamic_banking/islamic_halal_investments.html',
                             investment_data=investment_data)
    except Exception as e:
        error_logger.log_error("halal_investments_error", str(e))
        flash("Unable to load halal investments", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/treasury')
@login_required
def islamic_treasury():
    """Islamic treasury operations"""
    try:
        treasury_data = islamic_banking_service.get_islamic_treasury_operations()
        
        return render_template('islamic_banking/islamic_treasury.html',
                             treasury_data=treasury_data)
    except Exception as e:
        error_logger.log_error("islamic_treasury_error", str(e))
        flash("Unable to load Islamic treasury", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

@islamic_banking_bp.route('/zakat')
@login_required
def zakat_management():
    """Zakat calculation and distribution management"""
    try:
        zakat_data = islamic_banking_service.get_zakat_calculation_service()
        
        return render_template('islamic_banking/islamic_zakat.html',
                             zakat_data=zakat_data)
    except Exception as e:
        error_logger.log_error("zakat_management_error", str(e))
        flash("Unable to load Zakat management", "error")
        return redirect(url_for('islamic_banking.main_dashboard'))

# API Routes for data access
@islamic_banking_bp.route('/api/overview')
@login_required
def api_islamic_overview():
    """API endpoint for Islamic banking overview"""
    try:
        overview_data = {
            "products": islamic_banking_service.get_islamic_products_overview(),
            "compliance": islamic_banking_service.get_sharia_compliance_dashboard(),
            "profit_sharing": islamic_banking_service.get_profit_loss_sharing_dashboard()
        }
        return jsonify(overview_data)
    except Exception as e:
        error_logger.log_error("api_islamic_overview_error", str(e))
        return jsonify({"error": "Unable to retrieve Islamic banking overview"}), 500

@islamic_banking_bp.route('/api/products')
@login_required
def api_islamic_products():
    """API endpoint for Islamic banking products"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        return jsonify(products_data)
    except Exception as e:
        error_logger.log_error("api_islamic_products_error", str(e))
        return jsonify({"error": "Unable to retrieve Islamic products"}), 500

@islamic_banking_bp.route('/api/compliance')
@login_required
def api_sharia_compliance():
    """API endpoint for Sharia compliance data"""
    try:
        compliance_data = islamic_banking_service.get_sharia_compliance_dashboard()
        return jsonify(compliance_data)
    except Exception as e:
        error_logger.log_error("api_sharia_compliance_error", str(e))
        return jsonify({"error": "Unable to retrieve compliance data"}), 500

@islamic_banking_bp.route('/api/halal_screening')
@login_required
def api_halal_screening():
    """API endpoint for halal investment screening"""
    try:
        screening_data = islamic_banking_service.get_halal_investment_screening()
        return jsonify(screening_data)
    except Exception as e:
        error_logger.log_error("api_halal_screening_error", str(e))
        return jsonify({"error": "Unable to retrieve halal screening data"}), 500

@islamic_banking_bp.route('/api/treasury')
@login_required
def api_islamic_treasury():
    """API endpoint for Islamic treasury operations"""
    try:
        treasury_data = islamic_banking_service.get_islamic_treasury_operations()
        return jsonify(treasury_data)
    except Exception as e:
        error_logger.log_error("api_islamic_treasury_error", str(e))
        return jsonify({"error": "Unable to retrieve treasury data"}), 500

@islamic_banking_bp.route('/api/zakat')
@login_required
def api_zakat():
    """API endpoint for Zakat calculation and distribution"""
    try:
        zakat_data = islamic_banking_service.get_zakat_calculation_service()
        return jsonify(zakat_data)
    except Exception as e:
        error_logger.log_error("api_zakat_error", str(e))
        return jsonify({"error": "Unable to retrieve Zakat data"}), 500

# Transaction endpoints
@islamic_banking_bp.route('/api/murabaha/apply', methods=['POST'])
@login_required
def api_apply_murabaha():
    """API endpoint to apply for Murabaha financing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'purpose', 'asset_details', 'customer_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Process Murabaha application
        application_result = {
            "application_id": f"MUR-{current_user.id}-{hash(str(data))%10000:04d}",
            "status": "pending_sharia_review",
            "amount": data['amount'],
            "profit_rate": 4.85,
            "tenor": data.get('tenor', 12),
            "sharia_compliance": "under_review",
            "next_steps": [
                "Sharia board review",
                "Asset valuation",
                "Customer due diligence",
                "Final approval"
            ]
        }
        
        return jsonify(application_result)
    except Exception as e:
        error_logger.log_error("api_murabaha_apply_error", str(e))
        return jsonify({"error": "Unable to process Murabaha application"}), 500

@islamic_banking_bp.route('/api/sukuk/invest', methods=['POST'])
@login_required
def api_invest_sukuk():
    """API endpoint to invest in Sukuk"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sukuk_id', 'investment_amount', 'investor_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Process Sukuk investment
        investment_result = {
            "investment_id": f"SUK-{current_user.id}-{hash(str(data))%10000:04d}",
            "sukuk_id": data['sukuk_id'],
            "investment_amount": data['investment_amount'],
            "expected_yield": 4.25,
            "maturity_date": "2027-07-03",
            "sharia_certification": "AAOIFI_certified",
            "status": "confirmed",
            "settlement_date": "2025-07-05"
        }
        
        return jsonify(investment_result)
    except Exception as e:
        error_logger.log_error("api_sukuk_invest_error", str(e))
        return jsonify({"error": "Unable to process Sukuk investment"}), 500

# Missing route referenced in templates
@islamic_banking_bp.route('/static')
@login_required
def static():
    """Static resources for Islamic banking - redirect to main dashboard"""
    return redirect(url_for('islamic_banking.main_dashboard'))