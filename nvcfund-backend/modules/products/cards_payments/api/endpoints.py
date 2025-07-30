"""
Cards & Payments API Endpoints
RESTful API for Cards & Payments operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import cards_payments_service

# Create API blueprint
cards_payments_api_bp = Blueprint('cards_payments_api', __name__, url_prefix='/api/v1/cards_payments')

@cards_payments_api_bp.route('/', methods=['GET'])
@login_required
def get_module_info():
    """Get Cards & Payments module information"""
    return jsonify({
        "app_module": "Cards & Payments",
        "version": "1.0.0",
        "endpoints": 4,
        "status": "operational"
    })

@cards_payments_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data"""
    try:
        data = cards_payments_service.get_dashboard_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cards_payments_api_bp.route('/overview', methods=['GET'])
@login_required  
def get_overview_stats():
    """Get overview statistics"""
    try:
        stats = cards_payments_service.get_overview_stats(current_user.id)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cards_payments_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    return jsonify(cards_payments_service.health_check())
