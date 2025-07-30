"""
Compliance & Risk API Endpoints
RESTful API for Compliance & Risk operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import compliance_service

# Create API blueprint
compliance_api_bp = Blueprint('compliance_api', __name__, url_prefix='/api/v1/compliance')

@compliance_api_bp.route('/', methods=['GET'])
@login_required
def get_module_info():
    """Get Compliance & Risk module information"""
    return jsonify({
        "app_module": "Compliance & Risk",
        "version": "1.0.0",
        "endpoints": 4,
        "status": "operational"
    })

@compliance_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data"""
    try:
        data = compliance_service.get_dashboard_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@compliance_api_bp.route('/overview', methods=['GET'])
@login_required  
def get_overview_stats():
    """Get overview statistics"""
    try:
        stats = compliance_service.get_overview_stats(current_user.id)
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@compliance_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    return jsonify(compliance_service.health_check())
