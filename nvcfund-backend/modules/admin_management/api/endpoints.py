"""
Admin Management API Endpoints
RESTful API for administrative management operations
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import logging

from modules.core.decorators import admin_required, super_admin_required
from modules.core.security_enforcement import secure_banking_route
from ..services import AdminManagementService

# Configure logging
logger = logging.getLogger(__name__)

# Create API blueprint
admin_management_api_bp = Blueprint('admin_management_api', __name__, url_prefix='/admin/api')

# Initialize service
admin_service = AdminManagementService()

@admin_management_api_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_dashboard_data():
    """Get admin dashboard data"""
    try:
        dashboard_data = admin_service.get_admin_dashboard_data(current_user.id)
        
        logger.info(f"Admin dashboard API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_ADMIN_DASHBOARD',
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Admin dashboard API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load dashboard data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/platform/overview', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_platform_overview():
    """Get platform overview data"""
    try:
        platform_data = admin_service.get_platform_overview(current_user.id)
        
        logger.info(f"Platform overview API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_PLATFORM_OVERVIEW',
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'status': 'success',
            'data': platform_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Platform overview API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load platform data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_users():
    """Get users list with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        role_filter = request.args.get('role', None)
        
        user_data = admin_service.get_user_management_data(current_user.id)
        
        # Apply filters if provided
        users = user_data.get('users', [])
        if role_filter:
            users = [u for u in users if u['role'] == role_filter]
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = users[start:end]
        
        logger.info(f"Users API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_USERS_LIST',
            'app_module': 'admin_management',
            'page': page,
            'role_filter': role_filter
        })
        
        return jsonify({
            'status': 'success',
            'data': {
                'users': paginated_users,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(users),
                    'pages': (len(users) + per_page - 1) // per_page
                },
                'stats': user_data.get('user_stats', {})
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Users API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load users data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_user_details(user_id):
    """Get detailed information for a specific user"""
    try:
        user_details = admin_service.get_user_details(current_user.id, user_id)
        
        logger.info(f"User details API accessed for user {user_id}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'action': 'API_USER_DETAILS',
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'status': 'success',
            'data': user_details,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"User details API error: {e}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load user details',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def update_user(user_id):
    """Update user information"""
    try:
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({
                'status': 'error',
                'error': 'No update data provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        result = admin_service.update_user_information(
            admin_user_id=current_user.id,
            target_user_id=user_id,
            update_data=update_data
        )
        
        if result['success']:
            logger.info(f"User {user_id} updated via API", extra={
                'user_id': current_user.id,
                'target_user_id': user_id,
                'action': 'API_USER_UPDATE_SUCCESS',
                'app_module': 'admin_management',
                'changes': list(update_data.keys())
            })
            
            return jsonify({
                'status': 'success',
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.warning(f"User {user_id} update failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'target_user_id': user_id,
                'action': 'API_USER_UPDATE_FAILED',
                'app_module': 'admin_management',
                'error': result.get('error')
            })
            
            return jsonify({
                'status': 'error',
                'error': result.get('error', 'Update failed'),
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"User update API error: {e}", extra={
            'user_id': current_user.id,
            'target_user_id': user_id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Internal server error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/configuration', methods=['GET'])
@login_required
@super_admin_required
@secure_banking_route(max_requests=10)
def get_system_configuration():
    """Get system configuration"""
    try:
        config_data = admin_service.get_system_configuration(current_user.id)
        
        logger.info(f"System configuration API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_CONFIG_GET',
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'status': 'success',
            'data': config_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Configuration API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load configuration',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/configuration', methods=['PUT'])
@login_required
@super_admin_required
@secure_banking_route(max_requests=10)
def update_system_configuration():
    """Update system configuration"""
    try:
        config_data = request.get_json()
        
        if not config_data:
            return jsonify({
                'status': 'error',
                'error': 'No configuration data provided',
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        result = admin_service.update_system_configuration(
            admin_user_id=current_user.id,
            config_data=config_data
        )
        
        if result['success']:
            logger.info(f"System configuration updated via API", extra={
                'user_id': current_user.id,
                'action': 'API_CONFIG_UPDATE_SUCCESS',
                'app_module': 'admin_management',
                'changes': list(config_data.keys())
            })
            
            return jsonify({
                'status': 'success',
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            logger.warning(f"Configuration update failed via API: {result.get('error')}", extra={
                'user_id': current_user.id,
                'action': 'API_CONFIG_UPDATE_FAILED',
                'app_module': 'admin_management',
                'error': result.get('error')
            })
            
            return jsonify({
                'status': 'error',
                'error': result.get('error', 'Update failed'),
                'timestamp': datetime.utcnow().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Configuration update API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Internal server error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/audit/logs', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_audit_logs():
    """Get audit logs with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        log_type = request.args.get('type', 'all')
        
        audit_data = admin_service.get_audit_logs(
            admin_user_id=current_user.id,
            page=page,
            per_page=per_page,
            log_type=log_type
        )
        
        logger.info(f"Audit logs API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_AUDIT_LOGS',
            'app_module': 'admin_management',
            'page': page,
            'log_type': log_type
        })
        
        return jsonify({
            'status': 'success',
            'data': audit_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Audit logs API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load audit logs',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/system/stats', methods=['GET'])
@login_required
@admin_required
@secure_banking_route(max_requests=10)
def get_system_stats():
    """Get real-time system statistics"""
    try:
        # Get current system metrics
        dashboard_data = admin_service.get_admin_dashboard_data(current_user.id)
        platform_data = admin_service.get_platform_overview(current_user.id)
        
        stats = {
            'users': {
                'total': dashboard_data.get('total_users', 0),
                'active': dashboard_data.get('active_users', 0),
                'recent_registrations': dashboard_data.get('recent_registrations', 0)
            },
            'system': {
                'uptime': platform_data.get('platform_stats', {}).get('uptime', 'Unknown'),
                'load': platform_data.get('platform_stats', {}).get('system_load', {}),
                'database_status': platform_data.get('platform_stats', {}).get('database_status', 'Unknown')
            },
            'security': {
                'recent_events': dashboard_data.get('recent_security_events', 0),
                'pending_kyc': dashboard_data.get('pending_kyc', 0)
            }
        }
        
        logger.info(f"System stats API accessed", extra={
            'user_id': current_user.id,
            'action': 'API_SYSTEM_STATS',
            'app_module': 'admin_management'
        })
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"System stats API error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'admin_management'
        })
        return jsonify({
            'status': 'error',
            'error': 'Failed to load system stats',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_management_api_bp.route('/health', methods=['GET'])
def health_check():
    """Module health check"""
    try:
        health_status = admin_service.get_module_health()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'Admin Management API',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500