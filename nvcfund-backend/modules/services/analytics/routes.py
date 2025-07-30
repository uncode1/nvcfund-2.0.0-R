"""
Analytics Routes
NVC Banking Platform - Analytics and Reporting Dashboard Routes

This module provides routes for:
- Analytics dashboard
- Executive reporting
- Performance metrics
- Compliance analytics
- Risk analytics
"""

from flask import Blueprint, render_template, request, redirect, url_for, g
from flask_login import login_required, current_user
from modules.core.rbac import admin_required as admin_access, treasury_required as treasury_access
from modules.core.security_enforcement import secure_banking_route
from modules.utils.services import ErrorLoggerService
from .services import AnalyticsService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics', template_folder='templates')

# Initialize services
analytics_service = AnalyticsService()
error_logger = ErrorLoggerService()

@analytics_bp.route('/')
@analytics_bp.route('/dashboard')
@login_required
@admin_access
def analytics_dashboard():
    """
    Main analytics dashboard
    Comprehensive analytics overview for admins and executives
    """
    try:
        # Get user role for data filtering
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else 'standard'
        
        # Get dashboard analytics
        analytics_data = analytics_service.get_dashboard_analytics(current_user.id, user_role)
        
        # Prepare template context
        template_context = {
            'analytics': analytics_data.get('data', {}),
            'user_role': user_role,
            'page_title': 'Analytics Dashboard',
            'current_time': datetime.utcnow().isoformat(),
            'refresh_interval': 30000  # 30 seconds for real-time updates
        }
        
        # Return simple success page if templates don't exist
        return f"""
        <html>
        <head><title>Analytics Dashboard</title></head>
        <body>
            <h1>Analytics Dashboard</h1>
            <p>Welcome to the Analytics Dashboard, {current_user.username}!</p>
            <p>User Role: {user_role}</p>
            <p>Current Time: {datetime.utcnow().isoformat()}</p>
            <p>Analytics Data: {len(analytics_data.get('data', {}))} metrics loaded</p>
            <a href="/auth/logout">Logout</a>
        </body>
        </html>
        """
        
    except Exception as e:
        error_logger.log_error(f"Analytics dashboard error: {str(e)}")
        return f"""
        <html>
        <head><title>Analytics Error</title></head>
        <body>
            <h1>Analytics Error</h1>
            <p>Unable to load analytics dashboard: {str(e)}</p>
            <a href="/auth/logout">Logout</a>
        </body>
        </html>
        """

