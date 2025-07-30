"""
API Module Routes
NVC Banking Platform - Unified API System

Consolidates all legacy API routes into comprehensive modular API system:
- Banking API endpoints (/api/v1/banking/*)
- Blockchain API endpoints (/api/v1/blockchain/*)
- Security API endpoints (/api/v1/security/*)
- Analytics API endpoints (/api/v1/analytics/*)
- Admin API endpoints (/api/v1/admin/*)
- Real-time API endpoints (/api/v1/realtime/*)
- Public API endpoints (/api/v1/public/*)
- Core system API endpoints (/api/v1/core/*)
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import logging

from modules.core.security_enforcement import secure_banking_route, treasury_secure_route, admin_secure_route
from modules.core.rbac import has_permission, require_permission
from modules.core.decorators import rate_limit
from modules.core.jwt_auth import jwt_required, create_token_response, jwt_manager, get_jwt_user
from modules.core.api_security import secure_api_endpoint, api_auth_required, api_rate_limit, api_security_check, api_audit_log
from modules.core.enterprise_security import banking_grade_protection, enterprise_security_check
from .services import APIService

logger = logging.getLogger(__name__)

# Create unified API blueprint following standard modular structure
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Core API Routes
@api_bp.route('/health')
@api_rate_limit('public')
@api_audit_log()
def api_health():
    """API system health check - public endpoint with basic protection"""
    try:
        # Simple health check without complex services to avoid dependencies
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'modules': ['api', 'auth', 'banking', 'dashboard', 'exchange', 'public', 'utils'],
            'security': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@api_bp.route('/status')
@api_rate_limit('public')
@api_audit_log()
def api_status():
    """API system status and metrics"""
    try:
        service = APIService()
        status_data = service.get_api_status()
        return jsonify({
            'status': 'success',
            'data': status_data,
            'timestamp': datetime.utcnow().isoformat(),
            'security_level': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@api_bp.route('/version')
@api_rate_limit('public')
def api_version():
    """API version information"""
    return jsonify({
        'api_version': '1.0.0',
        'platform': 'NVC Banking Platform',
        'security_grade': 'enterprise',
        'endpoints': {
            'banking': 3,
            'security': 1,
            'admin': 1,
            'auth': 2,
            'public': 3
        },
        'protection_features': [
            'rate_limiting',
            'authentication_required',
            'role_based_access',
            'audit_logging',
            'input_validation',
            'csrf_protection'
        ]
    })

# Banking API Endpoints with Enterprise Security
@api_bp.route('/banking/accounts', methods=['GET'])
@banking_grade_protection(allowed_roles=['super_admin', 'admin', 'treasury_officer'])
@secure_api_endpoint(allowed_roles=['super_admin', 'admin', 'treasury_officer'], rate_limit_tier='admin')
def get_banking_accounts():
    """Get banking accounts - enterprise protected"""
    try:
        service = APIService()
        accounts_data = service.get_banking_accounts()
        return jsonify({
            'status': 'success',
            'data': accounts_data,
            'timestamp': datetime.utcnow().isoformat(),
            'security_level': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"Banking accounts API error: {e}")
        return jsonify({'error': 'Failed to retrieve banking accounts'}), 500

@api_bp.route('/banking/transactions', methods=['GET'])
@banking_grade_protection(allowed_roles=['super_admin', 'admin', 'treasury_officer', 'standard_user'])
@secure_api_endpoint(allowed_roles=['super_admin', 'admin', 'treasury_officer', 'standard_user'], rate_limit_tier='authenticated')
def get_banking_transactions():
    """Get banking transactions - enterprise protected"""
    try:
        service = APIService()
        transactions_data = service.get_banking_transactions()
        return jsonify({
            'status': 'success',
            'data': transactions_data,
            'timestamp': datetime.utcnow().isoformat(),
            'security_level': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"Banking transactions API error: {e}")
        return jsonify({'error': 'Failed to retrieve banking transactions'}), 500

@api_bp.route('/banking/transfer', methods=['POST'])
@banking_grade_protection(allowed_roles=['super_admin', 'admin', 'treasury_officer', 'standard_user'], require_mfa=True)
@secure_api_endpoint(allowed_roles=['super_admin', 'admin', 'treasury_officer', 'standard_user'], rate_limit_tier='authenticated', require_signature=True)
def banking_transfer():
    """Execute banking transfer - maximum security"""
    try:
        service = APIService()
        transfer_data = request.get_json()
        result = service.execute_banking_transfer(transfer_data)
        return jsonify({
            'status': 'success',
            'data': result,
            'timestamp': datetime.utcnow().isoformat(),
            'security_level': 'maximum_protection'
        })
    except Exception as e:
        logger.error(f"Banking transfer API error: {e}")
        return jsonify({'error': 'Transfer failed'}), 500

@api_bp.route('/security/monitoring', methods=['GET'])
@banking_grade_protection(allowed_roles=['super_admin', 'admin'])
@secure_api_endpoint(allowed_roles=['super_admin', 'admin'], rate_limit_tier='admin')
def security_monitoring():
    """Get security monitoring data - admin only"""
    try:
        from modules.core.enterprise_security import get_security_status, get_security_events
        security_data = {
            'status': get_security_status(),
            'recent_events': get_security_events(50),
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify({
            'status': 'success',
            'data': security_data,
            'security_level': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"Security monitoring API error: {e}")
        return jsonify({'error': 'Failed to retrieve security data'}), 500

@api_bp.route('/admin/system-status', methods=['GET'])
@banking_grade_protection(allowed_roles=['super_admin', 'admin'])
@secure_api_endpoint(allowed_roles=['super_admin', 'admin'], rate_limit_tier='admin')
def admin_system_status():
    """Get comprehensive system status - admin only"""
    try:
        service = APIService()
        system_data = service.get_admin_system_status()
        return jsonify({
            'status': 'success',
            'data': system_data,
            'timestamp': datetime.utcnow().isoformat(),
            'security_level': 'enterprise_grade'
        })
    except Exception as e:
        logger.error(f"Admin system status API error: {e}")
        return jsonify({'error': 'Failed to retrieve system status'}), 500

# JWT Token Endpoints
@api_bp.route('/auth/token', methods=['POST'])
@api_security_check()
@api_rate_limit('public')
def get_token():
    """Generate JWT tokens for API access"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Authenticate user (simplified for demo)
        from modules.auth.models import User
        from werkzeug.security import check_password_hash
        
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Update login tracking for API authentication
        from modules.auth.services import AuthService
        auth_service = AuthService()
        login_result = auth_service.complete_login(user, login_method='api_key', remember_me=False)

        if not login_result['success']:
            logger.error("Failed to complete API login tracking for user: %s", username)

        # Generate tokens
        token_data = create_token_response(user)
        token_data['login_timestamp'] = login_result.get('login_timestamp')
        return jsonify(token_data)
        
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        return jsonify({'error': 'Token generation failed'}), 500

