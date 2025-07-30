"""
Binance Integration Module Routes
OAuth 2.0 authentication and API integration with Binance
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
import logging
from urllib.parse import urlparse, parse_qs
import json
from datetime import datetime

# Import services
from .services import BinanceOAuthService, BinanceAPIService, BinanceIntegrationService

# Create blueprint with hyphenated URL for professional banking appearance
binance_bp = Blueprint(
    'binance_integration',
    __name__,
    url_prefix='/binance-integration',
    template_folder='templates',
    static_folder='static'
)

logger = logging.getLogger(__name__)

@binance_bp.route('/')
@login_required
def binance_dashboard():
    """Cryptocurrency Trading Dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing cryptocurrency trading dashboard")
        
        service = BinanceIntegrationService()
        dashboard_data = service.get_dashboard_data()
        
        return render_template(
            'binance_integration/binance_dashboard.html',
            dashboard_data=dashboard_data,
            page_title="Cryptocurrency Trading"
        )
    except Exception as e:
        logger.error(f"Error loading Binance dashboard: {e}")
        flash('Error loading cryptocurrency trading dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@binance_bp.route('/connect')
@login_required
def connect_binance():
    """Connect Trading Account"""
    try:
        logger.info(f"User {current_user.username} connecting trading account")
        
        # Get requested scopes from form or use defaults
        scopes = request.args.getlist('scopes') or ['user:openId', 'user:email']
        
        oauth_service = BinanceOAuthService()
        auth_data = oauth_service.generate_authorization_url(scopes)
        
        # Store OAuth data in session for verification
        session['binance_oauth_state'] = auth_data['state']
        session['binance_code_verifier'] = auth_data['code_verifier']
        session['binance_scopes_requested'] = auth_data['scopes_requested']
        
        logger.info(f"Redirecting user {current_user.username} to Binance OAuth: {auth_data['authorization_url']}")
        
        return redirect(auth_data['authorization_url'])
        
    except Exception as e:
        logger.error(f"Error initiating Binance OAuth: {e}")
        flash(f'Error connecting trading account: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/callback')
@login_required
def oauth_callback():
    """Handle Trading Account Connection"""
    try:
        logger.info(f"Processing trading account connection for user {current_user.username}")
        
        # Get authorization code and state from callback
        authorization_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        # Handle OAuth errors
        if error:
            logger.error(f"OAuth error: {error}")
            flash(f'Binance authorization failed: {error}', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        if not authorization_code:
            logger.error("No authorization code received")
            flash('No authorization code received from Binance', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        # Verify state parameter for CSRF protection
        stored_state = session.get('binance_oauth_state')
        if not state or state != stored_state:
            logger.error(f"State mismatch: received {state}, expected {stored_state}")
            flash('Invalid state parameter - potential CSRF attack', 'error')
            return redirect(url_for('binance.binance_dashboard'))
        
        # Exchange code for tokens
        oauth_service = BinanceOAuthService()
        code_verifier = session.get('binance_code_verifier')
        
        token_response = oauth_service.exchange_code_for_tokens(
            authorization_code, 
            code_verifier
        )
        
        # Validate the received tokens
        api_service = BinanceAPIService()
        validation_result = api_service.validate_token(token_response['access_token'])
        
        if validation_result['valid']:
            # Store tokens securely (in production, use encrypted storage)
            session['binance_access_token'] = token_response['access_token']
            session['binance_refresh_token'] = token_response.get('refresh_token')
            session['binance_token_expires_at'] = token_response['expires_at']
            session['binance_user_id'] = validation_result['user_id']
            session['binance_email'] = validation_result.get('email')
            
            # Clear OAuth session data
            session.pop('binance_oauth_state', None)
            session.pop('binance_code_verifier', None)
            
            logger.info(f"Successfully connected Binance account for user {current_user.username}")
            flash('Successfully connected to Binance!', 'success')
        else:
            logger.error(f"Token validation failed: {validation_result.get('error')}")
            flash('Failed to validate Binance connection', 'error')
        
        return redirect(url_for('binance.binance_dashboard'))
        
    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        flash(f'Error processing Binance connection: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect_binance():
    """Disconnect Trading Account"""
    try:
        logger.info(f"User {current_user.username} disconnecting Binance account")
        
        access_token = session.get('binance_access_token')
        
        if access_token:
            # Revoke access token
            oauth_service = BinanceOAuthService()
            revocation_success = oauth_service.revoke_access_token(access_token)
            
            if revocation_success:
                logger.info("Successfully revoked Binance access token")
            else:
                logger.warning("Failed to revoke Binance access token on server")
        
        # Clear all Binance session data
        binance_keys = [key for key in session.keys() if key.startswith('binance_')]
        for key in binance_keys:
            session.pop(key, None)
        
        flash('Binance account disconnected successfully', 'success')
        
        return redirect(url_for('binance.binance_dashboard'))
        
    except Exception as e:
        logger.error(f"Error disconnecting Binance: {e}")
        flash(f'Error disconnecting Binance: {str(e)}', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/account-info')
@login_required
def get_account_info():
    """Get Trading Account Information"""
    try:
        api_service = BinanceAPIService()
        account_info = api_service.get_account_info()
        
        return jsonify(account_info)
        
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/live-prices')
def get_live_prices():
    """Get live market prices (public endpoint for testing)"""
    try:
        api_service = BinanceAPIService()
        prices = api_service.get_ticker_prices()
        
        return jsonify(prices)
        
    except Exception as e:
        logger.error(f"Error getting live prices: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/price/<symbol>')
@login_required
def get_symbol_price(symbol):
    """Get price for a specific symbol"""
    try:
        api_service = BinanceAPIService()
        price = api_service.get_symbol_price(symbol.upper())
        
        return jsonify(price)
        
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/exchange-info')
def get_exchange_info():
    """Get exchange information and trading rules"""
    try:
        api_service = BinanceAPIService()
        exchange_info = api_service.get_exchange_info()
        return jsonify(exchange_info)
    except Exception as e:
        logger.error(f"Error getting exchange info: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@binance_bp.route('/order-book/<symbol>')
def get_order_book(symbol):
    """Get order book for a specific symbol"""
    try:
        limit = request.args.get('limit', 20, type=int)
        api_service = BinanceAPIService()
        order_book = api_service.get_order_book(symbol.upper(), limit)
        return jsonify(order_book)
    except Exception as e:
        logger.error(f"Error getting order book for {symbol}: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@binance_bp.route('/trades/<symbol>')
def get_recent_trades_route(symbol):
    """Get recent trades for a specific symbol"""
    try:
        limit = request.args.get('limit', 20, type=int)
        api_service = BinanceAPIService()
        trades = api_service.get_recent_trades(symbol.upper(), limit)
        return jsonify(trades)
    except Exception as e:
        logger.error(f"Error getting recent trades for {symbol}: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@binance_bp.route('/klines/<symbol>')
def get_kline_data_route(symbol):
    """Get kline/candlestick data for a specific symbol"""
    try:
        interval = request.args.get('interval', '1h')
        limit = request.args.get('limit', 24, type=int)
        api_service = BinanceAPIService()
        klines = api_service.get_kline_data(symbol.upper(), interval, limit)
        return jsonify(klines)
    except Exception as e:
        logger.error(f"Error getting kline data for {symbol}: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@binance_bp.route('/market-data')
def market_data_dashboard():
    """Comprehensive market data dashboard"""
    try:
        api_service = BinanceAPIService()
        
        # Get top cryptocurrencies
        prices = api_service.get_ticker_prices()
        
        # Get exchange info
        exchange_info = api_service.get_exchange_info()
        
        return render_template(
            'binance_integration/market_data.html',
            prices=prices,
            exchange_info=exchange_info,
            page_title="Market Data Dashboard"
        )
    except Exception as e:
        logger.error(f"Error loading market data dashboard: {e}")
        flash('Error loading market data dashboard', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/advanced-trading')
def advanced_trading():
    """Advanced trading interface with charts and order book"""
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        api_service = BinanceAPIService()
        
        # Get current price
        price_data = api_service.get_symbol_price(symbol)
        
        # Get order book
        order_book = api_service.get_order_book(symbol)
        
        # Get recent trades
        trades = api_service.get_recent_trades(symbol)
        
        # Get kline data for chart
        klines = api_service.get_kline_data(symbol, '1h', 24)
        
        return render_template(
            'binance_integration/advanced_trading.html',
            symbol=symbol,
            price_data=price_data,
            order_book=order_book,
            trades=trades,
            klines=klines,
            page_title=f"Advanced Trading - {symbol}"
        )
    except Exception as e:
        logger.error(f"Error loading advanced trading interface: {e}")
        flash('Error loading trading interface', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/portfolio-analytics')
@login_required
def portfolio_analytics():
    """Portfolio analytics and performance tracking"""
    try:
        api_service = BinanceAPIService()
        
        # Get account info if available
        account_info = api_service.get_account_info()
        
        # Get top market data for comparison
        market_data = api_service.get_ticker_prices()
        
        return render_template(
            'binance_integration/portfolio_analytics.html',
            account_info=account_info,
            market_data=market_data,
            page_title="Portfolio Analytics"
        )
    except Exception as e:
        logger.error(f"Error loading portfolio analytics: {e}")
        flash('Error loading portfolio analytics', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/trading-interface')
@login_required
def trading_interface():
    """Professional trading interface with real-time price charts and order management"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        trading_data = api_service.get_trading_data(access_token)
        
        return render_template('binance_integration/trading_interface.html',
                             trading_data=trading_data,
                             page_title='Trading Interface')
        
    except Exception as e:
        logger.error(f"Error loading trading interface: {e}")
        flash('Error loading trading interface', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/api-settings')
@login_required
def api_settings():
    """API settings management with security controls and permission management"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        api_settings_data = api_service.get_api_settings(access_token)
        
        return render_template('binance_integration/api_settings.html',
                             api_settings=api_settings_data,
                             page_title='API Settings')
        
    except Exception as e:
        logger.error(f"Error loading API settings: {e}")
        flash('Error loading API settings', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/main-dashboard')
@login_required
def binance_main_dashboard():
    """Main Binance dashboard using orphaned template"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            flash('Please connect your Binance account first', 'warning')
            return redirect(url_for('binance.binance_dashboard'))
            
        api_service = BinanceAPIService()
        dashboard_data = api_service.get_dashboard_data(access_token)
        
        return render_template('binance_dashboard.html',
                             dashboard_data=dashboard_data,
                             page_title='Binance Main Dashboard',
                             user=current_user)
        
    except Exception as e:
        logger.error(f"Error loading main dashboard: {e}")
        flash('Error loading main dashboard', 'error')
        return redirect(url_for('binance.binance_dashboard'))

@binance_bp.route('/connection-status')
@login_required
def connection_status():
    """Get Binance connection status"""
    try:
        access_token = session.get('binance_access_token')
        
        if not access_token:
            return jsonify({
                'connected': False,
                'status': 'not_connected'
            })
        
        # Validate current token
        api_service = BinanceAPIService()
        validation_result = api_service.validate_token(access_token)
        
        if validation_result['valid']:
            return jsonify({
                'connected': True,
                'status': 'connected',
                'user_id': validation_result['user_id'],
                'email': validation_result.get('email'),
                'token_expires_at': session.get('binance_token_expires_at'),
                'validated_at': validation_result['validated_at']
            })
        else:
            # Token is invalid, clear session
            binance_keys = [key for key in session.keys() if key.startswith('binance_')]
            for key in binance_keys:
                session.pop(key, None)
            
            return jsonify({
                'connected': False,
                'status': 'token_invalid',
                'error': validation_result.get('error')
            })
        
    except Exception as e:
        logger.error(f"Error checking connection status: {e}")
        return jsonify({
            'connected': False,
            'status': 'error',
            'error': str(e)
        }), 500

# API Routes
@binance_bp.route('/api/integration-status')
@login_required
def api_integration_status():
    """API endpoint for integration status"""
    try:
        service = BinanceIntegrationService()
        status = service.get_integration_status()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/api/market-overview')
@login_required
def api_market_overview():
    """API endpoint for market overview data (fallback for WebSocket)"""
    try:
        from .services import BinanceIntegrationService
        service = BinanceIntegrationService()
        
        # Get real-time market data
        market_data = service.get_market_data()
        
        return jsonify({
            'status': 'success',
            'market_data': market_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/api/refresh-token', methods=['POST'])
@login_required
def api_refresh_token():
    """Refresh Binance access token"""
    try:
        refresh_token = session.get('binance_refresh_token')
        
        if not refresh_token:
            return jsonify({
                'status': 'error',
                'error': 'No refresh token available'
            }), 401
        
        oauth_service = BinanceOAuthService()
        token_response = oauth_service.refresh_access_token(refresh_token)
        
        # Update session with new tokens
        session['binance_access_token'] = token_response['access_token']
        session['binance_refresh_token'] = token_response.get('refresh_token', refresh_token)
        session['binance_token_expires_at'] = token_response['expires_at']
        
        return jsonify({
            'status': 'success',
            'message': 'Token refreshed successfully',
            'expires_at': token_response['expires_at']
        })
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@binance_bp.route('/api/health')
def health_check():
    """Binance integration module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'binance_integration',
        'version': '1.0.0',
        'timestamp': '2025-07-03T17:30:00Z',
        'oauth_endpoints': {
            'authorization': 'https://accounts.binance.com/en/oauth/authorize',
            'token': 'https://accounts.binance.com/oauth/token',
            'api': 'https://www.binanceapis.com/oauth-api/v1'
        }
    })

# Additional health endpoints can be added here if needed

# Error handlers
@binance_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within Binance integration module"""
    return render_template('404.html'), 404

@binance_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within Binance integration module"""
    logger.error(f"Internal error in Binance integration module: {error}")
    return render_template('500.html'), 500

# API Health endpoint
@binance_bp.route('/api/health', methods=['GET'])
def api_health_check():
    """API health check endpoint for Binance Integration module"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'binance_integration',
            'version': '1.0.0',
            'services': {
                'oauth': 'available',
                'api': 'available'
            },
            'endpoints': [
                '/binance/',
                '/binance/connect',
                '/binance/callback',
                '/binance/disconnect',
                '/binance/user-info',
                '/binance/status',
                '/binance/api/health',
                '/binance/api/status'
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500

# API Status endpoint
@binance_bp.route('/api/status', methods=['GET'])
def api_status_check():
    """Detailed status endpoint for Binance Integration module"""
    try:
        service = BinanceIntegrationService()
        integration_status = service.get_integration_status()
        
        return jsonify({
            'status': 'operational',
            'app_module': 'binance_integration',
            'version': '1.0.0',
            'integration_status': integration_status,
            'oauth_service': {
                'status': 'ready',
                'client_configured': integration_status['has_credentials'],
                'flows_supported': integration_status['oauth_flows_supported']
            },
            'api_service': {
                'status': 'ready',
                'endpoints_available': len(integration_status['api_endpoints'])
            },
            'timestamp': integration_status['last_checked']
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500

# Create binance_integration blueprint alias for template compatibility
binance_integration_bp = Blueprint('binance_integration', __name__,
                                 template_folder='templates',
                                 url_prefix='/binance-integration')

# Missing routes referenced in templates with binance_integration prefix
@binance_integration_bp.route('/api-status')
@login_required
def api_status():
    """Binance API status - alias for api_status_check"""
    return api_status_check()

@binance_integration_bp.route('/connect')
@login_required
def connect():
    """Connect to Binance - alias for connect_binance"""
    return connect_binance()

@binance_integration_bp.route('/market-analysis')
@login_required
def market_analysis():
    """Market analysis dashboard"""
    try:
        analysis_data = {
            'market_trends': [
                {'symbol': 'BTCUSDT', 'trend': 'Bullish', 'strength': 85.2, 'volume': 125000000},
                {'symbol': 'ETHUSDT', 'trend': 'Bearish', 'strength': 72.8, 'volume': 89000000},
                {'symbol': 'ADAUSDT', 'trend': 'Neutral', 'strength': 45.5, 'volume': 45000000}
            ],
            'technical_indicators': {
                'rsi': 65.2,
                'macd': 'Bullish',
                'moving_averages': 'Above 50-day MA',
                'support_resistance': {'support': 42500, 'resistance': 48000}
            },
            'market_sentiment': {
                'fear_greed_index': 72,
                'sentiment': 'Greed',
                'social_volume': 'High'
            }
        }
        return render_template('binance_integration/market_analysis.html',
                             analysis_data=analysis_data,
                             page_title='Market Analysis')
    except Exception as e:
        logger.error(f"Market analysis error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('binance_integration.connect'))

@binance_integration_bp.route('/portfolio-analysis')
@login_required
def portfolio_analysis():
    """Portfolio analysis - alias for portfolio_analytics"""
    return portfolio_analytics()

@binance_integration_bp.route('/trading-interface')
@login_required
def trading_interface():
    """Trading interface - alias for existing trading_interface"""
    return redirect(url_for('binance.dashboard'))

# Missing binance routes referenced in templates
@binance_bp.route('/advanced-trading')
@login_required
def advanced_trading():
    """Advanced trading interface"""
    try:
        trading_data = {
            'advanced_features': [
                'Algorithmic Trading', 'Options Trading', 'Futures Trading',
                'Margin Trading', 'Stop-Loss Orders', 'Take-Profit Orders'
            ],
            'trading_pairs': [
                {'symbol': 'BTCUSDT', 'price': 43250.00, 'change': '+2.5%'},
                {'symbol': 'ETHUSDT', 'price': 2650.00, 'change': '-1.2%'},
                {'symbol': 'ADAUSDT', 'price': 0.485, 'change': '+0.8%'}
            ],
            'account_balance': 25000.00,
            'available_margin': 75000.00
        }
        return render_template('binance/advanced_trading.html',
                             trading_data=trading_data,
                             page_title='Advanced Trading')
    except Exception as e:
        logger.error(f"Advanced trading error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('binance.dashboard'))

@binance_bp.route('/binance-dashboard')
@login_required
def binance_dashboard():
    """Main Binance dashboard - alias for dashboard"""
    return dashboard()

@binance_bp.route('/market-data-dashboard')
@login_required
def market_data_dashboard():
    """Market data dashboard"""
    try:
        market_data = {
            'top_gainers': [
                {'symbol': 'ADAUSDT', 'price': 0.485, 'change': '+15.2%'},
                {'symbol': 'DOTUSDT', 'price': 6.25, 'change': '+12.8%'},
                {'symbol': 'LINKUSDT', 'price': 14.50, 'change': '+8.9%'}
            ],
            'top_losers': [
                {'symbol': 'XRPUSDT', 'price': 0.52, 'change': '-8.5%'},
                {'symbol': 'LTCUSDT', 'price': 72.30, 'change': '-6.2%'},
                {'symbol': 'BCHUSDT', 'price': 245.00, 'change': '-4.8%'}
            ],
            'market_overview': {
                'total_market_cap': '1.2T',
                'total_volume': '45.2B',
                'btc_dominance': '52.3%',
                'fear_greed_index': 68
            }
        }
        return render_template('binance/market_data_dashboard.html',
                             market_data=market_data,
                             page_title='Market Data Dashboard')
    except Exception as e:
        logger.error(f"Market data dashboard error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('binance.dashboard'))

@binance_bp.route('/portfolio-analytics')
@login_required
def portfolio_analytics():
    """Portfolio analytics"""
    try:
        portfolio_data = {
            'total_value': 125000.00,
            'total_pnl': 15250.00,
            'pnl_percentage': 13.9,
            'holdings': [
                {'symbol': 'BTC', 'amount': 2.5, 'value': 108125.00, 'pnl': '+12.5%'},
                {'symbol': 'ETH', 'amount': 15.0, 'value': 39750.00, 'pnl': '+8.2%'},
                {'symbol': 'ADA', 'amount': 5000, 'value': 2425.00, 'pnl': '+15.8%'}
            ],
            'performance_metrics': {
                'sharpe_ratio': 1.85,
                'max_drawdown': '-8.5%',
                'win_rate': '68.5%'
            }
        }
        return render_template('binance/portfolio_analytics.html',
                             portfolio_data=portfolio_data,
                             page_title='Portfolio Analytics')
    except Exception as e:
        logger.error(f"Portfolio analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('binance.dashboard'))