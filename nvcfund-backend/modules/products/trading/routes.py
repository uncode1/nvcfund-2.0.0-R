"""
Trading Platform Routes
Secure routes for trading operations with comprehensive FastRBAC integration
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal
import logging
from datetime import datetime, timezone

from modules.core.security_enforcement import (
    secure_banking_route, treasury_secure_route, admin_secure_route,
    rate_limit, require_session_security, validate_input, csrf_protect
)
from modules.core.rbac import require_permission, require_role
from .services import TradingService
from .forms import (
    EquityOrderForm, ForexOrderForm, CommodityOrderForm, DerivativeOrderForm,
    PortfolioRebalanceForm, RiskLimitForm, TradingAlgorithmForm
)

logger = logging.getLogger(__name__)

# Create Blueprint
trading_bp = Blueprint('trading', __name__, url_prefix='/trading', template_folder='templates')

# Initialize Trading Service
trading_service = TradingService()

# === DASHBOARD ROUTES ===

@trading_bp.route('/')
@trading_bp.route('/dashboard')
@login_required
@secure_banking_route(
    max_requests=10,
    required_permissions={'trading_dashboard'},
    session_timeout_minutes=15
)
def trading_dashboard():
    """Main trading dashboard with portfolio overview and market data"""
    try:
        # Get portfolio summary
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id))
        
        # Get market data for watchlist
        watchlist_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']  # Example watchlist
        market_data = {}
        for symbol in watchlist_symbols:
            market_data[symbol] = trading_service.get_market_data(symbol)
        
        # Get recent orders
        recent_orders = trading_service.get_recent_orders(str(current_user.id), limit=10)
        
        # Get risk metrics
        risk_metrics = trading_service.calculate_risk_metrics(str(current_user.id))
        
        return render_template('trading/trading_dashboard.html',
                               portfolio=portfolio_data,
                               market_data=market_data,
                               recent_orders=recent_orders,
                               risk_metrics=risk_metrics)
    
    except Exception as e:
        logger.error(f"Trading dashboard error for user {current_user.id}: {str(e)}")
        flash('Error loading trading dashboard', 'error')
        return render_template('trading/trading_dashboard.html', error=True)

# === EQUITY TRADING ===

@trading_bp.route('/securities')
@login_required
@require_permission('securities_trading')
def securities_trading():
    """Securities trading interface"""
    form = EquityOrderForm()
    return render_template('trading/securities.html', form=form)

@trading_bp.route('/securities/order', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=5,
    required_permissions={'securities_trading'},
    validation_rules={
        'symbol': 'symbol',
        'quantity': 'amount',
        'price': 'amount'
    }
)
def submit_equity_order():
    """Submit equity order with comprehensive validation"""
    form = EquityOrderForm()
    
    if form.validate_on_submit():
        try:
            order_data = {
                'symbol': form.symbol.data.upper(),
                'order_type': form.order_type.data,
                'order_side': form.order_side.data,
                'quantity': float(form.quantity.data),
                'price': float(form.limit_price.data) if form.limit_price.data else None,
                'stop_price': float(form.stop_price.data) if form.stop_price.data else None,
                'time_in_force': form.time_in_force.data,
                'all_or_none': form.all_or_none.data,
                'hidden_order': form.hidden_order.data
            }
            
            # Submit order through trading service
            result = trading_service.submit_order(str(current_user.id), order_data)
            
            if result.success:
                flash(f'Order submitted successfully. Order ID: {result.order_id}', 'success')
                logger.info(f"Equity order submitted: {result.order_id} by user {current_user.id}")
                return redirect(url_for('trading.trading_dashboard'))
            else:
                flash(f'Order failed: {result.message}', 'error')
                
        except Exception as e:
            logger.error(f"Equity order submission error: {str(e)}")
            flash('Order submission failed due to system error', 'error')
    
    # Render form with validation errors
    return render_template('trading/securities.html', form=form)

# === FOREX TRADING ===

@trading_bp.route('/forex')
@login_required
@require_permission('forex_trading')
def forex_trading():
    """Foreign exchange trading interface"""
    form = ForexOrderForm()
    return render_template('trading/trading_dashboard.html', form=form)

@trading_bp.route('/forex/order', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=3,  # Lower limit for FX due to higher risk
    required_permissions={'forex_trading'},
    validation_rules={
        'base_currency': 'currency',
        'quote_currency': 'currency',
        'notional_amount': 'amount'
    }
)
def submit_forex_order():
    """Submit forex order with enhanced risk controls"""
    form = ForexOrderForm()
    
    if form.validate_on_submit():
        try:
            # Construct currency pair symbol
            symbol = f"{form.base_currency.data}{form.quote_currency.data}"
            
            order_data = {
                'symbol': symbol,
                'order_type': form.order_type.data,
                'order_side': form.order_side.data,
                'quantity': float(form.notional_amount.data),
                'price': float(form.exchange_rate.data) if form.exchange_rate.data else None,
                'settlement_type': form.settlement_type.data,
                'max_slippage_pips': form.max_slippage_pips.data
            }
            
            result = trading_service.submit_order(str(current_user.id), order_data)
            
            if result.success:
                flash(f'FX order submitted successfully. Order ID: {result.order_id}', 'success')
                logger.info(f"FX order submitted: {result.order_id} by user {current_user.id}")
                return redirect(url_for('trading.trading_dashboard'))
            else:
                flash(f'FX order failed: {result.message}', 'error')
                
        except Exception as e:
            logger.error(f"FX order submission error: {str(e)}")
            flash('FX order submission failed', 'error')
    
    return render_template('trading/trading_dashboard.html', form=form)

# === COMMODITIES TRADING ===

@trading_bp.route('/commodities')
@login_required
@require_permission('commodities_trading')
def commodities_trading():
    """Commodities trading interface"""
    form = CommodityOrderForm()
    return render_template('trading/trading_dashboard.html', form=form)

@trading_bp.route('/commodities/order', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=5,
    required_permissions={'commodities_trading'},
    validation_rules={
        'commodity_symbol': 'symbol',
        'contracts': 'amount'
    }
)
def submit_commodity_order():
    """Submit commodity futures order"""
    form = CommodityOrderForm()
    
    if form.validate_on_submit():
        try:
            # Construct futures symbol
            symbol = f"{form.commodity_symbol.data}{form.contract_month.data}{form.contract_year.data}"
            
            order_data = {
                'symbol': symbol,
                'order_type': 'market',  # Commodities typically use market orders
                'order_side': form.order_side.data,
                'quantity': int(form.contracts.data),
                'commodity_type': form.commodity_type.data,
                'delivery_method': form.delivery_method.data,
                'storage_location': form.storage_location.data
            }
            
            result = trading_service.submit_order(str(current_user.id), order_data)
            
            if result.success:
                flash(f'Commodity order submitted successfully. Order ID: {result.order_id}', 'success')
                logger.info(f"Commodity order submitted: {result.order_id} by user {current_user.id}")
                return redirect(url_for('trading.trading_dashboard'))
            else:
                flash(f'Commodity order failed: {result.message}', 'error')
                
        except Exception as e:
            logger.error(f"Commodity order submission error: {str(e)}")
            flash('Commodity order submission failed', 'error')
    
    return render_template('trading/trading_dashboard.html', form=form)

# === DERIVATIVES TRADING ===

@trading_bp.route('/derivatives')
@login_required
@require_permission('derivatives_trading')
def derivatives_trading():
    """Options and derivatives trading interface"""
    form = DerivativeOrderForm()
    return render_template('trading/trading_dashboard.html', form=form)

@trading_bp.route('/derivatives/order', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=3,  # Very restrictive for derivatives
    required_permissions={'derivatives_trading'},
    validation_rules={
        'underlying_symbol': 'symbol',
        'strike_price': 'amount'
    }
)
def submit_derivative_order():
    """Submit options/derivatives order with enhanced risk controls"""
    form = DerivativeOrderForm()
    
    if form.validate_on_submit():
        try:
            order_data = {
                'underlying_symbol': form.underlying_symbol.data.upper(),
                'derivative_type': form.derivative_type.data,
                'order_side': 'buy',  # Simplified for demo
                'quantity': 1,  # Options are typically 1 contract
                'strike_price': float(form.strike_price.data) if form.strike_price.data else None,
                'expiration_date': form.expiration_date.data,
                'option_style': form.option_style.data,
                'strategy_type': form.strategy_type.data
            }
            
            result = trading_service.submit_order(str(current_user.id), order_data)
            
            if result.success:
                flash(f'Derivative order submitted successfully. Order ID: {result.order_id}', 'success')
                logger.info(f"Derivative order submitted: {result.order_id} by user {current_user.id}")
                return redirect(url_for('trading.trading_dashboard'))
            else:
                flash(f'Derivative order failed: {result.message}', 'error')
                
        except Exception as e:
            logger.error(f"Derivative order submission error: {str(e)}")
            flash('Derivative order submission failed', 'error')
    
    return render_template('trading/trading_dashboard.html', form=form)

# === PORTFOLIO MANAGEMENT ===

@trading_bp.route('/portfolio')
@login_required
@require_permission('portfolio_management')
def portfolio_management():
    """Portfolio analysis and management interface"""
    try:
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id))
        form = PortfolioRebalanceForm()
        
        return render_template('trading/trading_dashboard.html', 
                               portfolio=portfolio_data, 
                               form=form)
    
    except Exception as e:
        logger.error(f"Portfolio management error: {str(e)}")
        flash('Error loading portfolio data', 'error')
        return render_template('trading/trading_dashboard.html', error=True)

@trading_bp.route('/portfolio/rebalance', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=2,  # Very restrictive for portfolio rebalancing
    required_permissions={'portfolio_management'},
    validation_rules={
        'equity_target': 'amount',
        'fixed_income_target': 'amount',
        'cash_target': 'amount'
    }
)
def rebalance_portfolio():
    """Execute portfolio rebalancing"""
    form = PortfolioRebalanceForm()
    
    if form.validate_on_submit():
        try:
            # Validate allocation totals
            form.validate_allocation_total()
            
            target_allocations = {
                'equity': float(form.equity_target.data),
                'fixed_income': float(form.fixed_income_target.data),
                'commodity': float(form.commodity_target.data or 0),
                'cash': float(form.cash_target.data),
                'alternative': float(form.alternative_target.data or 0)
            }
            
            # Get user's trading account
            account_id = request.form.get('account_id')  # Would come from form
            
            result = trading_service.rebalance_portfolio(
                str(current_user.id), 
                account_id, 
                target_allocations
            )
            
            if result['success']:
                flash(f"Portfolio rebalancing completed: {result['message']}", 'success')
                logger.info(f"Portfolio rebalanced for user {current_user.id}: {result['total_trades']} trades")
            else:
                flash(f"Rebalancing failed: {result['message']}", 'error')
                
        except Exception as e:
            logger.error(f"Portfolio rebalancing error: {str(e)}")
            flash('Portfolio rebalancing failed', 'error')
    
    return redirect(url_for('trading.portfolio_management'))

# === RISK MANAGEMENT ===

@trading_bp.route('/risk')
@login_required
@require_permission('risk_management')
def risk_management():
    """Risk analysis and limit management"""
    try:
        risk_metrics = trading_service.calculate_risk_metrics(str(current_user.id))
        form = RiskLimitForm()
        
        return render_template('trading/trading_dashboard.html', 
                               risk_metrics=risk_metrics, 
                               form=form)
    
    except Exception as e:
        logger.error(f"Risk management error: {str(e)}")
        flash('Error loading risk data', 'error')
        return render_template('trading/trading_dashboard.html', error=True)

@trading_bp.route('/risk/limits', methods=['POST'])
@login_required
@secure_banking_route(
    max_requests=3,
    required_permissions={'risk_management'},
    validation_rules={
        'max_position_size': 'amount',
        'var_limit_1day': 'amount'
    }
)
def update_risk_limits():
    """Update risk limits and monitoring parameters"""
    form = RiskLimitForm()
    
    if form.validate_on_submit():
        try:
            risk_limits = {
                'max_position_size': float(form.max_position_size.data),
                'max_leverage_ratio': float(form.max_leverage_ratio.data),
                'var_limit_1day': float(form.var_limit_1day.data),
                'max_drawdown_limit': float(form.max_drawdown_limit.data),
                'margin_call_threshold': float(form.margin_call_threshold.data)
            }
            
            # Update risk limits in trading service
            result = trading_service.update_risk_limits(str(current_user.id), risk_limits)
            
            if result['success']:
                flash('Risk limits updated successfully', 'success')
                logger.info(f"Risk limits updated for user {current_user.id}")
            else:
                flash(f"Failed to update risk limits: {result['message']}", 'error')
                
        except Exception as e:
            logger.error(f"Risk limits update error: {str(e)}")
            flash('Failed to update risk limits', 'error')
    
    return redirect(url_for('trading.risk_management'))

# === ORDER MANAGEMENT ===

@trading_bp.route('/orders')
@login_required
@require_permission('trading_dashboard')
def order_management():
    """Order history and management"""
    try:
        # Get order history with pagination
        page = request.args.get('page', 1, type=int)
        orders = trading_service.get_order_history(
            str(current_user.id), 
            page=page, 
            per_page=20
        )
        
        return render_template('trading/trading_dashboard.html', orders=orders)
    
    except Exception as e:
        logger.error(f"Order management error: {str(e)}")
        flash('Error loading order data', 'error')
        return render_template('trading/trading_dashboard.html', error=True)

@trading_bp.route('/orders/cancel/<order_id>', methods=['POST'])
@login_required
@csrf_protect()
@rate_limit(max_requests=10, window_minutes=1)
def cancel_order(order_id):
    """Cancel pending order"""
    try:
        result = trading_service.cancel_order(str(current_user.id), order_id)
        
        if result.success:
            flash(f'Order {order_id} cancelled successfully', 'success')
            logger.info(f"Order cancelled: {order_id} by user {current_user.id}")
        else:
            flash(f'Failed to cancel order: {result.message}', 'error')
            
    except Exception as e:
        logger.error(f"Order cancellation error: {str(e)}")
        flash('Order cancellation failed', 'error')
    
    return redirect(url_for('trading.order_management'))

# === ALGORITHMIC TRADING ===

@trading_bp.route('/algorithms')
@login_required
@require_permission('trading_analytics')
def algorithmic_trading():
    """Algorithmic trading strategies management"""
    form = TradingAlgorithmForm()
    return render_template('trading/trading_dashboard.html', form=form)

@trading_bp.route('/algorithms/create', methods=['POST'])
@login_required
@admin_secure_route()  # Maximum security for algorithm creation
def create_algorithm():
    """Create new trading algorithm"""
    form = TradingAlgorithmForm()
    
    if form.validate_on_submit():
        try:
            algorithm_config = {
                'name': form.algorithm_name.data,
                'type': form.algorithm_type.data,
                'universe': form.trading_universe.data,
                'max_positions': int(form.max_position_count.data),
                'position_sizing': form.position_sizing_method.data,
                'rebalancing_frequency': form.rebalancing_frequency.data,
                'lookback_period': int(form.lookback_period.data),
                'stop_loss': float(form.stop_loss_percentage.data) if form.stop_loss_percentage.data else None,
                'take_profit': float(form.take_profit_percentage.data) if form.take_profit_percentage.data else None,
                'run_backtest': True,
                'paper_trading_only': form.paper_trading_only.data
            }
            
            result = trading_service.create_trading_algorithm(str(current_user.id), algorithm_config)
            
            if result['success']:
                flash(f"Algorithm '{form.algorithm_name.data}' created successfully", 'success')
                logger.info(f"Trading algorithm created: {result['algorithm_id']} by user {current_user.id}")
            else:
                flash(f"Algorithm creation failed: {result['message']}", 'error')
                
        except Exception as e:
            logger.error(f"Algorithm creation error: {str(e)}")
            flash('Algorithm creation failed', 'error')
    
    return redirect(url_for('trading.algorithmic_trading'))

# === ANALYTICS ===

@trading_bp.route('/analytics')
@login_required
@require_permission('trading_analytics')
def trading_analytics():
    """Trading performance analytics and reporting"""
    try:
        # Get performance analytics
        analytics_data = trading_service.get_trading_analytics(str(current_user.id))
        
        return render_template('trading/trading_dashboard.html', analytics=analytics_data)
    
    except Exception as e:
        logger.error(f"Trading analytics error: {str(e)}")
        flash('Error loading analytics data', 'error')
        return render_template('trading/trading_dashboard.html', error=True)

# === API ENDPOINTS ===

@trading_bp.route('/api/market-data/<symbol>')
@login_required
@rate_limit(max_requests=50, window_minutes=1)  # Higher limit for market data
def api_market_data(symbol):
    """API endpoint for real-time market data"""
    try:
        market_data = trading_service.get_market_data(symbol.upper())
        return jsonify(market_data)
    
    except Exception as e:
        logger.error(f"Market data API error for {symbol}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve market data'}), 500

@trading_bp.route('/api/portfolio/summary')
@login_required
@rate_limit(max_requests=20, window_minutes=1)
def api_portfolio_summary():
    """API endpoint for portfolio summary"""
    try:
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id))
        return jsonify(portfolio_data)
    
    except Exception as e:
        logger.error(f"Portfolio API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve portfolio data'}), 500

@trading_bp.route('/api/orders/recent')
@login_required
@rate_limit(max_requests=30, window_minutes=1)
def api_recent_orders():
    """API endpoint for recent orders"""
    try:
        limit = request.args.get('limit', 10, type=int)
        orders = trading_service.get_recent_orders(str(current_user.id), limit=limit)
        return jsonify(orders)
    
    except Exception as e:
        logger.error(f"Orders API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500

@trading_bp.route('/api/risk/metrics')
@login_required
@rate_limit(max_requests=10, window_minutes=1)
def api_risk_metrics():
    """API endpoint for risk metrics"""
    try:
        risk_data = trading_service.calculate_risk_metrics(str(current_user.id))
        return jsonify(risk_data)
    
    except Exception as e:
        logger.error(f"Risk metrics API error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve risk metrics'}), 500

# === ERROR HANDLERS ===

@trading_bp.errorhandler(403)
def trading_access_denied(error):
    """Handle trading access denied"""
    flash('You do not have permission to access this trading feature', 'error')
    return redirect(url_for('trading.trading_dashboard'))

@trading_bp.errorhandler(429)
def trading_rate_limit_exceeded(error):
    """Handle rate limit exceeded"""
    flash('Too many trading requests. Please wait before trying again.', 'warning')
    return redirect(url_for('trading.trading_dashboard'))

@trading_bp.errorhandler(500)
def trading_server_error(error):
    """Handle trading system errors"""
    logger.error(f"Trading system error: {str(error)}")
    flash('Trading system temporarily unavailable. Please try again later.', 'error')
    return redirect(url_for('trading.trading_dashboard'))

# === ROUTES FOR ORPHANED TEMPLATES ===

@trading_bp.route('/main-dashboard')
@login_required
@secure_banking_route(
    max_requests=10,
    required_permissions={'trading_dashboard'},
    session_timeout_minutes=15
)
def trading_main_dashboard():
    """Main trading dashboard using orphaned template"""
    try:
        portfolio_data = trading_service.get_portfolio_summary(str(current_user.id))
        
        return render_template('trading_main_dashboard.html',
                             portfolio_data=portfolio_data,
                             user=current_user,
                             page_title='Main Trading Dashboard')
        
    except Exception as e:
        logger.error(f"Trading main dashboard error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/base')
@login_required
@secure_banking_route(
    max_requests=10,
    required_permissions={'trading_dashboard'},
    session_timeout_minutes=15
)
def base_trading():
    """Base trading interface using orphaned template"""
    try:        
        return render_template('base_trading.html',
                             user=current_user,
                             page_title='Base Trading Interface')
        
    except Exception as e:
        logger.error(f"Base trading error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

# Drill-down routes for detailed views
@trading_bp.route('/portfolio/detailed')
@login_required
@secure_banking_route(max_requests=10, required_permissions={'trading_portfolio'})
def portfolio_detailed():
    """Detailed portfolio analysis drill-down view"""
    try:
        return render_template('trading/portfolio_detailed.html',
                             user=current_user,
                             page_title='Detailed Portfolio Analysis')
    except Exception as e:
        logger.error(f"Portfolio detailed error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/market/analysis')
@login_required
@secure_banking_route(max_requests=10, required_permissions={'trading_analysis'})
def market_analysis():
    """Market analysis drill-down view"""
    try:
        return render_template('trading/market_analysis.html',
                             user=current_user,
                             page_title='Market Analysis')
    except Exception as e:
        logger.error(f"Market analysis error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/orders/management')
@login_required
@secure_banking_route(max_requests=10, required_permissions={'trading_orders'})
def orders_management():
    """Orders management drill-down view"""
    try:
        return render_template('trading/orders_management.html',
                             user=current_user,
                             page_title='Orders Management')
    except Exception as e:
        logger.error(f"Orders management error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/risk/analysis')
@login_required
@secure_banking_route(max_requests=10, required_permissions={'trading_risk'})
def risk_analysis():
    """Risk analysis drill-down view"""
    try:
        return render_template('trading/risk_analysis.html',
                             user=current_user,
                             page_title='Risk Analysis')
    except Exception as e:
        logger.error(f"Risk analysis error: {str(e)}")
        return redirect(url_for('trading.trading_dashboard'))

# Missing routes referenced in templates
@trading_bp.route('/portfolio-analysis')
@login_required
def portfolio_analysis():
    """Portfolio analysis dashboard"""
    try:
        portfolio_data = {
            'total_value': 2450000.00,
            'daily_pnl': 12500.00,
            'positions': 15,
            'performance': 8.7
        }
        return render_template('trading/portfolio_analysis.html',
                             portfolio_data=portfolio_data,
                             page_title='Portfolio Analysis')
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/orders-analysis')
@login_required
def orders_analysis():
    """Orders analysis dashboard"""
    try:
        orders_data = {
            'total_orders': 1247,
            'executed_orders': 1198,
            'pending_orders': 49,
            'success_rate': 96.1
        }
        return render_template('trading/orders_analysis.html',
                             orders_data=orders_data,
                             page_title='Orders Analysis')
    except Exception as e:
        logger.error(f"Orders analysis error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/place-order')
@login_required
def place_order():
    """Place order interface"""
    try:
        instruments = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'price': 2750.00},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 415.25}
        ]
        return render_template('trading/place_order.html',
                             instruments=instruments,
                             page_title='Place Order')
    except Exception as e:
        logger.error(f"Place order error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/order-history')
@login_required
def order_history():
    """Order history dashboard"""
    try:
        history_data = {
            'recent_orders': [
                {'id': 'ORD-001', 'symbol': 'AAPL', 'side': 'BUY', 'quantity': 100, 'price': 175.50, 'status': 'FILLED'},
                {'id': 'ORD-002', 'symbol': 'GOOGL', 'side': 'SELL', 'quantity': 50, 'price': 2750.00, 'status': 'FILLED'},
                {'id': 'ORD-003', 'symbol': 'MSFT', 'side': 'BUY', 'quantity': 200, 'price': 415.25, 'status': 'PENDING'}
            ]
        }
        return render_template('trading/order_history.html',
                             history_data=history_data,
                             page_title='Order History')
    except Exception as e:
        logger.error(f"Order history error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('trading.trading_dashboard'))

@trading_bp.route('/order-entry')
@login_required
def order_entry():
    """Order entry interface"""
    try:
        return render_template('trading/order_entry.html',
                             page_title='Order Entry')
    except Exception as e:
        logger.error(f"Order entry error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('trading.trading_dashboard'))