@api_bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT access token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400
        
        new_access_token = jwt_manager.refresh_access_token(refresh_token)
        if not new_access_token:
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        return jsonify({'access_token': new_access_token})
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

# Auth API Endpoints
@api_bp.route('/auth/health')
@jwt_required(optional=True)
def auth_health():
    """Auth module health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'auth',
            'version': '1.0.0',
            'features': [
                'login',
                'logout', 
                'registration',
                'password_reset',
                'role_based_auth',
                'session_management'
            ]
        })
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@api_bp.route('/status')
@jwt_required()
@secure_banking_route()
def api_status():
    """API system status and metrics"""
    try:
        service = APIService()
        status_data = service.get_api_status()
        return jsonify(status_data)
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return jsonify({'error': 'Status check failed'}), 500

@api_bp.route('/version')
@secure_banking_route()
def api_version():
    """API version information"""
    return jsonify({
        'api_version': '1.0.0',
        'platform_version': '2.0.0',
        'modules_available': [
            'banking', 'blockchain', 'core', 'external', 'system',
            'treasury', 'trading', 'exchange', 'compliance'
        ],
        'authentication': 'JWT',
        'rate_limiting': 'enabled',
        'last_updated': datetime.utcnow().isoformat()
    })

# Banking API Routes
@api_bp.route('/banking/health')
def banking_health():
    """Banking module health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'banking',
            'version': '1.0.0',
            'features': [
                'accounts',
                'transfers',
                'cards',
                'payments',
                'statements',
                'security_settings'
            ]
        })
    except Exception as e:
        logger.error(f"Banking health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@api_bp.route('/banking/accounts')
@secure_banking_route()
@login_required
def banking_accounts():
    """Get user's banking accounts via API"""
    try:
        service = APIService()
        accounts_data = service.get_user_accounts(current_user.id)
        return jsonify({'success': True, 'accounts': accounts_data})
    except Exception as e:
        logger.error(f"Banking accounts API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/banking/transfers')
@secure_banking_route()
@login_required 
def banking_transfers():
    """API endpoint for transfer history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        service = APIService()
        transfers = service.get_transfer_history(current_user.id, limit)
        return jsonify({'success': True, 'transfers': transfers})
    except Exception as e:
        logger.error(f"Banking transfers API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/banking/cards')
@secure_banking_route()
@login_required
def banking_cards():
    """API endpoint for user cards"""
    try:
        service = APIService()
        cards = service.get_user_cards(current_user.id)
        return jsonify({'success': True, 'cards': cards})
    except Exception as e:
        logger.error(f"Banking cards API error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Dashboard API Endpoints
@api_bp.route('/dashboard/health')
def dashboard_health():
    """Dashboard module health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'dashboard',
            'version': '1.0.0',
            'features': [
                'overview',
                'quick_actions',
                'recent_activity',
                'live_data',
                'drill_down',
                'export'
            ]
        })
    except Exception as e:
        logger.error(f"Dashboard health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Utils API Endpoints  
@api_bp.route('/utils/health')
def utils_health():
    """Utils module health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'utils',
            'version': '1.0.0',
            'features': [
                'navbar_context',
                'error_logging',
                'service_management'
            ]
        })
    except Exception as e:
        logger.error(f"Utils health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Auth API Endpoints moved to line 48-67

# Banking API Endpoints  
@api_bp.route('/banking/health')
def banking_health_check():
    """Banking module health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'banking',
            'version': '1.0.0',
            'features': [
                'account_management',
                'payments',
                'transaction_history'
            ]
        })
    except Exception as e:
        logger.error(f"Banking health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@api_bp.route('/accounts/<int:account_id>/balance')
@secure_banking_route()
@login_required
def account_balance(account_id):
    """Get specific account balance"""
    try:
        service = APIService()
        balance_data = service.get_account_balance(current_user.id, account_id)
        if not balance_data:
            return jsonify({'error': 'Account not found'}), 404
        return jsonify(balance_data)
    except Exception as e:
        logger.error(f"Account balance API error: {e}")
        return jsonify({'error': 'Failed to retrieve balance'}), 500

@api_bp.route('/transactions')
@secure_banking_route()
@login_required
def banking_transactions():
    """Get user's transaction history via API"""
    try:
        service = APIService()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        account_id = request.args.get('account_id', type=int)
        
        transactions_data = service.get_user_transactions(
            current_user.id, page=page, per_page=per_page, account_id=account_id
        )
        return jsonify(transactions_data)
    except Exception as e:
        logger.error(f"Banking transactions API error: {e}")
        return jsonify({'error': 'Failed to retrieve transactions'}), 500

@api_bp.route('/transfer', methods=['POST'])
@secure_banking_route()
@login_required
def banking_transfer():
    """Execute banking transfer via API"""
    try:
        service = APIService()
        data = request.get_json()
        
        result = service.execute_transfer(current_user.id, data)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Banking transfer API error: {e}")
        return jsonify({'error': 'Transfer failed'}), 500

@api_bp.route('/treasury/operations')
@treasury_secure_route()
@require_permission('treasury:operations')
def treasury_operations():
    """Treasury operations API endpoint"""
    try:
        service = APIService()
        operations_data = service.get_treasury_operations()
        return jsonify(operations_data)
    except Exception as e:
        logger.error(f"Treasury operations API error: {e}")
        return jsonify({'error': 'Failed to retrieve treasury operations'}), 500

# Blockchain API Routes
@api_bp.route('/networks')
@secure_banking_route()
@login_required
def blockchain_networks():
    """Get supported blockchain networks"""
    try:
        service = APIService()
        networks_data = service.get_blockchain_networks()
        return jsonify(networks_data)
    except Exception as e:
        logger.error(f"Blockchain networks API error: {e}")
        return jsonify({'error': 'Failed to retrieve networks'}), 500

@api_bp.route('/transactions/<network>')
@secure_banking_route()
@login_required
def blockchain_transactions(network):
    """Get blockchain transactions for specific network"""
    try:
        service = APIService()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        transactions_data = service.get_blockchain_transactions(
            current_user.id, network, page=page, per_page=per_page
        )
        return jsonify(transactions_data)
    except Exception as e:
        logger.error(f"Blockchain transactions API error: {e}")
        return jsonify({'error': 'Failed to retrieve blockchain transactions'}), 500

@api_bp.route('/core/contracts')
@secure_banking_route()
@login_required
def blockchain_contracts():
    """Get deployed smart contracts information"""
    try:
        service = APIService()
        contracts_data = service.get_smart_contracts_info()
        return jsonify(contracts_data)
    except Exception as e:
        logger.error(f"Smart contracts API error: {e}")
        return jsonify({'error': 'Failed to retrieve contracts information'}), 500

@api_bp.route('/crypto/prices')
@secure_banking_route()
@login_required
def crypto_prices():
    """Get cryptocurrency prices"""
    try:
        service = APIService()
        symbols = request.args.get('symbols', '').split(',') if request.args.get('symbols') else []
        prices_data = service.get_crypto_prices(symbols)
        return jsonify(prices_data)
    except Exception as e:
        logger.error(f"Crypto prices API error: {e}")
        return jsonify({'error': 'Failed to retrieve crypto prices'}), 500

# Core System API Routes
@api_bp.route('/availability')
@secure_banking_route()
def core_availability():
    """Check core system availability"""
    try:
        service = APIService()
        availability_data = service.get_core_availability()
        return jsonify(availability_data)
    except Exception as e:
        logger.error(f"Core availability API error: {e}")
        return jsonify({'error': 'Availability check failed'}), 500

@api_bp.route('/session/status')
@secure_banking_route()
@login_required
def session_status():
    """Get current session status"""
    try:
        service = APIService()
        session_data = service.get_session_status(current_user.id)
        return jsonify(session_data)
    except Exception as e:
        logger.error(f"Session status API error: {e}")
        return jsonify({'error': 'Failed to retrieve session status'}), 500

@api_bp.route('/session/extend', methods=['POST'])
@secure_banking_route()
@login_required
def extend_session():
    """Extend current user session"""
    try:
        service = APIService()
        result = service.extend_user_session(current_user.id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Session extension API error: {e}")
        return jsonify({'error': 'Failed to extend session'}), 500

# External Integration API Routes
@api_bp.route('/integration/status')
@secure_banking_route()
@login_required
def external_integration_status():
    """Get status of external integrations"""
    try:
        service = APIService()
        integration_data = service.get_external_integrations_status()
        return jsonify(integration_data)
    except Exception as e:
        logger.error(f"External integration API error: {e}")
        return jsonify({'error': 'Failed to retrieve integration status'}), 500

@api_bp.route('/mojaloop/transfers')
@secure_banking_route()
@require_permission('banking:external_transfers')
def mojaloop_transfers():
    """Get Mojaloop transfer information"""
    try:
        service = APIService()
        transfers_data = service.get_mojaloop_transfers(current_user.id)
        return jsonify(transfers_data)
    except Exception as e:
        logger.error(f"Mojaloop transfers API error: {e}")
        return jsonify({'error': 'Failed to retrieve Mojaloop transfers'}), 500

@api_bp.route('/transfers/execute', methods=['POST'])
@secure_banking_route()
@login_required
def execute_external_transfer():
    """Execute external transfer via integrated services"""
    try:
        service = APIService()
        data = request.get_json()
        
        result = service.execute_external_transfer(current_user.id, data)
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"External transfer API error: {e}")
        return jsonify({'error': 'External transfer failed'}), 500

# System Performance API Routes
@api_bp.route('/performance/monitoring')
@admin_secure_route()
@require_permission('admin:system_monitoring')
def system_performance():
    """Get system performance metrics"""
    try:
        service = APIService()
        performance_data = service.get_system_performance_metrics()
        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"System performance API error: {e}")
        return jsonify({'error': 'Failed to retrieve performance metrics'}), 500

