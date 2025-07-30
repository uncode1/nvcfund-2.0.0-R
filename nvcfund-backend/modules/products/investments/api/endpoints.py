"""
Investment Services API Endpoints
RESTful API for Investment Services operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import investments_service

# Create API blueprint
investments_api_bp = Blueprint('investments_api', __name__, url_prefix='/api/v1/investments')

@investments_api_bp.route('/', methods=['GET'])
@login_required
def get_module_info():
    """Get Investment Services module information"""
    return jsonify({
        "app_module": "Investment Services",
        "version": "1.0.0",
        "endpoints": 4,
        "status": "operational"
    })

@investments_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data"""
    try:
        data = investments_service.get_dashboard_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@investments_api_bp.route('/overview', methods=['GET'])
@login_required  
def get_overview_stats():
    """Get overview statistics"""
    try:
        stats = investments_service.get_overview_stats(current_user.id)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@investments_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    return jsonify(investments_service.health_check())
