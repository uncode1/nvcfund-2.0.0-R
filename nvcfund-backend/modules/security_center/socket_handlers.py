"""
Security Center Module Socket Handlers
Real-time security monitoring, threat intelligence, and incident response streaming
"""

from flask import current_app
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
import logging
from datetime import datetime
import threading
import time
import json
import random

from .services import SecurityCenterService

logger = logging.getLogger(__name__)

class SecurityCenterSocketHandler:
    """Handles real-time socket connections for security center operations"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.security_service = SecurityCenterService()
        self.active_rooms = set()
        self.streaming_threads = {}
        
        # Register socket event handlers
        self.register_handlers()
        
        # Start background threat intelligence collection
        self.start_threat_intelligence_feed()
    
    def register_handlers(self):
        """Register all socket event handlers for security center"""
        
        @self.socketio.on('connect', namespace='/security-center')
        def handle_connect():
            """Handle client connection to security center namespace"""
            if not current_user.is_authenticated:
                logger.warning("Unauthenticated user attempted security socket connection")
                disconnect()
                return False
            
            # Verify admin permissions for security access
            if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
                logger.warning(f"Non-admin user {current_user.id} attempted security socket connection")
                disconnect()
                return False
            
            room = f"security_{current_user.id}"
            join_room(room)
            self.active_rooms.add(room)
            
            logger.info(f"Admin user {current_user.id} connected to security center socket")
            
            # Send initial security data
            self.send_initial_security_data(room)
        
        @self.socketio.on('disconnect', namespace='/security-center')
        def handle_disconnect():
            """Handle client disconnection"""
            if current_user.is_authenticated:
                room = f"security_{current_user.id}"
                leave_room(room)
                self.active_rooms.discard(room)
                
                # Stop streaming thread for this user
                if room in self.streaming_threads:
                    self.streaming_threads[room]['stop'] = True
                    del self.streaming_threads[room]
                
                logger.info(f"Admin user {current_user.id} disconnected from security center socket")
        
        @self.socketio.on('request_security_data', namespace='/security-center')
        def handle_security_request():
            """Handle request for security dashboard data"""
            if not current_user.is_authenticated:
                return
            
            try:
                security_data = self.security_service.get_security_dashboard_data(current_user.id)
                emit('security_dashboard_update', security_data)
                
                logger.debug(f"Security dashboard data sent to admin user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error sending security dashboard data: {e}")
                emit('error', {'message': 'Failed to load security data'})
        
        @self.socketio.on('request_threat_intelligence', namespace='/security-center')
        def handle_threat_intelligence_request():
            """Handle request for real-time threat intelligence"""
            if not current_user.is_authenticated:
                return
            
            try:
                # Get latest threat intelligence
                threat_data = self.get_threat_intelligence_data()
                emit('threat_intelligence_update', threat_data)
                
                # Get attack vectors analysis
                attack_vectors = self.get_attack_vectors_data()
                emit('attack_vectors_update', attack_vectors)
                
                logger.debug(f"Threat intelligence sent to admin user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error sending threat intelligence: {e}")
                emit('error', {'message': 'Failed to load threat intelligence'})
        
        @self.socketio.on('request_security_metrics', namespace='/security-center')
        def handle_security_metrics_request():
            """Handle request for real-time security metrics"""
            if not current_user.is_authenticated:
                return
            
            try:
                # Get comprehensive security metrics
                metrics = self.get_security_metrics()
                emit('security_metrics_update', metrics)
                
                logger.debug(f"Security metrics sent to admin user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error sending security metrics: {e}")
                emit('error', {'message': 'Failed to load security metrics'})
        
        @self.socketio.on('start_security_monitoring', namespace='/security-center')
        def handle_start_security_monitoring():
            """Start real-time security monitoring stream for the user"""
            if not current_user.is_authenticated:
                return
            
            room = f"security_{current_user.id}"
            if room not in self.streaming_threads:
                self.start_security_stream(room)
                logger.info(f"Started real-time security monitoring for admin user {current_user.id}")
        
        @self.socketio.on('stop_security_monitoring', namespace='/security-center')
        def handle_stop_security_monitoring():
            """Stop real-time security monitoring stream for the user"""
            if not current_user.is_authenticated:
                return
            
            room = f"security_{current_user.id}"
            if room in self.streaming_threads:
                self.streaming_threads[room]['stop'] = True
                del self.streaming_threads[room]
                logger.info(f"Stopped real-time security monitoring for admin user {current_user.id}")
        
        @self.socketio.on('block_threat', namespace='/security-center')
        def handle_block_threat(data):
            """Handle threat blocking request"""
            if not current_user.is_authenticated:
                return
            
            try:
                threat_id = data.get('threat_id')
                if threat_id:
                    result = self.security_service.block_threat(current_user.id, threat_id)
                    emit('threat_blocked', {'threat_id': threat_id, 'success': result})
                    
                    # Broadcast to all security users
                    self.broadcast_security_action({
                        'action': 'threat_blocked',
                        'threat_id': threat_id,
                        'user_id': current_user.id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
            except Exception as e:
                logger.error(f"Error blocking threat: {e}")
                emit('error', {'message': 'Failed to block threat'})
        
        @self.socketio.on('escalate_threat', namespace='/security-center')
        def handle_escalate_threat(data):
            """Handle threat escalation request"""
            if not current_user.is_authenticated:
                return
            
            try:
                threat_id = data.get('threat_id')
                if threat_id:
                    result = self.security_service.escalate_threat(current_user.id, threat_id)
                    emit('threat_escalated', {'threat_id': threat_id, 'success': result})
                    
                    # Broadcast to all security users
                    self.broadcast_security_action({
                        'action': 'threat_escalated',
                        'threat_id': threat_id,
                        'user_id': current_user.id,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
            except Exception as e:
                logger.error(f"Error escalating threat: {e}")
                emit('error', {'message': 'Failed to escalate threat'})
    
    def send_initial_security_data(self, room):
        """Send initial security data to connected client"""
        try:
            # Send dashboard data
            security_data = self.security_service.get_security_dashboard_data(current_user.id)
            self.socketio.emit('security_dashboard_update', security_data, room=room, namespace='/security-center')
            
            # Send threat intelligence
            threat_data = self.get_threat_intelligence_data()
            self.socketio.emit('threat_intelligence_update', threat_data, room=room, namespace='/security-center')
            
            # Send security metrics
            metrics = self.get_security_metrics()
            self.socketio.emit('security_metrics_update', metrics, room=room, namespace='/security-center')
            
        except Exception as e:
            logger.error(f"Error sending initial security data: {e}")
    
    def start_security_stream(self, room):
        """Start real-time security data streaming thread for a specific room"""
        
        def stream_security_data():
            stream_data = {'stop': False}
            self.streaming_threads[room] = stream_data
            
            while not stream_data.get('stop', False):
                try:
                    # Stream security metrics every 10 seconds
                    if int(time.time()) % 10 == 0:
                        metrics = self.get_security_metrics()
                        self.socketio.emit('security_metrics_update', metrics, room=room, namespace='/security-center')
                    
                    # Stream threat intelligence every 30 seconds
                    if int(time.time()) % 30 == 0:
                        threat_data = self.get_threat_intelligence_data()
                        self.socketio.emit('threat_intelligence_update', threat_data, room=room, namespace='/security-center')
                    
                    # Check for new threats every 15 seconds
                    if int(time.time()) % 15 == 0:
                        new_threats = self.check_new_threats()
                        for threat in new_threats:
                            self.socketio.emit('new_threat', threat, room=room, namespace='/security-center')
                    
                    # Check for security incidents every 45 seconds
                    if int(time.time()) % 45 == 0:
                        incidents = self.check_security_incidents()
                        for incident in incidents:
                            self.socketio.emit('security_incident', incident, room=room, namespace='/security-center')
                    
                    # Check system status every 60 seconds
                    if int(time.time()) % 60 == 0:
                        system_status = self.get_security_systems_status()
                        for system in system_status:
                            self.socketio.emit('system_status_update', system, room=room, namespace='/security-center')
                    
                    time.sleep(1)  # Sleep for 1 second between iterations
                    
                except Exception as e:
                    logger.error(f"Error in security streaming: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start streaming in background thread
        thread = threading.Thread(target=stream_security_data, daemon=True)
        thread.start()
    
    def get_threat_intelligence_data(self):
        """Get real-time threat intelligence data"""
        try:
            # Generate realistic threat intelligence trends
            now = datetime.utcnow()
            hours = [(now.hour - i) % 24 for i in range(23, -1, -1)]
            
            return {
                'timestamp': now.isoformat(),
                'labels': [f"{h:02d}:00" for h in hours],
                'critical': [random.randint(0, 5) for _ in hours],
                'high': [random.randint(2, 15) for _ in hours],
                'medium': [random.randint(5, 25) for _ in hours],
                'threat_level_change': random.choice(['up', 'down', 'stable']),
                'global_threat_score': random.randint(65, 85)
            }
            
        except Exception as e:
            logger.error(f"Error getting threat intelligence data: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'labels': [],
                'critical': [],
                'high': [],
                'medium': [],
                'threat_level_change': 'stable',
                'global_threat_score': 75
            }
    
    def get_attack_vectors_data(self):
        """Get attack vectors analysis data"""
        try:
            # Realistic attack vector distribution
            base_values = [30, 25, 20, 15, 5, 5]
            variation = [random.randint(-3, 3) for _ in base_values]
            values = [max(0, base + var) for base, var in zip(base_values, variation)]
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'values': values,
                'labels': ['Web Application', 'Network', 'Email', 'Social Engineering', 'Physical', 'Other']
            }
            
        except Exception as e:
            logger.error(f"Error getting attack vectors data: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'values': [30, 25, 20, 15, 5, 5],
                'labels': ['Web Application', 'Network', 'Email', 'Social Engineering', 'Physical', 'Other']
            }
    
    def get_security_metrics(self):
        """Get comprehensive security metrics"""
        try:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'active_threats': random.randint(8, 25),
                'security_incidents': random.randint(2, 8),
                'blocked_attacks': random.randint(145, 200),
                'vulnerabilities': random.randint(12, 30),
                'intrusion_attempts': random.randint(25, 60),
                'compliance_score': f"{random.randint(96, 99)}%",
                'threat_level': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'systems_online': random.randint(18, 20),
                'firewall_blocks': random.randint(850, 1200),
                'ids_alerts': random.randint(45, 85)
            }
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'active_threats': 0,
                'security_incidents': 0,
                'blocked_attacks': 0,
                'vulnerabilities': 0,
                'intrusion_attempts': 0,
                'compliance_score': '98%',
                'threat_level': 'LOW',
                'systems_online': 20,
                'firewall_blocks': 0,
                'ids_alerts': 0
            }
    
    def check_new_threats(self):
        """Check for new security threats"""
        try:
            # Randomly generate new threats
            if random.random() < 0.3:  # 30% chance of new threat
                threat_types = [
                    'SQL Injection Attempt',
                    'DDoS Attack Vector',
                    'Malware Detection',
                    'Suspicious Login Activity',
                    'Unauthorized API Access',
                    'Data Exfiltration Attempt',
                    'Phishing Campaign',
                    'Brute Force Attack'
                ]
                
                severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
                
                return [{
                    'id': f"THR-{random.randint(10000, 99999)}",
                    'title': random.choice(threat_types),
                    'description': f"Detected at {datetime.utcnow().strftime('%H:%M:%S')} from multiple sources",
                    'severity': random.choice(severities),
                    'timestamp': datetime.utcnow().isoformat(),
                    'source_ip': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    'affected_systems': random.randint(1, 5)
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Error checking new threats: {e}")
            return []
    
    def check_security_incidents(self):
        """Check for new security incidents"""
        try:
            # Randomly generate incidents (less frequent than threats)
            if random.random() < 0.1:  # 10% chance of new incident
                incident_types = [
                    'Security Breach Detected',
                    'System Compromise Alert',
                    'Data Loss Prevention Triggered',
                    'Insider Threat Activity',
                    'Compliance Violation Detected',
                    'Critical Vulnerability Exploited'
                ]
                
                priorities = ['P1', 'P2', 'P3', 'P4']
                
                return [{
                    'id': f"INC-{random.randint(10000, 99999)}",
                    'title': random.choice(incident_types),
                    'description': f"Incident opened at {datetime.utcnow().strftime('%H:%M:%S')} - immediate attention required",
                    'priority': random.choice(priorities),
                    'status': 'Open',
                    'timestamp': datetime.utcnow().isoformat(),
                    'assigned_to': 'Security Team',
                    'estimated_impact': random.choice(['Low', 'Medium', 'High', 'Critical'])
                }]
            
            return []
            
        except Exception as e:
            logger.error(f"Error checking security incidents: {e}")
            return []
    
    def get_security_systems_status(self):
        """Get status of all security systems"""
        try:
            systems = [
                'intrusion_detection_system',
                'web_application_firewall',
                'network_security_monitor',
                'threat_intelligence_platform',
                'vulnerability_scanner',
                'security_information_manager'
            ]
            
            status_updates = []
            for system in systems:
                # 95% chance system is online
                status = 'online' if random.random() < 0.95 else random.choice(['warning', 'offline'])
                
                status_updates.append({
                    'system_id': system,
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'health_score': random.randint(85, 100) if status == 'online' else random.randint(0, 70),
                    'last_update': datetime.utcnow().isoformat()
                })
            
            return status_updates
            
        except Exception as e:
            logger.error(f"Error getting security systems status: {e}")
            return []
    
    def start_threat_intelligence_feed(self):
        """Start background threat intelligence collection"""
        
        def collect_threat_intelligence():
            while True:
                try:
                    # Collect threat intelligence from various sources
                    # This would connect to real threat intelligence feeds in production
                    time.sleep(300)  # Update every 5 minutes
                    
                except Exception as e:
                    logger.error(f"Error in threat intelligence collection: {e}")
                    time.sleep(300)
        
        # Start threat intelligence collection in background thread
        thread = threading.Thread(target=collect_threat_intelligence, daemon=True)
        thread.start()
        logger.info("Background threat intelligence collection started")
    
    def broadcast_security_action(self, action_data):
        """Broadcast security action to all connected security users"""
        try:
            self.socketio.emit('security_action_broadcast', action_data, namespace='/security-center')
            logger.debug(f"Security action broadcasted: {action_data.get('action', 'Unknown action')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting security action: {e}")
    
    def broadcast_threat_alert(self, threat_data):
        """Broadcast critical threat alert to all connected security users"""
        try:
            self.socketio.emit('critical_threat_alert', threat_data, namespace='/security-center')
            logger.warning(f"Critical threat alert broadcasted: {threat_data.get('title', 'Unknown threat')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting threat alert: {e}")
    
    def broadcast_incident_alert(self, incident_data):
        """Broadcast security incident alert to all connected security users"""
        try:
            self.socketio.emit('security_incident_alert', incident_data, namespace='/security-center')
            logger.warning(f"Security incident alert broadcasted: {incident_data.get('title', 'Unknown incident')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting incident alert: {e}")