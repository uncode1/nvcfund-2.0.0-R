"""
Admin Management Module Socket Handlers
Real-time data streaming for admin dashboard and granular drill-downs
"""

from flask import current_app
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
import logging
from datetime import datetime
import threading
import time
import psutil
import json

from .services import AdminManagementService

logger = logging.getLogger(__name__)

class AdminManagementSocketHandler:
    """Handles real-time socket connections for admin management dashboard"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.admin_service = AdminManagementService()
        self.active_rooms = set()
        self.streaming_threads = {}
        
        # Register socket event handlers
        self.register_handlers()
        
        # Start background metrics collection
        self.start_metrics_collection()
    
    def register_handlers(self):
        """Register all socket event handlers for admin management"""
        
        @self.socketio.on('connect', namespace='/admin-management')
        def handle_connect():
            """Handle client connection to admin management namespace"""
            if not current_user.is_authenticated:
                logger.warning("Unauthenticated user attempted admin socket connection")
                disconnect()
                return False
            
            # Verify admin permissions
            if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
                logger.warning(f"Non-admin user {current_user.id} attempted admin socket connection")
                disconnect()
                return False
            
            room = f"admin_{current_user.id}"
            join_room(room)
            self.active_rooms.add(room)
            
            logger.info(f"Admin user {current_user.id} connected to admin management socket")
            
            # Send initial dashboard data
            self.send_initial_dashboard_data(room)
        
        @self.socketio.on('disconnect', namespace='/admin-management')
        def handle_disconnect():
            """Handle client disconnection"""
            if current_user.is_authenticated:
                room = f"admin_{current_user.id}"
                leave_room(room)
                self.active_rooms.discard(room)
                
                # Stop streaming thread for this user
                if room in self.streaming_threads:
                    self.streaming_threads[room]['stop'] = True
                    del self.streaming_threads[room]
                
                logger.info(f"Admin user {current_user.id} disconnected from admin management socket")
        
        @self.socketio.on('request_dashboard_data', namespace='/admin-management')
        def handle_dashboard_request():
            """Handle request for dashboard data"""
            if not current_user.is_authenticated:
                return
            
            try:
                dashboard_data = self.admin_service.get_admin_dashboard_data(current_user.id)
                emit('dashboard_update', dashboard_data)
                
                logger.debug(f"Dashboard data sent to admin user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error sending dashboard data: {e}")
                emit('error', {'message': 'Failed to load dashboard data'})
        
        @self.socketio.on('request_metrics_update', namespace='/admin-management')
        def handle_metrics_request():
            """Handle request for real-time metrics update"""
            if not current_user.is_authenticated:
                return
            
            try:
                # Get real-time system metrics
                metrics = self.get_real_time_metrics()
                emit('system_metrics', metrics)
                
                # Get user activity data
                user_activity = self.get_user_activity_data()
                emit('user_activity', user_activity)
                
                logger.debug(f"Metrics update sent to admin user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error sending metrics update: {e}")
                emit('error', {'message': 'Failed to load metrics'})
        
        @self.socketio.on('request_component_status', namespace='/admin-management')
        def handle_component_status_request(data):
            """Handle request for specific component status"""
            if not current_user.is_authenticated:
                return
            
            try:
                component_id = data.get('component_id')
                if component_id:
                    component_status = self.get_component_status(component_id)
                    emit('component_status', component_status)
                
            except Exception as e:
                logger.error(f"Error getting component status: {e}")
                emit('error', {'message': 'Failed to get component status'})
        
        @self.socketio.on('start_real_time_monitoring', namespace='/admin-management')
        def handle_start_monitoring():
            """Start real-time monitoring stream for the user"""
            if not current_user.is_authenticated:
                return
            
            room = f"admin_{current_user.id}"
            if room not in self.streaming_threads:
                self.start_real_time_stream(room)
                logger.info(f"Started real-time monitoring for admin user {current_user.id}")
        
        @self.socketio.on('stop_real_time_monitoring', namespace='/admin-management')
        def handle_stop_monitoring():
            """Stop real-time monitoring stream for the user"""
            if not current_user.is_authenticated:
                return
            
            room = f"admin_{current_user.id}"
            if room in self.streaming_threads:
                self.streaming_threads[room]['stop'] = True
                del self.streaming_threads[room]
                logger.info(f"Stopped real-time monitoring for admin user {current_user.id}")
    
    def send_initial_dashboard_data(self, room):
        """Send initial dashboard data to connected client"""
        try:
            dashboard_data = self.admin_service.get_admin_dashboard_data(current_user.id)
            self.socketio.emit('dashboard_update', dashboard_data, room=room, namespace='/admin-management')
            
            # Send initial metrics
            metrics = self.get_real_time_metrics()
            self.socketio.emit('system_metrics', metrics, room=room, namespace='/admin-management')
            
        except Exception as e:
            logger.error(f"Error sending initial dashboard data: {e}")
    
    def start_real_time_stream(self, room):
        """Start real-time data streaming thread for a specific room"""
        
        def stream_data():
            stream_data = {'stop': False}
            self.streaming_threads[room] = stream_data
            
            while not stream_data.get('stop', False):
                try:
                    # Stream system metrics every 5 seconds
                    metrics = self.get_real_time_metrics()
                    self.socketio.emit('system_metrics', metrics, room=room, namespace='/admin-management')
                    
                    # Stream user activity every 10 seconds
                    if int(time.time()) % 10 == 0:
                        user_activity = self.get_user_activity_data()
                        self.socketio.emit('user_activity', user_activity, room=room, namespace='/admin-management')
                    
                    # Check for new alerts every 15 seconds
                    if int(time.time()) % 15 == 0:
                        alerts = self.check_new_alerts()
                        for alert in alerts:
                            self.socketio.emit('new_alert', alert, room=room, namespace='/admin-management')
                    
                    # Check for admin actions every 30 seconds
                    if int(time.time()) % 30 == 0:
                        recent_actions = self.get_recent_admin_actions()
                        for action in recent_actions:
                            self.socketio.emit('admin_action', action, room=room, namespace='/admin-management')
                    
                    time.sleep(1)  # Sleep for 1 second between iterations
                    
                except Exception as e:
                    logger.error(f"Error in real-time streaming: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start streaming in background thread
        thread = threading.Thread(target=stream_data, daemon=True)
        thread.start()
    
    def get_real_time_metrics(self):
        """Get real-time system metrics"""
        try:
            # CPU and Memory usage
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = (network.bytes_sent + network.bytes_recv) / (1024 * 1024)  # MB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_usage': round(cpu_usage, 2),
                'memory_usage': round(memory_usage, 2),
                'network_io': round(network_io, 2),
                'disk_usage': round(disk_usage, 2),
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_usage': 0,
                'memory_usage': 0,
                'network_io': 0,
                'disk_usage': 0,
                'load_average': 0
            }
    
    def get_user_activity_data(self):
        """Get user activity data for charts"""
        try:
            # Get hourly user activity for last 24 hours
            activity_data = self.admin_service.get_hourly_user_activity()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'labels': activity_data.get('labels', []),
                'active_users': activity_data.get('active_users', []),
                'new_registrations': activity_data.get('new_registrations', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity data: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'labels': [],
                'active_users': [],
                'new_registrations': []
            }
    
    def check_new_alerts(self):
        """Check for new system alerts"""
        try:
            # Get alerts from the last minute
            new_alerts = self.admin_service.get_new_alerts_since_last_check()
            return new_alerts
            
        except Exception as e:
            logger.error(f"Error checking new alerts: {e}")
            return []
    
    def get_recent_admin_actions(self):
        """Get recent administrative actions"""
        try:
            # Get admin actions from the last 30 seconds
            recent_actions = self.admin_service.get_recent_admin_actions(limit=5)
            return recent_actions
            
        except Exception as e:
            logger.error(f"Error getting recent admin actions: {e}")
            return []
    
    def get_component_status(self, component_id):
        """Get status for a specific system component"""
        try:
            component_status = self.admin_service.get_component_status(component_id)
            return component_status
            
        except Exception as e:
            logger.error(f"Error getting component status: {e}")
            return None
    
    def start_metrics_collection(self):
        """Start background metrics collection"""
        
        def collect_metrics():
            while True:
                try:
                    # Collect and store system metrics
                    metrics = self.get_real_time_metrics()
                    self.admin_service.store_system_metrics(metrics)
                    
                    # Sleep for 60 seconds between collections
                    time.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Error in metrics collection: {e}")
                    time.sleep(60)
        
        # Start metrics collection in background thread
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
        logger.info("Background metrics collection started")
    
    def broadcast_system_alert(self, alert_data):
        """Broadcast system alert to all connected admin users"""
        try:
            self.socketio.emit('system_alert', alert_data, namespace='/admin-management')
            logger.info(f"System alert broadcasted: {alert_data.get('message', 'Unknown alert')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system alert: {e}")
    
    def broadcast_admin_action(self, action_data):
        """Broadcast admin action to all connected admin users"""
        try:
            self.socketio.emit('admin_action_broadcast', action_data, namespace='/admin-management')
            logger.debug(f"Admin action broadcasted: {action_data.get('action_type', 'Unknown action')}")
            
        except Exception as e:
            logger.error(f"Error broadcasting admin action: {e}")

def register_handlers(socketio):
    """Initialize admin management WebSocket handlers"""
    try:
        handler = AdminManagementSocketHandler(socketio)
        logger.info("Admin Management WebSocket handlers initialized successfully")
        return handler
    except Exception as e:
        logger.error(f"Failed to initialize admin management WebSocket handlers: {e}")
        return None