"""
Islamic Banking API Endpoints
RESTful API v1.0 for Sharia-compliant banking operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import IslamicBankingService
from modules.utils.services import ErrorLoggerService
import logging

# Initialize services
islamic_banking_service = IslamicBankingService()
error_logger = ErrorLoggerService()
logger = logging.getLogger(__name__)

# Create API blueprint
islamic_banking_api_bp = Blueprint('islamic_banking_api', __name__, 
                                 url_prefix='/islamic_banking/api')

@islamic_banking_api_bp.route('/health', methods=['GET'])
def health_check():
    """Islamic Banking module health check"""
    return jsonify(islamic_banking_service.health_check())

@islamic_banking_api_bp.route('/overview', methods=['GET'])
@login_required
def get_islamic_banking_overview():
    """Get comprehensive Islamic banking overview"""
    try:
        overview_data = {
            "products": islamic_banking_service.get_islamic_products_overview(),
            "compliance": islamic_banking_service.get_sharia_compliance_dashboard(),
            "profit_sharing": islamic_banking_service.get_profit_loss_sharing_dashboard(),
            "treasury": islamic_banking_service.get_islamic_treasury_operations()
        }
        return jsonify({
            "status": "success",
            "data": overview_data,
            "timestamp": islamic_banking_service.health_check()["timestamp"]
        })
    except Exception as e:
        error_logger.log_error("api_islamic_overview_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Islamic banking overview"
        }), 500

@islamic_banking_api_bp.route('/products', methods=['GET'])
@login_required
def get_islamic_products():
    """Get Islamic banking products"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        return jsonify({
            "status": "success",
            "data": products_data
        })
    except Exception as e:
        error_logger.log_error("api_islamic_products_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Islamic products"
        }), 500

@islamic_banking_api_bp.route('/products/murabaha', methods=['GET'])
@login_required
def get_murabaha_details():
    """Get Murabaha financing details"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        murabaha_data = products_data['financing_products']['murabaha']
        return jsonify({
            "status": "success",
            "data": murabaha_data
        })
    except Exception as e:
        error_logger.log_error("api_murabaha_details_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Murabaha details"
        }), 500

@islamic_banking_api_bp.route('/products/ijara', methods=['GET'])
@login_required
def get_ijara_details():
    """Get Ijara leasing details"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        ijara_data = products_data['financing_products']['ijara']
        return jsonify({
            "status": "success",
            "data": ijara_data
        })
    except Exception as e:
        error_logger.log_error("api_ijara_details_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Ijara details"
        }), 500

@islamic_banking_api_bp.route('/products/sukuk', methods=['GET'])
@login_required
def get_sukuk_details():
    """Get Sukuk (Islamic bonds) details"""
    try:
        products_data = islamic_banking_service.get_islamic_products_overview()
        sukuk_data = products_data['investment_products']['sukuk']
        return jsonify({
            "status": "success",
            "data": sukuk_data
        })
    except Exception as e:
        error_logger.log_error("api_sukuk_details_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Sukuk details"
        }), 500

@islamic_banking_api_bp.route('/compliance', methods=['GET'])
@login_required
def get_sharia_compliance():
    """Get Sharia compliance status and metrics"""
    try:
        compliance_data = islamic_banking_service.get_sharia_compliance_dashboard()
        return jsonify({
            "status": "success",
            "data": compliance_data
        })
    except Exception as e:
        error_logger.log_error("api_sharia_compliance_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve compliance data"
        }), 500

@islamic_banking_api_bp.route('/halal-screening', methods=['GET'])
@login_required
def get_halal_screening():
    """Get halal investment screening data"""
    try:
        screening_data = islamic_banking_service.get_halal_investment_screening()
        return jsonify({
            "status": "success",
            "data": screening_data
        })
    except Exception as e:
        error_logger.log_error("api_halal_screening_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve halal screening data"
        }), 500

@islamic_banking_api_bp.route('/treasury', methods=['GET'])
@login_required
def get_islamic_treasury():
    """Get Islamic treasury operations data"""
    try:
        treasury_data = islamic_banking_service.get_islamic_treasury_operations()
        return jsonify({
            "status": "success",
            "data": treasury_data
        })
    except Exception as e:
        error_logger.log_error("api_islamic_treasury_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve treasury data"
        }), 500

@islamic_banking_api_bp.route('/zakat', methods=['GET'])
@login_required
def get_zakat_calculation():
    """Get Zakat calculation and distribution data"""
    try:
        zakat_data = islamic_banking_service.get_zakat_calculation_service()
        return jsonify({
            "status": "success",
            "data": zakat_data
        })
    except Exception as e:
        error_logger.log_error("api_zakat_calculation_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve Zakat data"
        }), 500

