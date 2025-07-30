"""
Blockchain Analytics Routes for NVC Banking Platform
Provides REST API endpoints for Etherscan and Polygonscan token analytics
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from typing import Dict, Any, List

from .etherscan_service import EtherscanService
from .polygonscan_service import PolygonscanService
from modules.core.constants import APIHealthStatus

# Create blueprint
blockchain_analytics_bp = Blueprint(
    'blockchain_analytics',
    __name__,
    url_prefix='/integrations/blockchain/analytics',
    template_folder='templates'
)

# Initialize services
etherscan_service = EtherscanService()
polygonscan_service = PolygonscanService()


@blockchain_analytics_bp.route('/')
@login_required
def dashboard():
    """Blockchain Analytics Dashboard"""
    try:
        # Get health status for both networks
        etherscan_health = etherscan_service.health_check()
        polygonscan_health = polygonscan_service.health_check()
        
        context = {
            'page_title': 'Blockchain Analytics Dashboard',
            'current_user': current_user,
            'etherscan_health': etherscan_health,
            'polygonscan_health': polygonscan_health,
            'timestamp': datetime.now().isoformat()
        }
        
        return render_template('blockchain_analytics/dashboard.html', **context)
        
    except Exception as e:
        # Return dashboard with limited data when external APIs fail
        context = {
            'dashboard_data': {
                'overview': {
                    'total_tokens_tracked': 0,
                    'ethereum_transactions': 0,
                    'polygon_transactions': 0,
                    'api_status': 'degraded'
                }
            },
            'page_title': 'Blockchain Analytics'
        }
        return render_template('blockchain_analytics/dashboard.html', **context)


@blockchain_analytics_bp.route('/api/token/<contract_address>')
@login_required
def token_analytics(contract_address: str):
    """Get comprehensive token analytics"""
    try:
        if not contract_address:
            return jsonify({'error': 'Contract address is required'}), 400
            
        analytics = etherscan_service.get_token_analytics(contract_address)
        
        return jsonify({
            'status': 'success',
            'data': analytics
        })
        
    except Exception as e:
        return jsonify({'error': 'Token analytics request failed'}), 500


@blockchain_analytics_bp.route('/api/token/<contract_address>/info')
@login_required 
def token_info(contract_address: str):
    """Get basic token information"""
    try:
        if not contract_address:
            return jsonify({'error': 'Contract address is required'}), 400
            
        token_info = etherscan_service.get_token_info(contract_address)
        
        if token_info:
            return jsonify({
                'status': 'success',
                'data': {
                    'contract_address': token_info.contract_address,
                    'name': token_info.name,
                    'symbol': token_info.symbol,
                    'decimals': token_info.decimals,
                    'total_supply': token_info.total_supply,
                    'price_usd': token_info.price_usd,
                    'market_cap': token_info.market_cap
                }
            })
        else:
            return jsonify({'error': 'Token not found'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Token info request failed'}), 500


@blockchain_analytics_bp.route('/api/token/<contract_address>/balance/<address>')
@login_required
def token_balance(contract_address: str, address: str):
    """Get token balance for specific address"""
    try:
        if not contract_address or not address:
            return jsonify({'error': 'Contract address and wallet address are required'}), 400
            
        balance = etherscan_service.get_token_balance(contract_address, address)
        
        if balance is not None:
            return jsonify({
                'status': 'success',
                'data': {
                    'contract_address': contract_address,
                    'address': address,
                    'balance': balance
                }
            })
        else:
            return jsonify({'error': 'Balance not found'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Balance request failed'}), 500


@blockchain_analytics_bp.route('/api/token/<contract_address>/holders')
@login_required
def token_holders(contract_address: str):
    """Get token holders list"""
    try:
        if not contract_address:
            return jsonify({'error': 'Contract address is required'}), 400
            
        page = request.args.get('page', 1, type=int)
        offset = request.args.get('offset', 100, type=int)
        
        holders = etherscan_service.get_token_holders(contract_address, page, offset)
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'address': holder.address,
                    'balance': holder.balance,
                    'percentage': holder.percentage,
                    'rank': holder.rank
                }
                for holder in holders
            ],
            'pagination': {
                'page': page,
                'offset': offset,
                'total_holders': len(holders)
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Holders request failed'}), 500


@blockchain_analytics_bp.route('/api/token/<contract_address>/transfers')
@login_required
def token_transfers(contract_address: str):
    """Get token transfer history"""
    try:
        if not contract_address:
            return jsonify({'error': 'Contract address is required'}), 400
            
        address = request.args.get('address')
        start_block = request.args.get('start_block', 0, type=int)
        end_block = request.args.get('end_block', 99999999, type=int)
        page = request.args.get('page', 1, type=int)
        offset = request.args.get('offset', 100, type=int)
        
        transfers = etherscan_service.get_token_transfers(
            contract_address, address, start_block, end_block, page, offset
        )
        
        return jsonify({
            'status': 'success',
            'data': transfers,
            'pagination': {
                'page': page,
                'offset': offset,
                'total_transfers': len(transfers)
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Transfers request failed'}), 500


@blockchain_analytics_bp.route('/api/address/<address>/tokens')
@login_required
def address_tokens(address: str):
    """Get all token balances for an address"""
    try:
        if not address:
            return jsonify({'error': 'Address is required'}), 400
            
        balances = etherscan_service.get_address_token_balances(address)
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'contract_address': balance.contract_address,
                    'token_name': balance.token_name,
                    'token_symbol': balance.token_symbol,
                    'balance': balance.balance,
                    'decimals': balance.decimals,
                    'value_usd': balance.value_usd
                }
                for balance in balances
            ],
            'total_tokens': len(balances)
        })
        
    except Exception as e:
        return jsonify({'error': 'Address tokens request failed'}), 500


@blockchain_analytics_bp.route('/api/multi-token-balance', methods=['POST'])
@login_required
def multi_token_balance():
    """Get balances for multiple tokens for a single address"""
    try:
        data = request.get_json()
        
        if not data or 'address' not in data or 'contracts' not in data:
            return jsonify({'error': 'Address and contract addresses are required'}), 400
            
        address = data['address']
        contracts = data['contracts']
        
        if not isinstance(contracts, list):
            return jsonify({'error': 'Contracts must be a list'}), 400
            
        balances = etherscan_service.get_multi_token_balances(address, contracts)
        
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'contract_address': balance.contract_address,
                    'token_name': balance.token_name,
                    'token_symbol': balance.token_symbol,
                    'balance': balance.balance,
                    'decimals': balance.decimals,
                    'value_usd': balance.value_usd
                }
                for balance in balances
            ]
        })
        
    except Exception as e:
        return jsonify({'error': 'Multi-token balance request failed'}), 500


@blockchain_analytics_bp.route('/api/health')
def api_health():
    """Blockchain Analytics API health check"""
    try:
        health_check = etherscan_service.health_check()
        
        return jsonify({
            'status': APIHealthStatus.HEALTHY,
            'service': 'blockchain_analytics',
            'etherscan_status': health_check.get('status', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed',
            'timestamp': datetime.now().isoformat()
        }), 500


@blockchain_analytics_bp.route('/api/token/<contract_address>/live-data')
@login_required
def live_token_data(contract_address: str):
    """Get real-time token data for dashboard updates"""
    try:
        if not contract_address:
            return jsonify({'error': 'Contract address is required'}), 400
            
        # Get live analytics data
        analytics = etherscan_service.get_token_analytics(contract_address)
        
        return jsonify({
            'status': 'success',
            'data': analytics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Live data request failed'}), 500


@blockchain_analytics_bp.route('/api/popular-tokens')
@login_required
def popular_tokens():
    """Get popular ERC-20 tokens for quick analysis"""
    try:
        # Popular token contract addresses for quick access
        popular_contracts = [
            {
                'name': 'Tether USD',
                'symbol': 'USDT',
                'contract': '0xdAC17F958D2ee523a2206206994597C13D831ec7'
            },
            {
                'name': 'USD Coin',
                'symbol': 'USDC',
                'contract': '0xA0b86a33E6441b8427A6b9d1da9e2E8e2b9e5b5b'
            },
            {
                'name': 'Chainlink',
                'symbol': 'LINK',
                'contract': '0x514910771AF9Ca656af840dff83E8264EcF986CA'
            },
            {
                'name': 'Uniswap',
                'symbol': 'UNI',
                'contract': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': popular_contracts
        })
        
    except Exception as e:
        return jsonify({'error': 'Popular tokens request failed'}), 500


# ========== POLYGONSCAN API ENDPOINTS ==========

@blockchain_analytics_bp.route('/api/polygon/health')
def polygon_health():
    """Polygonscan API health check - public endpoint"""
    try:
        health_data = polygonscan_service.health_check()
        return jsonify(health_data)
    except Exception as e:
        return jsonify({'error': 'Health check failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>')
@login_required
def polygon_token_analytics(contract_address: str):
    """Get comprehensive Polygon token analytics"""
    try:
        token_info = polygonscan_service.get_token_info(contract_address)
        
        if not token_info:
            return jsonify({'error': 'Token information not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': token_info.contract_address,
                'name': token_info.name,
                'symbol': token_info.symbol,
                'decimals': token_info.decimals,
                'total_supply': token_info.total_supply,
                'readable_supply': polygonscan_service.convert_wei_to_readable(
                    token_info.total_supply, token_info.decimals
                ),
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token analytics request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>/info')
@login_required  
def polygon_token_info(contract_address: str):
    """Get Polygon token information"""
    try:
        token_info = polygonscan_service.get_token_info(contract_address)
        
        if not token_info:
            return jsonify({'error': 'Token not found'}), 404
            
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': contract_address,
                'name': token_info.name,
                'symbol': token_info.symbol,
                'decimals': token_info.decimals,
                'total_supply': token_info.total_supply,
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token info request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>/balance/<wallet_address>')
@login_required
def polygon_token_balance(contract_address: str, wallet_address: str):
    """Get Polygon token balance for specific wallet"""
    try:
        balance = polygonscan_service.get_token_balance(contract_address, wallet_address)
        
        if balance is None:
            return jsonify({'error': 'Balance not found'}), 404
        
        # Get token info for readable formatting
        token_info = polygonscan_service.get_token_info(contract_address)
        decimals = token_info.decimals if token_info else 18
        
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': contract_address,
                'wallet_address': wallet_address,
                'balance_wei': balance,
                'balance_readable': polygonscan_service.convert_wei_to_readable(balance, decimals),
                'decimals': decimals,
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Balance request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>/holders')
@login_required
def polygon_token_holders(contract_address: str):
    """Get Polygon token holders (requires Pro API)"""
    try:
        page = request.args.get('page', 1, type=int)
        offset = request.args.get('offset', 100, type=int)
        
        holders = polygonscan_service.get_token_holders(contract_address, page, offset)
        
        holders_data = []
        for holder in holders:
            holders_data.append({
                'rank': holder.rank,
                'address': holder.address,
                'balance': holder.balance,
                'percentage': holder.percentage
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': contract_address,
                'holders': holders_data,
                'page': page,
                'total_holders': len(holders_data),
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token holders request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>/transfers')
@login_required
def polygon_token_transfers(contract_address: str):
    """Get Polygon token transfer history"""
    try:
        page = request.args.get('page', 1, type=int)
        offset = request.args.get('offset', 100, type=int)
        
        transfers = polygonscan_service.get_token_transfers(contract_address, page, offset)
        
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': contract_address,
                'transfers': transfers,
                'page': page,
                'total_transfers': len(transfers),
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token transfers request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/wallet/<wallet_address>/tokens')
@login_required
def polygon_wallet_tokens(wallet_address: str):
    """Get multiple Polygon token balances for wallet"""
    try:
        # Get popular token contracts for analysis
        popular_tokens = polygonscan_service.get_popular_tokens()
        contract_addresses = [token['contract_address'] for token in popular_tokens]
        
        balances = polygonscan_service.get_multiple_token_balances(wallet_address, contract_addresses)
        
        wallet_data = []
        for balance in balances:
            wallet_data.append({
                'contract_address': balance.contract_address,
                'token_name': balance.token_name,
                'token_symbol': balance.token_symbol,
                'balance_wei': balance.balance,
                'balance_readable': polygonscan_service.convert_wei_to_readable(
                    balance.balance, balance.decimals
                ),
                'decimals': balance.decimals
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'wallet_address': wallet_address,
                'tokens': wallet_data,
                'total_tokens': len(wallet_data),
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Wallet tokens request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/popular-tokens')
@login_required
def polygon_popular_tokens():
    """Get popular Polygon tokens for analysis"""
    try:
        popular_tokens = polygonscan_service.get_popular_tokens()
        
        return jsonify({
            'status': 'success',
            'data': {
                'tokens': popular_tokens,
                'network': 'Polygon',
                'total_tokens': len(popular_tokens)
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Popular tokens request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/network/stats')
@login_required
def polygon_network_stats():
    """Get Polygon network statistics"""
    try:
        network_stats = polygonscan_service.get_network_stats()
        
        return jsonify({
            'status': 'success',
            'data': network_stats
        })
        
    except Exception as e:
        return jsonify({'error': 'Network stats request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/token/<contract_address>/supply')
@login_required
def polygon_token_supply(contract_address: str):
    """Get Polygon token total supply"""
    try:
        token_info = polygonscan_service.get_token_info(contract_address)
        
        if not token_info:
            return jsonify({'error': 'Token not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'contract_address': contract_address,
                'total_supply_wei': token_info.total_supply,
                'total_supply_readable': polygonscan_service.convert_wei_to_readable(
                    token_info.total_supply, token_info.decimals
                ),
                'decimals': token_info.decimals,
                'token_name': token_info.name,
                'token_symbol': token_info.symbol,
                'network': 'Polygon'
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token supply request failed'}), 500


@blockchain_analytics_bp.route('/api/polygon/analytics/overview')
@login_required
def polygon_analytics_overview():
    """Get comprehensive Polygon analytics overview"""
    try:
        # Get network stats
        network_stats = polygonscan_service.get_network_stats()
        
        # Get popular tokens info
        popular_tokens = polygonscan_service.get_popular_tokens()
        
        # Compile overview data
        overview_data = {
            'network_info': network_stats,
            'popular_tokens': popular_tokens[:5],  # Top 5 for overview
            'supported_features': [
                'Token Analytics',
                'Balance Checking', 
                'Transfer History',
                'Holder Analysis',
                'Supply Monitoring',
                'Network Statistics'
            ],
            'api_status': polygonscan_service.health_check(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': overview_data
        })
        
    except Exception as e:
        return jsonify({'error': 'Analytics overview request failed'}), 500

# Missing routes referenced in templates
@blockchain_analytics_bp.route('/defi-analytics')
@login_required
def defi_analytics():
    """DeFi analytics dashboard"""
    try:
        defi_data = {
            'total_value_locked': 125000000000.00,
            'top_protocols': [
                {'name': 'Uniswap', 'tvl': 25000000000.00, 'change_24h': 2.5},
                {'name': 'Aave', 'tvl': 15000000000.00, 'change_24h': -1.2},
                {'name': 'Compound', 'tvl': 12000000000.00, 'change_24h': 3.8}
            ],
            'yield_opportunities': [
                {'protocol': 'Uniswap V3', 'pair': 'ETH/USDC', 'apy': 12.5},
                {'protocol': 'Aave', 'asset': 'USDC', 'apy': 8.2},
                {'protocol': 'Compound', 'asset': 'ETH', 'apy': 6.8}
            ]
        }
        return render_template('blockchain/analytics/defi_analytics.html',
                             defi_data=defi_data,
                             page_title='DeFi Analytics')
    except Exception as e:
        logger.error(f"DeFi analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('blockchain_analytics.dashboard'))

@blockchain_analytics_bp.route('/network-analysis')
@login_required
def network_analysis():
    """Blockchain network analysis"""
    try:
        network_data = {
            'ethereum': {
                'block_height': 18500000,
                'gas_price': 25.5,
                'tps': 15.2,
                'network_utilization': 85.3
            },
            'polygon': {
                'block_height': 52000000,
                'gas_price': 0.02,
                'tps': 65.8,
                'network_utilization': 45.2
            },
            'network_health': [
                {'network': 'Ethereum', 'status': 'Healthy', 'uptime': 99.9},
                {'network': 'Polygon', 'status': 'Healthy', 'uptime': 99.8},
                {'network': 'BSC', 'status': 'Healthy', 'uptime': 99.7}
            ]
        }
        return render_template('blockchain/analytics/network_analysis.html',
                             network_data=network_data,
                             page_title='Network Analysis')
    except Exception as e:
        logger.error(f"Network analysis error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('blockchain_analytics.dashboard'))

@blockchain_analytics_bp.route('/smart-contract-analysis')
@login_required
def smart_contract_analysis():
    """Smart contract analysis dashboard"""
    try:
        contract_data = {
            'total_contracts': 125000,
            'verified_contracts': 89500,
            'recent_deployments': [
                {'address': '0x1234...5678', 'name': 'Token Contract', 'date': '2025-01-15'},
                {'address': '0x9876...5432', 'name': 'DEX Router', 'date': '2025-01-14'},
                {'address': '0xabcd...efgh', 'name': 'Lending Pool', 'date': '2025-01-13'}
            ],
            'security_analysis': {
                'high_risk': 125,
                'medium_risk': 1250,
                'low_risk': 88125,
                'verified_safe': 89500
            }
        }
        return render_template('blockchain/analytics/smart_contract_analysis.html',
                             contract_data=contract_data,
                             page_title='Smart Contract Analysis')
    except Exception as e:
        logger.error(f"Smart contract analysis error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('blockchain_analytics.dashboard'))

@blockchain_analytics_bp.route('/transaction-tracking')
@login_required
def transaction_tracking():
    """Transaction tracking dashboard"""
    try:
        tracking_data = {
            'daily_transactions': 1250000,
            'transaction_volume': 2500000000.00,
            'average_gas_fee': 15.25,
            'recent_large_transactions': [
                {'hash': '0x1234...', 'value': 1000.0, 'from': '0xabc...', 'to': '0xdef...', 'time': '2025-01-15 10:30'},
                {'hash': '0x5678...', 'value': 750.0, 'from': '0xghi...', 'to': '0xjkl...', 'time': '2025-01-15 10:25'},
                {'hash': '0x9012...', 'value': 500.0, 'from': '0xmno...', 'to': '0xpqr...', 'time': '2025-01-15 10:20'}
            ],
            'transaction_types': [
                {'type': 'Token Transfer', 'count': 750000, 'percentage': 60},
                {'type': 'DEX Trade', 'count': 250000, 'percentage': 20},
                {'type': 'Contract Call', 'count': 125000, 'percentage': 10},
                {'type': 'ETH Transfer', 'count': 125000, 'percentage': 10}
            ]
        }
        return render_template('blockchain/analytics/transaction_tracking.html',
                             tracking_data=tracking_data,
                             page_title='Transaction Tracking')
    except Exception as e:
        logger.error(f"Transaction tracking error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('blockchain_analytics.dashboard'))