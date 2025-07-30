"""
Smart Contracts WebSocket Handlers
Real-time streaming for blockchain events and smart contract monitoring
"""

import json
import logging
from datetime import datetime
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from typing import Dict, Any, List
import threading
import time
import random

logger = logging.getLogger(__name__)

class SmartContractStreamHandler:
    """
    Handles real-time streaming of smart contract events and blockchain data
    """
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.active_connections = {}
        self.streaming_threads = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def register_handlers(self):
        """Register all WebSocket event handlers"""
        
        @self.socketio.on('connect', namespace='/smart_contracts')
        def handle_connect():
            """Handle client connection to smart contracts namespace"""
            try:
                if not current_user.is_authenticated:
                    self.logger.warning("Unauthenticated user attempted to connect to smart contracts stream")
                    return False
                
                user_id = str(current_user.id)
                self.active_connections[user_id] = {
                    'connected_at': datetime.now().isoformat(),
                    'subscriptions': [],
                    'session_id': user_id
                }
                
                self.logger.info(f"User {current_user.username} connected to smart contracts stream")
                
                # Send initial connection confirmation
                emit('connection_status', {
                    'status': 'connected',
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Connected to Smart Contracts real-time stream'
                })
                
                # Send initial data
                self._send_initial_data()
                
            except Exception as e:
                self.logger.error(f"Error handling smart contracts connection: {e}")
                return False
        
        @self.socketio.on('disconnect', namespace='/smart_contracts')
        def handle_disconnect():
            """Handle client disconnection"""
            try:
                if current_user.is_authenticated:
                    user_id = str(current_user.id)
                    if user_id in self.active_connections:
                        del self.active_connections[user_id]
                    
                    # Stop streaming threads for this user
                    if user_id in self.streaming_threads:
                        thread = self.streaming_threads[user_id]
                        thread.stop()
                        del self.streaming_threads[user_id]
                    
                    self.logger.info(f"User {current_user.username} disconnected from smart contracts stream")
                    
            except Exception as e:
                self.logger.error(f"Error handling smart contracts disconnection: {e}")
        
        @self.socketio.on('subscribe_contract', namespace='/smart_contracts')
        def handle_contract_subscription(data):
            """Subscribe to specific contract events"""
            try:
                if not current_user.is_authenticated:
                    return
                
                contract_address = data.get('contract_address')
                event_types = data.get('event_types', ['all'])
                
                if not contract_address:
                    emit('error', {'message': 'Contract address is required'})
                    return
                
                user_id = str(current_user.id)
                room_name = f"contract_{contract_address}"
                
                join_room(room_name)
                
                # Update user subscriptions
                if user_id in self.active_connections:
                    self.active_connections[user_id]['subscriptions'].append({
                        'contract_address': contract_address,
                        'event_types': event_types,
                        'subscribed_at': datetime.now().isoformat()
                    })
                
                self.logger.info(f"User {current_user.username} subscribed to contract {contract_address}")
                
                emit('subscription_confirmed', {
                    'contract_address': contract_address,
                    'event_types': event_types,
                    'status': 'subscribed'
                })
                
                # Start contract-specific streaming
                self._start_contract_streaming(contract_address, user_id)
                
            except Exception as e:
                self.logger.error(f"Error subscribing to contract: {e}")
                emit('error', {'message': 'Failed to subscribe to contract'})
        
        @self.socketio.on('unsubscribe_contract', namespace='/smart_contracts')
        def handle_contract_unsubscription(data):
            """Unsubscribe from specific contract events"""
            try:
                if not current_user.is_authenticated:
                    return
                
                contract_address = data.get('contract_address')
                room_name = f"contract_{contract_address}"
                
                leave_room(room_name)
                
                user_id = str(current_user.id)
                if user_id in self.active_connections:
                    subscriptions = self.active_connections[user_id]['subscriptions']
                    self.active_connections[user_id]['subscriptions'] = [
                        sub for sub in subscriptions 
                        if sub['contract_address'] != contract_address
                    ]
                
                self.logger.info(f"User {current_user.username} unsubscribed from contract {contract_address}")
                
                emit('unsubscription_confirmed', {
                    'contract_address': contract_address,
                    'status': 'unsubscribed'
                })
                
            except Exception as e:
                self.logger.error(f"Error unsubscribing from contract: {e}")
        
        @self.socketio.on('request_gas_price', namespace='/smart_contracts')
        def handle_gas_price_request():
            """Handle request for current gas prices"""
            try:
                gas_data = self._get_current_gas_prices()
                emit('gas_price_update', gas_data)
                
            except Exception as e:
                self.logger.error(f"Error getting gas prices: {e}")
                emit('error', {'message': 'Failed to get gas prices'})
        
        @self.socketio.on('request_network_status', namespace='/smart_contracts')
        def handle_network_status_request():
            """Handle request for network status"""
            try:
                network_data = self._get_network_status()
                emit('network_status_update', network_data)
                
            except Exception as e:
                self.logger.error(f"Error getting network status: {e}")
                emit('error', {'message': 'Failed to get network status'})
    
    def _send_initial_data(self):
        """Send initial data to newly connected client"""
        try:
            # Send initial contract overview
            overview_data = {
                'active_contracts': 42,
                'total_transactions_today': 15847,
                'average_gas_price': 25,
                'network_health': 98.5,
                'timestamp': datetime.now().isoformat()
            }
            emit('contract_overview', overview_data)
            
            # Send recent transactions
            recent_transactions = self._get_recent_transactions()
            emit('recent_transactions', recent_transactions)
            
            # Send gas price data
            gas_data = self._get_current_gas_prices()
            emit('gas_price_update', gas_data)
            
        except Exception as e:
            self.logger.error(f"Error sending initial data: {e}")
    
    def _start_contract_streaming(self, contract_address: str, user_id: str):
        """Start streaming data for a specific contract"""
        try:
            if user_id not in self.streaming_threads:
                thread = ContractStreamingThread(
                    contract_address, 
                    user_id, 
                    self.socketio,
                    self.logger
                )
                thread.start()
                self.streaming_threads[user_id] = thread
                
        except Exception as e:
            self.logger.error(f"Error starting contract streaming: {e}")
    
    def _get_current_gas_prices(self) -> Dict[str, Any]:
        """Get current gas prices for supported networks"""
        # In production, this would fetch from actual blockchain nodes
        return {
            'ethereum': {
                'slow': random.randint(15, 25),
                'standard': random.randint(25, 35),
                'fast': random.randint(35, 50)
            },
            'polygon': {
                'slow': random.randint(30, 40),
                'standard': random.randint(40, 60),
                'fast': random.randint(60, 80)
            },
            'bsc': {
                'slow': random.randint(3, 7),
                'standard': random.randint(7, 12),
                'fast': random.randint(12, 20)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_network_status(self) -> Dict[str, Any]:
        """Get current network status for all supported chains"""
        return {
            'ethereum': {
                'status': 'operational',
                'block_height': 18745632 + random.randint(0, 100),
                'block_time': 12.5,
                'pending_transactions': random.randint(50000, 150000)
            },
            'polygon': {
                'status': 'operational',
                'block_height': 47856321 + random.randint(0, 500),
                'block_time': 2.1,
                'pending_transactions': random.randint(1000, 5000)
            },
            'bsc': {
                'status': 'operational',
                'block_height': 31247589 + random.randint(0, 200),
                'block_time': 3.0,
                'pending_transactions': random.randint(5000, 20000)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_recent_transactions(self) -> List[Dict[str, Any]]:
        """Get recent smart contract transactions"""
        transactions = []
        
        for i in range(5):
            tx = {
                'hash': f"0x{random.randint(100000000000000000, 999999999999999999):x}",
                'contract_address': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                'function': random.choice(['transfer', 'approve', 'mint', 'burn', 'swap']),
                'from_address': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                'gas_used': random.randint(21000, 200000),
                'timestamp': datetime.now().isoformat(),
                'status': 'success' if random.random() > 0.1 else 'pending'
            }
            transactions.append(tx)
        
        return transactions


class ContractStreamingThread(threading.Thread):
    """
    Background thread for streaming contract-specific data
    """
    
    def __init__(self, contract_address: str, user_id: str, socketio, logger):
        super().__init__(daemon=True)
        self.contract_address = contract_address
        self.user_id = user_id
        self.socketio = socketio
        self.logger = logger
        self.running = True
        
    def run(self):
        """Main streaming loop"""
        while self.running:
            try:
                # Simulate contract events
                event_data = self._generate_contract_event()
                
                # Emit to specific contract room
                room_name = f"contract_{self.contract_address}"
                self.socketio.emit(
                    'contract_event',
                    event_data,
                    room=room_name,
                    namespace='/smart_contracts'
                )
                
                # Wait before next event
                time.sleep(random.uniform(2, 8))
                
            except Exception as e:
                self.logger.error(f"Error in contract streaming thread: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the streaming thread"""
        self.running = False
    
    def _generate_contract_event(self) -> Dict[str, Any]:
        """Generate simulated contract event"""
        events = [
            {
                'event_type': 'Transfer',
                'data': {
                    'from': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                    'to': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                    'value': str(random.randint(1000, 1000000))
                }
            },
            {
                'event_type': 'Approval',
                'data': {
                    'owner': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                    'spender': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                    'value': str(random.randint(1000, 1000000))
                }
            },
            {
                'event_type': 'Mint',
                'data': {
                    'to': f"0x{random.randint(1000000000000000000, 9999999999999999999):x}",
                    'amount': str(random.randint(1000, 100000))
                }
            }
        ]
        
        event = random.choice(events)
        event.update({
            'contract_address': self.contract_address,
            'transaction_hash': f"0x{random.randint(100000000000000000, 999999999999999999):x}",
            'block_number': 18745632 + random.randint(0, 100),
            'timestamp': datetime.now().isoformat(),
            'gas_used': random.randint(21000, 150000)
        })
        
        return event


# Global stream handler instance
smart_contract_stream_handler = None

def initialize_smart_contract_streams(socketio):
    """Initialize smart contract streaming with SocketIO"""
    global smart_contract_stream_handler
    
    try:
        smart_contract_stream_handler = SmartContractStreamHandler(socketio)
        smart_contract_stream_handler.register_handlers()
        
        logger.info("Smart Contracts WebSocket streaming initialized successfully")
        return smart_contract_stream_handler
        
    except Exception as e:
        logger.error(f"Failed to initialize smart contract streams: {e}")
        return None

def get_stream_handler():
    """Get the global stream handler instance"""
    return smart_contract_stream_handler