@islamic_banking_api_bp.route('/profit-sharing', methods=['GET'])
@login_required
def get_profit_sharing():
    """Get profit and loss sharing data"""
    try:
        pls_data = islamic_banking_service.get_profit_loss_sharing_dashboard()
        return jsonify({
            "status": "success",
            "data": pls_data
        })
    except Exception as e:
        error_logger.log_error("api_profit_sharing_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve profit sharing data"
        }), 500

# Transaction endpoints
@islamic_banking_api_bp.route('/transactions/murabaha', methods=['POST'])
@login_required
def create_murabaha_application():
    """Create new Murabaha financing application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'purpose', 'asset_details']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Process Murabaha application
        application_result = {
            "application_id": f"MUR-{current_user.id}-{hash(str(data))%10000:04d}",
            "customer_id": current_user.id,
            "status": "pending_sharia_review",
            "amount": data['amount'],
            "purpose": data['purpose'],
            "asset_details": data['asset_details'],
            "profit_rate": 4.85,
            "tenor_months": data.get('tenor_months', 12),
            "sharia_compliance_status": "under_review",
            "estimated_monthly_payment": (data['amount'] * 1.0485) / data.get('tenor_months', 12),
            "next_steps": [
                "Sharia board review",
                "Asset valuation and verification", 
                "Customer creditworthiness assessment",
                "Final approval and documentation"
            ],
            "review_timeline": "5-7 business days"
        }
        
        return jsonify({
            "status": "success",
            "data": application_result
        })
        
    except Exception as e:
        error_logger.log_error("api_murabaha_application_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to process Murabaha application"
        }), 500

@islamic_banking_api_bp.route('/transactions/sukuk', methods=['POST'])
@login_required
def create_sukuk_investment():
    """Create new Sukuk investment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sukuk_id', 'investment_amount']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Process Sukuk investment
        investment_result = {
            "investment_id": f"SUK-{current_user.id}-{hash(str(data))%10000:04d}",
            "investor_id": current_user.id,
            "sukuk_id": data['sukuk_id'],
            "investment_amount": data['investment_amount'],
            "sukuk_type": "Ijara Sukuk",
            "expected_annual_yield": 4.25,
            "maturity_date": "2027-07-03",
            "profit_distribution": "Semi-annual",
            "sharia_certification": "AAOIFI Certified",
            "status": "confirmed",
            "settlement_date": "2025-07-05",
            "investment_details": {
                "underlying_assets": "Commercial real estate portfolio",
                "risk_rating": "A+",
                "minimum_investment": 10000,
                "liquidity": "Secondary market available"
            }
        }
        
        return jsonify({
            "status": "success", 
            "data": investment_result
        })
        
    except Exception as e:
        error_logger.log_error("api_sukuk_investment_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to process Sukuk investment"
        }), 500

@islamic_banking_api_bp.route('/transactions/ijara', methods=['POST'])
@login_required
def create_ijara_lease():
    """Create new Ijara lease arrangement"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['asset_type', 'asset_value', 'lease_term']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Process Ijara lease
        lease_result = {
            "lease_id": f"IJR-{current_user.id}-{hash(str(data))%10000:04d}",
            "lessee_id": current_user.id,
            "asset_type": data['asset_type'],
            "asset_value": data['asset_value'],
            "lease_term_months": data['lease_term'],
            "monthly_rental": data['asset_value'] * 0.052 / 12,  # 5.2% annual rental yield
            "security_deposit": data['asset_value'] * 0.1,  # 10% security deposit
            "purchase_option": data.get('purchase_option', True),
            "sharia_compliance": "AAOIFI Standard 9 compliant",
            "status": "pending_approval",
            "lease_structure": {
                "ownership": "Bank owns asset during lease term",
                "maintenance": "Lessee responsibility",
                "insurance": "Lessee responsibility", 
                "end_of_lease": "Purchase option available"
            }
        }
        
        return jsonify({
            "status": "success",
            "data": lease_result
        })
        
    except Exception as e:
        error_logger.log_error("api_ijara_lease_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to process Ijara lease"
        }), 500

@islamic_banking_api_bp.route('/screening/stock/<symbol>', methods=['GET'])
@login_required
def get_stock_screening(symbol):
    """Get Sharia compliance screening for a specific stock"""
    try:
        # Mock screening result for demonstration
        screening_result = {
            "symbol": symbol.upper(),
            "company_name": f"Sample Company {symbol.upper()}",
            "sharia_compliance": {
                "status": "compliant",
                "compliance_score": 85.5,
                "screening_date": "2025-07-03"
            },
            "financial_ratios": {
                "debt_to_market_cap": 28.5,
                "cash_to_market_cap": 15.2,
                "non_halal_income_ratio": 2.1
            },
            "business_screening": {
                "primary_business": "Technology Services",
                "prohibited_activities": [],
                "business_compliance": True
            },
            "recommendation": "Approved for Islamic investment"
        }
        
        return jsonify({
            "status": "success",
            "data": screening_result
        })
        
    except Exception as e:
        error_logger.log_error("api_stock_screening_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve stock screening"
        }), 500