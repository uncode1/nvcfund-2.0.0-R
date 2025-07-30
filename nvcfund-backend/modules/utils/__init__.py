"""
Utils Module - Self-contained utility services
Provides centralized utility functions for the NVC Banking Platform
"""

from flask import Blueprint
from .services import NavbarContextService, ErrorLoggerService

def create_utils_module():
    """Create and configure the Utils module"""
    utils_bp = Blueprint('utils', __name__, url_prefix='/utils')
    
    # Initialize services
    navbar_service = NavbarContextService()
    error_service = ErrorLoggerService()
    
    return utils_bp, navbar_service, error_service

__all__ = ['create_utils_module', 'NavbarContextService', 'ErrorLoggerService']