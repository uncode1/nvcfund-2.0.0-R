"""
Public Module for NVC Banking Platform
Handles all public-facing pages and contact functionality
"""

from flask import Blueprint
from .services import PublicService
from .chat.routes import chat_bp

__all__ = ['PublicService', 'chat_bp']

def create_public_blueprint():
    """Create and return the public blueprint"""
    from .routes import public_bp
    return public_bp

def get_public_blueprints():
    """Get all public module blueprints for registration"""
    from .routes import public_bp
    from .api import public_api_bp
    return [public_bp, public_api_bp]