@api_bp.route('/performance/realtime')
@admin_secure_route()
@require_permission('admin:system_monitoring')
def realtime_performance():
    """Get real-time system performance data"""
    try:
        service = APIService()
        realtime_data = service.get_realtime_performance_data()
        return jsonify(realtime_data)
    except Exception as e:
        logger.error(f"Real-time performance API error: {e}")
        return jsonify({'error': 'Failed to retrieve real-time data'}), 500

# Real-time API Endpoints
@api_bp.route('/realtime/dashboard')
@secure_banking_route()
@login_required
def realtime_dashboard_data():
    """Get real-time dashboard data"""
    try:
        service = APIService()
        dashboard_data = service.get_realtime_dashboard_data(current_user.id)
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Real-time dashboard API error: {e}")
        return jsonify({'error': 'Failed to retrieve dashboard data'}), 500

@api_bp.route('/realtime/notifications')
@secure_banking_route()
@login_required
def get_realtime_notifications():
    """Get real-time user notifications"""
    try:
        service = APIService()
        notifications_data = service.get_user_notifications(current_user.id)
        return jsonify(notifications_data)
    except Exception as e:
        logger.error(f"Real-time notifications API error: {e}")
        return jsonify({'error': 'Failed to retrieve notifications'}), 500

@api_bp.route('/realtime/alerts')
@admin_secure_route()
@require_permission('admin:system_alerts')
def realtime_system_alerts():
    """Get real-time system alerts"""
    try:
        service = APIService()
        alerts_data = service.get_system_alerts()
        return jsonify(alerts_data)
    except Exception as e:
        logger.error(f"Real-time alerts API error: {e}")
        return jsonify({'error': 'Failed to retrieve system alerts'}), 500

