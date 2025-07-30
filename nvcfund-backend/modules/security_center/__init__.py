"""
Security Center Module
Comprehensive security monitoring and threat management for NVC Banking Platform

Features:
- Real-time threat intelligence and monitoring
- Advanced intrusion detection and prevention
- Security incident response management
- Compliance monitoring and reporting
- Web application firewall controls
- Network security orchestration
"""

__version__ = "1.0.0"
__author__ = "NVC Banking Platform"
"""
Security Center Module - Security Management
Comprehensive security management system for NVC Banking Platform
"""

from flask import Blueprint
from modules.core.extensions import db

# Import existing models to avoid table conflicts
from modules.auth.models import User
from modules.core.models import Account

from .routes import security_center_bp
from .api import security_center_api_bp

def register_blueprints(app):
    """Register security center blueprints"""
    app.register_blueprint(security_center_bp)
    app.register_blueprint(security_center_api_bp)

__all__ = ['security_center_bp', 'register_blueprints']
