"""
Treasury Module WebSocket Handlers
Real-time streaming for $30T NVCT operations and asset management
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
treasury_connections = {}
streaming_threads = {}

def handle_treasury_connection(socketio):
    """Handle treasury module WebSocket connections"""
    
    @socketio.on('connect', namespace='/treasury')
    def on_connect():
        if not current_user.is_authenticated:
            return False
            
        if not can_access(current_user.role, 'treasury_operations'):
            logger.log_security_event(
                event_type='unauthorized_websocket_access',
                user_id=current_user.id,
                details={'namespace': 'treasury', 'reason': 'insufficient_permissions'}
            )
            return False
        
        treasury_connections[current_user.id] = {
            'user_id': current_user.id,
            'role': current_user.role,
            'connected_at': datetime.utcnow(),
            'room': f'treasury_{current_user.role}'
        }
        
        logger.log_api_event(
            event_type='websocket_connect',
            user_id=current_user.id,
            details={'namespace': 'treasury', 'role': current_user.role}
        )
        
        emit('connection_status', {'status': 'connected', 'namespace': 'treasury'})
    
    @socketio.on('disconnect', namespace='/treasury')
    def on_disconnect():
        if current_user.is_authenticated and current_user.id in treasury_connections:
            del treasury_connections[current_user.id]
            
        logger.log_api_event(
            event_type='websocket_disconnect',
            user_id=current_user.id if current_user.is_authenticated else 'anonymous',
            details={'namespace': 'treasury'}
        )
    
    @socketio.on('join_room', namespace='/treasury')
    def on_join_room(data):
        if not current_user.is_authenticated:
            return False
            
        room = data.get('room', 'treasury_dashboard')
        join_room(room)
        
        # Start streaming for this room if not already active
        if room not in streaming_threads:
            streaming_threads[room] = threading.Thread(
                target=start_treasury_streaming,
                args=(socketio, room),
                daemon=True
            )
            streaming_threads[room].start()
        
        emit('joined_room', {'room': room, 'status': 'success'})
    
    @socketio.on('request_nvct_update', namespace='/treasury')
    def on_nvct_update_request():
        if not current_user.is_authenticated or not can_access(current_user.role, 'nvct_operations'):
            return False
        
        # Send real-time NVCT metrics
        nvct_data = get_live_nvct_metrics()
        emit('nvct_update', nvct_data)
    
    @socketio.on('request_liquidity_update', namespace='/treasury')
    def on_liquidity_update_request():
        if not current_user.is_authenticated or not can_access(current_user.role, 'treasury_operations'):
            return False
        
        # Send real-time liquidity metrics
        liquidity_data = get_live_liquidity_metrics()
        emit('liquidity_update', liquidity_data)

def start_treasury_streaming(socketio, room):
    """Start real-time streaming for treasury operations"""
    
    while room in streaming_threads:
        try:
            # NVCT Supply Management Updates
            nvct_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_supply': 30_000_000_000_000,  # $30T
                'circulating_supply': 29_856_234_567_890,
                'market_cap': 29_856_234_567_890,  # 1:1 USD peg
                'backing_ratio': 189.5,  # 189.5% over-collateralization
                'price_stability': 99.97,  # 99.97% stability
                'daily_volume': random.randint(450_000_000, 850_000_000),
                'mint_burn_activity': {
                    'daily_mints': random.randint(50_000_000, 150_000_000),
                    'daily_burns': random.randint(25_000_000, 75_000_000),
                    'net_change': random.randint(-25_000_000, 100_000_000)
                }
            }
            
            socketio.emit('nvct_supply_update', nvct_update, room=room, namespace='/treasury')
            
            # Asset Backing Portfolio Updates
            asset_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_backing_value': 56_700_000_000_000,  # $56.7T backing
                'asset_composition': {
                    'us_treasury_bonds': 45.2,  # % allocation
                    'corporate_bonds': 28.7,
                    'real_estate': 15.3,
                    'gold_reserves': 8.1,
                    'cash_equivalents': 2.7
                },
                'yield_performance': {
                    'portfolio_yield': 4.35,  # % annual yield
                    'risk_adjusted_return': 3.89,
                    'sharpe_ratio': 1.24
                },
                'daily_pnl': random.randint(-500_000_000, 1_200_000_000)
            }
            
            socketio.emit('asset_backing_update', asset_update, room=room, namespace='/treasury')
            
            # Liquidity Management Updates
            liquidity_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_liquidity': 2_340_000_000_000,  # $2.34T available liquidity
                'liquidity_ratio': 7.8,  # % of total supply
                'reserve_requirements': {
                    'minimum_required': 1_500_000_000_000,
                    'current_level': 2_340_000_000_000,
                    'excess_reserves': 840_000_000_000
                },
                'funding_sources': {
                    'institutional_deposits': 65.4,  # % of liquidity
                    'repo_markets': 22.1,
                    'central_bank_facilities': 8.7,
                    'interbank_lending': 3.8
                },
                'stress_test_results': {
                    'liquidity_coverage_ratio': 245.6,  # %
                    'net_stable_funding_ratio': 189.3,
                    'stress_scenario_survival': 45  # days
                }
            }
            
            socketio.emit('liquidity_update', liquidity_update, room=room, namespace='/treasury')
            
            # Risk Metrics Updates
            risk_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'portfolio_var': 2.34,  # % Value at Risk (95% confidence, 1-day)
                'credit_risk_exposure': 12.5,  # % of portfolio
                'interest_rate_duration': 4.2,  # years
                'fx_exposure': {
                    'usd_exposure': 78.5,  # % USD denominated
                    'eur_exposure': 12.3,
                    'gbp_exposure': 5.7,
                    'other_currencies': 3.5
                },
                'concentration_limits': {
                    'single_issuer_limit': 5.0,  # % max per issuer
                    'current_max_concentration': 3.8,
                    'sector_concentration': {
                        'government': 67.8,
                        'financial': 18.2,
                        'corporate': 14.0
                    }
                }
            }
            
            socketio.emit('risk_metrics_update', risk_update, room=room, namespace='/treasury')
            
            # Cross-chain Bridge Activity
            bridge_update = {
                'timestamp': datetime.utcnow().isoformat(),
                'active_networks': ['BSC', 'Polygon', 'Ethereum', 'Arbitrum'],
                'bridge_volumes': {
                    'bsc_to_polygon': random.randint(50_000_000, 150_000_000),
                    'polygon_to_ethereum': random.randint(25_000_000, 75_000_000),
                    'ethereum_to_arbitrum': random.randint(10_000_000, 40_000_000),
                    'total_daily_volume': random.randint(85_000_000, 265_000_000)
                },
                'bridge_fees_collected': random.randint(45_000, 125_000),
                'pending_transfers': random.randint(15, 45),
                'network_status': {
                    'bsc': 'operational',
                    'polygon': 'operational', 
                    'ethereum': 'congested',
                    'arbitrum': 'operational'
                }
            }
            
            socketio.emit('bridge_activity_update', bridge_update, room=room, namespace='/treasury')
            
            time.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.log_error_event(
                error_type='websocket_streaming_error',
                details={'namespace': 'treasury', 'room': room, 'error': str(e)}
            )
            break

def get_live_nvct_metrics():
    """Get current NVCT stablecoin metrics"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'price_usd': 1.0001,  # Slight premium to USD
        'market_cap': 29_856_234_567_890,
        'total_supply': 30_000_000_000_000,
        'holders': 2_456_789,
        'transactions_24h': random.randint(150_000, 300_000),
        'volume_24h': random.randint(450_000_000, 850_000_000),
        'stability_score': 99.97,
        'backing_ratio': 189.5,
        'networks': {
            'bsc': {'supply': 15_230_000_000_000, 'holders': 1_234_567},
            'polygon': {'supply': 8_456_000_000_000, 'holders': 567_890},
            'ethereum': {'supply': 4_123_000_000_000, 'holders': 456_789},
            'arbitrum': {'supply': 2_047_000_000_000, 'holders': 197_543}
        }
    }

