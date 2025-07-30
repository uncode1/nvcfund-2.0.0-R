"""
Secure Route Decorators and Utilities
Provides comprehensive security for data in transit
Integrated with Security Center Module
"""

import functools
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from flask import request, jsonify, g, current_app
from flask_login import current_user
from werkzeug.exceptions import BadRequest, Unauthorized

from .data_security import security_framework, secure_transmission, SecurityError

logger = logging.getLogger(__name__)

def secure_data_transmission(require_encryption: bool = True):
    """
    Decorator for secure data transmission in routes
    Automatically encrypts/decrypts request and response data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Secure incoming data
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    # Get request data
                    if request.is_json:
                        request_data = request.get_json()
                    else:
                        request_data = request.form.to_dict()
                    
                    # Sanitize input data
                    sanitized_data = security_framework.sanitize_input_data(request_data)
                    
                    # Verify transmitted data if encrypted
                    if require_encryption and 'payload' in sanitized_data:
                        verified_data = security_framework.verify_transmitted_data(sanitized_data)
                        if verified_data is None:
                            logger.warning("Data transmission verification failed")
                            return jsonify({'error': 'Data verification failed'}), 400
                        g.secure_request_data = verified_data
                    else:
                        g.secure_request_data = sanitized_data
                        
                except Exception as e:
                    logger.error(f"Request data processing failed: {e}")
                    return jsonify({'error': 'Invalid request data'}), 400
            
            # Execute the original function
            try:
                result = func(*args, **kwargs)
                
                # Secure outgoing data
                if isinstance(result, dict):
                    # Add security headers
                    secured_result = security_framework.secure_data_transmission(
                        result, 
                        f"route_{func.__name__}"
                    )
                    
                    response = jsonify(secured_result)
                    response.headers['X-Content-Type-Options'] = 'nosniff'
                    response.headers['X-Frame-Options'] = 'DENY'
                    response.headers['X-XSS-Protection'] = '1; mode=block'
                    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
                    
                    return response
                elif isinstance(result, tuple) and len(result) == 2:
                    # Handle (data, status_code) tuples
                    data, status_code = result
                    if isinstance(data, dict):
                        secured_data = security_framework.secure_data_transmission(
                            data, 
                            f"route_{func.__name__}"
                        )
                        response = jsonify(secured_data)
                        response.status_code = status_code
                        
                        # Add security headers
                        response.headers['X-Content-Type-Options'] = 'nosniff'
                        response.headers['X-Frame-Options'] = 'DENY'
                        response.headers['X-XSS-Protection'] = '1; mode=block'
                        
                        return response
                
                return result
                
            except Exception as e:
                logger.error(f"Route execution failed: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return wrapper
    return decorator


def banking_grade_security(require_mfa: bool = False, audit_level: str = 'standard'):
    """
    Decorator for banking-grade security on routes
    Implements comprehensive security measures
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Authentication check
            if not current_user.is_authenticated:
                logger.warning("Unauthorized access attempt")
                return jsonify({'error': 'Authentication required'}), 401
            
            # MFA check if required
            if require_mfa and not getattr(current_user, 'mfa_verified', False):
                logger.warning(f"MFA required for user {current_user.id}")
                return jsonify({'error': 'Multi-factor authentication required'}), 403
            
            # Rate limiting check
            if not check_rate_limit(current_user.id, func.__name__):
                logger.warning(f"Rate limit exceeded for user {current_user.id}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Audit logging
            audit_data = {
                'user_id': current_user.id,
                'route': func.__name__,
                'method': request.method,
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string[:200],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if audit_level == 'detailed':
                audit_data['request_data'] = get_sanitized_request_data()
            
            logger.info(f"Banking operation: {func.__name__}", extra=audit_data)
            
            # Execute function with security context
            try:
                g.security_context = {
                    'user_id': current_user.id,
                    'audit_level': audit_level,
                    'timestamp': datetime.utcnow(),
                    'request_id': generate_request_id()
                }
                
                result = func(*args, **kwargs)
                
                # Log successful operation
                logger.info(f"Banking operation completed: {func.__name__}", extra={
                    'user_id': current_user.id,
                    'status': 'success',
                    'request_id': g.security_context['request_id']
                })
                
                return result
                
            except Exception as e:
                # Log failed operation
                logger.error(f"Banking operation failed: {func.__name__}", extra={
                    'user_id': current_user.id,
                    'error': str(e),
                    'request_id': g.security_context.get('request_id', 'unknown')
                })
                raise
        
        return wrapper
    return decorator


def secure_json_response(data: dict, status_code: int = 200, audit_operation: str = None) -> tuple:
    """
    Create a secure JSON response with proper headers and encryption
    """
    # Add metadata to response
    response_data = {
        'data': data,
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': getattr(g, 'security_context', {}).get('request_id', 'unknown')
    }
    
    # Add audit hash if operation specified
    if audit_operation and hasattr(g, 'security_context'):
        audit_hash = security_framework.create_audit_hash(
            audit_operation, 
            data, 
            g.security_context['user_id']
        )
        response_data['audit_hash'] = audit_hash
    
    # Secure the response data
    secured_response = security_framework.secure_data_transmission(
        response_data, 
        audit_operation or 'api_response'
    )
    
    return secured_response, status_code


def validate_secure_request() -> dict:
    """
    Validate and decrypt secure request data
    Returns decrypted data if valid, raises exception if invalid
    """
    if not hasattr(g, 'secure_request_data'):
        if request.is_json:
            return security_framework.sanitize_input_data(request.get_json())
        else:
            return security_framework.sanitize_input_data(request.form.to_dict())
    
    return g.secure_request_data


def check_rate_limit(user_id: str, operation: str, limit: int = 100, window: int = 3600) -> bool:
    """
    Check rate limit for user operation
    Returns True if within limit, False if exceeded
    """
    # This is a simplified implementation
    # In production, you would use Redis or similar for distributed rate limiting
    rate_limit_key = f"rate_limit:{user_id}:{operation}"
    
    # For now, return True (no rate limiting)
    # TODO: Implement proper rate limiting with Redis
    return True


def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return security_framework.secure_token_generation(16)


def get_sanitized_request_data() -> dict:
    """Get sanitized request data for audit logging"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Remove sensitive fields from audit log
        sensitive_keys = ['password', 'pin', 'ssn', 'account_number', 'routing_number']
        sanitized = {}
        
        for key, value in data.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = '***'
            else:
                sanitized[key] = value
        
        return sanitized
    except Exception:
        return {}


def secure_field_validation(field_name: str, field_value: Any, validation_rules: dict) -> bool:
    """
    Validate field data against security rules
    
    Args:
        field_name: Name of the field
        field_value: Value to validate
        validation_rules: Dictionary of validation rules
    
    Returns:
        True if valid, False otherwise
    """
    if not validation_rules:
        return True
    
    # Length validation
    if 'min_length' in validation_rules:
        if len(str(field_value)) < validation_rules['min_length']:
            return False
    
    if 'max_length' in validation_rules:
        if len(str(field_value)) > validation_rules['max_length']:
            return False
    
    # Pattern validation
    if 'pattern' in validation_rules:
        import re
        if not re.match(validation_rules['pattern'], str(field_value)):
            return False
    
    # Type validation
    if 'type' in validation_rules:
        expected_type = validation_rules['type']
        if expected_type == 'email':
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(field_value)):
                return False
        elif expected_type == 'phone':
            import re
            phone_pattern = r'^\+?1?[0-9]{10,}$'
            if not re.match(phone_pattern, str(field_value).replace('-', '').replace(' ', '')):
                return False
        elif expected_type == 'ssn':
            import re
            ssn_pattern = r'^\d{3}-?\d{2}-?\d{4}$'
            if not re.match(ssn_pattern, str(field_value)):
                return False
    
    return True


def secure_database_operation(operation_type: str):
    """
    Decorator for secure database operations
    Adds audit trails and data validation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Pre-operation audit
            if hasattr(g, 'security_context'):
                logger.info(f"Database operation: {operation_type}", extra={
                    'user_id': g.security_context['user_id'],
                    'operation': operation_type,
                    'function': func.__name__
                })
            
            try:
                # Execute the database operation
                result = func(*args, **kwargs)
                
                # Post-operation audit
                if hasattr(g, 'security_context'):
                    logger.info(f"Database operation completed: {operation_type}", extra={
                        'user_id': g.security_context['user_id'],
                        'operation': operation_type,
                        'status': 'success'
                    })
                
                return result
                
            except Exception as e:
                # Error audit
                if hasattr(g, 'security_context'):
                    logger.error(f"Database operation failed: {operation_type}", extra={
                        'user_id': g.security_context.get('user_id', 'unknown'),
                        'operation': operation_type,
                        'error': str(e)
                    })
                raise
        
        return wrapper
    return decorator


# Utility functions for secure route operations
def encrypt_response_data(data: dict) -> dict:
    """Encrypt response data for transmission"""
    return security_framework.secure_data_transmission(data)


def decrypt_request_data(encrypted_data: dict) -> dict:
    """Decrypt request data from transmission"""
    return security_framework.verify_transmitted_data(encrypted_data)


def add_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response