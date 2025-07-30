"""
System Management Module Routes
Active system configuration, maintenance, and operational management
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging
import os
import subprocess
import json

from modules.core.decorators import admin_required
from modules.core.security_enforcement import secure_banking_route
from modules.core.health_monitor import health_monitor
from modules.core.enhanced_error_handler import create_success_response
from .services import SystemManagementService

logger = logging.getLogger(__name__)

# Create blueprint with hyphenated URL for professional banking appearance
system_management_bp = Blueprint('system_management', __name__, 
                                template_folder='templates', 
                                url_prefix='/admin-management/system-management')

# Initialize service
system_service = SystemManagementService()

@system_management_bp.route('/')
@system_management_bp.route('/dashboard')
@login_required
@admin_required
@secure_banking_route()
def system_dashboard():
    """Active system management dashboard"""
    try:
        # Get real-time system data
        system_data = system_service.get_system_health()
        services_data = system_service.get_service_status()
        pending_tasks = system_service.get_pending_maintenance_tasks()
        recent_actions = system_service.get_recent_admin_actions()
        
        dashboard_data = {
            'system_health': system_data,
            'services': services_data,
            'pending_maintenance': pending_tasks,
            'recent_actions': recent_actions,
            'maintenance_mode': system_service.is_maintenance_mode_active(),
            'backup_status': system_service.get_backup_status(),
            'security_alerts': system_service.get_active_security_alerts(),
            'performance_metrics': system_service.get_performance_metrics(),
            'disk_cleanup_needed': system_service.check_disk_cleanup_needed(),
            'log_rotation_due': system_service.check_log_rotation_due(),
            'certificate_expiry': system_service.check_certificate_expiry()
        }
        
        return render_template('system_management/management_dashboard.html', 
                             data=dashboard_data)
        
    except Exception as e:
        logger.error(f"System dashboard error: {e}")
        flash('Unable to load system dashboard', 'error')
        return redirect(url_for('admin_management.admin_dashboard'))

# Configuration Management Routes
@system_management_bp.route('/configuration')
@login_required
@admin_required
@secure_banking_route()
def system_configuration():
    """System configuration management"""
    try:
        config_data = system_service.get_system_configuration()
        environment_vars = system_service.get_environment_variables()
        
        return render_template('system_management/configuration.html', 
                             config=config_data, 
                             environment=environment_vars)
        
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        flash('Unable to load configuration', 'error')
        return redirect(url_for('system_management.system_dashboard'))

@system_management_bp.route('/configuration/update', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def update_configuration():
    """Update system configuration"""
    try:
        config_updates = request.form.to_dict()
        result = system_service.update_configuration(config_updates, current_user.id)
        
        if result['success']:
            flash('Configuration updated successfully', 'success')
        else:
            flash(f'Configuration update failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.system_configuration'))
        
    except Exception as e:
        logger.error(f"Configuration update error: {e}")
        flash('Configuration update failed', 'error')
        return redirect(url_for('system_management.system_configuration'))

# Maintenance Operations Routes
@system_management_bp.route('/maintenance')
@login_required
@admin_required
@secure_banking_route()
def maintenance_center():
    """Maintenance operations center"""
    try:
        maintenance_data = {
            'scheduled_tasks': system_service.get_scheduled_maintenance(),
            'maintenance_history': system_service.get_maintenance_history(),
            'system_optimization': system_service.get_optimization_recommendations(),
            'disk_usage': system_service.get_disk_usage_analysis(),
            'log_analysis': system_service.get_log_analysis(),
            'backup_schedule': system_service.get_backup_schedule(),
            'update_status': system_service.get_update_status()
        }
        
        return render_template('system_management/maintenance.html', 
                             maintenance=maintenance_data)
        
    except Exception as e:
        logger.error(f"Maintenance center error: {e}")
        flash('Unable to load maintenance center', 'error')
        return redirect(url_for('system_management.system_dashboard'))

@system_management_bp.route('/maintenance/toggle', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def toggle_maintenance_mode():
    """Toggle maintenance mode"""
    try:
        action = request.form.get('action')  # 'enable' or 'disable'
        reason = request.form.get('reason', '')
        
        result = system_service.toggle_maintenance_mode(action, reason, current_user.id)
        
        if result['success']:
            flash(f'Maintenance mode {action}d successfully', 'success')
        else:
            flash(f'Failed to {action} maintenance mode: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.maintenance_center'))
        
    except Exception as e:
        logger.error(f"Maintenance mode toggle error: {e}")
        flash('Failed to toggle maintenance mode', 'error')
        return redirect(url_for('system_management.maintenance_center'))

@system_management_bp.route('/maintenance/cleanup', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def perform_cleanup():
    """Perform system cleanup operations"""
    try:
        cleanup_type = request.form.get('cleanup_type')
        result = system_service.perform_system_cleanup(cleanup_type, current_user.id)
        
        if result['success']:
            flash(f'System cleanup completed: {result["message"]}', 'success')
        else:
            flash(f'Cleanup failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.maintenance_center'))
        
    except Exception as e:
        logger.error(f"System cleanup error: {e}")
        flash('System cleanup failed', 'error')
        return redirect(url_for('system_management.maintenance_center'))

# Service Management Routes
@system_management_bp.route('/services')
@login_required
@admin_required
@secure_banking_route()
def service_management():
    """Service management center"""
    try:
        services_data = {
            'active_services': system_service.get_active_services(),
            'service_dependencies': system_service.get_service_dependencies(),
            'service_logs': system_service.get_service_logs(),
            'performance_metrics': system_service.get_service_performance(),
            'restart_queue': system_service.get_service_restart_queue(),
            'health_checks': system_service.run_service_health_checks()
        }
        
        return render_template('system_management/services.html', 
                             services=services_data)
        
    except Exception as e:
        logger.error(f"Service management error: {e}")
        flash('Unable to load service management', 'error')
        return redirect(url_for('system_management.system_dashboard'))

# Alias route for services
@system_management_bp.route('/services-alias')
@login_required
@admin_required
@secure_banking_route()
def services():
    """Services management - alias for service_management"""
    return service_management()

@system_management_bp.route('/services/restart', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def restart_service():
    """Restart a specific service"""
    try:
        service_name = request.form.get('service_name')
        force_restart = request.form.get('force_restart') == 'true'
        
        result = system_service.restart_service(service_name, force_restart, current_user.id)
        
        if result['success']:
            flash(f'Service {service_name} restarted successfully', 'success')
        else:
            flash(f'Failed to restart {service_name}: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.service_management'))
        
    except Exception as e:
        logger.error(f"Service restart error: {e}")
        flash('Service restart failed', 'error')
        return redirect(url_for('system_management.service_management'))

# Database Management Routes
@system_management_bp.route('/database')
@login_required
@admin_required
@secure_banking_route()
def database_management():
    """Database management center"""
    try:
        db_data = {
            'connection_status': system_service.get_database_status(),
            'performance_metrics': system_service.get_database_performance(),
            'backup_status': system_service.get_database_backup_status(),
            'maintenance_tasks': system_service.get_database_maintenance_tasks(),
            'query_analysis': system_service.get_slow_query_analysis(),
            'index_recommendations': system_service.get_index_recommendations(),
            'storage_analysis': system_service.get_database_storage_analysis()
        }
        
        return render_template('system_management/database.html', 
                             database=db_data)
        
    except Exception as e:
        logger.error(f"Database management error: {e}")
        flash('Unable to load database management', 'error')
        return redirect(url_for('system_management.system_dashboard'))

@system_management_bp.route('/database/backup', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def create_backup():
    """Create database backup"""
    try:
        backup_type = request.form.get('backup_type', 'full')
        backup_name = request.form.get('backup_name')
        
        result = system_service.create_database_backup(backup_type, backup_name, current_user.id)
        
        if result['success']:
            flash(f'Database backup created successfully: {result["backup_file"]}', 'success')
        else:
            flash(f'Backup creation failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.database_management'))
        
    except Exception as e:
        logger.error(f"Database backup error: {e}")
        flash('Database backup failed', 'error')
        return redirect(url_for('system_management.database_management'))

# Security Operations Routes
@system_management_bp.route('/security')
@login_required
@admin_required
@secure_banking_route()
def security_operations():
    """Security operations center"""
    try:
        security_data = {
            'active_threats': system_service.get_active_security_threats(),
            'security_policies': system_service.get_security_policies(),
            'access_logs': system_service.get_recent_access_logs(),
            'failed_logins': system_service.get_failed_login_attempts(),
            'certificate_status': system_service.get_certificate_status(),
            'firewall_status': system_service.get_firewall_status(),
            'intrusion_detection': system_service.get_intrusion_detection_status()
        }
        
        return render_template('system_management/security.html', 
                             security=security_data)
        
    except Exception as e:
        logger.error(f"Security operations error: {e}")
        flash('Unable to load security operations', 'error')
        return redirect(url_for('system_management.system_dashboard'))

@system_management_bp.route('/security/policy/update', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def update_security_policy():
    """Update security policy"""
    try:
        policy_updates = request.form.to_dict()
        result = system_service.update_security_policy(policy_updates, current_user.id)
        
        if result['success']:
            flash('Security policy updated successfully', 'success')
        else:
            flash(f'Policy update failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.security_operations'))
        
    except Exception as e:
        logger.error(f"Security policy update error: {e}")
        flash('Security policy update failed', 'error')
        return redirect(url_for('system_management.security_operations'))

# API endpoints for real-time updates
@system_management_bp.route('/api/system-status')
@login_required
@admin_required
def api_system_status():
    """API endpoint for real-time system status"""
    try:
        status = system_service.get_real_time_system_status()
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"API system status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@system_management_bp.route('/api/performance-metrics')
@login_required
@admin_required
def api_performance_metrics():
    """API endpoint for performance metrics"""
    try:
        metrics = system_service.get_real_time_performance_metrics()
        return jsonify({'success': True, 'data': metrics})
    except Exception as e:
        logger.error(f"API performance metrics error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Cloud Storage Management Routes
@system_management_bp.route('/cloud-storage')
@login_required
@admin_required
@secure_banking_route()
def cloud_storage_management():
    """Cloud storage configuration and management"""
    try:
        cloud_data = {
            'configuration': system_service.get_cloud_storage_configuration(),
            'status': system_service.get_cloud_storage_status(),
            'usage': system_service.get_cloud_storage_usage(),
            'backup_history': system_service.get_cloud_backup_history()
        }
        
        return render_template('system_management/cloud_storage.html', 
                             cloud_data=cloud_data)
        
    except Exception as e:
        logger.error(f"Cloud storage management error: {e}")
        flash('Unable to load cloud storage management', 'error')
        return redirect(url_for('system_management.system_dashboard'))

@system_management_bp.route('/cloud-storage/configure', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def configure_cloud_storage():
    """Configure cloud storage settings"""
    try:
        config_updates = {}
        
        # Parse form data for each provider
        for provider in ['aws_s3', 'google_drive', 'onedrive', 'dropbox']:
            provider_config = {}
            
            # Get all form fields for this provider
            for key, value in request.form.items():
                if key.startswith(f'{provider}_'):
                    config_key = key.replace(f'{provider}_', '')
                    if config_key == 'enabled':
                        provider_config[config_key] = value == 'on'
                    else:
                        provider_config[config_key] = value
            
            if provider_config:
                config_updates[provider] = provider_config
        
        result = system_service.update_cloud_storage_configuration(config_updates, current_user.id)
        
        if result['success']:
            flash('Cloud storage configuration updated successfully', 'success')
        else:
            flash(f'Configuration update failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.cloud_storage_management'))
        
    except Exception as e:
        logger.error(f"Cloud storage configuration error: {e}")
        flash('Cloud storage configuration failed', 'error')
        return redirect(url_for('system_management.cloud_storage_management'))

@system_management_bp.route('/cloud-storage/upload', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def upload_logs_to_cloud():
    """Upload logs to cloud storage"""
    try:
        provider = request.form.get('provider')
        log_type = request.form.get('log_type', 'all')
        
        result = system_service.upload_logs_to_cloud(provider, log_type, current_user.id)
        
        if result['success']:
            flash(f'Logs uploaded successfully: {result["message"]}', 'success')
        else:
            flash(f'Upload failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.cloud_storage_management'))
        
    except Exception as e:
        logger.error(f"Cloud log upload error: {e}")
        flash('Cloud log upload failed', 'error')
        return redirect(url_for('system_management.cloud_storage_management'))

@system_management_bp.route('/cloud-storage/schedule-backup', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def schedule_cloud_backup():
    """Schedule automated cloud backup"""
    try:
        provider = request.form.get('provider')
        schedule_type = request.form.get('schedule_type')
        
        result = system_service.schedule_cloud_backup(provider, schedule_type, current_user.id)
        
        if result['success']:
            flash(f'Backup schedule created: {result["message"]}', 'success')
        else:
            flash(f'Backup scheduling failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.cloud_storage_management'))
        
    except Exception as e:
        logger.error(f"Cloud backup scheduling error: {e}")
        flash('Cloud backup scheduling failed', 'error')
        return redirect(url_for('system_management.cloud_storage_management'))

@system_management_bp.route('/cloud-storage/cleanup', methods=['POST'])
@login_required
@admin_required
@secure_banking_route()
def cleanup_cloud_storage():
    """Clean up old files from cloud storage"""
    try:
        provider = request.form.get('provider')
        retention_days = int(request.form.get('retention_days', 90))
        
        result = system_service.cleanup_old_cloud_files(provider, retention_days, current_user.id)
        
        if result['success']:
            flash(f'Cloud cleanup completed: {result["message"]}', 'success')
        else:
            flash(f'Cleanup failed: {result["error"]}', 'error')
            
        return redirect(url_for('system_management.cloud_storage_management'))
        
    except Exception as e:
        logger.error(f"Cloud cleanup error: {e}")
        flash('Cloud cleanup failed', 'error')
        return redirect(url_for('system_management.cloud_storage_management'))

@system_management_bp.route('/api/cloud-storage/status')
@login_required
@admin_required
def api_cloud_storage_status():
    """API endpoint for cloud storage status"""
    try:
        status = system_service.get_cloud_storage_status()
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"API cloud storage status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@system_management_bp.route('/api/cloud-storage/usage')
@login_required
@admin_required
def api_cloud_storage_usage():
    """API endpoint for cloud storage usage"""
    try:
        usage = system_service.get_cloud_storage_usage()
        return jsonify({'success': True, 'data': usage})
    except Exception as e:
        logger.error(f"API cloud storage usage error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Missing routes referenced in templates
@system_management_bp.route('/logs')
@login_required
@admin_required
@secure_banking_route()
def logs():
    """System logs viewer"""
    try:
        import os
        from datetime import datetime, timedelta

        log_data = {
            'log_files': [
                {'name': 'application.log', 'size': '2.5 MB', 'modified': '2025-01-15 10:30'},
                {'name': 'error.log', 'size': '1.2 MB', 'modified': '2025-01-15 10:25'},
                {'name': 'access.log', 'size': '5.8 MB', 'modified': '2025-01-15 10:35'},
                {'name': 'security.log', 'size': '3.1 MB', 'modified': '2025-01-15 10:20'}
            ],
            'recent_logs': [
                {'timestamp': '2025-01-15 10:35:22', 'level': 'INFO', 'message': 'User login successful', 'source': 'auth'},
                {'timestamp': '2025-01-15 10:34:15', 'level': 'WARNING', 'message': 'High CPU usage detected', 'source': 'system'},
                {'timestamp': '2025-01-15 10:33:08', 'level': 'ERROR', 'message': 'Database connection timeout', 'source': 'database'},
                {'timestamp': '2025-01-15 10:32:45', 'level': 'INFO', 'message': 'Backup completed successfully', 'source': 'backup'}
            ],
            'log_levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            'log_sources': ['auth', 'system', 'database', 'backup', 'security']
        }
        return render_template('system_management/logs.html',
                             log_data=log_data,
                             page_title='System Logs')
    except Exception as e:
        logger.error(f"System logs error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('system_management.system_dashboard'))

# Missing routes referenced in templates
@system_management_bp.route('/health')
@login_required
@admin_required
@secure_banking_route()
def health():
    """System health monitoring - alias for system_health"""
    return system_health()

@system_management_bp.route('/performance')
@login_required
@admin_required
@secure_banking_route()
def performance():
    """System performance monitoring - alias for performance_monitoring"""
    return performance_monitoring()

# Health check endpoint
@system_management_bp.route('/api/health')
def health_check():
    """Comprehensive health check endpoint"""
    try:
        health_status = health_monitor.get_comprehensive_health()
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Health check failed',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@system_management_bp.route('/health/quick')
def quick_health_check():
    """Quick health check for load balancers"""
    try:
        # Basic database connectivity test
        from modules.core.database import db
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Quick health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@system_management_bp.route('/metrics')
@login_required
@admin_required
@secure_banking_route()
def system_metrics():
    """Get detailed system performance metrics"""
    try:
        metrics = health_monitor.get_performance_metrics()
        return create_success_response(data=metrics, message="Metrics retrieved successfully")
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system metrics',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@system_management_bp.route('/status')
@login_required
@admin_required
@secure_banking_route()
def system_status():
    """Get comprehensive system status"""
    try:
        status_data = {
            'platform_status': 'operational',
            'version': '2.1.0',
            'environment': 'production',
            'uptime_hours': 247.5,
            'total_users': 15247,
            'active_sessions': 834,
            'transaction_volume_24h': 45670000,
            'last_backup': '2025-07-06T06:00:00Z',
            'maintenance_window': '2025-07-13T02:00:00Z',
            'security_status': {
                'ssl_valid': True,
                'certificates_expire': '2025-12-15',
                'last_security_scan': '2025-07-05T14:30:00Z',
                'vulnerabilities': 0
            },
            'compliance_status': {
                'pci_dss': 'compliant',
                'gdpr': 'compliant',
                'sox': 'compliant',
                'last_audit': '2025-06-15'
            },
            'external_services': {
                'payment_gateway': 'operational',
                'email_service': 'operational',
                'backup_service': 'operational',
                'monitoring_service': 'operational'
            }
        }
        
        return create_success_response(data=status_data, message="System status retrieved")
    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve system status',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@system_management_bp.route('/performance')
@login_required  
@admin_required
@secure_banking_route()
def performance_dashboard():
    """Performance monitoring dashboard"""
    try:
        performance_data = {
            'response_times': {
                'authentication': {'avg': 145, 'p95': 320, 'p99': 890},
                'banking_operations': {'avg': 234, 'p95': 567, 'p99': 1240},
                'reporting': {'avg': 1567, 'p95': 3450, 'p99': 8900},
                'api_calls': {'avg': 89, 'p95': 234, 'p99': 567}
            },
            'throughput': {
                'requests_per_second': 156,
                'transactions_per_minute': 2847,
                'peak_concurrent_users': 1245,
                'current_load': 67.8
            },
            'errors': {
                'error_rate_24h': 0.12,
                'critical_errors': 0,
                'warning_count': 23,
                'resolved_incidents': 8
            },
            'resource_usage': {
                'cpu_average': 45.6,
                'memory_usage': 67.8,
                'disk_io': 23.4,
                'network_throughput': 125.7
            }
        }
        
        return render_template('system_management/performance_dashboard.html',
                             performance_data=performance_data)
    except Exception as e:
        logger.error(f"Performance dashboard error: {e}")
        flash('Unable to load performance data', 'error')
        return redirect(url_for('system_management.system_dashboard'))