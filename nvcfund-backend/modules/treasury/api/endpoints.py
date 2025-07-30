"""
Treasury Operations API Endpoints
RESTful API for Treasury Operations operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import treasury_service

# Create API blueprint
treasury_api_bp = Blueprint('treasury_api', __name__, url_prefix='/api/v1/treasury')

@treasury_api_bp.route('/', methods=['GET'])
@login_required
def get_module_info():
    """Get Treasury Operations module information"""
    return jsonify({
        "app_module": "Treasury Operations",
        "version": "1.0.0",
        "endpoints": 4,
        "status": "operational"
    })

@treasury_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data"""
    try:
        data = treasury_service.get_dashboard_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@treasury_api_bp.route('/overview', methods=['GET'])
@login_required  
def get_overview_stats():
    """Get overview statistics"""
    try:
        stats = treasury_service.get_overview_stats(current_user.id)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@treasury_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    return jsonify(treasury_service.health_check())
