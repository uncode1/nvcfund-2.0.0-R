"""
Trading Platform API Endpoints
RESTful API for trading operations, market data, and portfolio management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from decimal import Decimal
import logging
from datetime import datetime, timezone

from modules.core.security_enforcement import rate_limit, require_session_security
from modules.core.rbac import require_permission
from ..services import TradingService

logger = logging.getLogger(__name__)

# Create API Blueprint
trading_api_bp = Blueprint('trading_api', __name__, url_prefix='/trading/api')

# Initialize Trading Service
trading_service = TradingService()

# === MARKET DATA API ===

@trading_api_bp.route('/market-data/<symbol>')
@login_required
@rate_limit(max_requests=100, window_minutes=1)
def get_market_data(symbol):
    """Get real-time market data for a symbol"""
    try:
        market_data = trading_service.get_market_data(symbol.upper())
        
        if 'error' in market_data:
            return jsonify({'error': market_data['error']}), 404
        
        return jsonify(market_data)
    
    except Exception as e:
        logger.error(f"Market data API error for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve market data'}), 500

@trading_api_bp.route('/market-data/bulk', methods=['POST'])
@login_required
@rate_limit(max_requests=20, window_minutes=1)
def get_bulk_market_data():
    """Get market data for multiple symbols"""
    try:
        symbols = request.json.get('symbols', [])
        
        if not symbols or len(symbols) > 50:
            return jsonify({'error': 'Invalid symbols list (max 50)'}), 400
        
        results = {}
        for symbol in symbols:
            try:
                data = trading_service.get_market_data(symbol.upper())
                results[symbol] = data
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Bulk market data API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve market data'}), 500

# === PORTFOLIO API ===

@trading_api_bp.route('/portfolio/summary')
@login_required
@rate_limit(max_requests=30, window_minutes=1)
@require_permission('trading_dashboard')
def get_portfolio_summary():
    """Get complete portfolio summary"""
    try:
        account_id = request.args.get('account_id')
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id), account_id)
        
        if 'error' in portfolio_data:
            return jsonify({'error': portfolio_data['error']}), 404
        
        return jsonify(portfolio_data)
    
    except Exception as e:
        logger.error(f"Portfolio summary API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve portfolio data'}), 500

@trading_api_bp.route('/portfolio/positions')
@login_required
@rate_limit(max_requests=20, window_minutes=1)
@require_permission('trading_dashboard')
def get_positions():
    """Get current positions"""
    try:
        account_id = request.args.get('account_id')
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id), account_id)
        
        if 'error' in portfolio_data:
            return jsonify({'error': portfolio_data['error']}), 404
        
        return jsonify({
            'positions': portfolio_data.get('positions', []),
            'total_value': portfolio_data.get('account_summary', {}).get('securities_value', 0)
        })
    
    except Exception as e:
        logger.error(f"Positions API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve positions'}), 500

@trading_api_bp.route('/portfolio/performance')
@login_required
@rate_limit(max_requests=10, window_minutes=1)
@require_permission('trading_dashboard')
def get_performance():
    """Get portfolio performance metrics"""
    try:
        account_id = request.args.get('account_id')
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id), account_id)
        
        if 'error' in portfolio_data:
            return jsonify({'error': portfolio_data['error']}), 404
        
        return jsonify({
            'performance': portfolio_data.get('performance', {}),
            'allocation': portfolio_data.get('allocation', {})
        })
    
    except Exception as e:
        logger.error(f"Performance API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve performance data'}), 500

# === ORDERS API ===

@trading_api_bp.route('/orders/recent')
@login_required
@rate_limit(max_requests=30, window_minutes=1)
@require_permission('trading_dashboard')
def get_recent_orders():
    """Get recent orders"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        orders = trading_service.get_recent_orders(str(current_user.id), limit=limit)
        
        return jsonify({
            'orders': orders,
            'count': len(orders)
        })
    
    except Exception as e:
        logger.error(f"Recent orders API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500

@trading_api_bp.route('/orders/status/<order_id>')
@login_required
@rate_limit(max_requests=50, window_minutes=1)
@require_permission('trading_dashboard')
def get_order_status(order_id):
    """Get order status"""
    try:
        order_status = trading_service.get_order_status(str(current_user.id), order_id)
        
        if not order_status:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify(order_status)
    
    except Exception as e:
        logger.error(f"Order status API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve order status'}), 500

@trading_api_bp.route('/orders', methods=['POST'])
@login_required
@require_session_security()
@rate_limit(max_requests=10, window_minutes=1)
@require_permission('securities_trading')
def submit_order():
    """Submit trading order via API"""
    try:
        order_data = request.json
        
        if not order_data:
            return jsonify({'error': 'Invalid order data'}), 400
        
        # Validate required fields
        required_fields = ['symbol', 'order_type', 'order_side', 'quantity']
        for field in required_fields:
            if field not in order_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result = trading_service.submit_order(str(current_user.id), order_data)
        
        if result.success:
            return jsonify({
                'success': True,
                'order_id': result.order_id,
                'message': result.message,
                'trade_id': result.trade_id,
                'filled_quantity': float(result.filled_quantity) if result.filled_quantity else 0,
                'average_price': float(result.average_price) if result.average_price else None
            })
        else:
            return jsonify({
                'success': False,
                'message': result.message
            }), 400
    
    except Exception as e:
        logger.error(f"Order submission API error: {str(e)}")
        return jsonify({'error': 'Order submission failed'}), 500

@trading_api_bp.route('/orders/<order_id>/cancel', methods=['POST'])
@login_required
@require_session_security()
@rate_limit(max_requests=20, window_minutes=1)
@require_permission('trading_dashboard')
def cancel_order(order_id):
    """Cancel order via API"""
    try:
        result = trading_service.cancel_order(str(current_user.id), order_id)
        
        return jsonify({
            'success': result.success,
            'message': result.message
        })
    
    except Exception as e:
        logger.error(f"Order cancellation API error: {str(e)}")
        return jsonify({'error': 'Cancellation failed'}), 500

# === RISK MANAGEMENT API ===

@trading_api_bp.route('/risk/metrics')
@login_required
@rate_limit(max_requests=10, window_minutes=1)
@require_permission('risk_management')
def get_risk_metrics():
    """Get risk metrics"""
    try:
        account_id = request.args.get('account_id')
        risk_data = trading_service.calculate_risk_metrics(str(current_user.id), account_id)
        
        if 'error' in risk_data:
            return jsonify({'error': risk_data['error']}), 404
        
        return jsonify(risk_data)
    
    except Exception as e:
        logger.error(f"Risk metrics API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve risk metrics'}), 500

@trading_api_bp.route('/risk/limits', methods=['GET', 'POST'])
@login_required
@require_permission('risk_management')
def risk_limits():
    """Get or update risk limits"""
    try:
        if request.method == 'GET':
            limits = trading_service.get_risk_limits(str(current_user.id))
            return jsonify(limits)
        
        elif request.method == 'POST':
            risk_limits = request.json
            
            if not risk_limits:
                return jsonify({'error': 'Invalid risk limits data'}), 400
            
            result = trading_service.update_risk_limits(str(current_user.id), risk_limits)
            
            return jsonify({
                'success': result.get('success', False),
                'message': result.get('message', 'Update completed')
            })
    
    except Exception as e:
        logger.error(f"Risk limits API error: {str(e)}")
        return jsonify({'error': 'Risk limits operation failed'}), 500

# === ANALYTICS API ===

@trading_api_bp.route('/analytics/performance')
@login_required
@rate_limit(max_requests=5, window_minutes=1)
@require_permission('trading_analytics')
def get_performance_analytics():
    """Get detailed performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        days = min(days, 365)  # Cap at 1 year
        
        analytics = trading_service.get_performance_analytics(str(current_user.id), days)
        
        return jsonify(analytics)
    
    except Exception as e:
        logger.error(f"Performance analytics API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

@trading_api_bp.route('/analytics/trades')
@login_required
@rate_limit(max_requests=10, window_minutes=1)
@require_permission('trading_analytics')
def get_trade_analytics():
    """Get trade analytics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        analytics = trading_service.get_trade_analytics(
            str(current_user.id), 
            start_date, 
            end_date
        )
        
        return jsonify(analytics)
    
    except Exception as e:
        logger.error(f"Trade analytics API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve trade analytics'}), 500

# === ACCOUNT MANAGEMENT API ===

@trading_api_bp.route('/accounts')
@login_required
@rate_limit(max_requests=20, window_minutes=1)
@require_permission('trading_dashboard')
def get_trading_accounts():
    """Get user's trading accounts"""
    try:
        accounts = trading_service.get_trading_accounts(str(current_user.id))
        
        return jsonify({
            'accounts': accounts,
            'count': len(accounts)
        })
    
    except Exception as e:
        logger.error(f"Trading accounts API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve accounts'}), 500

@trading_api_bp.route('/accounts/<account_id>/balance')
@login_required
@rate_limit(max_requests=30, window_minutes=1)
@require_permission('trading_dashboard')
def get_account_balance(account_id):
    """Get account balance details"""
    try:
        balance = trading_service.get_account_balance(str(current_user.id), account_id)
        
        if not balance:
            return jsonify({'error': 'Account not found'}), 404
        
        return jsonify(balance)
    
    except Exception as e:
        logger.error(f"Account balance API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve balance'}), 500

# === WATCHLIST API ===

@trading_api_bp.route('/watchlist', methods=['GET', 'POST', 'DELETE'])
@login_required
@rate_limit(max_requests=30, window_minutes=1)
@require_permission('trading_dashboard')
def manage_watchlist():
    """Manage user watchlist"""
    try:
        if request.method == 'GET':
            watchlist = trading_service.get_watchlist(str(current_user.id))
            return jsonify(watchlist)
        
        elif request.method == 'POST':
            symbol = request.json.get('symbol')
            if not symbol:
                return jsonify({'error': 'Symbol required'}), 400
            
            result = trading_service.add_to_watchlist(str(current_user.id), symbol.upper())
            return jsonify(result)
        
        elif request.method == 'DELETE':
            symbol = request.args.get('symbol')
            if not symbol:
                return jsonify({'error': 'Symbol required'}), 400
            
            result = trading_service.remove_from_watchlist(str(current_user.id), symbol.upper())
            return jsonify(result)
    
    except Exception as e:
        logger.error(f"Watchlist API error: {str(e)}")
        return jsonify({'error': 'Watchlist operation failed'}), 500

# === QUOTES API ===

@trading_api_bp.route('/quotes/search')
@login_required
@rate_limit(max_requests=50, window_minutes=1)
def search_symbols():
    """Search for trading symbols"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 1:
            return jsonify({'symbols': []})
        
        symbols = trading_service.search_symbols(query.upper())
        
        return jsonify({
            'symbols': symbols,
            'query': query
        })
    
    except Exception as e:
        logger.error(f"Symbol search API error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

# === HEALTH CHECK ===

@trading_api_bp.route('/health')
@rate_limit(max_requests=100, window_minutes=1)
def health_check():
    """Trading API health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'trading_api',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0'
        })
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# === ERROR HANDLERS ===

@trading_api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({'error': 'Bad request'}), 400

@trading_api_bp.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized access"""
    return jsonify({'error': 'Unauthorized access'}), 401

@trading_api_bp.errorhandler(403)
def forbidden(error):
    """Handle forbidden access"""
    return jsonify({'error': 'Access forbidden'}), 403

@trading_api_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({'error': 'Resource not found'}), 404

@trading_api_bp.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit exceeded"""
    return jsonify({'error': 'Rate limit exceeded'}), 429

@trading_api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Trading API internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500