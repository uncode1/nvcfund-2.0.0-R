"""
Enterprise-Grade Centralized Logging System
NVC Banking Platform - Production-Ready Logging Infrastructure

Features:
- Structured JSON logging for enterprise CLM systems
- Contextual logging with request tracing
- Multiple handlers (file, console, rotating, security)
- PCI DSS compliant log masking
- Performance optimized with async capabilities
"""

import logging
import logging.handlers
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, current_app, has_request_context
from werkzeug.local import LocalProxy
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging compatible with ELK/Splunk/Datadog
    """
    
    def __init__(self, include_context=True, mask_sensitive=True):
        super().__init__()
        self.include_context = include_context
        self.mask_sensitive = mask_sensitive
        self.sensitive_fields = [
            'password', 'ssn', 'credit_card', 'account_number', 
            'routing_number', 'pin', 'token', 'secret', 'key'
        ]
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'logger_module': getattr(record, 'module', record.name.split('.')[-1]),
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': threading.current_thread().name,
            'process': os.getpid()
        }
        
        # Add contextual information if available
        if self.include_context and has_request_context():
            log_entry.update(self._get_request_context())
        
        # Add custom fields from record
        if hasattr(record, 'custom_fields'):
            custom_fields = record.custom_fields
            if self.mask_sensitive:
                custom_fields = self._mask_sensitive_data(custom_fields)
            log_entry.update(custom_fields)
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry, default=str)
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Extract contextual information from Flask request"""
        try:
            context = {
                'request_id': getattr(g, 'request_id', str(uuid.uuid4())),
                'url': request.url,
                'method': request.method,
                'endpoint': request.endpoint,
                'remote_addr': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
            
            # Add user context if authenticated
            if hasattr(g, 'current_user') and g.current_user:
                context.update({
                    'user_id': getattr(g.current_user, 'id', None),
                    'username': getattr(g.current_user, 'username', None),
                    'user_role': getattr(g.current_user, 'role', None)
                })
            
            return context
        except Exception:
            return {'context_error': 'Failed to extract request context'}
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data for PCI DSS compliance"""
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = f"***{value[-4:]}"
                else:
                    masked_data[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value
        
        return masked_data


class ContextualFilter(logging.Filter):
    """
    Logging filter that adds contextual information to log records
    """
    
    def filter(self, record):
        """Add contextual information to every log record"""
        # Add request ID for tracing
        if has_request_context():
            if not hasattr(g, 'request_id'):
                g.request_id = str(uuid.uuid4())
            record.request_id = g.request_id
        else:
            record.request_id = 'no-request-context'
        
        # Add module information (avoid overwriting existing 'module' attribute)
        record.logger_module = record.name.split('.')[-1] if '.' in record.name else record.name
        
        return True


class SecurityAuditHandler(logging.Handler):
    """
    Specialized handler for security-sensitive events
    Routes to dedicated security log files and alerting systems
    """
    
    def __init__(self, security_log_path, alert_threshold=logging.ERROR):
        super().__init__()
        self.security_log_path = security_log_path
        self.alert_threshold = alert_threshold
        self.file_handler = logging.handlers.RotatingFileHandler(
            security_log_path, maxBytes=50*1024*1024, backupCount=10
        )
        self.file_handler.setFormatter(StructuredFormatter())
    
    def emit(self, record):
        """Handle security-sensitive log records"""
        # Always write to security log file
        self.file_handler.emit(record)
        
        # Send alerts for critical security events
        if record.levelno >= self.alert_threshold:
            self._send_security_alert(record)
    
    def _send_security_alert(self, record):
        """Send real-time security alerts (implement based on your alerting system)"""
        # This would integrate with your alerting system (Slack, PagerDuty, etc.)
        try:
            alert_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'logger_module': getattr(record, 'module', 'unknown'),
                'request_id': getattr(record, 'request_id', 'unknown')
            }
            # TODO: Implement actual alerting mechanism
            print(f"SECURITY ALERT: {json.dumps(alert_data)}")
        except Exception as e:
            # Never let alerting failures break the application
            print(f"Security alert failed: {e}")


class EnterpriseLogger:
    """
    Central enterprise logging manager
    Coordinates multiple handlers and provides high-level logging interface
    """
    
    def __init__(self, app=None):
        self.app = app
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self.handlers = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize enterprise logging for Flask application"""
        self.app = app
        
        # Create logs directory structure
        self._setup_log_directories(app)
        
        # Configure logging levels
        log_level = logging.DEBUG if app.debug else logging.INFO
        
        # Keep existing console handlers but clear file handlers to prevent duplicates
        existing_console_handlers = [h for h in app.logger.handlers if isinstance(h, logging.StreamHandler) and h.stream.name == '<stderr>']
        app.logger.handlers.clear()
        # Restore console handlers
        for handler in existing_console_handlers:
            app.logger.addHandler(handler)
        
        # Add contextual filter to all loggers
        contextual_filter = ContextualFilter()
        
        # 1. Console Handler (only if debug mode or no handlers exist)
        if app.debug or not app.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s %(module)s.%(funcName)s: %(message)s'
            ))
            console_handler.addFilter(contextual_filter)
            app.logger.addHandler(console_handler)
            self.handlers['console'] = console_handler
        
        # 2. Main Application Log (structured JSON)
        app_log_path = os.path.join(app.config['LOG_DIRECTORIES']['application'], 'application.log')
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_path, maxBytes=100*1024*1024, backupCount=20
        )
        app_handler.setFormatter(StructuredFormatter())
        app_handler.addFilter(contextual_filter)
        app.logger.addHandler(app_handler)
        self.handlers['application'] = app_handler
        
        # 3. Security Audit Log
        security_log_path = os.path.join(app.config['LOG_DIRECTORIES']['security_audit'], 'security_audit.log')
        security_handler = SecurityAuditHandler(security_log_path)
        security_handler.addFilter(contextual_filter)
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
        self.handlers['security'] = security_handler
        
        # 4. Banking Operations Log
        banking_log_path = os.path.join(app.config['LOG_DIRECTORIES']['banking_operations'], 'banking_operations.log')
        banking_handler = logging.handlers.RotatingFileHandler(
            banking_log_path, maxBytes=100*1024*1024, backupCount=30
        )
        banking_handler.setFormatter(StructuredFormatter())
        banking_handler.addFilter(contextual_filter)
        banking_logger = logging.getLogger('banking')
        banking_logger.addHandler(banking_handler)
        banking_logger.setLevel(logging.INFO)
        self.handlers['banking'] = banking_handler
        
        # 5. API Access Log
        api_log_path = os.path.join(app.config['LOG_DIRECTORIES']['api_access'], 'api_access.log')
        api_handler = logging.handlers.RotatingFileHandler(
            api_log_path, maxBytes=50*1024*1024, backupCount=15
        )
        api_handler.setFormatter(StructuredFormatter())
        api_handler.addFilter(contextual_filter)
        api_logger = logging.getLogger('api')
        api_logger.addHandler(api_handler)
        api_logger.setLevel(logging.INFO)
        self.handlers['api'] = api_handler
        
        # 6. Compliance Log
        compliance_log_path = os.path.join(app.config['LOG_DIRECTORIES']['compliance'], 'compliance.log')
        compliance_handler = logging.handlers.RotatingFileHandler(
            compliance_log_path, maxBytes=100*1024*1024, backupCount=50
        )
        compliance_handler.setFormatter(StructuredFormatter())
        compliance_handler.addFilter(contextual_filter)
        compliance_logger = logging.getLogger('compliance')
        compliance_logger.addHandler(compliance_handler)
        compliance_logger.setLevel(logging.INFO)
        self.handlers['compliance'] = compliance_handler
        
        # 7. Performance Log
        performance_log_path = os.path.join(app.config['LOG_DIRECTORIES']['performance'], 'performance.log')
        performance_handler = logging.handlers.RotatingFileHandler(
            performance_log_path, maxBytes=75*1024*1024, backupCount=25
        )
        performance_handler.setFormatter(StructuredFormatter())
        performance_handler.addFilter(contextual_filter)
        performance_logger = logging.getLogger('performance')
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.INFO)
        self.handlers['performance'] = performance_handler
        
        # 8. Error Log
        error_log_path = os.path.join(app.config['LOG_DIRECTORIES']['errors'], 'errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path, maxBytes=50*1024*1024, backupCount=20
        )
        error_handler.setFormatter(StructuredFormatter())
        error_handler.addFilter(contextual_filter)
        error_logger = logging.getLogger('errors')
        error_logger.addHandler(error_handler)
        error_logger.setLevel(logging.WARNING)
        self.handlers['errors'] = error_handler
        
        # 9. User Activity Log
        user_activity_log_path = os.path.join(app.config['LOG_DIRECTORIES']['user_activity'], 'user_activity.log')
        user_activity_handler = logging.handlers.RotatingFileHandler(
            user_activity_log_path, maxBytes=75*1024*1024, backupCount=30
        )
        user_activity_handler.setFormatter(StructuredFormatter())
        user_activity_handler.addFilter(contextual_filter)
        user_activity_logger = logging.getLogger('user_activity')
        user_activity_logger.addHandler(user_activity_handler)
        user_activity_logger.setLevel(logging.INFO)
        self.handlers['user_activity'] = user_activity_handler
        
        # 10. System Monitoring Log
        system_monitoring_log_path = os.path.join(app.config['LOG_DIRECTORIES']['system_monitoring'], 'system_monitoring.log')
        system_monitoring_handler = logging.handlers.RotatingFileHandler(
            system_monitoring_log_path, maxBytes=50*1024*1024, backupCount=15
        )
        system_monitoring_handler.setFormatter(StructuredFormatter())
        system_monitoring_handler.addFilter(contextual_filter)
        system_monitoring_logger = logging.getLogger('system_monitoring')
        system_monitoring_logger.addHandler(system_monitoring_handler)
        system_monitoring_logger.setLevel(logging.INFO)
        self.handlers['system_monitoring'] = system_monitoring_handler
        
        # 11. Data Integrity Log
        data_integrity_log_path = os.path.join(app.config['LOG_DIRECTORIES']['data_integrity'], 'data_integrity.log')
        data_integrity_handler = logging.handlers.RotatingFileHandler(
            data_integrity_log_path, maxBytes=75*1024*1024, backupCount=40
        )
        data_integrity_handler.setFormatter(StructuredFormatter())
        data_integrity_handler.addFilter(contextual_filter)
        data_integrity_logger = logging.getLogger('data_integrity')
        data_integrity_logger.addHandler(data_integrity_handler)
        data_integrity_logger.setLevel(logging.INFO)
        self.handlers['data_integrity'] = data_integrity_handler
        
        # Set application logger level
        app.logger.setLevel(log_level)
        
        # Configure third-party loggers
        self._configure_third_party_loggers()
        
        # Register request context processor
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        app.logger.info("Enterprise logging system initialized", extra={
            'custom_fields': {
                'handlers_count': len(self.handlers),
                'log_level': logging.getLevelName(log_level),
                'structured_logging': True,
                'security_auditing': True
            }
        })
    
    def _setup_log_directories(self, app):
        """Create specialized log directory structure with individual folders for each log stream"""
        from datetime import datetime
        
        # Get the root logs directory from project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base_log_dir = os.path.join(project_root, 'logs')
        
        # Create nested year/month/date structure
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        date = now.strftime('%d')
        
        # Define individual log stream directories
        log_streams = [
            'application',      # Main application events and system operations
            'api_access',       # API request/response lifecycle tracking
            'security_audit',   # Security-sensitive events and authentication
            'banking_operations', # Financial transaction and banking operations
            'compliance',       # Regulatory compliance and audit trail
            'performance',      # System performance and monitoring
            'errors',          # Error logs and exceptions
            'user_activity',   # User behavior and session tracking
            'system_monitoring', # Infrastructure and system health
            'data_integrity'   # Data validation and integrity checks
        ]
        
        # Create individual directories for each log stream with nested date structure
        app.config['LOG_DIRECTORIES'] = {}
        
        for stream in log_streams:
            stream_dir = os.path.join(base_log_dir, stream, year, month, date)
            try:
                os.makedirs(stream_dir, mode=0o750, exist_ok=True)  # Force creation with exist_ok
            except Exception as e:
                # Create fallback without nested structure
                fallback_dir = os.path.join(base_log_dir, stream)
                os.makedirs(fallback_dir, mode=0o750, exist_ok=True)
                stream_dir = fallback_dir
            
            app.config['LOG_DIRECTORIES'][stream] = stream_dir
        
        # Store the main application log directory for backward compatibility
        app.config['CURRENT_LOG_DIR'] = app.config['LOG_DIRECTORIES']['application']
    
    def _configure_third_party_loggers(self):
        """Configure third-party library loggers"""
        # Reduce noise from third-party libraries
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('engineio').setLevel(logging.WARNING)
        logging.getLogger('socketio').setLevel(logging.WARNING)
        
        # Keep important gunicorn logs
        logging.getLogger('gunicorn.error').setLevel(logging.INFO)
        logging.getLogger('gunicorn.access').setLevel(logging.INFO)
    
    def _before_request(self):
        """Set up request context for logging"""
        g.request_id = str(uuid.uuid4())
        g.request_start_time = datetime.utcnow()
        
        # Log incoming request
        api_logger = logging.getLogger('api')
        api_logger.info("Request received", extra={
            'custom_fields': {
                'event_type': 'request_start',
                'method': request.method,
                'url': request.url,
                'content_length': request.content_length,
                'content_type': request.content_type
            }
        })
    
    def _after_request(self, response):
        """Log request completion"""
        try:
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()
            
            # Get response size safely, handling static files in passthrough mode
            response_size = 0
            try:
                # For static files and passthrough responses, this might fail
                response_size = len(response.get_data()) if hasattr(response, 'get_data') else 0
            except (RuntimeError, ValueError):
                # Response is in direct passthrough mode (static files)
                response_size = int(response.headers.get('Content-Length', 0))
            
            api_logger = logging.getLogger('api')
            api_logger.info("Request completed", extra={
                'custom_fields': {
                    'event_type': 'request_end',
                    'status_code': response.status_code,
                    'response_size': response_size,
                    'duration_seconds': duration,
                    'cache_control': response.headers.get('Cache-Control')
                }
            })
        except Exception as e:
            current_app.logger.error(f"Error in request logging: {e}")
        
        return response
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          level: str = 'WARNING', user_id: Optional[str] = None):
        """Log security-sensitive events"""
        security_logger = logging.getLogger('security')
        
        log_data = {
            'event_type': event_type,
            'details': details,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        log_level = getattr(logging, level.upper(), logging.WARNING)
        security_logger.log(log_level, f"Security event: {event_type}", extra={
            'custom_fields': log_data
        })
        
        # Also log to database
        from .centralized_audit_logger import centralized_audit_logger
        centralized_audit_logger.log_security_event(
            event_type=event_type,
            severity=level.lower(),
            user_id=user_id,
            event_data=details
        )

    def log_banking_operation(self, operation_type: str, details: Dict[str, Any],
                            user_id: str, amount: Optional[float] = None):
        """Log banking operations for audit compliance"""
        banking_logger = logging.getLogger('banking')
        
        log_data = {
            'operation_type': operation_type,
            'user_id': user_id,
            'details': details,
            'amount': amount,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        banking_logger.info(f"Banking operation: {operation_type}", extra={
            'custom_fields': log_data
        })
        
        # Log transaction audit if transaction_id is provided
        if 'transaction_id' in details:
            from .centralized_audit_logger import centralized_audit_logger
            centralized_audit_logger.log_transaction_audit(
                transaction_id=details['transaction_id'],
                event_type=operation_type,
                new_state=details,
                user_id=user_id
            )

    def get_logger(self, name: str) -> logging.Logger:
        """Get a configured logger for a specific module"""
        logger = logging.getLogger(name)
        
        # Ensure contextual filter is applied
        if not any(isinstance(f, ContextualFilter) for f in logger.filters):
            logger.addFilter(ContextualFilter())
        
        return logger


# Global enterprise logger instance
enterprise_logger = EnterpriseLogger()

# Convenience functions for common logging operations
def log_security_event(event_type: str, details: Dict[str, Any], 
                      level: str = 'WARNING', user_id: Optional[str] = None):
    """Log security events"""
    enterprise_logger.log_security_event(event_type, details, level, user_id)

def log_banking_operation(operation_type: str, details: Dict[str, Any],
                         user_id: str, amount: Optional[float] = None):
    """Log banking operations"""
    enterprise_logger.log_banking_operation(operation_type, details, user_id, amount)

def get_enterprise_logger(name: str) -> logging.Logger:
    """Get enterprise-configured logger"""
    return enterprise_logger.get_logger(name)