@analytics_bp.route('/financial')
@login_required
@admin_access
def financial_analytics():
    """
    Financial analytics dashboard
    Detailed financial metrics and performance indicators
    """
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else 'standard'
        analytics_data = analytics_service.get_dashboard_analytics(current_user.id, user_role)
        
        template_context = {
            'financial_metrics': analytics_data.get('data', {}).get('financial_metrics', {}),
            'transaction_analytics': analytics_data.get('data', {}).get('transaction_analytics', {}),
            'performance_indicators': analytics_data.get('data', {}).get('performance_indicators', {}),
            'trends': analytics_data.get('data', {}).get('trends', {}),
            'user_role': user_role,
            'page_title': 'Financial Analytics'
        }
        
        return render_template('analytics/analytics_dashboard.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Financial analytics error: {str(e)}")
        return render_template('analytics/analytics_dashboard.html', 
                             error_message="Unable to load financial analytics")

@analytics_bp.route('/risk')
@login_required
@admin_access
def risk_analytics():
    """
    Risk analytics dashboard
    Risk assessment, compliance, and security metrics
    """
    try:
        user_role = current_user.role.value if hasattr(current_user.role, 'value') else 'standard'
        
        # Check if user has risk analytics access
        if user_role not in ['admin', 'risk_manager', 'compliance_officer']:
            return render_template('analytics/analytics_access_denied.html',
                                 message="Risk analytics require elevated privileges")
        
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'risk_metrics': analytics_data.get('data', {}).get('risk_metrics', {}),
            'compliance_status': analytics_data.get('data', {}).get('compliance_status', {}),
            'real_time_stats': analytics_data.get('data', {}).get('real_time_stats', {}),
            'user_role': user_role,
            'page_title': 'Risk Analytics'
        }
        
        return render_template('analytics/analytics_dashboard.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Risk analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load risk analytics")

@analytics_bp.route('/performance-metrics')
@login_required
@admin_access
def performance_metrics():
    """Performance metrics dashboard with real-time monitoring"""
    try:
        user_role = getattr(g.user, 'role', 'standard')
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'performance_data': analytics_data.get('data', {}).get('performance_metrics', {}),
            'real_time_stats': analytics_data.get('data', {}).get('real_time_stats', {}),
            'user_role': user_role,
            'page_title': 'Performance Metrics'
        }
        
        return render_template('analytics/performance_metrics.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Performance metrics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load performance metrics")

@analytics_bp.route('/user-analytics')
@login_required
@admin_access
def user_analytics():
    """User analytics dashboard with engagement metrics"""
    try:
        user_role = getattr(g.user, 'role', 'standard')
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'user_metrics': analytics_data.get('data', {}).get('user_analytics', {}),
            'engagement_stats': analytics_data.get('data', {}).get('engagement_metrics', {}),
            'user_role': user_role,
            'page_title': 'User Analytics'
        }
        
        return render_template('analytics/user_analytics.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"User analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load user analytics")

@analytics_bp.route('/performance')
@login_required
@admin_access
def performance_analytics():
    """
    Performance analytics dashboard
    System performance, uptime, and operational metrics
    """
    try:
        user_role = getattr(g.user, 'role', 'standard')
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'performance_indicators': analytics_data.get('data', {}).get('performance_indicators', {}),
            'user_activity': analytics_data.get('data', {}).get('user_activity', {}),
            'real_time_stats': analytics_data.get('data', {}).get('real_time_stats', {}),
            'trends': analytics_data.get('data', {}).get('trends', {}),
            'user_role': user_role,
            'page_title': 'Performance Analytics'
        }
        
        return render_template('analytics/performance_analytics.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Performance analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load performance analytics")

@analytics_bp.route('/compliance')
@login_required
@admin_access
def compliance_analytics():
    """
    Compliance analytics dashboard
    Regulatory compliance, audit, and governance metrics
    """
    try:
        user_role = getattr(g.user, 'role', 'standard')
        
        # Check compliance access
        if user_role not in ['admin', 'compliance_officer', 'risk_manager']:
            return render_template('analytics/analytics_access_denied.html',
                                 message="Compliance analytics require elevated privileges")
        
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'compliance_status': analytics_data.get('data', {}).get('compliance_status', {}),
            'risk_metrics': analytics_data.get('data', {}).get('risk_metrics', {}),
            'user_role': user_role,
            'page_title': 'Compliance Analytics'
        }
        
        return render_template('analytics/compliance_analytics.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Compliance analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load compliance analytics")

@analytics_bp.route('/executive')
@login_required
@admin_access
def executive_dashboard():
    """
    Executive dashboard
    High-level strategic metrics for C-level executives
    """
    try:
        user_role = getattr(g.user, 'role', 'standard')
        
        # Check executive access
        if user_role not in ['admin', 'executive', 'ceo', 'cfo']:
            return render_template('analytics/analytics_access_denied.html',
                                 message="Executive dashboard requires C-level access")
        
        # Get executive report
        report_type = request.args.get('report_type', 'monthly')
        executive_report = analytics_service.generate_executive_report(report_type, user_role)
        
        if executive_report.get('status') == 'error':
            return render_template('analytics/analytics_error.html', 
                                 error_message=executive_report.get('error'))
        
        template_context = {
            'executive_data': executive_report.get('data', {}),
            'recommendations': executive_report.get('recommendations', []),
            'report_type': report_type,
            'user_role': user_role,
            'page_title': 'Executive Dashboard'
        }
        
        return render_template('analytics/executive_dashboard.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Executive dashboard error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load executive dashboard")

@analytics_bp.route('/reports')
@login_required
@admin_access
def reports_center():
    """
    Reports center
    Access to various analytics reports and export options
    """
    try:
        user_role = getattr(g.user, 'role', 'standard')
        
        # Available reports based on user role
        available_reports = {
            'financial_summary': {
                'title': 'Financial Summary Report',
                'description': 'Comprehensive financial performance metrics',
                'access': ['admin', 'cfo', 'executive'],
                'formats': ['PDF', 'Excel', 'CSV']
            },
            'risk_assessment': {
                'title': 'Risk Assessment Report',
                'description': 'Risk analysis and compliance status',
                'access': ['admin', 'risk_manager', 'compliance_officer'],
                'formats': ['PDF', 'Excel']
            },
            'performance_metrics': {
                'title': 'Performance Metrics Report',
                'description': 'System and operational performance indicators',
                'access': ['admin', 'executive'],
                'formats': ['PDF', 'Excel', 'CSV']
            },
            'compliance_audit': {
                'title': 'Compliance Audit Report',
                'description': 'Regulatory compliance and audit findings',
                'access': ['admin', 'compliance_officer'],
                'formats': ['PDF']
            },
            'executive_summary': {
                'title': 'Executive Summary Report',
                'description': 'High-level strategic overview for executives',
                'access': ['admin', 'executive', 'ceo', 'cfo'],
                'formats': ['PDF', 'PowerPoint']
            }
        }
        
        # Filter reports by user access
        accessible_reports = {
            key: report for key, report in available_reports.items()
            if user_role in report['access']
        }
        
        template_context = {
            'available_reports': accessible_reports,
            'user_role': user_role,
            'page_title': 'Reports Center'
        }
        
        return render_template('analytics/reports_center.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Reports center error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load reports center")

@analytics_bp.route('/real-time')
@login_required
@admin_access
def real_time_analytics():
    """
    Real-time analytics dashboard
    Live streaming analytics and monitoring
    """
    try:
        user_role = getattr(g.user, 'role', 'standard')
        analytics_data = analytics_service.get_dashboard_analytics(user_role)
        
        template_context = {
            'real_time_stats': analytics_data.get('data', {}).get('real_time_stats', {}),
            'user_activity': analytics_data.get('data', {}).get('user_activity', {}),
            'transaction_analytics': analytics_data.get('data', {}).get('transaction_analytics', {}),
            'user_role': user_role,
            'page_title': 'Real-Time Analytics',
            'websocket_url': '/analytics/api/websocket',
            'refresh_interval': 5000  # 5 seconds for real-time updates
        }
        
        return render_template('analytics/real_time_analytics.html', **template_context)
        
    except Exception as e:
        error_logger.log_error(f"Real-time analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html', 
                             error_message="Unable to load real-time analytics")

# Health check route
@analytics_bp.route('/health')
def health_check():
    """
    Analytics module health check
    Returns JSON health status
    """
    try:
        # Basic service health check
        test_analytics = analytics_service.get_dashboard_analytics('admin')
        
        if test_analytics.get('status') == 'success':
            return {'status': 'healthy', 'app_module': 'analytics', 'timestamp': datetime.utcnow().isoformat()}
        else:
            return {'status': 'degraded', 'app_module': 'analytics', 'timestamp': datetime.utcnow().isoformat()}
            
    except Exception as e:
        return {'status': 'unhealthy', 'app_module': 'analytics', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()}

# Legacy Monitoring Integration (Phase 2 Consolidation)

@analytics_bp.route('/system-monitoring')
@login_required
@admin_access
def system_monitoring():
    """Advanced system monitoring dashboard with legacy features"""
    try:
        monitoring_data = analytics_service.get_system_monitoring_data(current_user.id)
        
        logger.info(f"System monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'SYSTEM_MONITORING_ACCESS',
            'app_module': 'analytics'
        })
        
        return render_template('analytics/system_monitoring.html', 
                             monitoring_data=monitoring_data)
        
    except Exception as e:
        logger.error(f"System monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'analytics'
        })
        flash('Error loading system monitoring', 'error')
        return redirect(url_for('analytics.analytics_dashboard'))

@analytics_bp.route('/performance-analysis')
@login_required
@admin_access
def performance_analysis():
    """Performance analysis dashboard with route optimization"""
    try:
        performance_data = analytics_service.get_performance_analysis_data(current_user.id)
        
        logger.info(f"Performance analysis accessed", extra={
            'user_id': current_user.id,
            'action': 'PERFORMANCE_ANALYSIS_ACCESS',
            'app_module': 'analytics'
        })
        
        return render_template('analytics/performance_analysis.html', 
                             performance_data=performance_data)
        
    except Exception as e:
        logger.error(f"Performance analysis error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'analytics'
        })
        flash('Error loading performance analysis', 'error')
        return redirect(url_for('analytics.analytics_dashboard'))

