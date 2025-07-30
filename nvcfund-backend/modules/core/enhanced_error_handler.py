"""
NVC Banking Platform - Enhanced Error Handling System
Standardized error responses and comprehensive error tracking
"""

import json
import traceback
import uuid
from datetime import datetime
from flask import request, jsonify, current_app
from werkzeug.exceptions import HTTPException
try:
    from modules.core.logger import ErrorLoggerService
except ImportError:
    # Fallback if logger service is not available
    class ErrorLoggerService:
        @staticmethod
        def log_error(*args, **kwargs):
            pass


class BankingError(Exception):
    """Base exception for banking-specific errors"""
    
    def __init__(self, message, error_code=None, details=None, status_code=400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or 'BANKING_ERROR'
        self.details = details or {}
        self.status_code = status_code
        self.correlation_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()


class TransactionError(BankingError):
    """Transaction-specific errors"""
    
    def __init__(self, message, transaction_id=None, account_id=None, **kwargs):
        super().__init__(message, error_code='TRANSACTION_ERROR', **kwargs)
        self.details.update({
            'transaction_id': transaction_id,
            'account_id': account_id
        })


class AuthenticationError(BankingError):
    """Authentication-specific errors"""
    
    def __init__(self, message, user_id=None, **kwargs):
        super().__init__(message, error_code='AUTH_ERROR', status_code=401, **kwargs)
        self.details.update({'user_id': user_id})


class ComplianceError(BankingError):
    """Compliance-specific errors"""
    
    def __init__(self, message, regulation=None, **kwargs):
        super().__init__(message, error_code='COMPLIANCE_ERROR', status_code=403, **kwargs)
        self.details.update({'regulation': regulation})


class SecurityError(BankingError):
    """Security-specific errors"""
    
    def __init__(self, message, threat_level='medium', **kwargs):
        super().__init__(message, error_code='SECURITY_ERROR', status_code=403, **kwargs)
        self.details.update({'threat_level': threat_level})


class EnhancedErrorHandler:
    """Enhanced error handling with structured responses and logging"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handlers for the Flask app"""
        
        # Register error handlers
        app.register_error_handler(BankingError, self.handle_banking_error)
        app.register_error_handler(HTTPException, self.handle_http_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        # Add before/after request handlers for error context
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Set up request context for error handling"""
        request.start_time = datetime.utcnow()
        request.correlation_id = str(uuid.uuid4())
    
    def after_request(self, response):
        """Log request completion and performance metrics"""
        if hasattr(request, 'start_time'):
            duration = (datetime.utcnow() - request.start_time).total_seconds()
            
            # Log slow requests (>2 seconds)
            if duration > 2.0:
                current_app.logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s (correlation_id: {getattr(request, 'correlation_id', 'unknown')})"
                )
        
        return response
    
    def handle_banking_error(self, error):
        """Handle banking-specific errors"""
        
        # Log the error
        self._log_error(error)
        
        # Create standardized response
        response = {
            'error': {
                'type': 'banking_error',
                'code': error.error_code,
                'message': error.message,
                'correlation_id': error.correlation_id,
                'timestamp': error.timestamp,
                'details': error.details
            },
            'success': False
        }
        
        # Add request context if available
        if hasattr(request, 'correlation_id'):
            response['error']['request_id'] = request.correlation_id
        
        return jsonify(response), error.status_code
    
    def handle_http_error(self, error):
        """Handle HTTP errors (404, 500, etc.)"""
        
        correlation_id = str(uuid.uuid4())
        
        # Log the error
        error_info = {
            'type': 'http_error',
            'status_code': error.code,
            'message': error.description,
            'path': request.path,
            'method': request.method,
            'correlation_id': correlation_id
        }
        
        current_app.logger.error(f"HTTP Error: {json.dumps(error_info)}")
        
        # Create standardized response
        response = {
            'error': {
                'type': 'http_error',
                'code': f'HTTP_{error.code}',
                'message': error.description,
                'correlation_id': correlation_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            'success': False
        }
        
        return jsonify(response), error.code
    
    def handle_generic_error(self, error):
        """Handle unexpected errors"""
        
        correlation_id = str(uuid.uuid4())
        
        # Log the full error with traceback
        error_info = {
            'type': 'unexpected_error',
            'message': str(error),
            'path': request.path,
            'method': request.method,
            'correlation_id': correlation_id,
            'traceback': traceback.format_exc()
        }
        
        current_app.logger.error(f"Unexpected Error: {json.dumps(error_info)}")
        
        # In production, don't expose internal errors
        if current_app.config.get('DEBUG', False):
            message = str(error)
            details = {'traceback': traceback.format_exc()}
        else:
            message = 'An internal error occurred. Please contact support.'
            details = {}
        
        # Create standardized response
        response = {
            'error': {
                'type': 'internal_error',
                'code': 'INTERNAL_ERROR',
                'message': message,
                'correlation_id': correlation_id,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details
            },
            'success': False
        }
        
        return jsonify(response), 500
    
    def _log_error(self, error):
        """Log error with full context"""
        
        error_context = {
            'error_type': type(error).__name__,
            'error_code': getattr(error, 'error_code', 'UNKNOWN'),
            'message': str(error),
            'correlation_id': getattr(error, 'correlation_id', 'unknown'),
            'request_path': request.path,
            'request_method': request.method,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add user context if available
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                error_context['user_id'] = current_user.id
                error_context['user_role'] = getattr(current_user, 'role', 'unknown')
        except:
            pass
        
        # Log to application logger
        current_app.logger.error(f"Banking Error: {json.dumps(error_context)}")
        
        # Log to error tracking service if available
        try:
            ErrorLoggerService.log_error(
                error_type=type(error).__name__,
                error_message=str(error),
                request_path=request.path,
                additional_context=error_context
            )
        except Exception as e:
            current_app.logger.error(f"Failed to log error to ErrorLoggerService: {e}")


def create_success_response(data=None, message="Success", status_code=200):
    """Create standardized success response"""
    
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if hasattr(request, 'correlation_id'):
        response['request_id'] = request.correlation_id
    
    return jsonify(response), status_code


def validate_required_fields(data, required_fields):
    """Validate required fields in request data"""
    
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        raise BankingError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            error_code='VALIDATION_ERROR',
            details={'missing_fields': missing_fields},
            status_code=400
        )


def validate_amount(amount, min_amount=0.01, max_amount=None):
    """Validate monetary amounts"""
    
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise BankingError(
            message="Invalid amount format",
            error_code='INVALID_AMOUNT',
            status_code=400
        )
    
    if amount < min_amount:
        raise BankingError(
            message=f"Amount must be at least ${min_amount}",
            error_code='AMOUNT_TOO_LOW',
            details={'min_amount': min_amount},
            status_code=400
        )
    
    if max_amount and amount > max_amount:
        raise BankingError(
            message=f"Amount exceeds maximum limit of ${max_amount}",
            error_code='AMOUNT_TOO_HIGH',
            details={'max_amount': max_amount},
            status_code=400
        )
    
    return amount


# Global error handler instance
enhanced_error_handler = EnhancedErrorHandler()