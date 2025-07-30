"""
Analytics Module
NVC Banking Platform - Comprehensive Analytics and Reporting System

This module provides enterprise-grade analytics capabilities including:
- Real-time dashboard analytics
- Compliance reporting
- Risk analytics
- Performance monitoring
- Predictive analytics
- AI-powered insights

Features:
- Real-time data streaming
- Multi-role access control
- Export capabilities
- Interactive visualizations
- Automated report generation
"""

from .routes import analytics_bp
from .services import AnalyticsService

__version__ = "1.0.0"
__author__ = "NVC Banking Platform"

# Module configuration
MODULE_CONFIG = {
    'name': 'Analytics',
    'version': __version__,
    'description': 'Comprehensive analytics and reporting system',
    'blueprints': ['analytics_bp'],
    'dependencies': ['core', 'utils'],
    'health_check_url': '/analytics/api/health',
    'permissions': ['analytics_access', 'reporting_access', 'admin_analytics']
}

# Export main components
__all__ = [
    'analytics_bp',
    'AnalyticsService',
    'MODULE_CONFIG'
]