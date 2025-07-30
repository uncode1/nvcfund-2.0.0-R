"""
Trading Module WebSocket Handlers
Real-time streaming for advanced trading platform and market data
"""

from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
import json
import threading
import time
from decimal import Decimal
from datetime import datetime, timedelta
import random

from modules.core.rbac import can_access
from modules.utils.services import BankingLogger

logger = BankingLogger()

# Active WebSocket connections
trading_connections = {}
streaming_threads = {}

def handle_trading_connection(socketio):
    """Handle trading module WebSocket connections"""
    
    @socketio.on('connect', namespace='/trading')
    def on_connect():
        if not current_user.is_authenticated:
            return False
            
        if not can_access(current_user.role, 'trading_operations'):
            logger.log_security_event(
                event_type='unauthorized_websocket_access',
                user_id=current_user.id,
                details={'namespace': 'trading', 'reason': 'insufficient_permissions'}
            )
            return False
        
        trading_connections[current_user.id] = {
            'user_id': current_user.id,
            'role': current_user.role,
            'connected_at': datetime.utcnow(),
            'room': f'trading_{current_user.role}'
        }
        
        logger.log_api_event(
            event_type='websocket_connect',
            user_id=current_user.id,
            details={'namespace': 'trading', 'role': current_user.role}
        )
        
        emit('connection_status', {'status': 'connected', 'namespace': 'trading'})
    
    @socketio.on('disconnect', namespace='/trading')
    def on_disconnect():
        if current_user.is_authenticated and current_user.id in trading_connections:
            del trading_connections[current_user.id]
            
        logger.log_api_event(
            event_type='websocket_disconnect',
            user_id=current_user.id if current_user.is_authenticated else 'anonymous',
            details={'namespace': 'trading'}
        )
    
    @socketio.on('join_room', namespace='/trading')
    def on_join_room(data):
        if not current_user.is_authenticated:
            return False
            
        room = data.get('room', 'trading_dashboard')
        join_room(room)
        
        # Start streaming for this room if not already active
        if room not in streaming_threads:
            streaming_threads[room] = threading.Thread(
                target=start_trading_streaming,
                args=(socketio, room),
                daemon=True
            )
            streaming_threads[room].start()
        
        emit('joined_room', {'room': room, 'status': 'success'})
    
    @socketio.on('request_market_data', namespace='/trading')
    def on_market_data_request():
        if not current_user.is_authenticated or not can_access(current_user.role, 'trading_operations'):
            return False
        
        # Send real-time market data
        market_data = get_live_market_data()
        emit('market_data_update', market_data)
    
    @socketio.on('request_portfolio_update', namespace='/trading')
    def on_portfolio_update_request():
        if not current_user.is_authenticated or not can_access(current_user.role, 'trading_operations'):
            return False
        
        # Send real-time portfolio data
        portfolio_data = get_live_portfolio_data()
        emit('portfolio_update', portfolio_data)
    
    @socketio.on('subscribe_instrument', namespace='/trading')
    def on_instrument_subscribe(data):
        if not current_user.is_authenticated:
            return False
        
        instrument = data.get('instrument')
        if instrument:
            join_room(f'instrument_{instrument}')
            emit('subscribed', {'instrument': instrument, 'status': 'success'})

