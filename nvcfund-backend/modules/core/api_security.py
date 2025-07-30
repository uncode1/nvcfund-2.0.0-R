"""
Comprehensive API Security Framework
Banking-grade API endpoint protection for NVC Banking Platform
"""

import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any
from flask import request, jsonify, current_app, g
from flask_login import current_user
import logging
import redis
import os
from ipaddress import ip_address, ip_network

logger = logging.getLogger(__name__)

class APISecurityManager:
    """Centralized API security management"""
    
    def __init__(self):
        self.redis_client = None
        self.blocked_ips = set()
        self.rate_limits = self._init_rate_limits()
        self.security_rules = self._init_security_rules()
        
    def _init_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Initialize role-based rate limits"""
        return {
            'public': {
                'requests_per_minute': 30,
                'requests_per_hour': 500,
                'burst_limit': 10
            },
            'standard_user': {
                'requests_per_minute': 100,
                'requests_per_hour': 2000,
                'burst_limit': 25
            },
            'business_user': {
                'requests_per_minute': 200,
                'requests_per_hour': 5000,
                'burst_limit': 50
            },
            'admin': {
                'requests_per_minute': 500,
                'requests_per_hour': 10000,
                'burst_limit': 100
            },
            'super_admin': {
                'requests_per_minute': 1000,
                'requests_per_hour': 20000,
                'burst_limit': 200
            }
        }
    
    def _init_security_rules(self) -> Dict[str, Any]:
        """Initialize security rules and patterns"""
        return {
            'suspicious_patterns': [
                r'(?i)(\bunion\s+select\b)',
                r'(?i)(\bdrop\s+table\b)',
                r'(?i)(\bdelete\s+from\b)',
                r'(?i)(\binsert\s+into\b)',
                r'(?i)(\bupdate\s+set\b)',
                r'(?i)(<script[\s\S]*?>)',
                r'(?i)(javascript:)',
                r'(?i)(\beval\s*\()',
                r'(?i)(\balert\s*\()'
            ],
            'blocked_user_agents': [
                'sqlmap',
                'nikto',
                'nmap',
                'masscan',
                'burpsuite',
                'havij'
            ],
            'allowed_origins': [
                'https://nvcfund.com',
                'https://www.nvcfund.com',
                'https://app.nvcfund.com',
                'https://admin.nvcfund.com'
            ],
            'trusted_networks': [
                '10.0.0.0/8',
                '172.16.0.0/12',
                '192.168.0.0/16'
            ]
        }

# Global security manager instance
security_manager = APISecurityManager()

def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Validate API key and return user context"""
    if not api_key:
        return None
    
    try:
        # API key format: nvc_live_xxxxxxxxxxxx or nvc_test_xxxxxxxxxxxx
        if not (api_key.startswith('nvc_live_') or api_key.startswith('nvc_test_')):
            return None
        
        # In production, validate against database
        # For now, basic validation
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Mock validation - replace with database lookup
        valid_keys = {
            'nvc_test_1234567890abcdef': {
                'user_id': 1,
                'role': 'super_admin',
                'permissions': ['all'],
                'rate_limit_tier': 'super_admin'
            }
        }
        
        return valid_keys.get(api_key)
    except Exception as e:
        logger.error(f"API key validation error: {e}")
        return None

def check_rate_limit(user_role: str = 'public', endpoint: str = 'default') -> bool:
    """Check if request is within rate limits"""
    try:
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else 'anonymous'
        
        # Create rate limit key
        rate_key = f"rate_limit:{client_ip}:{user_id}:{endpoint}"
        minute_key = f"{rate_key}:minute"
        hour_key = f"{rate_key}:hour"
        
        limits = security_manager.rate_limits.get(user_role, security_manager.rate_limits['public'])
        
        # Simple in-memory rate limiting (replace with Redis in production)
        current_time = int(time.time())
        minute_window = current_time // 60
        hour_window = current_time // 3600
        
        # Check minute limits
        minute_count = getattr(g, f'rate_{minute_window}_{minute_key}', 0) + 1
        setattr(g, f'rate_{minute_window}_{minute_key}', minute_count)
        
        if minute_count > limits['requests_per_minute']:
            logger.warning(f"Rate limit exceeded for {client_ip}: {minute_count} requests/minute")
            return False
        
        # Check hour limits
        hour_count = getattr(g, f'rate_{hour_window}_{hour_key}', 0) + 1
        setattr(g, f'rate_{hour_window}_{hour_key}', hour_count)
        
        if hour_count > limits['requests_per_hour']:
            logger.warning(f"Hourly rate limit exceeded for {client_ip}: {hour_count} requests/hour")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow request on error to avoid service disruption