@analytics_bp.route('/network-monitoring')
@login_required
@admin_access
def network_monitoring():
    """Network performance and security monitoring"""
    try:
        network_data = analytics_service.get_network_monitoring_data(current_user.id)
        
        logger.info(f"Network monitoring accessed", extra={
            'user_id': current_user.id,
            'action': 'NETWORK_MONITORING_ACCESS',
            'app_module': 'analytics'
        })
        
        return render_template('analytics/network_monitoring.html', 
                             network_data=network_data)
        
    except Exception as e:
        logger.error(f"Network monitoring error: {e}", extra={
            'user_id': current_user.id,
            'error': str(e),
            'app_module': 'analytics'
        })
        flash('Error loading network monitoring', 'error')
        return redirect(url_for('analytics.analytics_dashboard'))

# Drill-down routes for detailed views
@analytics_bp.route('/financial/detailed')
@login_required
@admin_access
def financial_detailed():
    """Detailed financial analytics drill-down view"""
    try:
        return render_template('analytics/financial_detailed.html',
                             user=current_user,
                             page_title='Detailed Financial Analytics')
    except Exception as e:
        error_logger.log_error("FINANCIAL_DETAILED_ERROR", str(e), {"user_id": current_user.id})
        return redirect(url_for('analytics.analytics_dashboard'))

