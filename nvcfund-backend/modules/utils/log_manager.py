"""
Enhanced Log Manager with Nested Year/Month/Date Structure
Integrates with NVC Banking Platform logging system
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

class NestedLogManager:
    """Enhanced log manager with nested year/month/date structure"""
    
    def __init__(self, base_log_dir: str = "logs"):
        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(exist_ok=True)
        
        # Log categories for banking platform
        self.categories = {
            "security_reports": "Security audit reports and assessments",
            "application": "General application logs",
            "banking": "Banking operation logs",
            "compliance": "AML, KYC, regulatory compliance logs",
            "admin": "Administrative and management logs",
            "errors": "Error logs and exception reports",
            "audit": "Audit trail logs",
            "system": "System health and monitoring logs",
            "transactions": "Transaction processing logs",
            "auth": "Authentication and authorization logs",
            "api": "API access and integration logs"
        }
    
    def get_current_log_path(self, category: str = "application") -> Path:
        """Get current log path for specified category"""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        
        log_dir = self.base_log_dir / year / month / date / category
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir
    
    def get_log_file_path(self, filename: str, category: str = "application") -> Path:
        """Get full path for a log file in the appropriate category"""
        log_dir = self.get_current_log_path(category)
        return log_dir / filename
    
    def create_daily_structure(self) -> Path:
        """Create complete daily log structure"""
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        date = now.strftime("%d")
        
        current_date_dir = self.base_log_dir / year / month / date
        
        for category in self.categories.keys():
            category_dir = current_date_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
        
        return current_date_dir
    
    def log_security_event(self, event_type: str, data: Dict[str, Any], 
                          user_id: Optional[str] = None) -> str:
        """Log security events with proper categorization"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "data": data,
            "category": "security"
        }
        
        # Determine appropriate category
        if event_type in ["audit_report", "vulnerability_scan", "security_assessment"]:
            category = "security_reports"
        elif event_type in ["login_attempt", "authentication_failure", "session_expired"]:
            category = "auth"
        elif event_type in ["aml_screening", "kyc_verification", "compliance_check"]:
            category = "compliance"
        else:
            category = "system"
        
        log_file = self.get_log_file_path(f"security_{datetime.now().strftime('%Y%m%d')}.log", category)
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - SECURITY - {event_type} - {json.dumps(log_entry)}\n")
        
        return str(log_file)
    
    def log_banking_operation(self, operation_type: str, data: Dict[str, Any], 
                             user_id: Optional[str] = None) -> str:
        """Log banking operations with proper categorization"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "operation_type": operation_type,
            "user_id": user_id,
            "data": data,
            "category": "banking"
        }
        
        # Determine appropriate category
        if operation_type in ["transaction", "wire_transfer", "ach_transfer", "payment"]:
            category = "transactions"
        elif operation_type in ["account_creation", "account_update", "balance_inquiry"]:
            category = "banking"
        elif operation_type in ["admin_override", "bulk_operation", "system_maintenance"]:
            category = "admin"
        else:
            category = "banking"
        
        log_file = self.get_log_file_path(f"banking_{datetime.now().strftime('%Y%m%d')}.log", category)
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - BANKING - {operation_type} - {json.dumps(log_entry)}\n")
        
        return str(log_file)
    
    def log_compliance_event(self, event_type: str, data: Dict[str, Any], 
                           user_id: Optional[str] = None) -> str:
        """Log compliance events with audit trail"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "data": data,
            "category": "compliance",
            "audit_trail": True
        }
        
        log_file = self.get_log_file_path(f"compliance_{datetime.now().strftime('%Y%m%d')}.log", "compliance")
        
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - COMPLIANCE - {event_type} - {json.dumps(log_entry)}\n")
        
        # Also log to audit trail
        audit_file = self.get_log_file_path(f"audit_{datetime.now().strftime('%Y%m%d')}.log", "audit")
        with open(audit_file, 'a') as f:
            f.write(f"{timestamp} - AUDIT - {event_type} - {json.dumps(log_entry)}\n")
        
        return str(log_file)
    
    def create_security_report(self, report_type: str, content: str, 
                              filename: Optional[str] = None) -> str:
        """Create security report in proper category"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not filename:
            filename = f"{report_type}_{timestamp}.txt"
        
        report_file = self.get_log_file_path(filename, "security_reports")
        
        with open(report_file, 'w') as f:
            f.write(content)
        
        return str(report_file)
    
    def get_log_summary(self, days: int = 1) -> Dict[str, Any]:
        """Get summary of logs for specified number of days"""
        summary = {
            "categories": {},
            "total_files": 0,
            "date_range": days
        }
        
        # For now, get current day summary
        current_date_dir = self.get_current_log_path().parent
        
        if current_date_dir.exists():
            for category_dir in current_date_dir.iterdir():
                if category_dir.is_dir() and category_dir.name in self.categories:
                    file_count = len(list(category_dir.glob("*.log"))) + len(list(category_dir.glob("*.txt")))
                    summary["categories"][category_dir.name] = {
                        "files": file_count,
                        "description": self.categories[category_dir.name]
                    }
                    summary["total_files"] += file_count
        
        return summary

# Global log manager instance
log_manager = NestedLogManager()