# Network Security API
@api_bp.route('/security/network/status')
@admin_secure_route()
@require_permission('admin:security_monitoring')
def network_security_status():
    """Get network security status"""
    try:
        service = APIService()
        security_data = service.get_network_security_status()
        return jsonify(security_data)
    except Exception as e:
        logger.error(f"Network security API error: {e}")
        return jsonify({'error': 'Failed to retrieve security status'}), 500



# Deployment API
@api_bp.route('/deployment/status')
@admin_secure_route()
@require_permission('admin:deployment_management')
def deployment_status():
    """Get deployment status information"""
    try:
        service = APIService()
        deployment_data = service.get_deployment_status()
        return jsonify(deployment_data)
    except Exception as e:
        logger.error(f"Deployment status API error: {e}")
        return jsonify({'error': 'Failed to retrieve deployment status'}), 500

# Module health endpoints
@api_bp.route('/modules/health')
@secure_banking_route()
def modules_health():
    """Get health status of all modules"""
    try:
        service = APIService()
        modules_data = service.get_modules_health_status()
        return jsonify(modules_data)
    except Exception as e:
        logger.error(f"Modules health API error: {e}")
        return jsonify({'error': 'Failed to retrieve modules health'}), 500

@api_bp.route('/modules/features')
@secure_banking_route()
@login_required
def modules_features():
    """Get available module features for current user"""
    try:
        service = APIService()
        features_data = service.get_user_available_features(current_user.id)
        return jsonify(features_data)
    except Exception as e:
        logger.error(f"Module features API error: {e}")
        return jsonify({'error': 'Failed to retrieve module features'}), 500

