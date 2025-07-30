"""
Accounts Management WebSocket Handlers
Real-time data streaming for accounts dashboard with granular drill-down capabilities
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
import threading
import time
from flask_socketio import emit, join_room, leave_room

class AccountsWebSocketHandler:
    """Handles real-time WebSocket connections for accounts management"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.connected_clients = set()
        self.streaming_thread = None
        self.is_streaming = False
        
        # Register event handlers
        self.register_handlers()
        
    def register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('join_accounts_stream')
        def handle_join_accounts_stream():
            """Handle client joining accounts real-time stream"""
            room = 'accounts_stream'
            join_room(room)
            self.connected_clients.add(room)
            
            # Send initial data
            initial_data = self.get_current_metrics()
            emit('accounts_metrics_update', initial_data)
            
            # Start streaming if not already started
            if not self.is_streaming:
                self.start_streaming()
                
            print(f"Client joined accounts stream. Active clients: {len(self.connected_clients)}")
            
        @self.socketio.on('leave_accounts_stream')
        def handle_leave_accounts_stream():
            """Handle client leaving accounts stream"""
            room = 'accounts_stream'
            leave_room(room)
            if room in self.connected_clients:
                self.connected_clients.remove(room)
                
            # Stop streaming if no clients
            if not self.connected_clients:
                self.stop_streaming()
                
            print(f"Client left accounts stream. Active clients: {len(self.connected_clients)}")
            
        @self.socketio.on('request_accounts_data')
        def handle_request_accounts_data():
            """Handle request for current accounts data"""
            try:
                # Send current metrics
                metrics = self.get_current_metrics()
                emit('accounts_metrics_update', metrics)
                
                # Send chart data
                chart_data = self.get_chart_data()
                emit('accounts_chart_update', chart_data)
                
                # Send recent activities
                activities = self.get_recent_activities(20)
                for activity in activities:
                    emit('accounts_activity_update', activity)
                    
            except Exception as e:
                print(f"Error handling accounts data request: {e}")
                
        @self.socketio.on('request_filtered_activities')
        def handle_request_filtered_activities(data):
            """Handle request for filtered activities"""
            try:
                filter_type = data.get('filter', 'all')
                activities = self.get_filtered_activities(filter_type, 25)
                
                for activity in activities:
                    emit('accounts_activity_update', activity)
                    
            except Exception as e:
                print(f"Error handling filtered activities request: {e}")
                
        @self.socketio.on('request_more_activities')
        def handle_request_more_activities(data):
            """Handle request for more activities"""
            try:
                count = data.get('count', 25)
                activities = self.get_recent_activities(count)
                
                for activity in activities:
                    emit('accounts_activity_update', activity)
                    
            except Exception as e:
                print(f"Error handling more activities request: {e}")
    
    def start_streaming(self):
        """Start real-time data streaming"""
        if self.is_streaming:
            return
            
        self.is_streaming = True
        self.streaming_thread = threading.Thread(target=self._streaming_worker, daemon=True)
        self.streaming_thread.start()
        print("Accounts real-time streaming started")
        
    def stop_streaming(self):
        """Stop real-time data streaming"""
        self.is_streaming = False
        if self.streaming_thread:
            self.streaming_thread = None
        print("Accounts real-time streaming stopped")
        
    def _streaming_worker(self):
        """Background worker for streaming real-time data"""
        while self.is_streaming:
            try:
                if self.connected_clients:
                    # Stream metrics every 30 seconds
                    metrics = self.get_current_metrics()
                    self.socketio.emit('accounts_metrics_update', metrics, room='accounts_stream')
                    
                    # Stream new activities every 15 seconds
                    if random.random() > 0.7:  # 30% chance of new activity
                        activity = self.generate_random_activity()
                        self.socketio.emit('accounts_activity_update', activity, room='accounts_stream')
                    
                    # Stream chart updates every 60 seconds
                    if int(time.time()) % 60 == 0:
                        chart_data = self.get_chart_data()
                        self.socketio.emit('accounts_chart_update', chart_data, room='accounts_stream')
                
                time.sleep(15)  # Stream every 15 seconds
                
            except Exception as e:
                print(f"Error in accounts streaming worker: {e}")
                time.sleep(5)
                
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        base_time = datetime.utcnow()
        
        return {
            "active_accounts": 15247 + random.randint(-10, 10),
            "accounts_change": random.randint(15, 35),
            "pending_operations": 89 + random.randint(-15, 15),
            "avg_processing_time": round(3.2 + random.uniform(-0.5, 0.5), 1),
            "transaction_volume": 45670000 + random.randint(-500000, 500000),
            "volume_change": round(12.5 + random.uniform(-2.0, 2.0), 1),
            "security_score": round(98.5 + random.uniform(-0.3, 0.3), 1),
            "threats_blocked": 156 + random.randint(0, 10),
            "timestamp": base_time.isoformat()
        }
        
    def get_chart_data(self) -> Dict[str, Any]:
        """Get chart data for real-time updates"""
        current_time = datetime.utcnow()
        
        # Generate growth data for last 30 days
        growth_labels = []
        growth_values = []
        
        for i in range(30, 0, -1):
            date = current_time - timedelta(days=i)
            growth_labels.append(date.strftime("%m/%d"))
            # Simulate growth trend with some randomness
            base_value = 12000 + (30 - i) * 100
            growth_values.append(base_value + random.randint(-500, 500))
            
        # Account type distribution with some variation
        base_distribution = [8547, 4321, 1789, 590]
        type_distribution = [base + random.randint(-50, 50) for base in base_distribution]
        
        return {
            "growth_data": {
                "labels": growth_labels,
                "values": growth_values
            },
            "type_distribution": type_distribution,
            "timestamp": current_time.isoformat()
        }
        
    def get_recent_activities(self, count: int = 20) -> List[Dict[str, Any]]:
        """Get recent account activities"""
        activities = []
        current_time = datetime.utcnow()
        
        for i in range(count):
            activity = {
                "id": f"ACT-{random.randint(100000, 999999)}",
                "account_id": f"ACC-{random.randint(10000, 99999)}",
                "operation": random.choice([
                    "Account Opening", "Deposit", "Withdrawal", "Transfer", 
                    "Balance Inquiry", "Statement Request", "Card Activation",
                    "Wire Transfer", "Mobile Check Deposit", "ACH Transfer"
                ]),
                "amount": random.randint(100, 50000) if random.random() > 0.3 else None,
                "status": random.choice(["Success", "Success", "Success", "Pending", "Failed"]),  # Bias toward success
                "user": f"user_{random.randint(1000, 9999)}",
                "timestamp": (current_time - timedelta(seconds=random.randint(1, 3600))).isoformat()
            }
            activities.append(activity)
            
        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)
        
    def get_filtered_activities(self, filter_type: str, count: int = 25) -> List[Dict[str, Any]]:
        """Get filtered activities based on status"""
        activities = self.get_recent_activities(count * 2)  # Get more to filter from
        
        if filter_type == 'all':
            return activities[:count]
        
        # Filter by status
        filtered = [act for act in activities if act['status'].lower() == filter_type.lower()]
        return filtered[:count]
        
    def generate_random_activity(self) -> Dict[str, Any]:
        """Generate a random activity for real-time streaming"""
        current_time = datetime.utcnow()
        
        # More realistic operation distribution
        operations = [
            ("Balance Inquiry", 0.3),
            ("Deposit", 0.2),
            ("Transfer", 0.15),
            ("Withdrawal", 0.1),
            ("Account Opening", 0.05),
            ("Wire Transfer", 0.05),
            ("Mobile Check Deposit", 0.08),
            ("Statement Request", 0.04),
            ("Card Activation", 0.03)
        ]
        
        # Weighted random selection
        rand = random.random()
        cumulative = 0
        selected_operation = "Balance Inquiry"
        
        for operation, weight in operations:
            cumulative += weight
            if rand <= cumulative:
                selected_operation = operation
                break
                
        # Generate amount based on operation type
        amount = None
        if selected_operation in ["Deposit", "Withdrawal", "Transfer", "Wire Transfer", "Mobile Check Deposit"]:
            if selected_operation == "Wire Transfer":
                amount = random.randint(5000, 100000)  # Larger amounts for wire transfers
            elif selected_operation == "Mobile Check Deposit":
                amount = random.randint(50, 5000)  # Smaller amounts for mobile deposits
            else:
                amount = random.randint(100, 50000)
                
        # Status distribution (mostly successful)
        status_weights = [("Success", 0.85), ("Pending", 0.12), ("Failed", 0.03)]
        rand = random.random()
        cumulative = 0
        status = "Success"
        
        for s, weight in status_weights:
            cumulative += weight
            if rand <= cumulative:
                status = s
                break
        
        return {
            "id": f"ACT-{random.randint(100000, 999999)}",
            "account_id": f"ACC-{random.randint(10000, 99999)}",
            "operation": selected_operation,
            "amount": amount,
            "status": status,
            "user": f"user_{random.randint(1000, 9999)}",
            "timestamp": current_time.isoformat()
        }
        
    def get_drill_down_metrics(self, metric_type: str) -> Dict[str, Any]:
        """Get detailed drill-down metrics for specific metric types"""
        current_time = datetime.utcnow()
        
        if metric_type == "account_growth":
            return {
                "hourly_registrations": [random.randint(5, 25) for _ in range(24)],
                "daily_growth": [random.randint(150, 250) for _ in range(7)],
                "weekly_growth": [random.randint(800, 1200) for _ in range(4)],
                "growth_by_channel": {
                    "online": random.randint(60, 80),
                    "mobile": random.randint(15, 25),
                    "branch": random.randint(3, 8),
                    "referral": random.randint(5, 12)
                },
                "timestamp": current_time.isoformat()
            }
        elif metric_type == "transaction_patterns":
            return {
                "hourly_volume": [random.randint(500000, 2000000) for _ in range(24)],
                "transaction_types": {
                    "deposits": random.randint(40, 60),
                    "withdrawals": random.randint(20, 35),
                    "transfers": random.randint(15, 25),
                    "inquiries": random.randint(5, 15)
                },
                "avg_transaction_size": {
                    "deposits": random.randint(1500, 3500),
                    "withdrawals": random.randint(800, 2000),
                    "transfers": random.randint(1000, 5000)
                },
                "timestamp": current_time.isoformat()
            }
            
        return {}

def register_handlers(socketio):
    """Initialize accounts WebSocket handlers"""
    try:
        handler = AccountsWebSocketHandler(socketio)
        print("Accounts WebSocket handlers initialized successfully")
        return handler
    except Exception as e:
        print(f"Failed to initialize accounts WebSocket handlers: {e}")
        return None