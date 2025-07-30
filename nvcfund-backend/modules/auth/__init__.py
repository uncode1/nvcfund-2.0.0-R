"""
Auth Module - Authentication and Authorization
Modular authentication system for NVC Banking Platform
"""

from flask import Blueprint
from modules.core.extensions import db

# Import models first
from .models import User

# Then import routes
from .routes import auth_bp
# Enhanced auth routes not implemented yet
ENHANCED_AUTH_AVAILABLE = False
enhanced_auth_bp = None

def init_auth_module(app):
    """Initialize the auth module"""
    try:
        # Register the auth blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        
        # Register enhanced auth blueprint if available
        if ENHANCED_AUTH_AVAILABLE and enhanced_auth_bp:
            app.register_blueprint(enhanced_auth_bp, url_prefix='/auth')

        # Create tables if they don't exist
        with app.app_context():
            db.create_all()

        return True
    except Exception as e:
        print(f"Error initializing auth module: {e}")
        return False

__all__ = ['auth_bp', 'enhanced_auth_bp', 'User', 'init_auth_module']