# API Documentation endpoint
@api_bp.route('/docs')
@secure_banking_route()
def api_documentation():
    """Get API documentation"""
    try:
        service = APIService()
        docs_data = service.get_api_documentation()
        return jsonify(docs_data)
    except Exception as e:
        logger.error(f"API documentation error: {e}")
        return jsonify({'error': 'Failed to retrieve API documentation'}), 500

# =============================================================================
# SECURITY API ENDPOINTS (v1)
# =============================================================================

@api_bp.route('/status')
@admin_secure_route()
@require_permission('admin:security_monitoring')
def security_status():
    """Get comprehensive security status"""
    try:
        service = APIService()
        security_data = service.get_security_status()
        return jsonify(security_data)
    except Exception as e:
        logger.error(f"Security status API error: {e}")
        return jsonify({'error': 'Failed to retrieve security status'}), 500

@api_bp.route('/threats')
@admin_secure_route()
@require_permission('admin:security_monitoring')
def security_threats():
    """Get current security threats"""
    try:
        service = APIService()
        threats_data = service.get_security_threats()
        return jsonify(threats_data)
    except Exception as e:
        logger.error(f"Security threats API error: {e}")
        return jsonify({'error': 'Failed to retrieve security threats'}), 500

@api_bp.route('/incidents')
@admin_secure_route()
@require_permission('admin:security_monitoring')
def security_incidents():
    """Get security incidents"""
    try:
        service = APIService()
        incidents_data = service.get_security_incidents()
        return jsonify(incidents_data)
    except Exception as e:
        logger.error(f"Security incidents API error: {e}")
        return jsonify({'error': 'Failed to retrieve security incidents'}), 500

