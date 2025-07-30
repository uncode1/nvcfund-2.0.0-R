"""
Exchange Module Routes
NVC Banking Platform - Complete Exchange Operations

Integrates legacy exchange functionality into modular architecture:
- Internal exchange operations 
- Fiat to digital asset conversion
- Cross-chain asset swaps
- Integration with Binance external exchange
- Liquidity pool management
- Real-time exchange rates
"""

from datetime import datetime, timedelta
from decimal import Decimal
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import logging

from modules.core.extensions import db
from modules.banking.models import BankAccount, DigitalAssetAccount
from .models import ExchangeRate, ExchangeTransaction, ExchangeType, ExchangeStatus, ExchangeProvider, LiquidityPool, ExchangeAlert
from modules.core.security_enforcement import secure_banking_route, treasury_secure_route, admin_secure_route
from modules.core.rbac import has_permission, require_permission
from modules.services.integrations.blockchain.services import BlockchainIntegrationService
from .services import ExchangeService

logger = logging.getLogger(__name__)

# Create blueprint with unique name
exchange_bp = Blueprint('exchange', __name__, url_prefix='/exchange')

@exchange_bp.route('/')
@exchange_bp.route('/dashboard') 
@login_required
def exchange_dashboard():
    """Main exchange dashboard with internal and external exchange options"""
    try:
        service = ExchangeService()
        blockchain_service = BlockchainIntegrationService()
        
        # Get user's accounts
        fiat_accounts = BankAccount.query.filter_by(user_id=current_user.id, status='ACTIVE').all()
        digital_accounts = DigitalAssetAccount.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        # Get current exchange rates (internal)
        internal_rates = service.get_current_rates()
        
        # Get Binance rates (external) if available
        external_rates = []
        try:
            if blockchain_service.is_authenticated():
                external_rates = blockchain_service.get_ticker_prices()
        except Exception as e:
            logger.warning(f"Binance rates unavailable: {e}")
        
        # Get recent exchange transactions
        recent_exchanges = service.get_user_exchange_history(current_user.id, limit=10)
        
        # Get liquidity pool status
        liquidity_status = service.get_liquidity_pool_status()
        
        return render_template('exchange/dashboard.html',
                             fiat_accounts=fiat_accounts,
                             digital_accounts=digital_accounts,
                             internal_rates=internal_rates,
                             external_rates=external_rates,
                             recent_exchanges=recent_exchanges,
                             liquidity_status=liquidity_status,
                             binance_connected=blockchain_service.is_authenticated())
                             
    except Exception as e:
        logger.error(f"Error loading exchange dashboard: {e}")
        flash('Error loading exchange dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@exchange_bp.route('/internal')
@login_required
def internal_exchange():
    """Internal exchange interface for NVC platform assets"""
    try:
        service = ExchangeService()
        
        # Get user's accounts
        fiat_accounts = BankAccount.query.filter_by(user_id=current_user.id, status='ACTIVE').all()
        digital_accounts = DigitalAssetAccount.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        # Get supported exchange pairs
        supported_pairs = service.get_supported_exchange_pairs()
        
        # Get current rates
        current_rates = service.get_current_rates()
        
        return render_template('exchange/internal_exchange.html',
                             fiat_accounts=fiat_accounts,
                             digital_accounts=digital_accounts,
                             supported_pairs=supported_pairs,
                             current_rates=current_rates)
                             
    except Exception as e:
        logger.error(f"Error loading internal exchange: {e}")
        flash('Error loading internal exchange interface', 'error')
        return redirect(url_for('exchange_module.exchange_dashboard'))

@exchange_bp.route('/external')
@secure_banking_route()
@login_required
def external_exchange():
    """External exchange interface via Binance integration"""
    try:
        blockchain_service = BlockchainIntegrationService()
        
        if not blockchain_service.is_authenticated():
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance_integration.connect'))
        
        # Get Binance account info
        account_info = blockchain_service.get_account_info()
        
        # Get available trading pairs
        trading_pairs = blockchain_service.get_trading_pairs()
        
        # Get ticker prices
        ticker_prices = blockchain_service.get_ticker_prices()
        
        return render_template('exchange/external_exchange.html',
                             account_info=account_info,
                             trading_pairs=trading_pairs,
                             ticker_prices=ticker_prices)
                             
    except Exception as e:
        logger.error(f"Error loading external exchange: {e}")
        flash('Error loading external exchange interface', 'error')
        return redirect(url_for('exchange_module.exchange_dashboard'))

@exchange_bp.route('/quote', methods=['POST'])
@secure_banking_route()
@login_required
def get_exchange_quote():
    """Get real-time exchange quote for internal or external exchange"""
    try:
        data = request.get_json()
        exchange_type = data.get('exchange_type', 'internal')  # internal or external
        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')
        amount = Decimal(str(data.get('amount', 0)))
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
        
        service = ExchangeService()
        
        if exchange_type == 'internal':
            quote = service.get_internal_quote(from_currency, to_currency, amount)
        elif exchange_type == 'external':
            blockchain_service = BlockchainIntegrationService()
            if not blockchain_service.is_authenticated():
                return jsonify({'error': 'External exchange not connected'}), 400
            quote = service.get_external_quote(from_currency, to_currency, amount, blockchain_service)
        else:
            return jsonify({'error': 'Invalid exchange type'}), 400
        
        if not quote:
            return jsonify({'error': 'Unable to get quote'}), 404
        
        return jsonify(quote), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid amount format'}), 400
    except Exception as e:
        logger.error(f"Error getting exchange quote: {e}")
        return jsonify({'error': 'Unable to get quote'}), 500

@exchange_bp.route('/execute', methods=['POST'])
@secure_banking_route()
@login_required
def execute_exchange():
    """Execute exchange transaction (internal or external)"""
    try:
        data = request.get_json()
        exchange_type = data.get('exchange_type', 'internal')
        
        service = ExchangeService()
        
        if exchange_type == 'internal':
            result = service.execute_internal_exchange(current_user.id, data)
        elif exchange_type == 'external':
            blockchain_service = BlockchainIntegrationService()
            if not blockchain_service.is_authenticated():
                return jsonify({'error': 'External exchange not connected'}), 400
            result = service.execute_external_exchange(current_user.id, data, blockchain_service)
        else:
            return jsonify({'error': 'Invalid exchange type'}), 400
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error executing exchange: {e}")
        return jsonify({'error': 'Exchange execution failed'}), 500

@exchange_bp.route('/history')
@login_required
def exchange_history():
    """Exchange transaction history"""
    try:
        service = ExchangeService()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get filter parameters
        exchange_type = request.args.get('type')  # internal, external, all
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Get exchange history
        history = service.get_user_exchange_history(
            current_user.id,
            page=page,
            per_page=per_page,
            exchange_type=exchange_type,
            from_date=from_date,
            to_date=to_date
        )
        
        return render_template('exchange/history.html',
                             exchange_history=history,
                             pagination_data={
                                 'page': page,
                                 'per_page': per_page,
                                 'total': history['total'],
                                 'pages': history['pages']
                             })
                             
    except Exception as e:
        logger.error(f"Error loading exchange history: {e}")
        flash('Error loading exchange history', 'error')
        return redirect(url_for('exchange_module.exchange_dashboard'))

@exchange_bp.route('/rates')
@secure_banking_route()
@login_required
def current_rates():
    """Current exchange rates (internal and external)"""
    try:
        service = ExchangeService()
        blockchain_service = BlockchainIntegrationService()
        
        # Get internal rates
        internal_rates = service.get_current_rates()
        
        # Get external rates
        external_rates = []
        if blockchain_service.is_authenticated():
            try:
                external_rates = blockchain_service.get_ticker_prices()
            except Exception as e:
                logger.warning(f"Could not fetch external rates: {e}")
        
        return render_template('exchange/rates.html',
                             internal_rates=internal_rates,
                             external_rates=external_rates,
                             binance_connected=blockchain_service.is_authenticated())
                             
    except Exception as e:
        logger.error(f"Error loading exchange rates: {e}")
        flash('Error loading exchange rates', 'error')
        return redirect(url_for('exchange_module.exchange_dashboard'))

# Admin routes for exchange management
@exchange_bp.route('/admin')
@admin_secure_route()
@require_permission('admin:exchange_management')
def admin_dashboard():
    """Admin dashboard for exchange operations"""
    try:
        service = ExchangeService()
        
        # Get exchange statistics
        stats = service.get_exchange_statistics()
        
        # Get liquidity pool status
        liquidity_pools = service.get_all_liquidity_pools()
        
        # Get recent transactions for monitoring
        recent_transactions = service.get_recent_exchange_transactions(limit=50)
        
        # Get rate management data
        rate_providers = service.get_rate_providers_status()
        
        return render_template('exchange/admin_dashboard.html',
                             exchange_stats=stats,
                             liquidity_pools=liquidity_pools,
                             recent_transactions=recent_transactions,
                             rate_providers=rate_providers)
                             
    except Exception as e:
        logger.error(f"Error loading exchange admin dashboard: {e}")
        flash('Error loading admin dashboard', 'error')
        return redirect(url_for('admin_management.dashboard'))

@exchange_bp.route('/admin/liquidity')
@admin_secure_route()
@require_permission('admin:liquidity_management')
def admin_liquidity():
    """Admin liquidity pool management"""
    try:
        service = ExchangeService()
        
        # Get all liquidity pools
        liquidity_pools = service.get_all_liquidity_pools()
        
        # Get liquidity analytics
        liquidity_analytics = service.get_liquidity_analytics()
        
        return render_template('exchange/admin_liquidity.html',
                             liquidity_pools=liquidity_pools,
                             liquidity_analytics=liquidity_analytics)
                             
    except Exception as e:
        logger.error(f"Error loading liquidity management: {e}")
        flash('Error loading liquidity management', 'error')
        return redirect(url_for('exchange_module.admin_dashboard'))

@exchange_bp.route('/admin/rates')
@admin_secure_route()
@require_permission('admin:rate_management')
def admin_rates():
    """Admin exchange rate management"""
    try:
        service = ExchangeService()
        
        # Get rate management data
        current_rates = service.get_current_rates()
        rate_history = service.get_rate_history()
        rate_providers = service.get_rate_providers_status()
        
        return render_template('exchange/admin_rates.html',
                             current_rates=current_rates,
                             rate_history=rate_history,
                             rate_providers=rate_providers)
                             
    except Exception as e:
        logger.error(f"Error loading rate management: {e}")
        flash('Error loading rate management', 'error')
        return redirect(url_for('exchange_module.admin_dashboard'))

# API endpoints for AJAX and mobile integration
@exchange_bp.route('/api/supported-pairs')
@secure_banking_route()
@login_required
def api_supported_pairs():
    """Get supported exchange pairs"""
    try:
        service = ExchangeService()
        pairs = service.get_supported_exchange_pairs()
        return jsonify(pairs)
    except Exception as e:
        logger.error(f"Error getting supported pairs: {e}")
        return jsonify({'error': 'Unable to get supported pairs'}), 500

@exchange_bp.route('/api/liquidity/<currency>')
@secure_banking_route()
@login_required
def api_liquidity_status(currency):
    """Get liquidity status for specific currency"""
    try:
        service = ExchangeService()
        status = service.get_currency_liquidity_status(currency)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting liquidity status: {e}")
        return jsonify({'error': 'Unable to get liquidity status'}), 500

@exchange_bp.route('/orders')
@login_required
def orders():
    """Exchange orders management page"""
    try:
        service = ExchangeService()
        user_orders = service.get_user_orders(current_user.id) if hasattr(service, 'get_user_orders') else []
        
        return render_template('exchange/orders.html',
                             user_orders=user_orders,
                             user=current_user,
                             page_title='Exchange Orders')
    except Exception as e:
        logger.error(f"Error loading orders: {e}")
        flash('Error loading orders', 'error')
        return redirect(url_for('exchange.exchange_dashboard'))

@exchange_bp.route('/settings')
@login_required
def settings():
    """Exchange settings and preferences"""
    try:
        service = ExchangeService()
        user_settings = service.get_user_exchange_settings(current_user.id) if hasattr(service, 'get_user_exchange_settings') else {}
        
        return render_template('exchange/settings.html',
                             user_settings=user_settings,
                             user=current_user,
                             page_title='Exchange Settings')
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        flash('Error loading settings', 'error')
        return redirect(url_for('exchange.exchange_dashboard'))

@exchange_bp.route('/markets')
@login_required
def markets():
    """Exchange markets and trading pairs"""
    try:
        service = ExchangeService()
        blockchain_service = BlockchainIntegrationService()
        
        # Get supported trading pairs and market data
        supported_pairs = service.get_supported_trading_pairs() if hasattr(service, 'get_supported_trading_pairs') else []
        market_data = {}
        
        return render_template('exchange/markets.html',
                             supported_pairs=supported_pairs,
                             market_data=market_data,
                             user=current_user,
                             page_title='Exchange Markets')
    except Exception as e:
        logger.error(f"Error loading markets: {e}")
        flash('Error loading markets', 'error')
        return redirect(url_for('exchange.exchange_dashboard'))

@exchange_bp.route('/api/health')
def api_health():
    """Exchange module health check"""
    try:
        service = ExchangeService()
        health_data = service.get_health_status()
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"Exchange module health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

# Missing route aliases referenced in templates
@exchange_bp.route('/history-alias')
@login_required
def history():
    """Exchange history - alias for exchange_history"""
    return exchange_history()