@analytics_bp.route('/performance/metrics')
@login_required
@admin_access
def performance_metrics():
    """Performance metrics drill-down view"""
    try:
        return render_template('analytics/performance_metrics.html',
                             user=current_user,
                             page_title='Performance Metrics')
    except Exception as e:
        error_logger.log_error("PERFORMANCE_METRICS_ERROR", str(e), {"user_id": current_user.id})
        return redirect(url_for('analytics.analytics_dashboard'))

@analytics_bp.route('/risk/analytics')
@login_required
@admin_access
def risk_analytics():
    """Risk analytics drill-down view"""
    try:
        return render_template('analytics/risk_analytics.html',
                             user=current_user,
                             page_title='Risk Analytics')
    except Exception as e:
        error_logger.log_error("RISK_ANALYTICS_ERROR", str(e), {"user_id": current_user.id})
        return redirect(url_for('analytics.analytics_dashboard'))

@analytics_bp.route('/compliance/monitoring')
@login_required
@admin_access
def compliance_monitoring():
    """Compliance monitoring drill-down view"""
    try:
        return render_template('analytics/compliance_monitoring.html',
                             user=current_user,
                             page_title='Compliance Monitoring')
    except Exception as e:
        error_logger.log_error("COMPLIANCE_MONITORING_ERROR", str(e), {"user_id": current_user.id})
        return redirect(url_for('analytics.analytics_dashboard'))

# Error handlers
@analytics_bp.errorhandler(403)
def forbidden_error(error):
    return render_template('analytics/analytics_access_denied.html', 
                         message="Access denied: insufficient privileges for analytics")

