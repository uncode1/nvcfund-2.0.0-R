"""
Enhanced Security Framework - Comprehensive Security Gap Closure
Implements missing security controls while maintaining modular architecture
"""

import re
import os
import hmac
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from functools import wraps
from flask import request, jsonify, g, current_app, abort, session
from flask_login import current_user
from werkzeug.exceptions import BadRequest
import bleach
from email_validator import validate_email, EmailNotValidError

logger = logging.getLogger(__name__)

class EnhancedSecurityFramework:
    """
    Enhanced security framework implementing missing controls
    Addresses gaps identified in security policy compliance review
    """
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        
        # Banking-grade password complexity requirements
        self.password_requirements = {
            'min_length': 12,
            'min_uppercase': 2,
            'min_lowercase': 2,
            'min_digits': 2,
            'min_special': 2,
            'min_unique_chars': 8,
            'max_repeated_chars': 2,
            'forbidden_patterns': [
                'password', 'admin', 'banking', 'finance', 'money',
                'account', 'credit', 'debit', 'login', 'user'
            ]
        }
        
        # Comprehensive input validation patterns
        self.validation_patterns = {
            'ssn': re.compile(r'^\d{3}-\d{2}-\d{4}$'),
            'phone': re.compile(r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'),
            'account_number': re.compile(r'^[0-9]{8,20}$'),
            'routing_number': re.compile(r'^[0-9]{9}$'),
            'amount': re.compile(r'^\d+(\.\d{1,2})?$'),
            'zip_code': re.compile(r'^\d{5}(-\d{4})?$'),
            'credit_card': re.compile(r'^[0-9]{13,19}$'),
            'cvv': re.compile(r'^[0-9]{3,4}$'),
            'username': re.compile(r'^[a-zA-Z0-9_]{3,30}$'),
            'name': re.compile(r'^[a-zA-Z\s\-\'\.]{1,50}$'),
            'address': re.compile(r'^[a-zA-Z0-9\s\-\#\.,\']{1,100}$')
        }
        
        # XSS prevention - banking-safe HTML tags
        self.allowed_tags = {
            'p', 'br', 'strong', 'em', 'u', 'b', 'i',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'div', 'span',
            'table', 'thead', 'tbody', 'tr', 'td', 'th'
        }
        
        self.allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }

    def validate_banking_password(self, password: str) -> Dict[str, Any]:
        """
        Banking-grade password validation
        Implements comprehensive password security requirements
        """
        errors = []
        requirements = self.password_requirements
        
        # Length check
        if len(password) < requirements['min_length']:
            errors.append(f"Password must be at least {requirements['min_length']} characters long")
        
        # Character composition checks
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digit_count = sum(1 for c in password if c.isdigit())
        special_count = sum(1 for c in password if c in "!@#$%^&*()_+-=[]{}|;:,.<>?")
        
        if uppercase_count < requirements['min_uppercase']:
            errors.append(f"Password must contain at least {requirements['min_uppercase']} uppercase letters")
        
        if lowercase_count < requirements['min_lowercase']:
            errors.append(f"Password must contain at least {requirements['min_lowercase']} lowercase letters")
        
        if digit_count < requirements['min_digits']:
            errors.append(f"Password must contain at least {requirements['min_digits']} digits")
        
        if special_count < requirements['min_special']:
            errors.append(f"Password must contain at least {requirements['min_special']} special characters")
        
        # Unique characters check
        unique_chars = len(set(password))
        if unique_chars < requirements['min_unique_chars']:
            errors.append(f"Password must contain at least {requirements['min_unique_chars']} unique characters")
        
        # Repeated characters check
        for i in range(len(password) - requirements['max_repeated_chars']):
            if password[i] == password[i + 1] == password[i + 2]:
                errors.append("Password cannot contain more than 2 consecutive identical characters")
                break
        
        # Consecutive sequence check
        for i in range(len(password) - 2):
            if (ord(password[i]) + 1 == ord(password[i + 1]) and 
                ord(password[i + 1]) + 1 == ord(password[i + 2])):
                errors.append("Password cannot contain 3 or more consecutive characters")
                break
        
        # Forbidden patterns check
        password_lower = password.lower()
        for pattern in requirements['forbidden_patterns']:
            if pattern in password_lower:
                errors.append(f"Password cannot contain common words like '{pattern}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_password_strength(password)
        }

    def _calculate_password_strength(self, password: str) -> int:
        """Calculate password strength score (0-100)"""
        score = 0
        
        # Length bonus
        if len(password) >= 12:
            score += 20
        if len(password) >= 16:
            score += 10
        
        # Character variety bonus
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 15
        
        # Complexity bonus
        unique_chars = len(set(password))
        if unique_chars >= 10:
            score += 10
        
        return min(score, 100)

    def comprehensive_input_validation(self, data: Dict[str, Any], validation_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        Comprehensive input validation for banking forms
        Prevents injection attacks and ensures data integrity
        """
        validated_data = {}
        validation_errors = {}
        
        for field, value in data.items():
            if field not in validation_rules:
                continue
                
            rule = validation_rules[field]
            
            try:
                # Basic sanitization
                if isinstance(value, str):
                    value = value.strip()
                    
                    # Remove null bytes and control characters
                    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
                    
                    # Prevent script injection
                    if re.search(r'<script|javascript:|data:|vbscript:', value, re.IGNORECASE):
                        validation_errors[field] = "Invalid characters detected"
                        continue
                
                # Field-specific validation
                if rule == 'email':
                    try:
                        validated_email = validate_email(value)
                        validated_data[field] = validated_email.email
                    except EmailNotValidError:
                        validation_errors[field] = "Invalid email format"
                
                elif rule == 'phone':
                    # Clean phone number
                    clean_phone = re.sub(r'[^\d\+]', '', value)
                    if self.validation_patterns['phone'].match(clean_phone):
                        validated_data[field] = clean_phone
                    else:
                        validation_errors[field] = "Invalid phone number format"
                
                elif rule == 'ssn':
                    # Clean SSN
                    clean_ssn = re.sub(r'[^\d]', '', value)
                    if len(clean_ssn) == 9:
                        formatted_ssn = f"{clean_ssn[:3]}-{clean_ssn[3:5]}-{clean_ssn[5:]}"
                        if self.validation_patterns['ssn'].match(formatted_ssn):
                            validated_data[field] = formatted_ssn
                        else:
                            validation_errors[field] = "Invalid SSN format"
                    else:
                        validation_errors[field] = "SSN must be 9 digits"
                
                elif rule == 'amount':
                    try:
                        # Convert to float and validate
                        amount = float(value)
                        if amount < 0:
                            validation_errors[field] = "Amount cannot be negative"
                        elif amount > 999999999.99:
                            validation_errors[field] = "Amount exceeds maximum limit"
                        else:
                            validated_data[field] = round(amount, 2)
                    except ValueError:
                        validation_errors[field] = "Invalid amount format"
                
                elif rule in self.validation_patterns:
                    if self.validation_patterns[rule].match(value):
                        validated_data[field] = value
                    else:
                        validation_errors[field] = f"Invalid {rule} format"
                
                elif rule == 'safe_html':
                    # Clean HTML for banking content
                    cleaned_html = bleach.clean(
                        value,
                        tags=self.allowed_tags,
                        attributes=self.allowed_attributes,
                        strip=True
                    )
                    validated_data[field] = cleaned_html
                
                else:
                    # Default string validation
                    if len(value) > 1000:  # Prevent DoS attacks
                        validation_errors[field] = "Input too long"
                    else:
                        validated_data[field] = value
                        
            except Exception as e:
                logger.error(f"Validation error for field {field}: {e}")
                validation_errors[field] = "Validation failed"
        
        return {
            'valid': len(validation_errors) == 0,
            'data': validated_data,
            'errors': validation_errors
        }

    def enhanced_session_security(self, func):
        """
        Enhanced session security with anomaly detection
        Prevents session hijacking and unauthorized access
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Session anomaly detection
            current_fingerprint = self._generate_enhanced_fingerprint()
            stored_fingerprint = session.get('security_fingerprint')
            
            if stored_fingerprint and stored_fingerprint != current_fingerprint:
                logger.warning(f"Session anomaly detected for user {current_user.id}")
                session.clear()
                return jsonify({'error': 'Session security violation'}), 401
            
            # Store fingerprint for new sessions
            if not stored_fingerprint:
                session['security_fingerprint'] = current_fingerprint
            
            # Update last activity
            session['last_activity'] = datetime.utcnow().isoformat()
            
            return func(*args, **kwargs)
        return wrapper

    def _generate_enhanced_fingerprint(self) -> str:
        """Generate enhanced session fingerprint"""
        components = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            request.headers.get('Accept-Encoding', ''),
            request.remote_addr or ''
        ]
        
        fingerprint_data = '|'.join(components)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]

    def security_headers_middleware(self, response):
        """
        Enhanced security headers for banking applications
        Implements comprehensive browser security controls
        """
        # Content Security Policy for XSS prevention
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self';"
        )
        
        # Apply comprehensive security headers
        response.headers['Content-Security-Policy'] = csp_policy
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS for production
        if current_app.config.get('PREFERRED_URL_SCHEME') == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

    def audit_log_decorator(self, action_type: str, resource: str = None):
        """
        Comprehensive audit logging decorator
        Ensures all banking operations are logged for compliance
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = datetime.utcnow()
                
                # Capture request details
                audit_data = {
                    'timestamp': start_time.isoformat(),
                    'user_id': current_user.id if current_user.is_authenticated else None,
                    'username': current_user.username if current_user.is_authenticated else 'anonymous',
                    'action_type': action_type,
                    'resource': resource or func.__name__,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'url': request.url
                }
                
                try:
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Log successful operation
                    audit_data['status'] = 'success'
                    audit_data['duration_ms'] = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    logger.info(f"AUDIT: {audit_data}")
                    
                    return result
                    
                except Exception as e:
                    # Log failed operation
                    audit_data['status'] = 'failure'
                    audit_data['error'] = str(e)
                    audit_data['duration_ms'] = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    logger.error(f"AUDIT: {audit_data}")
                    raise
                    
            return wrapper
        return decorator

# Global instance for use across modules
enhanced_security = EnhancedSecurityFramework()