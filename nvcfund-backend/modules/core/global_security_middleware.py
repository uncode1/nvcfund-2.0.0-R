"""
Global Security Middleware
Enterprise-grade protection applied to all Flask endpoints automatically
"""

from flask import Flask, request, g, jsonify, session, abort
from werkzeug.exceptions import TooManyRequests, Forbidden, BadRequest
from modules.core.enterprise_security import security_manager, enterprise_security_check
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class GlobalSecurityMiddleware:
    """Global security middleware for automatic protection"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.errorhandler(429)(self.handle_rate_limit)
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(400)(self.handle_bad_request)
        
        # Register security status endpoint
        @app.route('/api/v1/security/status')
        @enterprise_security_check()
        def security_status():
            """Get security system status"""
            from modules.core.enterprise_security import get_security_status
            return jsonify(get_security_status())
        
        logger.info("Global Security Middleware initialized")
    
    def before_request(self):
        """Execute before each request"""
        try:
            # Skip security checks for static files
            if request.endpoint and 'static' in request.endpoint:
                return
            
            # Skip for health checks and public chat endpoints
            if request.path in ['/health', '/api/v1/health', '/chat/api/start-session', '/chat/api/send-message']:
                return
            
            start_time = time.time()
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            # Store request start time for performance monitoring (as datetime for consistency)
            from datetime import datetime
            g.request_start_time = datetime.utcnow()
            g.request_start_time_float = start_time
            g.client_ip = client_ip
            
            # 1. IP Reputation and Blocking Check
            if client_ip in security_manager.blocked_ips:
                security_manager.log_security_event(
                    'blocked_ip_access', 'high',
                    f'Blocked IP attempted access: {client_ip}',
                    {'ip': client_ip, 'endpoint': request.endpoint}, 9
                )
                abort(403, description="IP address blocked")
            
            # 2. Basic Rate Limiting (more detailed in decorators)
            user_id = str(getattr(g, 'current_user', {}).get('id', 'anonymous'))
            rate_ok, rate_info = security_manager.check_rate_limit(
                client_ip, user_id, request.endpoint or 'unknown'
            )
            
            if not rate_ok:
                security_manager.log_security_event(
                    'global_rate_limit', 'medium',
                    f'Global rate limit exceeded: {rate_info["reason"]}',
                    rate_info, 6
                )
                raise TooManyRequests(description=rate_info['reason'])
            
            # 3. Suspicious User Agent Detection
            user_agent = request.headers.get('User-Agent', '').lower()
            for suspicious_agent in security_manager.threat_intelligence.suspicious_user_agents:
                if suspicious_agent in user_agent:
                    security_manager.log_security_event(
                        'suspicious_user_agent_global', 'medium',
                        f'Suspicious user agent in global middleware: {suspicious_agent}',
                        {'user_agent': request.headers.get('User-Agent'), 'ip': client_ip}, 7
                    )
                    abort(403, description="Suspicious user agent detected")
            
            # 4. Basic Content Length Check
            content_length = request.content_length
            if content_length and content_length > 50 * 1024 * 1024:  # 50MB limit
                security_manager.log_security_event(
                    'oversized_request_global', 'medium',
                    f'Oversized request: {content_length} bytes',
                    {'size': content_length, 'ip': client_ip}, 6
                )
                abort(413, description="Request too large")
            
            # 5. Set security context
            g.security_context = {
                'ip_checked': True,
                'rate_limit_passed': True,
                'user_agent_clean': True,
                'request_size_ok': True
            }
            
        except (TooManyRequests, Forbidden, BadRequest):
            raise
        except Exception as e:
            logger.error(f"Global security middleware error: {e}")
            # Don't block requests on middleware errors
            pass
    
    def after_request(self, response):
        """Execute after each request"""
        try:
            # Add security headers to all responses
            security_headers = {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'X-Powered-By': 'NVC Banking Platform',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
            
            # Add Content Security Policy for HTML responses
            if response.content_type and 'text/html' in response.content_type:
                security_headers['Content-Security-Policy'] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdnjs.cloudflare.com cdn.jsdelivr.net; "
                    "style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com; "
                    "img-src 'self' data: https: blob:; "
                    "font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com; "
                    "connect-src 'self' wss: ws:; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'"
                )
            
            # Apply headers
            for header, value in security_headers.items():
                response.headers[header] = value
            
            # Log response time for monitoring
            if hasattr(g, 'request_start_time_float'):
                response_time = (time.time() - g.request_start_time_float) * 1000
                if response_time > 5000:  # Log slow requests
                    logger.warning(f"Slow request: {request.endpoint} took {response_time:.2f}ms")
            
            return response
            
        except Exception as e:
            logger.error(f"After request middleware error: {e}")
            return response
    
    def handle_rate_limit(self, e):
        """Handle rate limit errors"""
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        response_data = {
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please wait before trying again.',
            'code': 'RATE_LIMIT_EXCEEDED',
            'retry_after': 60,
            'timestamp': time.time()
        }
        
        # Log rate limit hit
        logger.warning(f"Rate limit exceeded for IP {client_ip} on {request.endpoint}")
        
        response = jsonify(response_data)
        response.status_code = 429
        response.headers['Retry-After'] = '60'
        return response
    
    def handle_forbidden(self, e):
        """Handle forbidden access errors"""
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        response_data = {
            'error': 'Access forbidden',
            'message': 'You do not have permission to access this resource.',
            'code': 'ACCESS_FORBIDDEN',
            'timestamp': time.time()
        }
        
        # Log forbidden access
        logger.warning(f"Forbidden access attempt from IP {client_ip} to {request.endpoint}")
        
        response = jsonify(response_data)
        response.status_code = 403
        return response
    
    def handle_bad_request(self, e):
        """Handle bad request errors"""
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        response_data = {
            'error': 'Bad request',
            'message': 'The request could not be processed due to invalid data.',
            'code': 'BAD_REQUEST',
            'timestamp': time.time()
        }
        
        # Log bad request
        logger.warning(f"Bad request from IP {client_ip} to {request.endpoint}: {e.description}")
        
        response = jsonify(response_data)
        response.status_code = 400
        return response

# Global middleware instance
global_security = GlobalSecurityMiddleware()

def register_global_security(app: Flask):
    """Register global security middleware with Flask app"""
    global_security.init_app(app)
    
    # Add additional security configurations
    # Only use secure cookies in production (HTTPS)
    is_production = app.config.get('PREFERRED_URL_SCHEME') == 'https'
    is_development = app.config.get('DEBUG', False)

    # Prepare security config without overriding existing session settings
    security_config = {
        'WTF_CSRF_TIME_LIMIT': 3600,
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024  # 50MB
    }

    # Only override session settings if not already configured in development
    if not is_development:
        security_config.update({
            'SESSION_COOKIE_SECURE': is_production,  # Only secure in production
            'SESSION_COOKIE_HTTPONLY': True,
            'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
        })

        # Only set SameSite if not already configured
        if 'SESSION_COOKIE_SAMESITE' not in app.config:
            security_config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    app.config.update(security_config)
    
    logger.info("Global security middleware registered with enhanced configurations")