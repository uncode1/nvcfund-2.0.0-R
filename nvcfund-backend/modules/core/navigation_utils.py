"""
Navigation Utilities
RBAC-controlled navigation utilities for the NVC Banking Platform
"""

from flask_login import current_user
from modules.auth.models import UserRole
import logging

logger = logging.getLogger(__name__)

def is_view_only_mode():
    """Simple view-only mode check"""
    return False

def get_user_nav_items(user):
    """
    Get user navigation items based on RBAC permissions
    This is a simplified version that delegates to the NavbarContextService
    """
    try:
        from modules.utils.services import NavbarContextService
        navbar_service = NavbarContextService()
        
        # Get user role as string
        user_role = getattr(user, 'role', None)
        if user_role:
            if hasattr(user_role, 'value'):
                role_str = user_role.value.lower()
            elif hasattr(user_role, 'name'):
                role_str = user_role.name.lower()
            else:
                role_str = str(user_role).lower()
        else:
            role_str = 'standard_user'
            
        # Get navigation context from service
        navbar_context = navbar_service.get_navbar_context()
        user_navigation = navbar_context.get('user_navigation', {})

        # Defensive check: ensure all navigation items are lists, not method references
        for section_key, section in user_navigation.items():
            if callable(section.get('items')):
                logger.warning(f"Navigation section '{section_key}' has callable items, converting to list")
                section['items'] = section['items']()
            elif not isinstance(section.get('items'), list):
                logger.warning(f"Navigation section '{section_key}' has non-list items: {type(section.get('items'))}")
                section['items'] = []

        # Return in the expected format for backward compatibility
        return {
            'nav_items': [],
            'dropdowns': user_navigation
        }
    except Exception as e:
        logger.error(f"Error getting user navigation items: {e}")
        return {
            'nav_items': [],
            'dropdowns': {}
        }
