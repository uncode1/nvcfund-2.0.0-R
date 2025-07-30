"""
Admin Management Module - Administrative Functions
Comprehensive admin management system for NVC Banking Platform
"""

from flask import Blueprint
from modules.core.extensions import db

# Import existing models to avoid table conflicts
from modules.auth.models import User
from modules.core.models import Account

from .routes import admin_management_bp, admin_management_hyphen_bp

def init_admin_management_module(app):
    """Initialize the admin management module"""
    try:
        # Register the admin management blueprint
        app.register_blueprint(admin_management_bp, url_prefix='/admin')
        return True
    except Exception as e:
        print(f"Error initializing admin management module: {e}")
        return False

__all__ = ['admin_management_bp', 'admin_management_hyphen_bp', 'init_admin_management_module']