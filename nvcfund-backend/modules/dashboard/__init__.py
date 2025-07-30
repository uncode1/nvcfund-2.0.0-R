"""
Dashboard Module - Simplified Self-Contained Implementation
Provides dashboard functionality without complex dependencies
"""

from .routes import dashboard_bp
from .api_routes import dashboard_api_bp

__all__ = ['dashboard_bp', 'dashboard_api_bp']