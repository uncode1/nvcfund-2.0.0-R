"""
User Security Event Tracer
Privacy-preserving security logging with investigative mapping capabilities
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app, g
from sqlalchemy import text
from modules.core.database import get_db_connection
from modules.utils.services import ErrorLoggerService

class UserSecurityTracer:
    """
    Privacy-preserving user security event tracer
    
    Features:
    - Logs events with user IDs only (no usernames in security logs)
    - Provides secure mapping for authorized investigations
    - Maintains audit trail for compliance
    - Supports event correlation and pattern analysis
    """
    
    def __init__(self):
        self.error_logger = ErrorLoggerService()
        self.trace_db = get_db_connection()
    
    def log_security_event(self, user_id: str, event_type: str, event_data: Dict[str, Any], 
                          severity: str = 'medium', source_ip: str = None, 
                          user_agent: str = None) -> str:
        """
        Log a security event with privacy protection
        
        Args:
            user_id: User identifier (numeric ID or username)
            event_type: Type of security event
            event_data: Event details and context
            severity: Event severity (low, medium, high, critical)
            source_ip: Source IP address
            user_agent: User agent string
            
        Returns:
            Event trace ID for correlation
        """
        try:
            # Generate unique trace ID
            trace_id = self._generate_trace_id(user_id, event_type)
            
            # Get internal user ID if username provided
            internal_user_id = self._get_internal_user_id(user_id)
            
            # Create privacy-protected event record
            event_record = {
                'trace_id': trace_id,
                'user_id': internal_user_id,  # Only numeric ID stored
                'event_type': event_type,
                'severity': severity,
                'timestamp': datetime.utcnow().isoformat(),
                'source_ip': self._hash_ip(source_ip) if source_ip else None,
                'user_agent_hash': self._hash_user_agent(user_agent) if user_agent else None,
                'event_data': self._sanitize_event_data(event_data)
            }
            
            # Store in security events table
            self._store_security_event(event_record)
            
            # Create investigation mapping (separate, access-controlled)
            self._store_investigation_mapping(trace_id, user_id, internal_user_id)
            
            # Log to security audit trail
            self._log_to_audit_trail(event_record)
            
            return trace_id
            
        except Exception as e:
            self.error_logger.log_error(f"Security event logging failed: {str(e)}", 
                                      {'user_id': user_id, 'event_type': event_type})
            return None
    
    def get_user_security_timeline(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get security event timeline for a user (authorized access only)
        
        Args:
            user_id: User identifier
            days: Number of days to retrieve
            
        Returns:
            List of security events with timestamps
        """
        try:
            # Verify authorization for user timeline access
            if not self._verify_timeline_access():
                raise PermissionError("Unauthorized access to user security timeline")
            
            internal_user_id = self._get_internal_user_id(user_id)
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = """
                SELECT trace_id, event_type, severity, timestamp, event_data, source_ip
                FROM security_events 
                WHERE user_id = :user_id AND timestamp >= :start_date
                ORDER BY timestamp DESC
                LIMIT 1000
            """
            
            with self.trace_db.connect() as conn:
                result = conn.execute(text(query), {
                    'user_id': internal_user_id,
                    'start_date': start_date.isoformat()
                })
                
                events = []
                for row in result:
                    event = {
                        'trace_id': row.trace_id,
                        'event_type': row.event_type,
                        'severity': row.severity,
                        'timestamp': row.timestamp,
                        'event_data': json.loads(row.event_data) if row.event_data else {},
                        'source_ip_hash': row.source_ip  # Hashed for privacy
                    }
                    events.append(event)
                
                return events
                
        except Exception as e:
            self.error_logger.log_error(f"Failed to retrieve user timeline: {str(e)}", 
                                      {'user_id': user_id})
            return []
    
    def investigate_trace_id(self, trace_id: str) -> Dict[str, Any]:
        """
        Investigate a security event by trace ID (authorized access only)
        
        Args:
            trace_id: Security event trace identifier
            
        Returns:
            Complete event details with user mapping
        """
        try:
            # Verify authorization for investigation
            if not self._verify_investigation_access():
                raise PermissionError("Unauthorized access to security investigation data")
            
            # Get event details
            event_query = """
                SELECT * FROM security_events WHERE trace_id = :trace_id
            """
            
            # Get user mapping
            mapping_query = """
                SELECT user_identifier, internal_user_id, username, email, account_type
                FROM investigation_user_mapping 
                WHERE trace_id = :trace_id
            """
            
            with self.trace_db.connect() as conn:
                # Get event data
                event_result = conn.execute(text(event_query), {'trace_id': trace_id}).fetchone()
                if not event_result:
                    return {'error': 'Trace ID not found'}
                
                # Get user mapping
                mapping_result = conn.execute(text(mapping_query), {'trace_id': trace_id}).fetchone()
                
                investigation_data = {
                    'trace_id': trace_id,
                    'event_type': event_result.event_type,
                    'severity': event_result.severity,
                    'timestamp': event_result.timestamp,
                    'event_data': json.loads(event_result.event_data) if event_result.event_data else {},
                    'source_ip_hash': event_result.source_ip,
                    'user_agent_hash': event_result.user_agent_hash
                }
                
                # Add user details for authorized investigation
                if mapping_result:
                    investigation_data['user_details'] = {
                        'user_id': mapping_result.internal_user_id,
                        'username': mapping_result.username,
                        'email': mapping_result.email,
                        'account_type': mapping_result.account_type
                    }
                
                # Add related events
                investigation_data['related_events'] = self._get_related_events(trace_id, mapping_result.internal_user_id if mapping_result else None)
                
                # Log investigation access
                self._log_investigation_access(trace_id, g.user.id if hasattr(g, 'user') else 'system')
                
                return investigation_data
                
        except Exception as e:
            self.error_logger.log_error(f"Investigation failed: {str(e)}", {'trace_id': trace_id})
            return {'error': 'Investigation failed'}
    
    def get_security_patterns(self, user_id: str = None, event_type: str = None, 
                            hours: int = 24) -> Dict[str, Any]:
        """
        Analyze security event patterns for threat detection
        
        Args:
            user_id: Optional user filter
            event_type: Optional event type filter
            hours: Time window for analysis
            
        Returns:
            Pattern analysis results
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Build dynamic query based on filters
            where_conditions = ["timestamp >= :start_time"]
            params = {'start_time': start_time.isoformat()}
            
            if user_id:
                internal_user_id = self._get_internal_user_id(user_id)
                where_conditions.append("user_id = :user_id")
                params['user_id'] = internal_user_id
            
            if event_type:
                where_conditions.append("event_type = :event_type")
                params['event_type'] = event_type
            
            where_clause = " AND ".join(where_conditions)
            
            # Pattern analysis queries
            patterns = {}
            
            # Event frequency analysis
            frequency_query = f"""
                SELECT event_type, severity, COUNT(*) as event_count
                FROM security_events 
                WHERE {where_clause}
                GROUP BY event_type, severity
                ORDER BY event_count DESC
            """
            
            # Source IP analysis
            ip_query = f"""
                SELECT source_ip, COUNT(*) as event_count
                FROM security_events 
                WHERE {where_clause} AND source_ip IS NOT NULL
                GROUP BY source_ip
                HAVING COUNT(*) > 5
                ORDER BY event_count DESC
            """
            
            # User activity patterns
            user_query = f"""
                SELECT user_id, COUNT(*) as event_count,
                       COUNT(DISTINCT event_type) as unique_events
                FROM security_events 
                WHERE {where_clause}
                GROUP BY user_id
                HAVING COUNT(*) > 10
                ORDER BY event_count DESC
            """
            
            with self.trace_db.connect() as conn:
                # Get frequency patterns
                patterns['frequency'] = [dict(row._mapping) for row in conn.execute(text(frequency_query), params)]
                
                # Get IP patterns
                patterns['suspicious_ips'] = [dict(row._mapping) for row in conn.execute(text(ip_query), params)]
                
                # Get user patterns
                patterns['active_users'] = [dict(row._mapping) for row in conn.execute(text(user_query), params)]
                
                # Calculate risk scores
                patterns['risk_analysis'] = self._calculate_risk_scores(patterns)
            
            return patterns
            
        except Exception as e:
            self.error_logger.log_error(f"Pattern analysis failed: {str(e)}")
            return {'error': 'Pattern analysis failed'}
    
    def _generate_trace_id(self, user_id: str, event_type: str) -> str:
        """Generate unique trace ID for event correlation"""
        timestamp = str(datetime.utcnow().timestamp())
        trace_data = f"{user_id}:{event_type}:{timestamp}"
        return hashlib.sha256(trace_data.encode()).hexdigest()[:16]
    
    def _get_internal_user_id(self, user_identifier: str) -> str:
        """Get internal numeric user ID from username or ID"""
        try:
            # If already numeric, return as-is
            if user_identifier.isdigit():
                return user_identifier
            
            # Look up by username
            query = "SELECT id FROM users WHERE username = :username"
            with self.trace_db.connect() as conn:
                result = conn.execute(text(query), {'username': user_identifier}).fetchone()
                return str(result.id) if result else user_identifier
                
        except Exception:
            return user_identifier  # Fallback to provided identifier
    
    def _hash_ip(self, ip_address: str) -> str:
        """Hash IP address for privacy protection"""
        if not ip_address:
            return None
        salt = current_app.config.get('IP_HASH_SALT', 'nvc_security_salt')
        return hashlib.sha256(f"{ip_address}:{salt}".encode()).hexdigest()[:16]
    
    def _hash_user_agent(self, user_agent: str) -> str:
        """Hash user agent for privacy protection"""
        if not user_agent:
            return None
        return hashlib.sha256(user_agent.encode()).hexdigest()[:16]
    
    def _sanitize_event_data(self, event_data: Dict[str, Any]) -> str:
        """Sanitize and serialize event data"""
        try:
            # Remove sensitive fields
            sanitized = {}
            for key, value in event_data.items():
                if key.lower() not in ['password', 'token', 'secret', 'key', 'credential']:
                    sanitized[key] = str(value) if not isinstance(value, (dict, list)) else value
            
            return json.dumps(sanitized, default=str)
        except Exception:
            return "{}"
    
    def _store_security_event(self, event_record: Dict[str, Any]) -> None:
        """Store security event in database"""
        try:
            query = """
                INSERT INTO security_events 
                (trace_id, user_id, event_type, severity, timestamp, source_ip, user_agent_hash, event_data)
                VALUES (:trace_id, :user_id, :event_type, :severity, :timestamp, :source_ip, :user_agent_hash, :event_data)
            """
            
            with self.trace_db.connect() as conn:
                conn.execute(text(query), event_record)
                conn.commit()
                
        except Exception as e:
            self.error_logger.log_error(f"Failed to store security event: {str(e)}")
    
    def _store_investigation_mapping(self, trace_id: str, user_identifier: str, internal_user_id: str) -> None:
        """Store user mapping for authorized investigations"""
        try:
            # Get additional user details for investigation
            user_query = """
                SELECT username, email, account_type 
                FROM users WHERE id = :user_id
            """
            
            with self.trace_db.connect() as conn:
                user_result = conn.execute(text(user_query), {'user_id': internal_user_id}).fetchone()
                
                mapping_query = """
                    INSERT INTO investigation_user_mapping 
                    (trace_id, user_identifier, internal_user_id, username, email, account_type, created_at)
                    VALUES (:trace_id, :user_identifier, :internal_user_id, :username, :email, :account_type, :created_at)
                """
                
                mapping_data = {
                    'trace_id': trace_id,
                    'user_identifier': user_identifier,
                    'internal_user_id': internal_user_id,
                    'username': user_result.username if user_result else None,
                    'email': user_result.email if user_result else None,
                    'account_type': user_result.account_type if user_result else None,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                conn.execute(text(mapping_query), mapping_data)
                conn.commit()
                
        except Exception as e:
            self.error_logger.log_error(f"Failed to store investigation mapping: {str(e)}")
    
    def _log_to_audit_trail(self, event_record: Dict[str, Any]) -> None:
        """Log event to security audit trail"""
        try:
            audit_query = """
                INSERT INTO security_audit_trail 
                (trace_id, event_type, severity, timestamp, logged_at)
                VALUES (:trace_id, :event_type, :severity, :timestamp, :logged_at)
            """
            
            audit_data = {
                'trace_id': event_record['trace_id'],
                'event_type': event_record['event_type'],
                'severity': event_record['severity'],
                'timestamp': event_record['timestamp'],
                'logged_at': datetime.utcnow().isoformat()
            }
            
            with self.trace_db.connect() as conn:
                conn.execute(text(audit_query), audit_data)
                conn.commit()
                
        except Exception as e:
            self.error_logger.log_error(f"Failed to log audit trail: {str(e)}")
    
    def _verify_timeline_access(self) -> bool:
        """Verify authorization for user timeline access"""
        # Check if user has security analyst or admin role
        if hasattr(g, 'user') and g.user:
            return g.user.role in ['admin', 'security_analyst', 'compliance_officer', 'super_admin']
        return False
    
    def _verify_investigation_access(self) -> bool:
        """Verify authorization for investigation access"""
        # Check if user has investigation privileges
        if hasattr(g, 'user') and g.user:
            return g.user.role in ['admin', 'security_analyst', 'super_admin']
        return False
    
    def _get_related_events(self, trace_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get related security events for investigation"""
        try:
            if not user_id:
                return []
            
            # Get events from same user within 24 hours
            query = """
                SELECT trace_id, event_type, severity, timestamp
                FROM security_events 
                WHERE user_id = :user_id 
                AND timestamp >= DATE_SUB(
                    (SELECT timestamp FROM security_events WHERE trace_id = :trace_id), 
                    INTERVAL 24 HOUR
                )
                AND trace_id != :trace_id
                ORDER BY timestamp DESC
                LIMIT 50
            """
            
            with self.trace_db.connect() as conn:
                result = conn.execute(text(query), {'trace_id': trace_id, 'user_id': user_id})
                return [dict(row._mapping) for row in result]
                
        except Exception:
            return []
    
    def _log_investigation_access(self, trace_id: str, investigator_id: str) -> None:
        """Log access to investigation data for audit"""
        try:
            query = """
                INSERT INTO investigation_access_log 
                (trace_id, investigator_id, access_timestamp, access_type)
                VALUES (:trace_id, :investigator_id, :access_timestamp, 'investigation')
            """
            
            with self.trace_db.connect() as conn:
                conn.execute(text(query), {
                    'trace_id': trace_id,
                    'investigator_id': investigator_id,
                    'access_timestamp': datetime.utcnow().isoformat()
                })
                conn.commit()
                
        except Exception as e:
            self.error_logger.log_error(f"Failed to log investigation access: {str(e)}")
    
    def _calculate_risk_scores(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk scores based on event patterns"""
        risk_analysis = {
            'overall_risk': 'low',
            'risk_factors': [],
            'recommendations': []
        }
        
        # Analyze frequency patterns
        if patterns.get('frequency'):
            critical_events = sum(1 for event in patterns['frequency'] 
                                if event['severity'] == 'critical')
            if critical_events > 5:
                risk_analysis['risk_factors'].append('High critical event frequency')
                risk_analysis['overall_risk'] = 'high'
        
        # Analyze IP patterns
        if patterns.get('suspicious_ips'):
            if len(patterns['suspicious_ips']) > 3:
                risk_analysis['risk_factors'].append('Multiple suspicious IP addresses')
                if risk_analysis['overall_risk'] == 'low':
                    risk_analysis['overall_risk'] = 'medium'
        
        # Add recommendations
        if risk_analysis['risk_factors']:
            risk_analysis['recommendations'] = [
                'Increase monitoring frequency',
                'Review user access patterns',
                'Consider additional authentication factors'
            ]
        
        return risk_analysis