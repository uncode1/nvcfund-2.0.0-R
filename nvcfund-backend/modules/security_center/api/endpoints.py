"""
Security Center API Endpoints
RESTful API for Security Center operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..services import SecurityCenterService

# Create API blueprint
security_center_api_bp = Blueprint('security_center_api', __name__, url_prefix='/api/v1/security-center')

security_service = SecurityCenterService()

@security_center_api_bp.route('/', methods=['GET'])
@login_required
def get_module_info():
    """Get Security Center module information"""
    return jsonify({
        "app_module": "Security Center",
        "version": "1.0.0",
        "endpoints": 12,
        "status": "operational"
    })

@security_center_api_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get security dashboard data"""
    try:
        data = security_service.get_security_dashboard_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/threat-intelligence', methods=['GET'])
@login_required
def get_threat_intelligence():
    """Get threat intelligence data"""
    try:
        data = security_service.get_threat_intelligence_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/intrusion-detection', methods=['GET'])
@login_required
def get_intrusion_detection():
    """Get intrusion detection data"""
    try:
        data = security_service.get_intrusion_detection_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/compliance-monitoring', methods=['GET'])
@login_required
def get_compliance_monitoring():
    """Get compliance monitoring data"""
    try:
        data = security_service.get_compliance_monitoring_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/network-security', methods=['GET'])
@login_required
def get_network_security():
    """Get network security data"""
    try:
        data = security_service.get_network_security_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/vulnerability-assessment', methods=['GET'])
@login_required
def get_vulnerability_assessment():
    """Get vulnerability assessment data"""
    try:
        data = security_service.get_vulnerability_assessment_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/incident-response', methods=['GET'])
@login_required
def get_incident_response():
    """Get incident response data"""
    try:
        data = security_service.get_incident_response_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/incidents', methods=['POST'])
@login_required
def create_incident():
    """Create security incident"""
    try:
        incident_data = request.get_json()
        if not incident_data:
            return jsonify({"success": False, "error": "No incident data provided"}), 400
        
        result = security_service.create_security_incident(current_user.id, incident_data)
        return jsonify(result), 201 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/waf', methods=['GET'])
@login_required
def get_waf_data():
    """Get Web Application Firewall data"""
    try:
        data = security_service.get_waf_data(current_user.id)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/waf/rules', methods=['PUT'])
@login_required
def update_waf_rules():
    """Update WAF rules"""
    try:
        waf_rules = request.get_json()
        if not waf_rules:
            return jsonify({"success": False, "error": "No WAF rules provided"}), 400
        
        result = security_service.update_waf_rules(current_user.id, waf_rules)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/api-keys', methods=['POST'])
@login_required
def generate_api_key():
    """Generate new API key"""
    try:
        result = security_service.generate_api_key(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@security_center_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    return jsonify(security_service.health_check())