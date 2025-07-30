"""
NVC Banking Platform - Services Module
Centralized service management and integration system
"""

from flask import Blueprint
from .routes import services_bp

# Import sub-module blueprints
from .communications.routes import communications_bp
from .mfa.routes import mfa_bp
from .api.routes import api_bp
from .integrations.routes import integrations_bp

from .exchange.routes import exchange_bp
from .analytics.routes import analytics_bp

# Export the blueprint for registration (chat_bp removed - now in modules/public)
__all__ = ['services_bp', 'communications_bp', 'mfa_bp', 'api_bp', 'integrations_bp', 'exchange_bp', 'analytics_bp']