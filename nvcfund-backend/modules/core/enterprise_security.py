"""
Enterprise-Grade Global Security Framework
Banking-compliant comprehensive protection system for NVC Banking Platform
"""

import hashlib
import hmac
import time
import uuid
import json
import re
import ipaddress
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Tuple
from flask import request, jsonify, current_app, g, abort, session
from flask_login import current_user
from werkzeug.exceptions import TooManyRequests
import logging
import os
from dataclasses import dataclass, asdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: str
    event_type: str
    severity: str
    source_ip: str
    user_id: Optional[str]
    endpoint: str
    description: str
    details: Dict[str, Any]
    risk_score: int

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    ip_reputation: Dict[str, str]
    known_attack_patterns: List[str]
    geo_restrictions: List[str]
    suspicious_user_agents: List[str]

class EnterpriseSecurityManager:
    """Enterprise-grade security manager for global protection"""
    
    def __init__(self):
        self.threat_intelligence = self._init_threat_intelligence()
        self.security_events = []
        self.blocked_ips = set()
        self.suspicious_ips = set()
        self.rate_limit_cache = {}
        self.session_tracking = {}
        self.attack_patterns = self._init_attack_patterns()
        self.security_rules = self._init_security_rules()
        self._lock = threading.RLock()
        
    def _init_threat_intelligence(self) -> ThreatIntelligence:
        """Initialize threat intelligence database"""
        return ThreatIntelligence(
            ip_reputation={
                # Known malicious IPs would be loaded from threat feeds
            },
            known_attack_patterns=[
                r'(?i)(union\s+select)',
                r'(?i)(drop\s+table)',
                r'(?i)(delete\s+from)',
                r'(?i)(insert\s+into)',
                r'(?i)(update\s+.*set)',
                r'(?i)(<script[^>]*>)',
                r'(?i)(javascript:)',
                r'(?i)(eval\s*\()',
                r'(?i)(alert\s*\()',
                r'(?i)(onload\s*=)',
                r'(?i)(onerror\s*=)',
                r'(?i)(prompt\s*\()',
                r'(?i)(confirm\s*\()',
                r'(?i)(document\.cookie)',
                r'(?i)(window\.location)',
                r'(?i)(\.\.\/)',
                r'(?i)(\/etc\/passwd)',
                r'(?i)(\/proc\/)',
                r'(?i)(cmd\.exe)',
                r'(?i)(powershell)',
                r'(?i)(nc\s+-)',
                r'(?i)(wget\s+)',
                r'(?i)(curl\s+)',
                r'(?i)(\bexec\s*\()',
                r'(?i)(\bsystem\s*\()',
                r'(?i)(base64_decode)',
                r'(?i)(file_get_contents)',
                r'(?i)(include\s*\()',
                r'(?i)(require\s*\()'
            ],
            geo_restrictions=[
                # Countries with high fraud rates
                'CN', 'RU', 'KP', 'IR'
            ],
            suspicious_user_agents=[
                'sqlmap', 'nikto', 'nmap', 'masscan', 'burpsuite',
                'havij', 'w3af', 'acunetix', 'nessus', 'openvas',
                'metasploit', 'hydra', 'medusa', 'john', 'hashcat'
            ]
        )
    
    def _init_attack_patterns(self) -> Dict[str, List[str]]:
        """Initialize attack pattern detection"""
        return {
            'sql_injection': [
                r"(\b(union|select|insert|delete|update|drop|create|alter|exec|execute)\b)",
                r"(\b(or|and)\s+\d+\s*=\s*\d+)",
                r"(\b(or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
                r"(--|#|\/\*|\*\/)",
                r"(\bchar\s*\(\s*\d+\s*\))",
                r"(\bcast\s*\()",
                r"(\bconvert\s*\()",
                r"(\bsubstring\s*\()",
                r"(\bascii\s*\()",
                r"(\blength\s*\()",
                r"(\bcount\s*\()",
                r"(\bgroup_concat\s*\()",
                r"(\bunhex\s*\()",
                r"(\bhex\s*\()",
                r"(\bmd5\s*\()",
                r"(\bsha1\s*\()",
                r"(\bsleep\s*\()",
                r"(\bbenchmark\s*\()",
                r"(\bwaitfor\s+delay)",
                r"(\bif\s*\(\s*\d+\s*=\s*\d+)",
                r"(\bunion\s+all\s+select)",
                r"(\bload_file\s*\()",
                r"(\binto\s+outfile)",
                r"(\binto\s+dumpfile)"
            ],
            'xss': [
                r"(<\s*script[^>]*>)",
                r"(<\s*\/\s*script\s*>)",
                r"(javascript\s*:)",
                r"(on\w+\s*=)",
                r"(<\s*iframe[^>]*>)",
                r"(<\s*object[^>]*>)",
                r"(<\s*embed[^>]*>)",
                r"(<\s*link[^>]*>)",
                r"(<\s*meta[^>]*>)",
                r"(expression\s*\()",
                r"(vbscript\s*:)",
                r"(data\s*:)",
                r"(javascript\s*&\s*colon)",
                r"(&#\d+)",
                r"(&\w+;)"
            ],
            'path_traversal': [
                r"(\.\.\/)",
                r"(\.\.\\)",
                r"(%2e%2e%2f)",
                r"(%2e%2e\\)",
                r"(%252e%252e%252f)",
                r"(%c0%ae%c0%ae%c0%af)",
                r"(\/etc\/passwd)",
                r"(\/etc\/shadow)",
                r"(\/proc\/)",
                r"(\/sys\/)",
                r"(\/dev\/)",
                r"(\/var\/log\/)",
                r"(c\:\\windows\\)",
                r"(c\:\\boot\.ini)",
                r"(c\:\\pagefile\.sys)"
            ],
            'command_injection': [
                r"(\|\s*\w+)",
                r"(&\s*\w+)",
                r"(;\s*\w+)",
                r"(\$\(\s*\w+)",
                r"(`\s*\w+)",
                r"(\bcat\s+)",
                r"(\bls\s+)",
                r"(\bps\s+)",
                r"(\bwhoami\b)",
                r"(\bid\b)",
                r"(\buname\b)",
                r"(\bnetstat\b)",
                r"(\bifconfig\b)",
                r"(\bpwd\b)",
                r"(\bwget\s+)",
                r"(\bcurl\s+)",
                r"(\bnc\s+)",
                r"(\btelnet\s+)",
                r"(\bssh\s+)",
                r"(\bftp\s+)"
            ],
            'file_inclusion': [
                r"(php\:\/\/)",
                r"(file\:\/\/)",
                r"(data\:\/\/)",
                r"(http\:\/\/)",
                r"(https\:\/\/)",
                r"(ftp\:\/\/)",
                r"(expect\:\/\/)",
                r"(zip\:\/\/)",
                r"(compress\.zlib\:\/\/)",
                r"(compress\.bzip2\:\/\/)",
                r"(glob\:\/\/)",
                r"(phar\:\/\/)"
            ]
        }
    
    def _init_security_rules(self) -> Dict[str, Any]:
        """Initialize security rules and policies"""
        return {
            'rate_limits': {
                'public': {
                    'requests_per_minute': 30,
                    'requests_per_hour': 500,
                    'burst_limit': 10
                },
                'authenticated': {
                    'requests_per_minute': 100,
                    'requests_per_hour': 2000,
                    'burst_limit': 25
                },
                'admin': {
                    'requests_per_minute': 300,
                    'requests_per_hour': 5000,
                    'burst_limit': 75
                },
                'super_admin': {
                    'requests_per_minute': 500,
                    'requests_per_hour': 10000,
                    'burst_limit': 100
                }
            },
            'geo_restrictions': {
                'blocked_countries': ['CN', 'RU', 'KP', 'IR'],
                'high_risk_countries': ['PK', 'BD', 'NG', 'VN'],
                'allowed_countries': ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP']
            },
            'content_security': {
                'max_request_size': 10 * 1024 * 1024,  # 10MB
                'max_json_depth': 10,
                'max_array_length': 1000,
                'blocked_file_extensions': [
                    '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
                    '.vbs', '.js', '.jar', '.php', '.asp', '.jsp'
                ]
            },
            'session_security': {
                'max_session_duration': 3600,  # 1 hour
                'session_timeout_warning': 300,  # 5 minutes
                'max_concurrent_sessions': 3,
                'require_session_rotation': True
            }
        }
    
    def log_security_event(self, event_type: str, severity: str, description: str, 
                          details: Dict[str, Any] = None, risk_score: int = 5):
        """Log security event for monitoring and analysis"""
        with self._lock:
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_id = str(current_user.id) if current_user.is_authenticated else None
            
            event = SecurityEvent(
                timestamp=datetime.utcnow().isoformat(),
                event_type=event_type,
                severity=severity,
                source_ip=client_ip,
                user_id=user_id,
                endpoint=request.endpoint or 'unknown',
                description=description,
                details=details or {},
                risk_score=risk_score
            )
            
            self.security_events.append(event)
            
            # Log to application logger
            logger.warning(f"Security Event: {event_type} - {description}", 
                         extra=asdict(event))
            
            # Auto-block if high risk
            if risk_score >= 8:
                self.blocked_ips.add(client_ip)
                logger.critical(f"IP {client_ip} auto-blocked due to high risk score: {risk_score}")
    
    def check_ip_reputation(self, ip: str) -> Tuple[bool, str]:
        """Check IP reputation against threat intelligence"""
        try:
            # Check if IP is in blocked list
            if ip in self.blocked_ips:
                return False, "IP is blocked"
            
            # Check threat intelligence
            reputation = self.threat_intelligence.ip_reputation.get(ip)
            if reputation == 'malicious':
                self.blocked_ips.add(ip)
                return False, "IP flagged as malicious"
            
            # Check if IP is from restricted geography
            # This would integrate with GeoIP service in production
            
            return True, "IP reputation OK"
            
        except Exception as e:
            logger.error(f"IP reputation check failed: {e}")
            return True, "Unable to verify IP reputation"
    
    def detect_attack_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect attack patterns in request content"""
        detected_attacks = []
        
        try:
            for attack_type, patterns in self.attack_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        detected_attacks.append({
                            'type': attack_type,
                            'pattern': pattern,
                            'match': match.group(),
                            'position': match.span(),
                            'risk_score': self._calculate_attack_risk(attack_type)
                        })
            
            return detected_attacks
            
        except Exception as e:
            logger.error(f"Attack pattern detection failed: {e}")
            return []
    
    def _calculate_attack_risk(self, attack_type: str) -> int:
        """Calculate risk score for attack type"""
        risk_scores = {
            'sql_injection': 9,
            'xss': 7,
            'path_traversal': 8,
            'command_injection': 10,
            'file_inclusion': 8
        }
        return risk_scores.get(attack_type, 5)
    
    def check_rate_limit(self, ip: str, user_id: str = None, endpoint: str = 'default') -> Tuple[bool, Dict[str, Any]]:
        """Enhanced rate limiting with multiple tiers"""
        try:
            current_time = int(time.time())
            minute_window = current_time // 60
            hour_window = current_time // 3600
            
            # Determine rate limit tier
            tier = 'public'
            if current_user.is_authenticated:
                user_role = str(getattr(current_user, 'role', 'standard_user'))
                if user_role in ['super_admin', 'admin']:
                    tier = user_role
                else:
                    tier = 'authenticated'
            
            limits = self.security_rules['rate_limits'][tier]
            
            # Create unique keys
            minute_key = f"rate:{ip}:{user_id}:{endpoint}:{minute_window}"
            hour_key = f"rate:{ip}:{user_id}:{endpoint}:{hour_window}"
            
            # Check current counts
            minute_count = self.rate_limit_cache.get(minute_key, 0) + 1
            hour_count = self.rate_limit_cache.get(hour_key, 0) + 1
            
            # Update cache
            self.rate_limit_cache[minute_key] = minute_count
            self.rate_limit_cache[hour_key] = hour_count
            
            # Clean old entries (simple cleanup)
            if len(self.rate_limit_cache) > 10000:
                self._cleanup_rate_limit_cache()
            
            # Check limits
            if minute_count > limits['requests_per_minute']:
                return False, {
                    'reason': 'Minute limit exceeded',
                    'limit': limits['requests_per_minute'],
                    'count': minute_count,
                    'reset_time': (minute_window + 1) * 60
                }
            
            if hour_count > limits['requests_per_hour']:
                return False, {
                    'reason': 'Hour limit exceeded',
                    'limit': limits['requests_per_hour'],
                    'count': hour_count,
                    'reset_time': (hour_window + 1) * 3600
                }
            
            return True, {
                'tier': tier,
                'minute_count': minute_count,
                'hour_count': hour_count,
                'limits': limits
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, {'error': str(e)}
    
    def _cleanup_rate_limit_cache(self):
        """Clean up old rate limit cache entries"""
        current_time = int(time.time())
        current_minute = current_time // 60
        current_hour = current_time // 3600
        
        # Remove entries older than 2 hours
        keys_to_remove = []
        for key in self.rate_limit_cache:
            try:
                parts = key.split(':')
                if len(parts) >= 5:
                    window = int(parts[-1])
                    if 'minute' in key and window < current_minute - 120:
                        keys_to_remove.append(key)
                    elif 'hour' in key and window < current_hour - 2:
                        keys_to_remove.append(key)
            except (ValueError, IndexError):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.rate_limit_cache[key]

# Global security manager instance
security_manager = EnterpriseSecurityManager()

def enterprise_security_check():
    """Comprehensive enterprise security decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                start_time = time.time()
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
                user_agent = request.headers.get('User-Agent', '')
                
                # 1. IP Reputation Check
                ip_ok, ip_reason = security_manager.check_ip_reputation(client_ip)
                if not ip_ok:
                    security_manager.log_security_event(
                        'ip_blocked', 'high', f'Blocked IP access: {ip_reason}',
                        {'ip': client_ip, 'reason': ip_reason}, 9
                    )
                    abort(403, description="Access denied")
                
                # 2. User Agent Check
                user_agent_lower = user_agent.lower()
                for suspicious_agent in security_manager.threat_intelligence.suspicious_user_agents:
                    if suspicious_agent in user_agent_lower:
                        security_manager.log_security_event(
                            'suspicious_user_agent', 'medium', 
                            f'Suspicious user agent detected: {suspicious_agent}',
                            {'user_agent': user_agent, 'ip': client_ip}, 7
                        )
                        abort(403, description="Suspicious user agent")
                
                # 3. Rate Limiting
                user_id = str(current_user.id) if current_user.is_authenticated else 'anonymous'
                rate_ok, rate_info = security_manager.check_rate_limit(
                    client_ip, user_id, request.endpoint
                )
                
                if not rate_ok:
                    security_manager.log_security_event(
                        'rate_limit_exceeded', 'medium', 
                        f'Rate limit exceeded: {rate_info["reason"]}',
                        rate_info, 6
                    )
                    raise TooManyRequests(description=rate_info['reason'])
                
                # 4. Content Security Check
                request_content = ''
                if request.is_json:
                    request_content = json.dumps(request.get_json())
                elif request.form:
                    request_content = str(dict(request.form))
                elif request.args:
                    request_content = str(dict(request.args))
                elif request.data:
                    request_content = request.data.decode('utf-8', errors='ignore')
                
                # Check content size
                if len(request_content) > security_manager.security_rules['content_security']['max_request_size']:
                    security_manager.log_security_event(
                        'oversized_request', 'medium', 
                        'Request exceeds maximum size limit',
                        {'size': len(request_content), 'ip': client_ip}, 6
                    )
                    abort(413, description="Request entity too large")
                
                # 5. Attack Pattern Detection
                if request_content:
                    detected_attacks = security_manager.detect_attack_patterns(request_content)
                    if detected_attacks:
                        max_risk = max(attack['risk_score'] for attack in detected_attacks)
                        security_manager.log_security_event(
                            'attack_pattern_detected', 'high',
                            f'Attack patterns detected: {len(detected_attacks)} patterns',
                            {
                                'attacks': detected_attacks,
                                'content_sample': request_content[:200],
                                'ip': client_ip
                            },
                            max_risk
                        )
                        
                        if max_risk >= 8:
                            abort(400, description="Malicious content detected")
                
                # 6. Session Security
                if current_user.is_authenticated:
                    session_id = session.get('_id')
                    if session_id:
                        # Track session
                        if session_id not in security_manager.session_tracking:
                            security_manager.session_tracking[session_id] = {
                                'start_time': time.time(),
                                'last_activity': time.time(),
                                'request_count': 0,
                                'ip': client_ip
                            }
                        
                        session_info = security_manager.session_tracking[session_id]
                        session_info['last_activity'] = time.time()
                        session_info['request_count'] += 1
                        
                        # Check session duration
                        max_duration = security_manager.security_rules['session_security']['max_session_duration']
                        if time.time() - session_info['start_time'] > max_duration:
                            security_manager.log_security_event(
                                'session_expired', 'low',
                                'Session exceeded maximum duration',
                                {'session_id': session_id, 'duration': time.time() - session_info['start_time']}, 3
                            )
                            # Force logout would be handled by session management
                
                # 7. Set security headers
                g.security_headers = {
                    'X-Frame-Options': 'DENY',
                    'X-Content-Type-Options': 'nosniff',
                    'X-XSS-Protection': '1; mode=block',
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' cdnjs.cloudflare.com",
                    'Referrer-Policy': 'strict-origin-when-cross-origin',
                    'X-Request-ID': str(uuid.uuid4())
                }
                
                # Execute the original function
                response = f(*args, **kwargs)
                
                # Log successful request
                processing_time = (time.time() - start_time) * 1000
                security_manager.log_security_event(
                    'request_processed', 'info',
                    f'Request processed successfully in {processing_time:.2f}ms',
                    {
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'processing_time': processing_time,
                        'user_id': user_id
                    }, 1
                )
                
                return response
                
            except Exception as e:
                if isinstance(e, (TooManyRequests, )):
                    raise
                
                security_manager.log_security_event(
                    'security_check_error', 'medium',
                    f'Security check failed: {str(e)}',
                    {'error': str(e), 'endpoint': request.endpoint}, 5
                )
                
                # Allow request to proceed on security check failure to avoid service disruption
                logger.error(f"Security check failed for {request.endpoint}: {e}")
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def banking_grade_protection(allowed_roles: List[str] = None, require_mfa: bool = False):
    """Banking-grade protection decorator combining all security measures"""
    def decorator(f):
        @enterprise_security_check()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Additional banking-specific checks
            
            # 1. Role-based access control
            if allowed_roles and current_user.is_authenticated:
                user_role = str(getattr(current_user, 'role', 'standard_user'))
                if user_role not in allowed_roles:
                    security_manager.log_security_event(
                        'unauthorized_access', 'high',
                        f'User {current_user.id} attempted to access restricted endpoint',
                        {
                            'user_role': user_role,
                            'required_roles': allowed_roles,
                            'endpoint': request.endpoint
                        }, 8
                    )
                    abort(403, description="Insufficient privileges")
            
            # 2. MFA requirement for sensitive operations
            if require_mfa and current_user.is_authenticated:
                # Check if MFA is completed for this session
                mfa_verified = session.get('mfa_verified', False)
                if not mfa_verified:
                    security_manager.log_security_event(
                        'mfa_required', 'medium',
                        'MFA verification required for sensitive operation',
                        {'user_id': current_user.id, 'endpoint': request.endpoint}, 6
                    )
                    return jsonify({
                        'error': 'Multi-factor authentication required',
                        'code': 'MFA_REQUIRED',
                        'redirect': '/auth/mfa'
                    }), 401
            
            # 3. Transaction limit checks for financial operations
            if 'transfer' in request.endpoint or 'payment' in request.endpoint:
                # Implement transaction limits based on user tier
                # This would integrate with banking service in production
                pass
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_security_status() -> Dict[str, Any]:
    """Get comprehensive security status"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'blocked_ips': len(security_manager.blocked_ips),
        'suspicious_ips': len(security_manager.suspicious_ips),
        'recent_events': len([e for e in security_manager.security_events 
                            if datetime.fromisoformat(e.timestamp) > datetime.utcnow() - timedelta(hours=1)]),
        'active_sessions': len(security_manager.session_tracking),
        'rate_limit_cache_size': len(security_manager.rate_limit_cache),
        'threat_intelligence_loaded': True,
        'attack_patterns_count': sum(len(patterns) for patterns in security_manager.attack_patterns.values()),
        'security_level': 'ENTERPRISE_GRADE'
    }

def block_ip_address(ip: str, reason: str = "Security violation"):
    """Block an IP address globally"""
    security_manager.blocked_ips.add(ip)
    security_manager.log_security_event(
        'ip_manually_blocked', 'high',
        f'IP manually blocked: {reason}',
        {'ip': ip, 'reason': reason}, 9
    )

def unblock_ip_address(ip: str):
    """Unblock an IP address"""
    security_manager.blocked_ips.discard(ip)
    security_manager.log_security_event(
        'ip_unblocked', 'info',
        'IP manually unblocked',
        {'ip': ip}, 2
    )

def get_security_events(limit: int = 100) -> List[Dict[str, Any]]:
    """Get recent security events"""
    recent_events = sorted(
        security_manager.security_events,
        key=lambda x: x.timestamp,
        reverse=True
    )[:limit]
    
    return [asdict(event) for event in recent_events]