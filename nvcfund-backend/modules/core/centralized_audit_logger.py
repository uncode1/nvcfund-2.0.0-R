"""
Centralized Audit Logging System
Implements comprehensive audit trails for banking compliance
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path
import threading
from flask import request, g
from flask_login import current_user

# Create centralized audit logger
audit_logger = logging.getLogger('banking_audit')

class AuditEventType(Enum):
    """Banking audit event types for compliance"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    MFA_SETUP = "mfa_setup"
    MFA_DISABLE = "mfa_disable"
    ACCOUNT_ACCESS = "account_access"
    TRANSACTION_CREATE = "transaction_create"
    TRANSACTION_MODIFY = "transaction_modify"
    TRANSACTION_DELETE = "transaction_delete"
    FUNDS_TRANSFER = "funds_transfer"
    ACCOUNT_CREATE = "account_create"
    ACCOUNT_MODIFY = "account_modify"
    ACCOUNT_CLOSE = "account_close"
    USER_CREATE = "user_create"
    USER_MODIFY = "user_modify"
    USER_DELETE = "user_delete"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change"
    ADMIN_ACTION = "admin_action"
    SECURITY_INCIDENT = "security_incident"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    SYSTEM_CONFIG = "system_config"
    COMPLIANCE_ACTION = "compliance_action"
    GDPR_REQUEST = "gdpr_request"
    API_ACCESS = "api_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CentralizedAuditLogger:
    """
    Centralized audit logging system for banking compliance
    Ensures all actions are logged with appropriate detail
    """
    
    def __init__(self):
        self.setup_audit_logging()
        self._lock = threading.Lock()
        
    def setup_audit_logging(self):
        """Setup centralized audit logging configuration"""
        try:
            # Create audit logs directory
            audit_dir = Path('logs/audit')
            audit_dir.mkdir(parents=True, exist_ok=True)
            
            # Configure audit logger
            audit_logger.setLevel(logging.INFO)
            
            # Remove existing handlers to avoid duplication
            audit_logger.handlers.clear()
            
            # Create file handler with rotation
            from logging.handlers import TimedRotatingFileHandler
            
            audit_file_handler = TimedRotatingFileHandler(
                filename=audit_dir / 'banking_audit.log',
                when='midnight',
                interval=1,
                backupCount=2555,  # Keep 7 years of audit logs
                encoding='utf-8'
            )
            
            # Custom audit format
            audit_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | AUDIT | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S UTC'
            )
            audit_file_handler.setFormatter(audit_formatter)
            
            # Add handler to audit logger
            audit_logger.addHandler(audit_file_handler)
            
            # Ensure audit logger doesn't propagate to root logger
            audit_logger.propagate = False
            
            # Create separate handlers for different severity levels
            self._setup_severity_handlers(audit_dir)
            
        except Exception as e:
            # Fallback to console logging if file setup fails
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(audit_formatter)
            audit_logger.addHandler(console_handler)
            audit_logger.error(f"Failed to setup file audit logging: {e}")
    
    def _setup_severity_handlers(self, audit_dir: Path):
        """Setup separate log files for different severity levels"""
        try:
            from logging.handlers import TimedRotatingFileHandler
            
            # Critical events log
            critical_handler = TimedRotatingFileHandler(
                filename=audit_dir / 'critical_events.log',
                when='midnight',
                interval=1,
                backupCount=2555,
                encoding='utf-8'
            )
            critical_handler.setLevel(logging.CRITICAL)
            critical_handler.addFilter(lambda record: 'CRITICAL' in record.getMessage())
            
            # Security events log
            security_handler = TimedRotatingFileHandler(
                filename=audit_dir / 'security_events.log',
                when='midnight',
                interval=1,
                backupCount=2555,
                encoding='utf-8'
            )
            security_handler.addFilter(lambda record: 'SECURITY' in record.getMessage())
            
            # Transaction events log
            transaction_handler = TimedRotatingFileHandler(
                filename=audit_dir / 'transaction_events.log',
                when='midnight',
                interval=1,
                backupCount=2555,
                encoding='utf-8'
            )
            transaction_handler.addFilter(lambda record: 'TRANSACTION' in record.getMessage())
            
            # Apply formatter to all handlers
            audit_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | AUDIT | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S UTC'
            )
            
            for handler in [critical_handler, security_handler, transaction_handler]:
                handler.setFormatter(audit_formatter)
                audit_logger.addHandler(handler)
                
        except Exception as e:
            audit_logger.error(f"Failed to setup severity-specific handlers: {e}")
    
    def log_event(self, 
                  event_type: AuditEventType, 
                  severity: AuditSeverity = AuditSeverity.MEDIUM,
                  description: str = "",
                  resource: str = None,
                  resource_id: str = None,
                  additional_data: Dict[str, Any] = None,
                  correlation_id: str = None) -> str:
        """
        Log audit event with comprehensive details
        Returns correlation ID for tracking
        """
        
        try:
            with self._lock:
                # Generate correlation ID if not provided
                if not correlation_id:
                    correlation_id = self._generate_correlation_id()
                
                # Collect request context
                request_context = self._get_request_context()
                
                # Collect user context
                user_context = self._get_user_context()
                
                # Build audit record
                audit_record = {
                    'correlation_id': correlation_id,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'event_type': event_type.value,
                    'severity': severity.value,
                    'description': description,
                    'resource': resource,
                    'resource_id': resource_id,
                    'user_context': user_context,
                    'request_context': request_context,
                    'additional_data': additional_data or {},
                    'compliance_flags': self._get_compliance_flags(event_type),
                    'retention_period': self._get_retention_period(event_type)
                }
                
                # Log the audit record
                log_level = self._get_log_level(severity)
                audit_message = self._format_audit_message(audit_record)
                
                audit_logger.log(log_level, audit_message)
                
                # Log to appropriate severity-specific log
                if severity == AuditSeverity.CRITICAL:
                    audit_logger.critical(f"CRITICAL | {audit_message}")
                elif event_type in [AuditEventType.LOGIN_FAILED, AuditEventType.SECURITY_INCIDENT, AuditEventType.SUSPICIOUS_ACTIVITY]:
                    audit_logger.warning(f"SECURITY | {audit_message}")
                elif event_type in [AuditEventType.TRANSACTION_CREATE, AuditEventType.FUNDS_TRANSFER, AuditEventType.TRANSACTION_MODIFY]:
                    audit_logger.info(f"TRANSACTION | {audit_message}")
                
                # Store in database
                self._store_audit_record(audit_record)
                
                return correlation_id
                
        except Exception as e:
            # Ensure audit logging failures don't break the application
            try:
                audit_logger.error(f"Audit logging failed: {e}")
            except:
                pass  # Ultimate fallback - don't let audit logging break the app
            return "AUDIT_ERROR"
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for event tracking"""
        import uuid
        return f"AUDIT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Collect request context information"""
        try:
            if request:
                return {
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'url': request.url,
                    'referrer': request.headers.get('Referer', ''),
                    'session_id': getattr(g, 'session_id', None)
                }
        except:
            pass
        
        return {
            'ip_address': 'unknown',
            'user_agent': 'unknown',
            'method': 'unknown',
            'endpoint': 'unknown',
            'url': 'unknown',
            'referrer': 'unknown',
            'session_id': None
        }
    
    def _get_user_context(self) -> Dict[str, Any]:
        """Collect user context information"""
        try:
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                return {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'role': getattr(current_user, 'role', 'unknown'),
                    'email': getattr(current_user, 'email', ''),
                    'last_login': getattr(current_user, 'last_login', '').isoformat() if hasattr(getattr(current_user, 'last_login', ''), 'isoformat') else str(getattr(current_user, 'last_login', ''))
                }
        except:
            pass
        
        return {
            'user_id': None,
            'username': 'anonymous',
            'role': 'unauthenticated',
            'email': '',
            'last_login': ''
        }
    
    def _get_compliance_flags(self, event_type: AuditEventType) -> list:
        """Get compliance flags for event type"""
        compliance_mapping = {
            AuditEventType.LOGIN: ['SOX', 'PCI-DSS'],
            AuditEventType.LOGIN_FAILED: ['SOX', 'PCI-DSS', 'SECURITY'],
            AuditEventType.TRANSACTION_CREATE: ['SOX', 'BSA', 'AML'],
            AuditEventType.FUNDS_TRANSFER: ['SOX', 'BSA', 'AML', 'WIRE_TRANSFER'],
            AuditEventType.ACCOUNT_CREATE: ['SOX', 'KYC', 'CDD'],
            AuditEventType.USER_CREATE: ['SOX', 'ACCESS_CONTROL'],
            AuditEventType.ROLE_CHANGE: ['SOX', 'ACCESS_CONTROL'],
            AuditEventType.ADMIN_ACTION: ['SOX', 'PRIVILEGED_ACCESS'],
            AuditEventType.SECURITY_INCIDENT: ['SECURITY', 'INCIDENT_RESPONSE'],
            AuditEventType.DATA_EXPORT: ['GDPR', 'DATA_PROTECTION'],
            AuditEventType.GDPR_REQUEST: ['GDPR', 'DATA_PROTECTION'],
            AuditEventType.SUSPICIOUS_ACTIVITY: ['AML', 'BSA', 'SAR']
        }
        
        return compliance_mapping.get(event_type, ['GENERAL'])
    
    def _get_retention_period(self, event_type: AuditEventType) -> str:
        """Get retention period for event type"""
        retention_mapping = {
            AuditEventType.LOGIN: '3_years',
            AuditEventType.LOGIN_FAILED: '3_years',
            AuditEventType.TRANSACTION_CREATE: '7_years',
            AuditEventType.FUNDS_TRANSFER: '7_years',
            AuditEventType.ACCOUNT_CREATE: '7_years',
            AuditEventType.SECURITY_INCIDENT: '7_years',
            AuditEventType.ADMIN_ACTION: '7_years',
            AuditEventType.GDPR_REQUEST: '3_years'
        }
        
        return retention_mapping.get(event_type, '5_years')
    
    def _get_log_level(self, severity: AuditSeverity) -> int:
        """Map audit severity to logging level"""
        mapping = {
            AuditSeverity.LOW: logging.INFO,
            AuditSeverity.MEDIUM: logging.INFO,
            AuditSeverity.HIGH: logging.WARNING,
            AuditSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.INFO)
    
    def _format_audit_message(self, audit_record: dict) -> str:
        """Format audit record for logging"""
        try:
            # Create a serializable copy of the audit record
            serializable_record = self._make_serializable(audit_record)
            return json.dumps(serializable_record, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            # Fallback to basic string representation
            return f"AUDIT_FORMAT_ERROR: {str(audit_record)[:500]}..."

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):  # Handle Enum objects
            return obj.value
        elif hasattr(obj, '__dict__'):  # Handle custom objects
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        else:
            return obj
    
    def _store_audit_record(self, audit_record: dict):
        """Store audit record in database"""
        try:
            from .models import AuditLog
            from . import db
            
            # Create database audit log entry
            db_audit_log = AuditLog(
                event_type=audit_record['event_type'],
                event_description=audit_record['description'],
                user_id=audit_record['user_context'].get('user_id'),
                session_id=audit_record['request_context'].get('session_id', ''),
                user_ip=audit_record['request_context'].get('ip_address', ''),
                additional_data=json.dumps(audit_record, default=str)
            )
            
            db.session.add(db_audit_log)
            db.session.commit()
            
        except Exception as e:
            # Log database storage failure but don't break audit logging
            audit_logger.error(f"Failed to store audit record in database: {e}")
    
    def search_audit_logs(self, 
                         start_date: datetime = None,
                         end_date: datetime = None,
                         event_types: list = None,
                         user_id: int = None,
                         correlation_id: str = None,
                         limit: int = 1000) -> list:
        """
        Search audit logs with filters
        Returns list of matching audit records
        """
        # Implementation would search through audit log files
        # This is a placeholder for the search functionality
        # In production, this would integrate with log management systems
        return []
    
    def generate_compliance_report(self, 
                                 start_date: datetime,
                                 end_date: datetime,
                                 compliance_type: str = 'SOX') -> Dict[str, Any]:
        """
        Generate compliance report for specific period
        Returns compliance metrics and event summaries
        """
        # Implementation would generate compliance-specific reports
        # This is a placeholder for the reporting functionality
        return {
            'report_type': compliance_type,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_events': 0,
            'event_summary': {},
            'compliance_status': 'compliant'
        }

# Global centralized audit logger instance
centralized_audit_logger = CentralizedAuditLogger()
