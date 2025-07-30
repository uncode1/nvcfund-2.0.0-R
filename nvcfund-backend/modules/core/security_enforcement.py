"""
Comprehensive Security Enforcement System
Implements all three pillars: Authentication, Authorization, and Data Integrity & Confidentiality
"""

import re
import time
import hmac
import hashlib
import logging
from functools import wraps
from typing import Dict, Set, Any, Optional, Callable
from flask import request, jsonify, g, current_app, abort, render_template, redirect, url_for
from flask_login import current_user
from werkzeug.exceptions import TooManyRequests
from collections import defaultdict, deque
import bleach
from markupsafe import Markup

logger = logging.getLogger(__name__)

class SecurityEnforcement:
    """
    Comprehensive security enforcement following the three pillars:
    1. Authentication (Who are you?)
    2. Authorization (What are you allowed to do?) 
    3. Data Integrity & Confidentiality (Is the data safe?)
    """
    
    def __init__(self):
        # Rate limiting storage
        self._rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self._blocked_ips: Dict[str, float] = {}
        
        # Input validation patterns
        self._validation_patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'phone': re.compile(r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'),
            'account_number': re.compile(r'^[0-9]{8,20}$'),
            'routing_number': re.compile(r'^[0-9]{9}$'),
            'amount': re.compile(r'^\d+(\.\d{1,2})?$'),
            'username': re.compile(r'^[a-zA-Z0-9_]{3,30}$'),
            'password': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        }
        
        # XSS prevention - allowed HTML tags for banking content
        self._allowed_tags = {
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
        }
        
        self._allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }

    # === PILLAR 1: AUTHENTICATION ENFORCEMENT ===
    
    def enforce_session_security(self, max_age_minutes: int = 15):
        """Enforce banking-grade session security"""
        def session_security_decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not current_user.is_authenticated:
                    return self._handle_authentication_failure("Authentication required")
                
                # Check session expiration
                if hasattr(g, 'session_start'):
                    session_duration = time.time() - g.session_start
                    if session_duration > (max_age_minutes * 60):
                        return self._handle_authentication_failure("Session expired")
                
                # Check for session hijacking indicators
                if self._detect_session_anomalies():
                    return self._handle_authentication_failure("Session security violation")
                
                return func(*args, **kwargs)
            return wrapper
        return session_security_decorator
    
    def _detect_session_anomalies(self) -> bool:
        """Detect potential session hijacking"""
        if not hasattr(g, 'session_fingerprint'):
            return False
        
        # Check user agent consistency
        current_fingerprint = self._generate_session_fingerprint()
        return current_fingerprint != g.session_fingerprint
    
    def _generate_session_fingerprint(self) -> str:
        """Generate session fingerprint for security"""
        user_agent = request.headers.get('User-Agent', '')
        accept_language = request.headers.get('Accept-Language', '')
        fingerprint_data = f"{user_agent}:{accept_language}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    # === PILLAR 2: AUTHORIZATION ENFORCEMENT ===
    
    def enforce_data_scope(self, scope_check: Callable[[Any], bool]):
        """Enforce data access scope (prevents horizontal privilege escalation)"""
        def data_scope_decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract data identifier from request
                data_id = request.view_args.get('id') or request.json.get('id') if request.is_json else None
                
                if data_id and not scope_check(data_id):
                    logger.warning(f"Scope violation: User {current_user.id} attempted to access {data_id}")
                    return self._handle_authorization_failure("Access denied: insufficient scope")
                
                return func(*args, **kwargs)
            return wrapper
        return data_scope_decorator
    
    def enforce_least_privilege(self, required_permissions: Set[str]):
        """Enforce least privilege principle with granular permissions"""
        def privilege_wrapper(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                from .rbac import rbac, get_user_role
                
                user_role = get_user_role()
                user_permissions = rbac.get_user_permissions(user_role)
                
                if not required_permissions.issubset(user_permissions):
                    missing = required_permissions - user_permissions
                    logger.warning(f"Privilege violation: User {current_user.id} lacks {missing}")
                    return self._handle_authorization_failure(f"Missing permissions: {', '.join(missing)}")
                
                return func(*args, **kwargs)
            return wrapper
        return privilege_wrapper

    # === PILLAR 3: DATA INTEGRITY & CONFIDENTIALITY ===
    
    def enforce_input_validation(self, validation_rules: Dict[str, str]):
        """Comprehensive input validation and sanitization"""
        def validation_wrapper(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Validate form data
                if request.form:
                    for field, rule in validation_rules.items():
                        value = request.form.get(field)
                        if value and not self._validate_input(value, rule):
                            return self._handle_validation_failure(f"Invalid {field}")
                
                # Validate JSON data
                if request.is_json and request.json:
                    for field, rule in validation_rules.items():
                        value = request.json.get(field)
                        if value and not self._validate_input(str(value), rule):
                            return self._handle_validation_failure(f"Invalid {field}")
                
                return func(*args, **kwargs)
            return wrapper
        return validation_wrapper
    
    def sanitize_output(self, data: Any) -> Any:
        """Sanitize output to prevent XSS and data leakage"""
        if isinstance(data, str):
            # Clean HTML content
            clean_html = bleach.clean(data, tags=self._allowed_tags, attributes=self._allowed_attributes)
            return Markup(clean_html)
        elif isinstance(data, dict):
            return {key: self.sanitize_output(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_output(item) for item in data]
        return data
    
    def mask_sensitive_data(self, data: Dict[str, Any], sensitive_fields: Set[str]) -> Dict[str, Any]:
        """Mask sensitive data in responses"""
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                value = str(masked_data[field])
                if field in ['ssn', 'tax_id']:
                    masked_data[field] = f"***-**-{value[-4:]}" if len(value) >= 4 else "***"
                elif field in ['account_number']:
                    masked_data[field] = f"****{value[-4:]}" if len(value) >= 4 else "***"
                elif field in ['credit_card', 'debit_card']:
                    masked_data[field] = f"****-****-****-{value[-4:]}" if len(value) >= 4 else "***"
                elif field in ['phone']:
                    masked_data[field] = f"***-***-{value[-4:]}" if len(value) >= 4 else "***"
                else:
                    masked_data[field] = "***"
        
        return masked_data

    # === RATE LIMITING & ABUSE PREVENTION ===
    
    def enforce_rate_limit(self, max_requests: int = 10, window_minutes: int = 1, block_duration_minutes: int = 15):
        """Advanced rate limiting with IP blocking"""
        def rate_limit_wrapper(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                client_ip = self._get_client_ip()
                current_time = time.time()
                
                # Check if IP is currently blocked
                if client_ip in self._blocked_ips:
                    if current_time < self._blocked_ips[client_ip]:
                        logger.warning(f"Blocked IP {client_ip} attempted access")
                        raise TooManyRequests("IP temporarily blocked due to excessive requests")
                    else:
                        del self._blocked_ips[client_ip]
                
                # Rate limiting logic
                window_start = current_time - (window_minutes * 60)
                requests = self._rate_limits[client_ip]
                
                # Remove old requests outside the window
                while requests and requests[0] < window_start:
                    requests.popleft()
                
                # Check if limit exceeded
                if len(requests) >= max_requests:
                    # Block the IP
                    self._blocked_ips[client_ip] = current_time + (block_duration_minutes * 60)
                    logger.warning(f"Rate limit exceeded for IP {client_ip}, blocking for {block_duration_minutes} minutes")
                    raise TooManyRequests(f"Rate limit exceeded. Blocked for {block_duration_minutes} minutes.")
                
                # Record this request
                requests.append(current_time)
                
                return func(*args, **kwargs)
            return wrapper
        return rate_limit_wrapper

    # === CSRF PROTECTION ===
    
    def enforce_csrf_protection(self):
        """Enhanced CSRF protection for state-changing operations"""
        def csrf_decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                    if not self._verify_csrf_token():
                        logger.warning(f"CSRF attack detected from IP {self._get_client_ip()}")
                        return self._handle_csrf_failure()
                
                return func(*args, **kwargs)
            return wrapper
        return csrf_decorator
    
    def _verify_csrf_token(self) -> bool:
        """Verify CSRF token"""
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        if not token:
            return False
        
        # Use Flask-WTF's CSRF validation if available
        try:
            from flask_wtf.csrf import validate_csrf
            validate_csrf(token)
            return True
        except:
            return False

    # === UTILITY METHODS ===
    
    def _validate_input(self, value: str, rule: str) -> bool:
        """Validate input against predefined patterns"""
        pattern = self._validation_patterns.get(rule)
        if pattern:
            return bool(pattern.match(value))
        return True  # No validation rule found
    
    def _get_client_ip(self) -> str:
        """Get real client IP considering proxies"""
        return (request.headers.get('X-Forwarded-For', request.remote_addr) or '').split(',')[0].strip()
    
    def _handle_authentication_failure(self, message: str):
        """Handle authentication failures"""
        logger.warning(f"Authentication failure: {message} from IP {self._get_client_ip()}")
        if request.is_json:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('auth.login'))
    
    def _handle_authorization_failure(self, message: str):
        """Handle authorization failures"""
        logger.warning(f"Authorization failure: {message} for user {getattr(current_user, 'id', 'anonymous')}")
        if request.is_json:
            return jsonify({'error': 'Access denied'}), 403
        return render_template('errors/403.html'), 403
    
    def _handle_validation_failure(self, message: str):
        """Handle input validation failures"""
        logger.warning(f"Validation failure: {message} from IP {self._get_client_ip()}")
        if request.is_json:
            return jsonify({'error': 'Invalid input data', 'details': message}), 400
        return render_template('errors/400.html', message="Invalid input data"), 400
    
    def _handle_csrf_failure(self):
        """Handle CSRF token failures"""
        if request.is_json:
            return jsonify({'error': 'CSRF token missing or invalid'}), 403
        return render_template('errors/403.html', message="Security token invalid"), 403

# Global security enforcement instance
security = SecurityEnforcement()

# === DECORATOR EXPORTS FOR EASY USE ===

def require_session_security(max_age_minutes: int = 15):
    """Banking-grade session security with automatic timeout"""
    return security.enforce_session_security(max_age_minutes)

def require_data_scope(scope_check: Callable[[Any], bool]):
    """Prevent horizontal privilege escalation"""
    return security.enforce_data_scope(scope_check)

def require_permissions(*permissions: str):
    """Enforce least privilege with granular permissions"""
    return security.enforce_least_privilege(set(permissions))

def validate_input(**validation_rules: str):
    """Comprehensive input validation"""
    return security.enforce_input_validation(validation_rules)

def rate_limit(max_requests: int = 10, window_minutes: int = 1, block_duration_minutes: int = 15):
    """Advanced rate limiting with IP blocking"""
    return security.enforce_rate_limit(max_requests, window_minutes, block_duration_minutes)

def csrf_protect():
    """Enhanced CSRF protection"""
    return security.enforce_csrf_protection()

# === BANKING-SPECIFIC SECURITY DECORATORS ===

def secure_banking_route(
    max_requests: int = 5,
    session_timeout_minutes: int = 15,
    required_permissions: Optional[Set[str]] = None,
    validation_rules: Optional[Dict[str, str]] = None,
    scope_check: Optional[Callable] = None,
    rate_limit: Optional[int] = None,  # Backward compatibility
    **kwargs  # Catch any additional parameters
):
    """Comprehensive security decorator for banking routes"""
    
    # Handle backward compatibility with rate_limit parameter
    if rate_limit is not None:
        max_requests = rate_limit
    
    # Make the decorator function name unique to avoid Flask conflicts
    import uuid
    import inspect
    
    # Get the module name from the calling context
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back
        if caller_frame:
            module_name = caller_frame.f_globals.get('__name__', 'unknown')
            # Extract just the module name part
            if 'modules.' in module_name:
                module_parts = module_name.split('.')
                if len(module_parts) >= 2:
                    module_name = module_parts[1]  # e.g., 'admin_management'
                else:
                    module_name = 'unknown'
            else:
                module_name = 'core'
        else:
            module_name = 'unknown'
    except:
        module_name = 'fallback'
    finally:
        del frame
    
    # Create simple decorator function name for easier error tracking
    decorator_name = f"_secure_route_wrapper_{module_name}"
    
    # Define the decorator function with unique name
    def decorator_func(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Health endpoints bypass security for monitoring purposes
            if '/api/health' in request.path:
                return func(*args, **kwargs)
            
            # All users including super admins go through proper security auditing
            
            # Apply all security measures
            decorated_func = func
            
            # Rate limiting with fallback
            try:
                rate_limiter = security.enforce_rate_limit(max_requests, 1, 15)
                if rate_limiter is not None:
                    decorated_func = rate_limiter(decorated_func)
            except Exception as e:
                logger.warning(f"Rate limiting skipped due to error: {e}")
            
            # Session security
            decorated_func = require_session_security(session_timeout_minutes)(decorated_func)
            
            # CSRF protection for state-changing operations
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                decorated_func = security.enforce_csrf_protection()(decorated_func)
            
            # Permission checking with super admin bypass
            if required_permissions:
                # Super admin bypass
                if hasattr(current_user, 'role') and current_user.role == 'super_admin':
                    pass  # Super admin has all permissions
                else:
                    decorated_func = require_permissions(*required_permissions)(decorated_func)
            
            # Input validation
            if validation_rules:
                decorated_func = validate_input(**validation_rules)(decorated_func)
            
            # Data scope checking
            if scope_check:
                decorated_func = require_data_scope(scope_check)(decorated_func)
            
            return decorated_func(*args, **kwargs)
        # Make wrapper function name relatable for error tracking
        wrapper.__name__ = f"{module_name}_{func.__name__}_wrapper"
        wrapper.__qualname__ = wrapper.__name__
        
        # Force endpoint uniqueness in Flask's routing table
        if hasattr(func, '_endpoint_override'):
            func._endpoint_override = f"{module_name}_{func._endpoint_override}"
        else:
            func._endpoint_override = f"{module_name}_{func.__name__}"
        return wrapper
    
    # Set the unique name to the decorator function itself
    decorator_func.__name__ = decorator_name
    decorator_func.__qualname__ = decorator_name
    
    return decorator_func

def treasury_secure_route():
    """High-security route for treasury operations"""
    return secure_banking_route(
        max_requests=3,
        session_timeout_minutes=10,
        required_permissions={'treasury_dashboard', 'nvct_operations'},
        validation_rules={
            'amount': 'amount',
            'account_number': 'account_number'
        }
    )

def admin_secure_route():
    """Maximum security route for admin operations"""
    return secure_banking_route(
        max_requests=2,
        session_timeout_minutes=5,
        required_permissions={'user_management', 'system_config'},
        validation_rules={
            'username': 'username',
            'email': 'email'
        }
    )

def admin_required(func):
    """Admin required decorator for backward compatibility"""
    return secure_banking_route(required_permissions={'user_management'})(func)