@api_bp.route('/vulnerabilities')
@admin_secure_route()
@require_permission('admin:security_monitoring')
def security_vulnerabilities():
    """Get vulnerability assessment data"""
    try:
        service = APIService()
        vuln_data = service.get_vulnerabilities()
        return jsonify(vuln_data)
    except Exception as e:
        logger.error(f"Security vulnerabilities API error: {e}")
        return jsonify({'error': 'Failed to retrieve vulnerabilities'}), 500

@api_bp.route('/compliance')
@admin_secure_route()
@require_permission('admin:compliance_monitoring')
def security_compliance():
    """Get security compliance status"""
    try:
        service = APIService()
        compliance_data = service.get_security_compliance()
        return jsonify(compliance_data)
    except Exception as e:
        logger.error(f"Security compliance API error: {e}")
        return jsonify({'error': 'Failed to retrieve compliance data'}), 500

@api_bp.route('/waf/rules')
@admin_secure_route()
@require_permission('admin:security_management')
def waf_rules():
    """Get WAF rules"""
    try:
        service = APIService()
        waf_data = service.get_waf_rules()
        return jsonify(waf_data)
    except Exception as e:
        logger.error(f"WAF rules API error: {e}")
        return jsonify({'error': 'Failed to retrieve WAF rules'}), 500

@api_bp.route('/firewall/status')
@admin_secure_route()
@require_permission('admin:security_management')
def firewall_status():
    """Get firewall status"""
    try:
        service = APIService()
        firewall_data = service.get_firewall_status()
        return jsonify(firewall_data)
    except Exception as e:
        logger.error(f"Firewall status API error: {e}")
        return jsonify({'error': 'Failed to retrieve firewall status'}), 500

# =============================================================================
# ANALYTICS API ENDPOINTS (v1)
# =============================================================================

@api_bp.route('/dashboard')
@secure_banking_route()
@require_permission('analytics:view_dashboard')
def api_analytics_dashboard():
    """Get analytics dashboard data"""
    try:
        service = APIService()
        dashboard_data = service.get_analytics_dashboard()
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Analytics dashboard API error: {e}")
        return jsonify({'error': 'Failed to retrieve analytics dashboard'}), 500

@api_bp.route('/metrics')
@secure_banking_route()
@require_permission('analytics:view_metrics')
def api_analytics_metrics():
    """Get system metrics"""
    try:
        service = APIService()
        metrics_data = service.get_system_metrics()
        return jsonify(metrics_data)
    except Exception as e:
        logger.error(f"Analytics metrics API error: {e}")
        return jsonify({'error': 'Failed to retrieve metrics'}), 500

@api_bp.route('/reports')
@secure_banking_route()
@require_permission('analytics:view_reports')
def api_analytics_reports():
    """Get analytics reports"""
    try:
        service = APIService()
        reports_data = service.get_analytics_reports()
        return jsonify(reports_data)
    except Exception as e:
        logger.error(f"Analytics reports API error: {e}")
        return jsonify({'error': 'Failed to retrieve reports'}), 500

@api_bp.route('/trends')
@secure_banking_route()
@require_permission('analytics:view_trends')
def api_analytics_trends():
    """Get analytics trends"""
    try:
        service = APIService()
        trends_data = service.get_analytics_trends()
        return jsonify(trends_data)
    except Exception as e:
        logger.error(f"Analytics trends API error: {e}")
        return jsonify({'error': 'Failed to retrieve trends'}), 500

# =============================================================================
# ADMIN API ENDPOINTS (v1)
# =============================================================================

@api_bp.route('/users')
@admin_secure_route()
@require_permission('admin:user_management')
def admin_users():
    """Get user management data"""
    try:
        service = APIService()
        users_data = service.get_admin_users()
        return jsonify(users_data)
    except Exception as e:
        logger.error(f"Admin users API error: {e}")
        return jsonify({'error': 'Failed to retrieve users data'}), 500

@api_bp.route('/system-health')
@admin_secure_route()
@require_permission('admin:system_monitoring')
def admin_system_health():
    """Get system health data"""
    try:
        service = APIService()
        health_data = service.get_system_health()
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"Admin system health API error: {e}")
        return jsonify({'error': 'Failed to retrieve system health'}), 500