def start_trading_streaming(socketio, room):
    """Start real-time streaming for trading operations"""
    
    while room in streaming_threads:
        try:
            # Live Market Data Updates
            market_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'major_indices': {
                    'sp500': {
                        'price': 4567.89 + random.uniform(-5, 5),
                        'change': random.uniform(-0.5, 0.8),
                        'change_pct': random.uniform(-0.15, 0.18),
                        'volume': random.randint(85_000_000, 125_000_000)
                    },
                    'nasdaq': {
                        'price': 14234.56 + random.uniform(-15, 15),
                        'change': random.uniform(-1.2, 1.5),
                        'change_pct': random.uniform(-0.12, 0.15),
                        'volume': random.randint(65_000_000, 95_000_000)
                    },
                    'dow': {
                        'price': 34567.12 + random.uniform(-25, 25),
                        'change': random.uniform(-2.0, 2.5),
                        'change_pct': random.uniform(-0.08, 0.10),
                        'volume': random.randint(45_000_000, 75_000_000)
                    }
                },
                'fx_rates': {
                    'eur_usd': 1.0856 + random.uniform(-0.001, 0.001),
                    'gbp_usd': 1.2734 + random.uniform(-0.001, 0.001),
                    'usd_jpy': 149.67 + random.uniform(-0.05, 0.05),
                    'usd_chf': 0.8945 + random.uniform(-0.001, 0.001)
                },
                'commodities': {
                    'gold': 1945.60 + random.uniform(-2, 2),
                    'oil_wti': 78.45 + random.uniform(-0.5, 0.5),
                    'silver': 24.89 + random.uniform(-0.1, 0.1),
                    'copper': 3.67 + random.uniform(-0.02, 0.02)
                }
            }
            
            socketio.emit('market_data_update', market_update, room=room, namespace='/trading')
            
            # Live Trading Activity Updates
            trading_activity = {
                'timestamp': datetime.utcnow().isoformat(),
                'active_orders': random.randint(45, 89),
                'executed_trades': random.randint(12, 28),
                'total_volume': random.randint(15_000_000, 45_000_000),
                'pnl_today': random.randint(-250_000, 850_000),
                'open_positions': random.randint(15, 35),
                'recent_executions': [
                    {
                        'id': f'trade_{random.randint(10000, 99999)}',
                        'instrument': random.choice(['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']),
                        'side': random.choice(['BUY', 'SELL']),
                        'quantity': random.randint(100, 1000),
                        'price': round(random.uniform(150, 350), 2),
                        'timestamp': datetime.utcnow().isoformat(),
                        'status': 'FILLED'
                    }
                    for _ in range(3)
                ]
            }
            
            socketio.emit('trading_activity_update', trading_activity, room=room, namespace='/trading')
            
            # Portfolio Performance Updates
            portfolio_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_value': 12_450_000 + random.randint(-50_000, 150_000),
                'daily_pnl': random.randint(-125_000, 275_000),
                'daily_pnl_pct': random.uniform(-1.2, 2.8),
                'unrealized_pnl': random.randint(-75_000, 185_000),
                'realized_pnl': random.randint(-25_000, 95_000),
                'cash_balance': 2_350_000 + random.randint(-25_000, 75_000),
                'buying_power': 4_700_000 + random.randint(-50_000, 150_000),
                'margin_used': random.uniform(15.5, 45.8),
                'top_performers': [
                    {
                        'symbol': 'NVDA',
                        'position_value': 1_250_000,
                        'pnl': 85_000,
                        'pnl_pct': 7.3
                    },
                    {
                        'symbol': 'AAPL',
                        'position_value': 875_000,
                        'pnl': 42_500,
                        'pnl_pct': 5.1
                    }
                ],
                'risk_metrics': {
                    'var_1d': random.uniform(125_000, 185_000),
                    'var_5d': random.uniform(275_000, 425_000),
                    'sharpe_ratio': random.uniform(1.2, 2.1),
                    'max_drawdown': random.uniform(-3.5, -1.8),
                    'beta': random.uniform(0.85, 1.25)
                }
            }
            
            socketio.emit('portfolio_update', portfolio_update, room=room, namespace='/trading')
            
            # Risk Management Updates
            risk_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'risk_limits': {
                    'daily_loss_limit': 500_000,
                    'current_daily_loss': abs(min(0, portfolio_update['daily_pnl'])),
                    'position_limit': 2_000_000,
                    'largest_position': 1_250_000,
                    'concentration_limit': 15.0,  # % of portfolio
                    'current_max_concentration': 12.3
                },
                'compliance_status': {
                    'risk_limits_ok': True,
                    'margin_requirements_met': True,
                    'position_limits_ok': True,
                    'exposure_limits_ok': True
                },
                'alerts': [
                    {
                        'type': 'position_size',
                        'message': 'NVDA position approaching concentration limit',
                        'severity': 'warning',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                ] if random.random() < 0.3 else []
            }
            
            socketio.emit('risk_update', risk_update, room=room, namespace='/trading')
            
            # Algorithm Performance Updates
            algo_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'active_strategies': 7,
                'total_algo_pnl': random.randint(-45_000, 125_000),
                'strategies': [
                    {
                        'name': 'Mean Reversion Alpha',
                        'status': 'active',
                        'pnl_today': random.randint(-15_000, 35_000),
                        'sharpe_ratio': random.uniform(1.1, 2.3),
                        'win_rate': random.uniform(58, 72),
                        'trades_today': random.randint(15, 45)
                    },
                    {
                        'name': 'Momentum Scalper',
                        'status': 'active',
                        'pnl_today': random.randint(-8_000, 18_000),
                        'sharpe_ratio': random.uniform(0.9, 1.8),
                        'win_rate': random.uniform(52, 68),
                        'trades_today': random.randint(25, 75)
                    },
                    {
                        'name': 'Arbitrage Engine',
                        'status': 'active',
                        'pnl_today': random.randint(-2_000, 12_000),
                        'sharpe_ratio': random.uniform(1.8, 2.8),
                        'win_rate': random.uniform(75, 85),
                        'trades_today': random.randint(5, 15)
                    }
                ]
            }
            
            socketio.emit('algo_update', algo_update, room=room, namespace='/trading')
            
            time.sleep(15)  # Update every 15 seconds for trading data
            
        except Exception as e:
            logger.log_error_event(
                error_type='websocket_streaming_error',
                details={'namespace': 'trading', 'room': room, 'error': str(e)}
            )
            break

