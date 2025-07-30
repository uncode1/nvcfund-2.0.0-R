"""
Log Viewer Service with RBAC and Quality Filters
Provides secure access to nested logs based on user roles
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    SECURITY_REPORTS = "security_reports"
    APPLICATION = "application"
    BANKING = "banking"
    COMPLIANCE = "compliance"
    ADMIN = "admin"
    ERRORS = "errors"
    AUDIT = "audit"
    SYSTEM = "system"
    TRANSACTIONS = "transactions"
    AUTH = "auth"
    API = "api"

class LogViewerService:
    """Service for viewing logs with RBAC and filtering"""
    
    def __init__(self, base_log_dir: str = "logs"):
        self.base_log_dir = Path(base_log_dir)
        
        # RBAC permissions for log categories
        self.role_permissions = {
            'super_admin': [cat.value for cat in LogCategory],
            'admin': [
                LogCategory.APPLICATION.value,
                LogCategory.BANKING.value,
                LogCategory.ADMIN.value,
                LogCategory.ERRORS.value,
                LogCategory.SYSTEM.value,
                LogCategory.API.value
            ],
            'compliance_officer': [
                LogCategory.COMPLIANCE.value,
                LogCategory.AUDIT.value,
                LogCategory.BANKING.value,
                LogCategory.TRANSACTIONS.value
            ],
            'security_officer': [
                LogCategory.SECURITY_REPORTS.value,
                LogCategory.AUTH.value,
                LogCategory.ERRORS.value,
                LogCategory.AUDIT.value,
                LogCategory.SYSTEM.value
            ],
            'treasury_officer': [
                LogCategory.BANKING.value,
                LogCategory.TRANSACTIONS.value,
                LogCategory.AUDIT.value
            ],
            'banking_officer': [
                LogCategory.BANKING.value,
                LogCategory.TRANSACTIONS.value
            ],
            'operations_officer': [
                LogCategory.APPLICATION.value,
                LogCategory.SYSTEM.value,
                LogCategory.ERRORS.value
            ],
            'standard_user': []  # No log access for standard users
        }
    
    def get_user_log_categories(self, user_role: str) -> List[str]:
        """Get log categories accessible to user role"""
        return self.role_permissions.get(user_role, [])
    
    def get_available_dates(self, user_role: str, days_back: int = 30) -> List[Dict[str, str]]:
        """Get available log dates within user's permission and time range"""
        accessible_dates = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        current_date = start_date
        while current_date <= end_date:
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")
            
            date_dir = self.base_log_dir / year / month / day
            if date_dir.exists():
                # Check if user has access to any logs in this date
                user_categories = self.get_user_log_categories(user_role)
                has_accessible_logs = False
                
                for category in user_categories:
                    category_dir = date_dir / category
                    if category_dir.exists() and any(category_dir.iterdir()):
                        has_accessible_logs = True
                        break
                
                if has_accessible_logs:
                    accessible_dates.append({
                        'date': current_date.strftime("%Y-%m-%d"),
                        'display_date': current_date.strftime("%B %d, %Y"),
                        'path': f"{year}/{month}/{day}"
                    })
            
            current_date += timedelta(days=1)
        
        return sorted(accessible_dates, key=lambda x: x['date'], reverse=True)
    
    def get_log_files(self, user_role: str, date_path: str, category: str) -> List[Dict[str, Any]]:
        """Get log files for specific date and category"""
        if category not in self.get_user_log_categories(user_role):
            return []
        
        log_dir = self.base_log_dir / date_path / category
        if not log_dir.exists():
            return []
        
        log_files = []
        for file_path in log_dir.iterdir():
            if file_path.is_file() and (file_path.suffix in ['.log', '.txt']):
                try:
                    stat = file_path.stat()
                    log_files.append({
                        'name': file_path.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'path': str(file_path.relative_to(self.base_log_dir))
                    })
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        return sorted(log_files, key=lambda x: x['modified'], reverse=True)
    
    def read_log_content(self, user_role: str, file_path: str, 
                        filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Read and filter log content based on user permissions and filters"""
        # Parse file path to extract category
        path_parts = Path(file_path).parts
        if len(path_parts) < 4:
            return {'error': 'Invalid file path'}
        
        category = path_parts[3]  # Year/Month/Day/Category structure
        
        if category not in self.get_user_log_categories(user_role):
            return {'error': 'Access denied to this log category'}
        
        full_path = self.base_log_dir / file_path
        if not full_path.exists() or not full_path.is_file():
            return {'error': 'Log file not found'}
        
        try:
            filtered_lines = []
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Process file line-by-line to avoid high memory usage
                for line in f:
                    parsed_line = self._parse_and_filter_line(line, filters or {})
                    if parsed_line:
                        filtered_lines.append(parsed_line)
            
            return {
                'content': filtered_lines,
                'total_lines': len(lines),
                'filtered_lines': len(filtered_lines),
                'file_info': {
                    'name': full_path.name,
                    'size': full_path.stat().st_size,
                    'category': category,
                    'modified': datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
                }
            }
        
        except Exception as e:
            logger.error(f"Error reading log file {file_path}: {e}")
            return {'error': f'Error reading log file: {str(e)}'}
    
    def _parse_and_filter_line(self, line: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and apply filters to a single log line."""
        line = line.strip()
        if not line:
            return None

        # Extract filter parameters
        log_level = filters.get('level', '').upper()
        search_term = filters.get('search', '').lower()
        start_time = filters.get('start_time')
        end_time = filters.get('end_time')
        max_lines = int(filters.get('max_lines', 1000))
        
        # Convert time filters to datetime objects
        start_dt = None
        end_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                pass
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                pass
        
        # Parse log line
        parsed_line = self._parse_log_line(line, 0) # line_num is not critical here

        # Apply level filter
        if log_level and parsed_line['level'] != log_level:
            return None

        # Apply search filter
        if search_term and search_term not in line.lower():
            return None

        # Apply time filters
        if start_dt and parsed_line['timestamp_dt'] and parsed_line['timestamp_dt'] < start_dt:
            return None
        if end_dt and parsed_line['timestamp_dt'] and parsed_line['timestamp_dt'] > end_dt:
            return None

        return parsed_line
    
    def _parse_log_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse a log line into structured data"""
        # Common log patterns
        patterns = [
            # Standard format: TIMESTAMP - LEVEL - MESSAGE
            r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.,]\d+).*? - (\w+) - (.+)$',
            # ISO format: [TIMESTAMP] LEVEL [context] message
            r'^\[(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.,]\d+)\] (\w+) (.+)$',
            # Simple format: TIMESTAMP LEVEL MESSAGE
            r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.,]\d+) (\w+): (.+)$'
        ]
        
        timestamp_str = ""
        level = "INFO"
        message = line
        timestamp_dt = None
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                timestamp_str = match.group(1)
                level = match.group(2).upper()
                message = match.group(3)
                
                # Parse timestamp
                try:
                    # Handle different timestamp formats
                    timestamp_str_clean = timestamp_str.replace(',', '.')
                    if 'T' in timestamp_str_clean:
                        timestamp_dt = datetime.fromisoformat(timestamp_str_clean.replace('Z', '+00:00'))
                    else:
                        timestamp_dt = datetime.strptime(timestamp_str_clean[:19], '%Y-%m-%d %H:%M:%S')
                except:
                    pass
                break
        
        return {
            'line_number': line_num,
            'timestamp': timestamp_str,
            'timestamp_dt': timestamp_dt,
            'level': level,
            'message': message,
            'raw_line': line,
            'severity_class': self._get_severity_class(level)
        }
    
    def _get_severity_class(self, level: str) -> str:
        """Get CSS class for log level severity"""
        severity_map = {
            'DEBUG': 'text-muted',
            'INFO': 'text-info',
            'WARNING': 'text-warning',
            'ERROR': 'text-danger',
            'CRITICAL': 'text-danger fw-bold'
        }
        return severity_map.get(level.upper(), 'text-secondary')
    
    def get_log_statistics(self, user_role: str, date_path: str) -> Dict[str, Any]:
        """Get log statistics for a specific date"""
        stats = {
            'categories': {},
            'total_files': 0,
            'total_size': 0,
            'accessible_categories': self.get_user_log_categories(user_role)
        }
        
        date_dir = self.base_log_dir / date_path
        if not date_dir.exists():
            return stats
        
        for category in self.get_user_log_categories(user_role):
            category_dir = date_dir / category
            if category_dir.exists():
                files = list(category_dir.glob('*'))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                
                stats['categories'][category] = {
                    'files': file_count,
                    'size': total_size,
                    'size_human': self._format_file_size(total_size)
                }
                stats['total_files'] += file_count
                stats['total_size'] += total_size
        
        stats['total_size_human'] = self._format_file_size(stats['total_size'])
        return stats
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"

# Service instance
log_viewer_service = LogViewerService()