@api_bp.route('/settings')
@admin_secure_route()
@require_permission('admin:system_configuration')
def admin_settings():
    """Get system settings"""
    try:
        service = APIService()
        settings_data = service.get_system_settings()
        return jsonify(settings_data)
    except Exception as e:
        logger.error(f"Admin settings API error: {e}")
        return jsonify({'error': 'Failed to retrieve settings'}), 500

@api_bp.route('/logs')
@admin_secure_route()
@require_permission('admin:log_management')
def admin_logs():
    """Get system logs"""
    try:
        service = APIService()
        logs_data = service.get_system_logs()
        return jsonify(logs_data)
    except Exception as e:
        logger.error(f"Admin logs API error: {e}")
        return jsonify({'error': 'Failed to retrieve logs'}), 500

@api_bp.route('/backup')
@admin_secure_route()
@require_permission('admin:backup_management')
def admin_backup():
    """Get backup status"""
    try:
        service = APIService()
        backup_data = service.get_backup_status()
        return jsonify(backup_data)
    except Exception as e:
        logger.error(f"Admin backup API error: {e}")
        return jsonify({'error': 'Failed to retrieve backup status'}), 500

# =============================================================================
# REALTIME API ENDPOINTS (v1)
# =============================================================================

@api_bp.route('/dashboard')
@secure_banking_route()
@login_required
def realtime_dashboard():
    """Get real-time dashboard data"""
    try:
        service = APIService()
        dashboard_data = service.get_realtime_dashboard()
        return jsonify(dashboard_data)
    except Exception as e:
        logger.error(f"Realtime dashboard API error: {e}")
        return jsonify({'error': 'Failed to retrieve realtime dashboard'}), 500

@api_bp.route('/notifications')
@secure_banking_route()
@login_required
def realtime_notifications():
    """Get real-time notifications"""
    try:
        service = APIService()
        notifications_data = service.get_realtime_notifications(current_user.id)
        return jsonify(notifications_data)
    except Exception as e:
        logger.error(f"Realtime notifications API error: {e}")
        return jsonify({'error': 'Failed to retrieve notifications'}), 500

@api_bp.route('/alerts')
@admin_secure_route()
@require_permission('admin:system_alerts')
def realtime_alerts():
    """Get real-time system alerts"""
    try:
        service = APIService()
        alerts_data = service.get_realtime_alerts()
        return jsonify(alerts_data)
    except Exception as e:
        logger.error(f"Realtime alerts API error: {e}")
        return jsonify({'error': 'Failed to retrieve alerts'}), 500

@api_bp.route('/metrics')
@secure_banking_route()
@require_permission('analytics:view_realtime')
def realtime_metrics():
    """Get real-time metrics"""
    try:
        service = APIService()
        metrics_data = service.get_realtime_metrics()
        return jsonify(metrics_data)
    except Exception as e:
        logger.error(f"Realtime metrics API error: {e}")
        return jsonify({'error': 'Failed to retrieve realtime metrics'}), 500

# =============================================================================
# PUBLIC API ENDPOINTS (v1)
# =============================================================================

@api_bp.route('/health')
def public_health():
    """Public health check endpoint"""
    try:
        service = APIService()
        health_data = service.get_public_health()
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"Public health API error: {e}")
        return jsonify({'error': 'Health check failed'}), 500

@api_bp.route('/contact', methods=['POST'])
@rate_limit("10/minute")
def public_contact():
    """Public contact form submission"""
    try:
        service = APIService()
        contact_data = service.submit_contact_form(request.json)
        return jsonify(contact_data)
    except Exception as e:
        logger.error(f"Public contact API error: {e}")
        return jsonify({'error': 'Failed to submit contact form'}), 500

@api_bp.route('/services')
def public_services():
    """Get public banking services information"""
    try:
        service = APIService()
        services_data = service.get_public_services()
        return jsonify(services_data)
    except Exception as e:
        logger.error(f"Public services API error: {e}")
        return jsonify({'error': 'Failed to retrieve services'}), 500

@api_bp.route('/news')
def public_news():
    """Get public news and updates"""
    try:
        service = APIService()
        news_data = service.get_public_news()
        return jsonify(news_data)
    except Exception as e:
        logger.error(f"Public news API error: {e}")
        return jsonify({'error': 'Failed to retrieve news'}), 500

# Export the unified API blueprint for registration
api_blueprints = [api_bp]