"""
MFA (Multi-Factor Authentication) Module
NVC Banking Platform - Enterprise-grade Multi-Factor Authentication

This module provides comprehensive MFA capabilities including:
- TOTP (Time-based One-Time Password) authentication
- QR code generation for authenticator apps
- MFA setup and management
- Backup codes generation
- MFA enforcement for sensitive operations

Features:
- Integration with Google Authenticator, Authy, Microsoft Authenticator
- Enterprise-grade security with rate limiting
- Audit logging for all MFA operations
- Graceful fallback mechanisms
"""

from flask import Blueprint

# Create MFA blueprint
mfa_bp = Blueprint('mfa', __name__, url_prefix='/mfa', template_folder='templates')

# Import routes to register them
from . import routes

# Module metadata
__version__ = '1.0.0'
__author__ = 'NVC Banking Platform'
__description__ = 'Enterprise Multi-Factor Authentication Module'