def get_live_market_data():
    """Get current market data for major instruments"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'equities': {
            'AAPL': {'price': 189.45, 'change': 2.34, 'volume': 45_000_000},
            'MSFT': {'price': 342.67, 'change': -1.23, 'volume': 28_000_000},
            'GOOGL': {'price': 142.89, 'change': 3.45, 'volume': 32_000_000},
            'TSLA': {'price': 248.56, 'change': -5.67, 'volume': 75_000_000},
            'NVDA': {'price': 456.78, 'change': 12.34, 'volume': 55_000_000}
        },
        'forex': {
            'EUR/USD': {'price': 1.0856, 'change': 0.0012, 'spread': 0.0001},
            'GBP/USD': {'price': 1.2734, 'change': -0.0045, 'spread': 0.0002},
            'USD/JPY': {'price': 149.67, 'change': 0.23, 'spread': 0.01},
            'USD/CHF': {'price': 0.8945, 'change': -0.0008, 'spread': 0.0001}
        },
        'commodities': {
            'Gold': {'price': 1945.60, 'change': 8.45, 'unit': 'USD/oz'},
            'Oil (WTI)': {'price': 78.45, 'change': -0.89, 'unit': 'USD/barrel'},
            'Silver': {'price': 24.89, 'change': 0.34, 'unit': 'USD/oz'},
            'Copper': {'price': 3.67, 'change': 0.05, 'unit': 'USD/lb'}
        },
        'crypto': {
            'BTC/USD': {'price': 42500.00, 'change': 1250.00, 'volume': 15_000},
            'ETH/USD': {'price': 2650.00, 'change': 125.00, 'volume': 45_000},
            'NVCT/USD': {'price': 1.0001, 'change': 0.0001, 'volume': 850_000}
        }
    }

def get_live_portfolio_data():
    """Get current portfolio performance data"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'total_value': 12_567_890,
        'cash_balance': 2_345_678,
        'invested_value': 10_222_212,
        'daily_pnl': 125_789,
        'daily_pnl_pct': 1.01,
        'unrealized_pnl': 856_789,
        'realized_pnl': 234_567,
        'positions': [
            {
                'symbol': 'AAPL',
                'quantity': 1000,
                'avg_price': 185.50,
                'current_price': 189.45,
                'market_value': 189_450,
                'pnl': 3_950,
                'pnl_pct': 2.13
            },
            {
                'symbol': 'MSFT',
                'quantity': 500,
                'avg_price': 345.20,
                'current_price': 342.67,
                'market_value': 171_335,
                'pnl': -1_265,
                'pnl_pct': -0.73
            }
        ],
        'allocation': {
            'equities': 78.5,
            'cash': 18.7,
            'bonds': 2.8
        }
    }

def send_trading_alert(alert_type, message, severity='info', user_ids=None):
    """Send real-time alert to trading users"""
    from app import socketio
    
    alert_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': alert_type,
        'message': message,
        'severity': severity,
        'source': 'trading_operations'
    }
    
    if user_ids:
        for user_id in user_ids:
            if user_id in trading_connections:
                socketio.emit('trading_alert', alert_data, 
                            room=trading_connections[user_id]['room'], 
                            namespace='/trading')
    else:
        # Send to all trading users
        socketio.emit('trading_alert', alert_data, 
                     room='trading_dashboard', 
                     namespace='/trading')
    
    logger.log_security_event(
        event_type='trading_alert_sent',
        details={'alert_type': alert_type, 'severity': severity, 'message': message}
    )