@analytics_bp.errorhandler(404)
def not_found_error(error):
    return render_template('analytics/analytics_error.html', 
                         error_message="Analytics page not found")

@analytics_bp.errorhandler(500)
def internal_error(error):
    return render_template('analytics/analytics_error.html', 
                         error_message="Internal analytics system error")

# Missing routes referenced in templates
@analytics_bp.route('/custom-dashboard')
@login_required
def custom_dashboard():
    """Custom analytics dashboard"""
    try:
        custom_data = {
            'widgets': [
                {'name': 'Revenue Trends', 'type': 'line_chart', 'data': [100, 120, 140, 160, 180]},
                {'name': 'User Activity', 'type': 'bar_chart', 'data': [50, 75, 90, 85, 95]},
                {'name': 'Transaction Volume', 'type': 'area_chart', 'data': [200, 250, 300, 280, 320]}
            ],
            'customization_options': ['Chart Type', 'Time Range', 'Data Source', 'Filters']
        }
        return render_template('analytics/custom_dashboard.html',
                             custom_data=custom_data,
                             page_title='Custom Analytics Dashboard')
    except Exception as e:
        error_logger.log_error(f"Custom dashboard error: {str(e)}")
        return render_template('analytics/analytics_error.html',
                             error_message="Unable to load custom dashboard")

@analytics_bp.route('/executive-analytics')
@login_required
def executive_analytics():
    """Executive analytics dashboard"""
    try:
        executive_data = {
            'kpi_summary': {
                'revenue': 12500000.00,
                'growth_rate': 15.2,
                'customer_acquisition': 2547,
                'retention_rate': 94.5
            },
            'executive_reports': [
                {'name': 'Monthly Performance', 'status': 'Ready', 'date': '2025-01-15'},
                {'name': 'Quarterly Review', 'status': 'In Progress', 'date': '2025-01-20'},
                {'name': 'Annual Strategy', 'status': 'Scheduled', 'date': '2025-02-01'}
            ]
        }
        return render_template('analytics/executive_analytics.html',
                             executive_data=executive_data,
                             page_title='Executive Analytics')
    except Exception as e:
        error_logger.log_error(f"Executive analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html',
                             error_message="Unable to load executive analytics")

@analytics_bp.route('/schedule-report')
@login_required
def schedule_report():
    """Schedule analytics report"""
    try:
        schedule_data = {
            'report_types': ['Daily Summary', 'Weekly Analysis', 'Monthly Report', 'Quarterly Review'],
            'delivery_options': ['Email', 'Dashboard', 'API', 'Download'],
            'frequency_options': ['Daily', 'Weekly', 'Monthly', 'Quarterly']
        }
        return render_template('analytics/schedule_report.html',
                             schedule_data=schedule_data,
                             page_title='Schedule Report')
    except Exception as e:
        error_logger.log_error(f"Schedule report error: {str(e)}")
        return render_template('analytics/analytics_error.html',
                             error_message="Unable to load schedule report")

@analytics_bp.route('/transaction-analytics')
@login_required
def transaction_analytics():
    """Transaction analytics dashboard"""
    try:
        transaction_data = {
            'daily_transactions': 2547,
            'transaction_volume': 12500000.00,
            'success_rate': 99.7,
            'average_amount': 4907.32,
            'transaction_trends': [
                {'date': '2025-01-15', 'count': 2547, 'volume': 12500000.00},
                {'date': '2025-01-14', 'count': 2398, 'volume': 11800000.00},
                {'date': '2025-01-13', 'count': 2654, 'volume': 13200000.00}
            ]
        }
        return render_template('analytics/transaction_analytics.html',
                             transaction_data=transaction_data,
                             page_title='Transaction Analytics')
    except Exception as e:
        error_logger.log_error(f"Transaction analytics error: {str(e)}")
        return render_template('analytics/analytics_error.html',
                             error_message="Unable to load transaction analytics")