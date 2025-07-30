"""
Security Center Module Routes
Web interface routes for security monitoring and management
"""

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import logging

from modules.core.decorators import admin_required
from .services import SecurityCenterService

logger = logging.getLogger(__name__)

# Create blueprint for web interface routes
security_center_bp = Blueprint('security_center', __name__,
                              url_prefix='/security-center',
                              template_folder='templates')

security_service = SecurityCenterService()

# Dashboard Routes
@security_center_bp.route('/dashboard')
@login_required
@admin_required
def security_dashboard():
    """Main security center dashboard with real-time threat monitoring"""
    try:
        security_data = security_service.get_security_dashboard_data(current_user.id)
        
        logger.info(f"Security dashboard accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_DASHBOARD_ACCESS',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/security_dashboard.html', 
                             security_data=security_data)
        
    except Exception as e:
        logger.error(f"Security dashboard error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading security dashboard', 'error')
        return redirect(url_for('public.index'))

@security_center_bp.route('/')
@login_required
@admin_required
def security_dashboard_new():
    """Security center main dashboard"""
    return security_dashboard()

# Monitoring Routes
@security_center_bp.route('/threat-monitoring')
@login_required
@admin_required  
def threat_monitoring():
    """Threat monitoring dashboard"""
    try:
        threat_data = security_service.get_detailed_threats_data(current_user.id)
        return render_template('security_center/threat_monitoring.html', 
                             threat_data=threat_data)
    except Exception as e:
        logger.error(f"Threat monitoring error: {e}")
        flash('Error loading threat monitoring', 'error')
        return redirect(url_for('public.index'))

@security_center_bp.route('/incident-response')
@login_required
@admin_required
def incident_response_dropdown():
    """Incident response dashboard"""
    try:
        incident_data = security_service.get_incidents_management_data(current_user.id)
        return render_template('security_center/incident_response.html', 
                             incident_data=incident_data)
    except Exception as e:
        logger.error(f"Incident response error: {e}")
        flash('Error loading incident response', 'error')
        return redirect(url_for('public.index'))

@security_center_bp.route('/investigation')
@login_required
@admin_required
def investigation_tools():
    """Security investigation tools"""
    try:
        investigation_data = {
            'active_investigations': 2,
            'pending_cases': 5,
            'completed_cases': 18
        }
        return render_template('security_center/investigation_tools.html', 
                             investigation_data=investigation_data)
    except Exception as e:
        logger.error(f"Investigation tools error: {e}")
        flash('Error loading investigation tools', 'error')
        return redirect(url_for('public.index'))

# API Endpoints for Real-time Updates

@security_center_bp.route('/api/dashboard')
@login_required
@admin_required

def api_security_dashboard():
    """Get security dashboard data via API for real-time updates"""
    try:
        dashboard_data = security_service.get_security_dashboard_data(current_user.id)
        
        logger.info(f"Security dashboard API accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_DASHBOARD_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': dashboard_data})
        
    except Exception as e:
        logger.error(f"Security dashboard API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load security dashboard'}), 500

# Granular Drill-down Routes

@security_center_bp.route('/threats/detailed-analysis')
@login_required
@admin_required

def threats_detailed_analysis():
    """Detailed threat analysis with real-time intelligence"""
    try:
        threats_data = security_service.get_detailed_threats_data(current_user.id)
        
        logger.info(f"Threats detailed analysis accessed", extra={
            'user_id': current_user.id,
            'action': 'THREATS_DETAILED_ANALYSIS',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/threat_monitoring.html', 
                             threats_data=threats_data)
        
    except Exception as e:
        logger.error(f"Threats analysis error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading threat analysis', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/incidents/management')
@login_required
@admin_required

def incidents_management():
    """Security incidents management with response workflows"""
    try:
        incidents_data = security_service.get_incidents_management_data(current_user.id)
        
        logger.info(f"Incidents management accessed", extra={
            'user_id': current_user.id,
            'action': 'INCIDENTS_MANAGEMENT',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/incident_response.html', 
                             incidents_data=incidents_data)
        
    except Exception as e:
        logger.error(f"Incidents management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading incidents management', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/blocked-attacks/analysis')
@login_required
@admin_required

def blocked_attacks_analysis():
    """Blocked attacks analysis with attack vectors and patterns"""
    try:
        attacks_data = security_service.get_blocked_attacks_data(current_user.id)
        
        logger.info(f"Blocked attacks analysis accessed", extra={
            'user_id': current_user.id,
            'action': 'BLOCKED_ATTACKS_ANALYSIS',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/security_dashboard.html', 
                             attacks_data=attacks_data)
        
    except Exception as e:
        logger.error(f"Blocked attacks analysis error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading blocked attacks analysis', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/vulnerabilities/assessment')
@login_required
@admin_required

def vulnerabilities_assessment():
    """Comprehensive vulnerability assessment and remediation tracking"""
    try:
        vulnerabilities_data = security_service.get_vulnerabilities_assessment_data(current_user.id)
        
        logger.info(f"Vulnerabilities assessment accessed", extra={
            'user_id': current_user.id,
            'action': 'VULNERABILITIES_ASSESSMENT',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/security_dashboard.html', 
                             vulnerabilities_data=vulnerabilities_data)
        
    except Exception as e:
        logger.error(f"Vulnerabilities assessment error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading vulnerabilities assessment', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/intrusions/detection')
@login_required
@admin_required

def intrusions_detection():
    """Intrusion detection system monitoring and analysis"""
    try:
        intrusions_data = security_service.get_intrusions_detection_data(current_user.id)
        
        logger.info(f"Intrusions detection accessed", extra={
            'user_id': current_user.id,
            'action': 'INTRUSIONS_DETECTION',
            'app_module': 'security_center'
        })
        
        return render_template('security_center/security_dashboard.html', 
                             intrusions_data=intrusions_data)
        
    except Exception as e:
        logger.error(f"Intrusions detection error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading intrusions detection', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/compliance/monitoring')
@login_required
@admin_required

def compliance_monitoring():
    """Security compliance monitoring and reporting"""
    try:
        compliance_data = security_service.get_compliance_monitoring_data(current_user.id)
        
        logger.info(f"Compliance monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'COMPLIANCE_MONITORING',
            'app_module': 'security_center'
        })
        
        return render_template('compliance_monitoring.html', 
                             compliance_data=compliance_data)
        
    except Exception as e:
        logger.error(f"Compliance monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading compliance monitoring', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/systems/<system_id>/monitor')
@login_required
@admin_required

def system_monitor(system_id):
    """Individual security system monitoring with real-time metrics"""
    try:
        system_data = security_service.get_system_monitor_data(current_user.id, system_id)
        
        logger.info(f"Security system monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_SYSTEM_MONITOR',
            'system_id': system_id,
            'app_module': 'security_center'
        })
        
        return render_template('system_monitor.html', 
                             system_data=system_data, system_id=system_id)
        
    except Exception as e:
        logger.error(f"Security system monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'system_id': system_id,
            'app_module': 'security_center'
        })
        flash('Error loading system monitoring', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/threats/<threat_id>/investigate')
@login_required
@admin_required

def threat_investigation(threat_id):
    """Individual threat investigation with forensics and remediation"""
    try:
        threat_data = security_service.get_threat_investigation_data(current_user.id, threat_id)
        
        logger.info(f"Threat investigation accessed", extra={
            'user_id': current_user.id,
            'action': 'THREAT_INVESTIGATION',
            'threat_id': threat_id,
            'app_module': 'security_center'
        })
        
        return render_template('threat_investigation.html', 
                             threat_data=threat_data, threat_id=threat_id)
        
    except Exception as e:
        logger.error(f"Threat investigation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'threat_id': threat_id,
            'app_module': 'security_center'
        })
        flash('Error loading threat investigation', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/incidents/<incident_id>/response')
@login_required
@admin_required

def incident_response(incident_id):
    """Individual incident response management with timeline and actions"""
    try:
        incident_data = security_service.get_incident_response_data(current_user.id, incident_id)
        
        logger.info(f"Incident response accessed", extra={
            'user_id': current_user.id,
            'action': 'INCIDENT_RESPONSE',
            'incident_id': incident_id,
            'app_module': 'security_center'
        })
        
        return render_template('security_center/incident_response.html', 
                             incident_data=incident_data, incident_id=incident_id)
        
    except Exception as e:
        logger.error(f"Incident response error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'incident_id': incident_id,
            'app_module': 'security_center'
        })
        flash('Error loading incident response', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/api/threat-intelligence')
@login_required
@admin_required

def api_threat_intelligence():
    """Get threat intelligence data via API"""
    try:
        threat_data = security_service.get_threat_intelligence_data(current_user.id)
        
        logger.info(f"Threat intelligence API accessed", extra={
            'user_id': current_user.id,
            'action': 'THREAT_INTELLIGENCE_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': threat_data})
        
    except Exception as e:
        logger.error(f"Threat intelligence API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load threat intelligence'}), 500

@security_center_bp.route('/api/intrusion-detection')
@login_required
@admin_required

def api_intrusion_detection():
    """Get intrusion detection data via API"""
    try:
        ids_data = security_service.get_intrusion_detection_data(current_user.id)
        
        logger.info(f"Intrusion detection API accessed", extra={
            'user_id': current_user.id,
            'action': 'INTRUSION_DETECTION_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': ids_data})
        
    except Exception as e:
        logger.error(f"Intrusion detection API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load intrusion detection data'}), 500

@security_center_bp.route('/api/incident-response')
@login_required
@admin_required

def api_incident_response():
    """Get incident response data via API"""
    try:
        incident_data = security_service.get_incident_response_data(current_user.id)
        
        logger.info(f"Incident response API accessed", extra={
            'user_id': current_user.id,
            'action': 'INCIDENT_RESPONSE_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': incident_data})
        
    except Exception as e:
        logger.error(f"Incident response API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load incident response data'}), 500

@security_center_bp.route('/api/incidents', methods=['POST'])
@login_required
@admin_required

def api_create_incident():
    """Create new security incident via API"""
    try:
        incident_data = request.get_json()
        if not incident_data:
            return jsonify({'success': False, 'error': 'No incident data provided'}), 400
        
        result = security_service.create_security_incident(current_user.id, incident_data)
        
        if result['success']:
            logger.info(f"Security incident created via API: {result.get('incident_id')}", extra={
                'user_id': current_user.id,
                'action': 'SECURITY_INCIDENT_CREATE_API_SUCCESS',
                'app_module': 'security_center',
                'incident_id': result.get('incident_id')
            })
        else:
            logger.warning(f"Security incident creation failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'action': 'SECURITY_INCIDENT_CREATE_API_FAILED',
                'app_module': 'security_center',
                'error': result.get('error')
            })
        
        return jsonify(result), 201 if result['success'] else 400
                
    except Exception as e:
        logger.error(f"Security incident creation API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@security_center_bp.route('/api/compliance-monitoring')
@login_required
@admin_required

def api_compliance_monitoring():
    """Get compliance monitoring data via API"""
    try:
        compliance_data = security_service.get_compliance_monitoring_data(current_user.id)
        
        logger.info(f"Compliance monitoring API accessed", extra={
            'user_id': current_user.id,
            'action': 'COMPLIANCE_MONITORING_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': compliance_data})
        
    except Exception as e:
        logger.error(f"Compliance monitoring API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load compliance data'}), 500

@security_center_bp.route('/api/waf')
@login_required
@admin_required

def api_waf():
    """Get Web Application Firewall data via API"""
    try:
        waf_data = security_service.get_waf_data(current_user.id)
        
        logger.info(f"WAF API accessed", extra={
            'user_id': current_user.id,
            'action': 'WAF_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': waf_data})
        
    except Exception as e:
        logger.error(f"WAF API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load WAF data'}), 500

@security_center_bp.route('/api/waf/rules', methods=['PUT'])
@login_required
@admin_required

def api_update_waf_rules():
    """Update WAF rules via API"""
    try:
        waf_rules = request.get_json()
        if not waf_rules:
            return jsonify({'success': False, 'error': 'No WAF rules provided'}), 400
        
        result = security_service.update_waf_rules(current_user.id, waf_rules)
        
        if result['success']:
            logger.info(f"WAF rules updated via API", extra={
                'user_id': current_user.id,
                'action': 'WAF_RULES_UPDATE_API_SUCCESS',
                'app_module': 'security_center',
                'rules_count': result.get('rules_updated', 0)
            })
        else:
            logger.warning(f"WAF rules update failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'action': 'WAF_RULES_UPDATE_API_FAILED',
                'app_module': 'security_center',
                'error': result.get('error')
            })
        
        return jsonify(result), 200 if result['success'] else 400
                
    except Exception as e:
        logger.error(f"WAF rules update API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@security_center_bp.route('/api/network-security')
@login_required
@admin_required

def api_network_security():
    """Get network security data via API"""
    try:
        network_data = security_service.get_network_security_data(current_user.id)
        
        logger.info(f"Network security API accessed", extra={
            'user_id': current_user.id,
            'action': 'NETWORK_SECURITY_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': network_data})
        
    except Exception as e:
        logger.error(f"Network security API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load network security data'}), 500

@security_center_bp.route('/api/vulnerability-assessment')
@login_required
@admin_required

def api_vulnerability_assessment():
    """Get vulnerability assessment data via API"""
    try:
        vuln_data = security_service.get_vulnerability_assessment_data(current_user.id)
        
        logger.info(f"Vulnerability assessment API accessed", extra={
            'user_id': current_user.id,
            'action': 'VULNERABILITY_ASSESSMENT_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': vuln_data})
        
    except Exception as e:
        logger.error(f"Vulnerability assessment API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load vulnerability data'}), 500

@security_center_bp.route('/api/security-policies')
@login_required
@admin_required

def api_security_policies():
    """Get security policies data via API"""
    try:
        policies_data = security_service.get_security_policies_data(current_user.id)
        
        logger.info(f"Security policies API accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_POLICIES_API',
            'app_module': 'security_center'
        })
        
        return jsonify({'success': True, 'data': policies_data})
        
    except Exception as e:
        logger.error(f"Security policies API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({'success': False, 'error': 'Unable to load security policies'}), 500

# Security Management Routes (Migrated from Legacy Admin Security)

@security_center_bp.route('/key-management')
@login_required
@admin_required

def key_management():
    """Cryptographic key management dashboard"""
    try:
        key_data = security_service.get_key_management_data(current_user.id)
        
        logger.info(f"Key management accessed", extra={
            'user_id': current_user.id,
            'action': 'KEY_MANAGEMENT_ACCESS',
            'app_module': 'security_center'
        })
        
        return render_template('key_management.html', 
                             key_data=key_data)
        
    except Exception as e:
        logger.error(f"Key management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading key management', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/api-keys')
@login_required
@admin_required

def api_keys():
    """API key management and rotation dashboard"""
    try:
        api_key_data = security_service.get_api_key_data(current_user.id)
        
        logger.info(f"API key management accessed", extra={
            'user_id': current_user.id,
            'action': 'API_KEY_MANAGEMENT_ACCESS',
            'app_module': 'security_center'
        })
        
        return render_template('api_keys.html', 
                             api_key_data=api_key_data)
        
    except Exception as e:
        logger.error(f"API key management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading API key management', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/firewall-management')
@login_required
@admin_required

def firewall_management():
    """Firewall configuration and management dashboard"""
    try:
        firewall_data = security_service.get_firewall_data(current_user.id)
        
        logger.info(f"Firewall management accessed", extra={
            'user_id': current_user.id,
            'action': 'FIREWALL_MANAGEMENT_ACCESS',
            'app_module': 'security_center'
        })
        
        return render_template('firewall_management.html', 
                             firewall_data=firewall_data)
        
    except Exception as e:
        logger.error(f"Firewall management error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading firewall management', 'error')
        return redirect(url_for("public.index"))

@security_center_bp.route('/security-settings')
@login_required
@admin_required

def security_settings():
    """Security settings and configuration panel"""
    try:
        settings_data = security_service.get_security_settings_data(current_user.id)
        
        logger.info(f"Security settings accessed", extra={
            'user_id': current_user.id,
            'action': 'SECURITY_SETTINGS_ACCESS',
            'app_module': 'security_center'
        })
        
        return render_template('security_settings.html', 
                             settings_data=settings_data)
        
    except Exception as e:
        logger.error(f"Security settings error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        flash('Error loading security settings', 'error')
        return redirect(url_for("public.index"))

# Security Operations Routes (Enhanced with Legacy Features)

@security_center_bp.route('/rotate-key/<key_name>', methods=['POST'])
@login_required
@admin_required

def rotate_key(key_name):
    """Rotate a specific cryptographic key"""
    try:
        result = security_service.rotate_key(key_name, current_user.id)
        
        logger.info(f"Key rotation performed", extra={
            'user_id': current_user.id,
            'action': 'KEY_ROTATION',
            'key_name': key_name,
            'app_module': 'security_center'
        })
        
        return jsonify({
            'success': True,
            'message': f'Key {key_name} rotated successfully',
            'new_key': result.get('new_key', 'Key rotated')
        })
        
    except Exception as e:
        logger.error(f"Key rotation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'key_name': key_name,
            'app_module': 'security_center'
        })
        return jsonify({
            'success': False,
            'error': 'Failed to rotate key'
        }), 500

@security_center_bp.route('/generate-api-key', methods=['POST'])
@login_required
@admin_required

def generate_api_key():
    """Generate new API key"""
    try:
        result = security_service.generate_api_key(current_user.id)
        
        logger.info(f"API key generated", extra={
            'user_id': current_user.id,
            'action': 'API_KEY_GENERATION',
            'app_module': 'security_center'
        })
        
        return jsonify({
            'success': True,
            'message': 'API key generated successfully',
            'api_key': result.get('api_key', 'Key generated')
        })
        
    except Exception as e:
        logger.error(f"API key generation error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'security_center'
        })
        return jsonify({
            'success': False,
            'error': 'Failed to generate API key'
        }), 500

@security_center_bp.route('/health')

@security_center_bp.route('/waf')

@security_center_bp.route('/ngfw')

@security_center_bp.route('/xdr')

@security_center_bp.route('/fraud-detection')
@login_required
@admin_required
def fraud_detection_aml_page():
    """Fraud detection and AML using orphaned template"""
    try:
        fraud_data = security_service.get_fraud_detection_data(current_user.id)

        return render_template('fraud_detection_aml.html',
                             fraud_data=fraud_data,
                             page_title='Fraud Detection & AML')

    except Exception as e:
        logger.error(f"Fraud detection AML error: {e}")
        flash('Error loading fraud detection', 'error')
        return redirect(url_for("public.index"))

# Enhanced Fraud Detection Routes
@security_center_bp.route('/aml/reports')
@login_required
@admin_required
def aml_reports():
    """AML Reports dashboard"""
    try:
        aml_data = security_service.get_aml_reports_data(current_user.id)
        return render_template('security_center/aml_reports.html',
                             aml_data=aml_data,
                             page_title='AML Reports')
    except Exception as e:
        logger.error(f"AML reports error: {e}")
        flash('Error loading AML reports', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

@security_center_bp.route('/create-fraud-alert')
@login_required
@admin_required
def create_fraud_alert():
    """Create fraud alert page"""
    try:
        return render_template('security_center/create_fraud_alert.html',
                             page_title='Create Fraud Alert')
    except Exception as e:
        logger.error(f"Create fraud alert error: {e}")
        flash('Error loading alert creation', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

@security_center_bp.route('/fraud/suspicious-activities')
@login_required
@admin_required
def suspicious_activities():
    """Suspicious activities dashboard"""
    try:
        activities_data = security_service.get_suspicious_activities_data(current_user.id)
        return render_template('security_center/suspicious_activities.html',
                             activities_data=activities_data,
                             page_title='Suspicious Activities')
    except Exception as e:
        logger.error(f"Suspicious activities error: {e}")
        flash('Error loading suspicious activities', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

@security_center_bp.route('/fraud/blocked-transactions')
@login_required
@admin_required
def blocked_transactions():
    """Blocked transactions dashboard"""
    try:
        blocked_data = security_service.get_blocked_transactions_data(current_user.id)
        return render_template('security_center/blocked_transactions.html',
                             blocked_data=blocked_data,
                             page_title='Blocked Transactions')
    except Exception as e:
        logger.error(f"Blocked transactions error: {e}")
        flash('Error loading blocked transactions', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

@security_center_bp.route('/fraud/unusual-patterns')
@login_required
@admin_required
def unusual_patterns():
    """Unusual patterns analysis"""
    try:
        patterns_data = security_service.get_unusual_patterns_data(current_user.id)
        return render_template('security_center/unusual_patterns.html',
                             patterns_data=patterns_data,
                             page_title='Unusual Patterns')
    except Exception as e:
        logger.error(f"Unusual patterns error: {e}")
        flash('Error loading unusual patterns', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

@security_center_bp.route('/aml/alerts')
@login_required
@admin_required
def aml_alerts():
    """AML alerts dashboard"""
    try:
        alerts_data = security_service.get_aml_alerts_data(current_user.id)
        return render_template('security_center/aml_alerts.html',
                             alerts_data=alerts_data,
                             page_title='AML Alerts')
    except Exception as e:
        logger.error(f"AML alerts error: {e}")
        flash('Error loading AML alerts', 'error')
        return redirect(url_for('security_center.fraud_detection_aml_page'))

# Enhanced Vulnerability Assessment Routes
@security_center_bp.route('/vulnerability/export-data')
@login_required
@admin_required
def export_vuln_data():
    """Export vulnerability data"""
    try:
        from flask import make_response
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['CVE ID', 'Severity', 'CVSS Score', 'Status', 'Affected System', 'Discovery Date'])
        writer.writerow(['CVE-2024-0001', 'Critical', '9.8', 'Open', 'Web Server', '2024-01-15'])
        writer.writerow(['CVE-2024-0002', 'High', '7.5', 'Patched', 'Database', '2024-01-10'])

        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=vulnerability_report.csv'

        return response

    except Exception as e:
        logger.error(f"Vulnerability data export error: {e}")
        flash('Error exporting vulnerability data', 'error')
        return redirect(url_for('security_center.vulnerabilities_assessment_page'))

@security_center_bp.route('/vulnerability/start-scan')
@login_required
@admin_required
def start_scan():
    """Start vulnerability scan"""
    try:
        scan_result = security_service.start_vulnerability_scan(current_user.id)
        flash('Vulnerability scan initiated successfully', 'success')
        return redirect(url_for('security_center.vulnerabilities_assessment_page'))
    except Exception as e:
        logger.error(f"Vulnerability scan start error: {e}")
        flash('Error starting vulnerability scan', 'error')
        return redirect(url_for('security_center.vulnerabilities_assessment_page'))

@security_center_bp.route('/vulnerability/remediation')
@login_required
@admin_required
def view_remediation():
    """View remediation dashboard"""
    try:
        remediation_data = security_service.get_remediation_data(current_user.id)
        return render_template('security_center/remediation.html',
                             remediation_data=remediation_data,
                             page_title='Vulnerability Remediation')
    except Exception as e:
        logger.error(f"Remediation view error: {e}")
        flash('Error loading remediation data', 'error')
        return redirect(url_for('security_center.vulnerabilities_assessment_page'))

@security_center_bp.route('/ip-management')

@security_center_bp.route('/investigation')
@login_required
def security_investigation():
    """Security investigation dashboard"""
    try:
        return render_template('security_investigation.html',
                             user=current_user,
                             page_title='Security investigation dashboard')
    except Exception as e:
        error_service.log_error("SECURITY_INVESTIGATION_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
@login_required
def ip_management():
    """IP address management"""
    try:
        return render_template('ip_management.html',
                             user=current_user,
                             page_title='IP address management')
    except Exception as e:
        error_service.log_error("IP_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
@login_required
def fraud_detection():
    """Fraud detection and AML"""
    try:
        return render_template('fraud_detection.html',
                             user=current_user,
                             page_title='Fraud detection and AML')
    except Exception as e:
        error_service.log_error("FRAUD_DETECTION_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
@login_required
def xdr_dashboard():
    """XDR security dashboard"""
    try:
        return render_template('xdr_dashboard.html',
                             user=current_user,
                             page_title='XDR security dashboard')
    except Exception as e:
        error_service.log_error("XDR_DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
@login_required
def ngfw_management():
    """Next-Gen Firewall management"""
    try:
        return render_template('ngfw_management.html',
                             user=current_user,
                             page_title='Next-Gen Firewall management')
    except Exception as e:
        error_service.log_error("NGFW_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
@login_required
def waf_management():
    """WAF management dashboard"""
    try:
        return render_template('waf_management.html',
                             user=current_user,
                             page_title='WAF management dashboard')
    except Exception as e:
        error_service.log_error("WAF_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('security_center.main_dashboard'))
def health():
    """Module health check endpoint"""
    try:
        health_status = security_service.get_module_health()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Security center health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Drill-down routes for detailed views
@security_center_bp.route('/threats/analysis')
@login_required
@admin_required

def threats_analysis():
    """Threat analysis drill-down view"""
    try:
        return render_template('security_center/threats_analysis.html',
                             user=current_user,
                             page_title='Threat Analysis')
    except Exception as e:
        logger.error(f"Threats analysis error: {e}")
        return redirect(url_for('security_center.security_dashboard'))

@security_center_bp.route('/incidents/management')
@security_center_bp.route('/access/monitoring')
@login_required
@admin_required

def access_monitoring():
    """Access monitoring drill-down view"""
    try:
        return render_template('security_center/access_monitoring.html',
                             user=current_user,
                             page_title='Access Monitoring')
    except Exception as e:
        logger.error(f"Access monitoring error: {e}")
        return redirect(url_for('security_center.security_dashboard'))

@security_center_bp.route('/compliance/audit')
@login_required
@admin_required

def compliance_audit():
    """Compliance audit drill-down view"""
    try:
        return render_template('security_center/compliance_audit.html',
                             user=current_user,
                             page_title='Compliance Audit')
    except Exception as e:
        logger.error(f"Compliance audit error: {e}")
        return redirect(url_for('security_center.security_dashboard'))

# Missing routes referenced in templates
@security_center_bp.route('/incident-response-dropdown')
@login_required
def incident_response_dropdown_redirect():
    """Incident response dropdown - redirect to incident response"""
    return redirect(url_for('security_center.incident_response_dropdown'))
