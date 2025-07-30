"""
Auth Module Configuration
Comprehensive configuration for enterprise authentication module
"""

import os
from datetime import timedelta
from .models import UserRole

class AuthConfig:
    """Authentication module configuration"""
    
    # Session Configuration
    SESSION_TIMEOUT = timedelta(minutes=15)  # Banking-grade security
    ADMIN_SESSION_TIMEOUT = timedelta(minutes=10)  # Shorter for admin users
    REMEMBER_COOKIE_DURATION = timedelta(days=1)
    
    # Password Requirements - Banking-Grade Security
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    MIN_UPPERCASE_COUNT = 2
    MIN_LOWERCASE_COUNT = 2
    MIN_NUMBERS_COUNT = 2
    MIN_SPECIAL_CHARS_COUNT = 2
    FORBIDDEN_PATTERNS = [
        'password', 'admin', 'user', 'banking', 'nvc', 'fund',
        '12345', 'qwerty', 'abcdef', 'password123', 'admin123'
    ]
    
    # Security Settings
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION = timedelta(minutes=30)
    ENABLE_2FA = True
    
    # Registration Settings
    REQUIRE_EMAIL_VERIFICATION = True
    REQUIRE_KYC_VERIFICATION = True
    MIN_AGE_REQUIREMENT = 18
    
    # Template Configuration
    TEMPLATE_FOLDER = 'auth'
    LOGIN_TEMPLATE = 'modular_auth_login.html'
    REGISTER_TEMPLATE = 'modular_auth_register.html'
    LOGOUT_TEMPLATE = 'modular_auth_logout.html'
    FORGOT_PASSWORD_TEMPLATE = 'modular_auth_forgot_password.html'
    RESET_PASSWORD_TEMPLATE = 'modular_auth_reset_password.html'
    
    # URL Configuration
    LOGIN_URL = '/auth/login'
    LOGOUT_URL = '/auth/logout'
    REGISTER_URL = '/auth/register'
    FORGOT_PASSWORD_URL = '/auth/forgot-password'
    RESET_PASSWORD_URL = '/auth/reset-password'
    
    # Redirect Configuration
    POST_LOGIN_REDIRECT = '/dashboard/'
    POST_LOGOUT_REDIRECT = '/auth/login'
    POST_REGISTER_REDIRECT = '/auth/login'
    
    @classmethod
    def get_session_timeout(cls, user_role=None):
        """Get session timeout based on user role"""
        if user_role in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
            return cls.ADMIN_SESSION_TIMEOUT
        return cls.SESSION_TIMEOUT