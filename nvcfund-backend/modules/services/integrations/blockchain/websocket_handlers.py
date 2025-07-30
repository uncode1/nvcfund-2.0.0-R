"""
WebSocket Handlers for Blockchain Integration
Real-time blockchain data streaming and notifications
"""

import logging
from flask_socketio import emit, join_room, leave_room
from modules.utils.services import ErrorLoggerService

logger = logging.getLogger(__name__)
error_service = ErrorLoggerService()

def register_blockchain_websocket_handlers(socketio):
    """Register all blockchain-related WebSocket handlers"""
    
    @socketio.on('join_blockchain_room')
    def on_join_blockchain(data):
        """Join blockchain monitoring room"""
        try:
            room = data.get('room', 'blockchain_general')
            join_room(room)
            emit('blockchain_status', {
                'status': 'connected',
                'room': room,
                'message': f'Connected to blockchain monitoring room: {room}'
            })
            logger.info(f"Client joined blockchain room: {room}")
        except Exception as e:
            error_service.log_error('websocket', 'blockchain_join_error', str(e))
            emit('blockchain_error', {'error': 'Failed to join blockchain room'})

    @socketio.on('leave_blockchain_room')
    def on_leave_blockchain(data):
        """Leave blockchain monitoring room"""
        try:
            room = data.get('room', 'blockchain_general')
            leave_room(room)
            emit('blockchain_status', {
                'status': 'disconnected',
                'room': room,
                'message': f'Disconnected from blockchain monitoring room: {room}'
            })
            logger.info(f"Client left blockchain room: {room}")
        except Exception as e:
            error_service.log_error('websocket', 'blockchain_leave_error', str(e))
            emit('blockchain_error', {'error': 'Failed to leave blockchain room'})

    @socketio.on('blockchain_subscribe')
    def on_blockchain_subscribe(data):
        """Subscribe to specific blockchain events"""
        try:
            event_type = data.get('event_type', 'all')
            network = data.get('network', 'ethereum')
            
            # Join specific subscription room
            room = f"blockchain_{network}_{event_type}"
            join_room(room)
            
            emit('blockchain_subscription', {
                'status': 'subscribed',
                'event_type': event_type,
                'network': network,
                'room': room
            })
            
            logger.info(f"Client subscribed to {event_type} events on {network}")
        except Exception as e:
            error_service.log_error('websocket', 'blockchain_subscribe_error', str(e))
            emit('blockchain_error', {'error': 'Failed to subscribe to blockchain events'})

    @socketio.on('blockchain_unsubscribe')
    def on_blockchain_unsubscribe(data):
        """Unsubscribe from specific blockchain events"""
        try:
            event_type = data.get('event_type', 'all')
            network = data.get('network', 'ethereum')
            
            # Leave specific subscription room
            room = f"blockchain_{network}_{event_type}"
            leave_room(room)
            
            emit('blockchain_subscription', {
                'status': 'unsubscribed',
                'event_type': event_type,
                'network': network,
                'room': room
            })
            
            logger.info(f"Client unsubscribed from {event_type} events on {network}")
        except Exception as e:
            error_service.log_error('websocket', 'blockchain_unsubscribe_error', str(e))
            emit('blockchain_error', {'error': 'Failed to unsubscribe from blockchain events'})

def emit_blockchain_update(socketio, data):
    """Emit blockchain update to all connected clients"""
    try:
        network = data.get('network', 'ethereum')
        event_type = data.get('event_type', 'transaction')
        room = f"blockchain_{network}_{event_type}"
        
        socketio.emit('blockchain_update', data, room=room)
        logger.info(f"Emitted blockchain update to room: {room}")
    except Exception as e:
        error_service.log_error('websocket', 'blockchain_emit_error', str(e))

def emit_price_update(socketio, price_data):
    """Emit cryptocurrency price updates"""
    try:
        socketio.emit('price_update', price_data, room='blockchain_general')
        logger.info("Emitted price update to blockchain room")
    except Exception as e:
        error_service.log_error('websocket', 'price_emit_error', str(e))

def emit_network_status(socketio, status_data):
    """Emit blockchain network status updates"""
    try:
        network = status_data.get('network', 'ethereum')
        room = f"blockchain_{network}_status"
        
        socketio.emit('network_status', status_data, room=room)
        logger.info(f"Emitted network status for {network}")
    except Exception as e:
        error_service.log_error('websocket', 'network_status_emit_error', str(e))

def handle_binance_connection(socketio):
    """Handle Binance WebSocket connection for real-time trading data"""
    
    @socketio.on('binance_connect')
    def on_binance_connect(data):
        """Connect to Binance WebSocket streams"""
        try:
            symbols = data.get('symbols', ['BTCUSDT', 'ETHUSDT'])
            room = 'binance_trading'
            join_room(room)
            
            emit('binance_status', {
                'status': 'connected',
                'symbols': symbols,
                'message': 'Connected to Binance real-time data'
            })
            
            logger.info(f"Client connected to Binance trading room with symbols: {symbols}")
        except Exception as e:
            error_service.log_error('websocket', 'binance_connect_error', str(e))
            emit('binance_error', {'error': 'Failed to connect to Binance streams'})

    @socketio.on('binance_disconnect')
    def on_binance_disconnect():
        """Disconnect from Binance WebSocket streams"""
        try:
            leave_room('binance_trading')
            emit('binance_status', {
                'status': 'disconnected',
                'message': 'Disconnected from Binance real-time data'
            })
            logger.info("Client disconnected from Binance trading room")
        except Exception as e:
            error_service.log_error('websocket', 'binance_disconnect_error', str(e))

def emit_binance_price_update(socketio, price_data):
    """Emit Binance price updates to connected clients"""
    try:
        socketio.emit('binance_price', price_data, room='binance_trading')
        logger.info(f"Emitted Binance price update for {price_data.get('symbol', 'unknown')}")
    except Exception as e:
        error_service.log_error('websocket', 'binance_price_emit_error', str(e))