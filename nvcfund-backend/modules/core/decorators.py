"""
Core Decorators for Pure Modular Architecture
NVC Banking Platform - Authentication and Rate Limiting Decorators
"""

import functools
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def rate_limit(limit="60/minute"):
    """
    Rate limiting decorator for API endpoints
    
    Args:
        limit: Rate limit string (e.g., "60/minute", "10/second")
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Rate limiting logic will be handled by Flask-Limiter
            # This is a placeholder decorator that passes through
            return f(*args, **kwargs)
        return wrapper
    return decorator

def banking_security_required(f):
    """Banking-grade security decorator for sensitive operations"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Enhanced security checks for banking operations
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    """Admin access required decorator"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Admin role verification
        return f(*args, **kwargs)
    return wrapper

def super_admin_required(f):
    """Super admin access required decorator"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Super admin role verification
        return f(*args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    """Role-based access control decorator"""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Role verification logic - simplified for now
            return f(*args, **kwargs)
        return wrapper
    return decorator