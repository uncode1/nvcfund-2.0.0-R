"""
Interest Rate Management API Endpoints
RESTful API v1.0 for comprehensive interest rate management
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import InterestRateManagementService
from modules.utils.services import ErrorLoggerService
import logging

# Initialize services
rate_service = InterestRateManagementService()
error_logger = ErrorLoggerService()
logger = logging.getLogger(__name__)

# Create API blueprint
interest_rate_management_api_bp = Blueprint('interest_rate_management_api', __name__, 
                                          url_prefix='/interest_rate_management/api')

@interest_rate_management_api_bp.route('/health', methods=['GET'])
def health_check():
    """Interest Rate Management module health check"""
    return jsonify(rate_service.health_check())

@interest_rate_management_api_bp.route('/rates/overview', methods=['GET'])
@login_required
def get_rates_overview():
    """Get comprehensive rates overview"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges for rate management"}), 403
        
        overview_data = {
            "central_bank_rates": rate_service.get_central_bank_rates(),
            "lending_rates": rate_service.get_lending_rates_structure(),
            "deposit_rates": rate_service.get_deposit_rates_structure(),
            "rate_authority": rate_service.get_rate_setting_authority()
        }
        
        return jsonify({
            "status": "success",
            "data": overview_data,
            "timestamp": rate_service.health_check()["timestamp"]
        })
    except Exception as e:
        error_logger.log_error("api_rates_overview_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve rates overview"
        }), 500

@interest_rate_management_api_bp.route('/rates/central-bank', methods=['GET'])
@login_required
def get_central_bank_rates():
    """Get central bank rates and benchmarks"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        central_bank_data = rate_service.get_central_bank_rates()
        return jsonify({
            "status": "success",
            "data": central_bank_data
        })
    except Exception as e:
        error_logger.log_error("api_central_bank_rates_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve central bank rates"
        }), 500

@interest_rate_management_api_bp.route('/rates/lending', methods=['GET'])
@login_required
def get_lending_rates():
    """Get lending rates structure"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        lending_data = rate_service.get_lending_rates_structure()
        return jsonify({
            "status": "success",
            "data": lending_data
        })
    except Exception as e:
        error_logger.log_error("api_lending_rates_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve lending rates"
        }), 500

@interest_rate_management_api_bp.route('/rates/deposits', methods=['GET'])
@login_required
def get_deposit_rates():
    """Get deposit rates structure"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        deposit_data = rate_service.get_deposit_rates_structure()
        return jsonify({
            "status": "success",
            "data": deposit_data
        })
    except Exception as e:
        error_logger.log_error("api_deposit_rates_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve deposit rates"
        }), 500

@interest_rate_management_api_bp.route('/rates/authority', methods=['GET'])
@login_required
def get_rate_authority():
    """Get rate setting authority and approval hierarchy"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        authority_data = rate_service.get_rate_setting_authority()
        return jsonify({
            "status": "success",
            "data": authority_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_authority_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve authority data"
        }), 500

@interest_rate_management_api_bp.route('/rates/algorithms', methods=['GET'])
@login_required
def get_rate_algorithms():
    """Get rate adjustment algorithms"""
    try:
        if not _has_senior_rate_authority(current_user):
            return jsonify({"error": "Senior authorization required"}), 403
        
        algorithms_data = rate_service.get_rate_adjustment_algorithms()
        return jsonify({
            "status": "success",
            "data": algorithms_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_algorithms_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve algorithms"
        }), 500

@interest_rate_management_api_bp.route('/rates/history', methods=['GET'])
@login_required
def get_rate_history():
    """Get historical rate data and trends"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        historical_data = rate_service.get_historical_rate_data()
        return jsonify({
            "status": "success",
            "data": historical_data
        })
    except Exception as e:
        error_logger.log_error("api_rate_history_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to retrieve rate history"
        }), 500

# Rate management operations
@interest_rate_management_api_bp.route('/rates/update', methods=['POST'])
@login_required
def update_rates():
    """Update interest rates with proper authorization"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges for rate updates"}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_category', 'rate_changes']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Apply rate changes
        result = rate_service.apply_rate_change(
            product_category=data['product_category'],
            rate_changes=data['rate_changes'],
            authorized_by=current_user.username,
            effective_date=data.get('effective_date')
        )
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    except Exception as e:
        error_logger.log_error("api_update_rates_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to process rate update"
        }), 500