def validate_request_signature(request_data: bytes, signature: str, secret: str) -> bool:
    """Validate HMAC signature for sensitive operations"""
    try:
        expected_signature = hmac.new(
            secret.encode(),
            request_data,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    except Exception as e:
        logger.error(f"Signature validation error: {e}")
        return False

def check_security_threats(request_data: str) -> List[str]:
    """Check for common security threats in request data"""
    threats = []
    
    try:
        import re
        
        # Check for SQL injection patterns
        for pattern in security_manager.security_rules['suspicious_patterns']:
            if re.search(pattern, request_data):
                threats.append(f"Suspicious pattern detected: {pattern}")
        
        # Check user agent
        user_agent = request.headers.get('User-Agent', '').lower()
        for blocked_agent in security_manager.security_rules['blocked_user_agents']:
            if blocked_agent in user_agent:
                threats.append(f"Blocked user agent: {blocked_agent}")
        
        return threats
        
    except Exception as e:
        logger.error(f"Security threat check error: {e}")
        return []

def api_auth_required(allowed_roles: List[str] = None):
    """Enhanced API authentication decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for API key authentication
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            auth_header = request.headers.get('Authorization', '')
            
            user_context = None
            user_role = 'public'
            
            # API Key authentication
            if api_key:
                user_context = validate_api_key(api_key)
                if not user_context:
                    return jsonify({
                        'error': 'Invalid API key',
                        'code': 'INVALID_API_KEY'
                    }), 401
                user_role = user_context.get('role', 'standard_user')
            
            # Bearer token authentication
            elif auth_header.startswith('Bearer '):
                token = auth_header.split(' ', 1)[1]
                # Validate JWT token (implement JWT validation)
                user_role = 'standard_user'  # Extract from token
            
            # Session-based authentication
            elif current_user.is_authenticated:
                user_role = str(getattr(current_user, 'role', 'standard_user'))
            
            # Check role permissions
            if allowed_roles and user_role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'required_roles': allowed_roles
                }), 403
            
            # Set user context in request
            g.api_user_context = user_context
            g.api_user_role = user_role
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_rate_limit(tier: str = 'public'):
    """API rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = getattr(g, 'api_user_role', tier)
            endpoint = f"{request.endpoint}"
            
            if not check_rate_limit(user_role, endpoint):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': 60
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_security_check():
    """Comprehensive API security check decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Get client information
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
                user_agent = request.headers.get('User-Agent', '')
                origin = request.headers.get('Origin', '')
                
                # Check if IP is blocked
                if client_ip in security_manager.blocked_ips:
                    logger.warning(f"Blocked IP attempted access: {client_ip}")
                    return jsonify({
                        'error': 'Access denied',
                        'code': 'IP_BLOCKED'
                    }), 403
                
                # Check origin for CORS
                if origin and origin not in security_manager.security_rules['allowed_origins']:
                    logger.warning(f"Unauthorized origin: {origin}")
                    return jsonify({
                        'error': 'Unauthorized origin',
                        'code': 'CORS_VIOLATION'
                    }), 403
                
                # Check request data for threats
                request_data = ''
                if request.is_json:
                    request_data = str(request.get_json())
                elif request.form:
                    request_data = str(dict(request.form))
                elif request.args:
                    request_data = str(dict(request.args))
                
                threats = check_security_threats(request_data)
                if threats:
                    logger.warning(f"Security threats detected from {client_ip}: {threats}")
                    return jsonify({
                        'error': 'Security violation detected',
                        'code': 'SECURITY_VIOLATION'
                    }), 400
                
                # Log API access
                logger.info(f"API access: {request.method} {request.path} from {client_ip}")
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"API security check error: {e}")
                return jsonify({
                    'error': 'Security check failed',
                    'code': 'SECURITY_ERROR'
                }), 500
        
        return decorated_function
    return decorator

def api_audit_log():
    """API audit logging decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_id = getattr(current_user, 'id', None) if current_user.is_authenticated else None
            
            audit_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path,
                'client_ip': client_ip,
                'user_id': user_id,
                'user_agent': request.headers.get('User-Agent', ''),
                'request_id': str(uuid.uuid4())
            }
            
            try:
                response = f(*args, **kwargs)
                
                # Log successful request
                audit_data.update({
                    'status': 'success',
                    'response_time': round((time.time() - start_time) * 1000, 2),
                    'status_code': getattr(response, 'status_code', 200)
                })
                
                logger.info("API audit log", extra=audit_data)
                return response
                
            except Exception as e:
                # Log failed request
                audit_data.update({
                    'status': 'error',
                    'error': str(e),
                    'response_time': round((time.time() - start_time) * 1000, 2)
                })
                
                logger.error("API audit log - error", extra=audit_data)
                raise
        
        return decorated_function
    return decorator

def secure_api_endpoint(allowed_roles: List[str] = None, rate_limit_tier: str = 'public', require_signature: bool = False):
    """Combined secure API endpoint decorator"""
    def decorator(f):
        @api_security_check()
        @api_rate_limit(rate_limit_tier)
        @api_auth_required(allowed_roles)
        @api_audit_log()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Additional signature validation for sensitive operations
            if require_signature:
                signature = request.headers.get('X-Signature')
                if not signature:
                    return jsonify({
                        'error': 'Signature required',
                        'code': 'SIGNATURE_REQUIRED'
                    }), 400
                
                # Validate signature
                secret = current_app.config.get('API_SIGNATURE_SECRET', 'default-secret')
                request_data = request.get_data()
                
                if not validate_request_signature(request_data, signature, secret):
                    return jsonify({
                        'error': 'Invalid signature',
                        'code': 'INVALID_SIGNATURE'
                    }), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def block_ip(ip_address: str, reason: str = "Security violation"):
    """Block an IP address"""
    security_manager.blocked_ips.add(ip_address)
    logger.warning(f"IP blocked: {ip_address} - Reason: {reason}")

def unblock_ip(ip_address: str):
    """Unblock an IP address"""
    security_manager.blocked_ips.discard(ip_address)
    logger.info(f"IP unblocked: {ip_address}")

def get_api_security_status() -> Dict[str, Any]:
    """Get current API security status"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'blocked_ips_count': len(security_manager.blocked_ips),
        'rate_limits_active': True,
        'security_checks_active': True,
        'audit_logging_active': True,
        'supported_auth_methods': ['api_key', 'bearer_token', 'session'],
        'rate_limit_tiers': list(security_manager.rate_limits.keys())
    }