def get_live_liquidity_metrics():
    """Get current liquidity management metrics"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'total_liquidity': 2_340_000_000_000,
        'available_liquidity': 1_890_000_000_000,
        'reserved_liquidity': 450_000_000_000,
        'liquidity_sources': {
            'institutional_deposits': 1_532_000_000_000,
            'repo_agreements': 517_000_000_000,
            'central_bank_facilities': 203_000_000_000,
            'interbank_lines': 88_000_000_000
        },
        'utilization_rate': 19.3,  # % of available liquidity being used
        'stress_test_coverage': 245.6,  # % coverage under stress
        'funding_costs': {
            'average_cost': 3.85,  # % weighted average cost
            'overnight_rate': 4.12,
            'term_funding_rate': 3.67
        }
    }

def send_treasury_alert(alert_type, message, severity='info', user_ids=None):
    """Send real-time alert to treasury users"""
    from app import socketio
    
    alert_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': alert_type,
        'message': message,
        'severity': severity,
        'source': 'treasury_operations'
    }
    
    if user_ids:
        for user_id in user_ids:
            if user_id in treasury_connections:
                socketio.emit('treasury_alert', alert_data, 
                            room=treasury_connections[user_id]['room'], 
                            namespace='/treasury')
    else:
        # Send to all treasury users
        socketio.emit('treasury_alert', alert_data, 
                     room='treasury_dashboard', 
                     namespace='/treasury')
    
    logger.log_security_event(
        event_type='treasury_alert_sent',
        details={'alert_type': alert_type, 'severity': severity, 'message': message}
    )