@interest_rate_management_api_bp.route('/rates/propose', methods=['POST'])
@login_required
def propose_rate_change():
    """Propose a rate change for approval workflow"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        data = request.get_json()
        
        # Validate proposal data
        required_fields = ['product_category', 'proposed_rates', 'justification']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Create rate change proposal
        proposal_id = f"PROP-{current_user.id}-{hash(str(data))%10000:04d}"
        
        proposal_result = {
            "proposal_id": proposal_id,
            "proposer": current_user.username,
            "status": "pending_approval",
            "product_category": data['product_category'],
            "proposed_rates": data['proposed_rates'],
            "justification": data['justification'],
            "effective_date": data.get('effective_date'),
            "required_approvals": _get_required_approvals(data['product_category']),
            "submission_timestamp": rate_service.health_check()["timestamp"],
            "next_steps": [
                "Rate committee review",
                "Impact analysis",
                "Competitive assessment",
                "Final authorization"
            ]
        }
        
        return jsonify({
            "status": "success",
            "data": proposal_result
        })
        
    except Exception as e:
        error_logger.log_error("api_propose_rate_change_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to submit rate proposal"
        }), 500

@interest_rate_management_api_bp.route('/rates/calculator', methods=['POST'])
@login_required
def rate_calculator():
    """Calculate impact of rate changes"""
    try:
        if not _has_rate_authority(current_user):
            return jsonify({"error": "Insufficient privileges"}), 403
        
        data = request.get_json()
        
        # Validate calculator input
        required_fields = ['product_type', 'current_rate', 'proposed_rate', 'portfolio_amount']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "error": "Missing required fields",
                "required": required_fields
            }), 400
        
        # Calculate rate change impact
        rate_change = data['proposed_rate'] - data['current_rate']
        portfolio_amount = data['portfolio_amount']
        
        calculation_result = {
            "product_type": data['product_type'],
            "current_rate": data['current_rate'],
            "proposed_rate": data['proposed_rate'],
            "rate_change": rate_change,
            "portfolio_amount": portfolio_amount,
            "impact_analysis": {
                "annual_revenue_impact": rate_change * portfolio_amount * 10000,  # basis points calculation
                "monthly_impact": (rate_change * portfolio_amount * 10000) / 12,
                "break_even_volume_change": abs(rate_change) * 0.15,  # 15% rule of thumb
                "customer_impact": {
                    "typical_account_change": rate_change * 100,  # $100 balance example
                    "impact_direction": "positive" if rate_change > 0 else "negative"
                }
            },
            "recommendations": {
                "implementation_timeline": "30 days notice recommended",
                "competitive_monitoring": "Monitor peer responses",
                "customer_communication": "Proactive notification advised"
            }
        }
        
        return jsonify({
            "status": "success",
            "data": calculation_result
        })
        
    except Exception as e:
        error_logger.log_error("api_rate_calculator_error", str(e))
        return jsonify({
            "status": "error",
            "error": "Unable to calculate rate impact"
        }), 500

# Utility functions
def _has_rate_authority(user) -> bool:
    """Check if user has basic rate management authority"""
    authorized_roles = [
        'treasury_officer', 'asset_liability_manager', 'chief_financial_officer',
        'board_of_directors', 'monetary_policy_committee', 'admin', 'super_admin'
    ]
    return hasattr(user, 'role') and user.role in authorized_roles

def _has_senior_rate_authority(user) -> bool:
    """Check if user has senior rate management authority"""
    senior_roles = [
        'chief_financial_officer', 'board_of_directors', 
        'monetary_policy_committee', 'admin', 'super_admin'
    ]
    return hasattr(user, 'role') and user.role in senior_roles

def _get_required_approvals(product_category: str) -> list:
    """Get required approval roles for product category"""
    approval_matrix = {
        'consumer_deposits': ['treasury_officer', 'asset_liability_manager'],
        'consumer_lending': ['chief_financial_officer', 'asset_liability_committee'],
        'commercial_lending': ['board_of_directors', 'monetary_policy_committee'],
        'institutional_lending': ['board_of_directors', 'federal_reserve_approval']
    }
    return approval_matrix.get(product_category, ['chief_financial_officer'])