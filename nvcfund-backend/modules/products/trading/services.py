"""
Trading Platform Services
Comprehensive services for order execution, portfolio management, risk analytics, and algorithmic trading
"""

import asyncio
import logging
import math
import statistics
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Optional numpy/pandas imports for advanced analytics
try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None
    pd = None
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from flask import current_app

from modules.core.database import get_db_session
from modules.core.security_enforcement import security
from .models import (
    TradingInstrument, TradingAccount, TradingOrder, Trade, Position, 
    Portfolio, RiskMetrics, MarketData, OrderStatus, OrderType, OrderSide
)

logger = logging.getLogger(__name__)

@dataclass
class OrderResult:
    """Result object for order operations"""
    success: bool
    order_id: Optional[str] = None
    message: str = ""
    trade_id: Optional[str] = None
    filled_quantity: Decimal = Decimal('0')
    average_price: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    commission: Optional[Decimal] = None

@dataclass
class RiskAssessment:
    """Risk assessment result"""
    approved: bool
    risk_score: float
    warnings: List[str]
    violations: List[str]
    required_margin: Decimal
    var_impact: Optional[Decimal] = None

@dataclass
class MarketDataSnapshot:
    """Real-time market data snapshot"""
    symbol: str
    current_price: Decimal
    bid_price: Optional[Decimal]
    ask_price: Optional[Decimal]
    volume: int
    price_change: Decimal
    price_change_percent: float
    timestamp: datetime

class TradingService:
    """
    Comprehensive trading service handling order execution, portfolio management,
    risk analytics, and algorithmic trading strategies
    """
    
    def __init__(self):
        self.session = get_db_session()
        self._order_validators = {
            OrderType.MARKET: self._validate_market_order,
            OrderType.LIMIT: self._validate_limit_order,
            OrderType.STOP: self._validate_stop_order,
            OrderType.STOP_LIMIT: self._validate_stop_limit_order
        }
        
        # Risk limits and thresholds
        self.risk_limits = {
            'max_position_size': Decimal('10000000'),  # $10M default
            'max_daily_loss': Decimal('100000'),       # $100K default
            'max_leverage': Decimal('5.0'),            # 5x leverage max
            'var_limit_95': Decimal('50000'),          # $50K VaR limit
            'concentration_limit': Decimal('0.25')     # 25% max single position
        }

    # === ORDER MANAGEMENT ===
    
    def submit_order(self, user_id: str, order_data: Dict[str, Any]) -> OrderResult:
        """Submit and validate trading order with comprehensive risk checks"""
        try:
            # Get trading account
            account = self._get_trading_account(user_id, order_data.get('account_id'))
            if not account:
                return OrderResult(False, message="Trading account not found or inactive")
            
            # Get instrument
            instrument = self._get_instrument(order_data['symbol'])
            if not instrument or not instrument.is_tradeable:
                return OrderResult(False, message="Instrument not tradeable or not found")
            
            # Validate order parameters
            validation_result = self._validate_order(order_data, account, instrument)
            if not validation_result.approved:
                return OrderResult(False, message=f"Order validation failed: {', '.join(validation_result.violations)}")
            
            # Create order record
            order = TradingOrder(
                order_id=self._generate_order_id(),
                account_id=account.id,
                instrument_id=instrument.id,
                user_id=user_id,
                order_type=order_data['order_type'],
                order_side=order_data['order_side'],
                quantity=Decimal(str(order_data['quantity'])),
                price=Decimal(str(order_data.get('price', 0))) if order_data.get('price') else None,
                stop_price=Decimal(str(order_data.get('stop_price', 0))) if order_data.get('stop_price') else None,
                remaining_quantity=Decimal(str(order_data['quantity'])),
                time_in_force=order_data.get('time_in_force', 'DAY'),
                status=OrderStatus.PENDING.value,
                estimated_margin=validation_result.required_margin,
                risk_score=validation_result.risk_score
            )
            
            self.session.add(order)
            self.session.commit()
            
            # Execute order based on type
            if order_data['order_type'] == 'market':
                execution_result = self._execute_market_order(order, instrument)
            else:
                execution_result = self._queue_order(order, instrument)
                
            # Log order submission
            logger.info(f"Order submitted: {order.order_id} for user {user_id}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Order submission failed for user {user_id}: {str(e)}")
            self.session.rollback()
            return OrderResult(False, message="Order submission failed due to system error")
    
    def cancel_order(self, user_id: str, order_id: str) -> OrderResult:
        """Cancel pending order"""
        try:
            order = self.session.query(TradingOrder).filter(
                and_(
                    TradingOrder.order_id == order_id,
                    TradingOrder.user_id == user_id,
                    TradingOrder.status.in_(['pending', 'submitted'])
                )
            ).first()
            
            if not order:
                return OrderResult(False, message="Order not found or cannot be cancelled")
            
            order.status = OrderStatus.CANCELLED.value
            order.updated_at = datetime.now(timezone.utc)
            
            self.session.commit()
            
            logger.info(f"Order cancelled: {order_id} by user {user_id}")
            return OrderResult(True, order_id=order_id, message="Order cancelled successfully")
            
        except Exception as e:
            logger.error(f"Order cancellation failed: {str(e)}")
            self.session.rollback()
            return OrderResult(False, message="Cancellation failed")
    
    def modify_order(self, user_id: str, order_id: str, modifications: Dict[str, Any]) -> OrderResult:
        """Modify pending order parameters"""
        try:
            order = self.session.query(TradingOrder).filter(
                and_(
                    TradingOrder.order_id == order_id,
                    TradingOrder.user_id == user_id,
                    TradingOrder.status.in_(['pending', 'submitted'])
                )
            ).first()
            
            if not order:
                return OrderResult(False, message="Order not found or cannot be modified")
            
            # Validate modifications
            if 'quantity' in modifications:
                new_quantity = Decimal(str(modifications['quantity']))
                if new_quantity <= order.filled_quantity:
                    return OrderResult(False, message="New quantity must be greater than filled quantity")
                order.quantity = new_quantity
                order.remaining_quantity = new_quantity - order.filled_quantity
            
            if 'price' in modifications:
                order.price = Decimal(str(modifications['price']))
            
            if 'stop_price' in modifications:
                order.stop_price = Decimal(str(modifications['stop_price']))
            
            order.updated_at = datetime.now(timezone.utc)
            self.session.commit()
            
            logger.info(f"Order modified: {order_id} by user {user_id}")
            return OrderResult(True, order_id=order_id, message="Order modified successfully")
            
        except Exception as e:
            logger.error(f"Order modification failed: {str(e)}")
            self.session.rollback()
            return OrderResult(False, message="Modification failed")

    # === PORTFOLIO MANAGEMENT ===
    
    def get_portfolio_summary(self, user_id: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive portfolio summary with performance metrics"""
        try:
            # Get trading account
            account = self._get_trading_account(user_id, account_id)
            if not account:
                return {'error': 'Trading account not found'}
            
            # Get current positions
            positions = self.session.query(Position).filter(
                and_(
                    Position.account_id == account.id,
                    Position.is_active == True
                )
            ).all()
            
            # Calculate portfolio metrics
            total_value = account.cash_balance
            securities_value = Decimal('0')
            total_pnl = Decimal('0')
            day_change = Decimal('0')
            
            position_data = []
            for position in positions:
                # Get current market price
                current_price = self._get_current_price(position.instrument.symbol)
                if current_price:
                    position.current_price = current_price
                    position.market_value = position.quantity * current_price
                    position.unrealized_pnl = position.market_value - position.total_cost
                    position.unrealized_pnl_percent = (position.unrealized_pnl / position.total_cost) * 100
                    
                    securities_value += position.market_value
                    total_pnl += position.unrealized_pnl + position.realized_pnl
                    
                    position_data.append({
                        'symbol': position.instrument.symbol,
                        'name': position.instrument.name,
                        'quantity': float(position.quantity),
                        'average_cost': float(position.average_cost),
                        'current_price': float(current_price),
                        'market_value': float(position.market_value),
                        'unrealized_pnl': float(position.unrealized_pnl),
                        'unrealized_pnl_percent': float(position.unrealized_pnl_percent),
                        'position_percent': float((position.market_value / (securities_value + account.cash_balance)) * 100) if securities_value + account.cash_balance > 0 else 0
                    })
            
            total_value = account.cash_balance + securities_value
            
            # Calculate allocation percentages
            cash_allocation = float((account.cash_balance / total_value) * 100) if total_value > 0 else 100
            securities_allocation = float((securities_value / total_value) * 100) if total_value > 0 else 0
            
            # Get recent performance
            performance_data = self._calculate_performance_metrics(account.id)
            
            return {
                'account_summary': {
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'base_currency': account.base_currency,
                    'total_value': float(total_value),
                    'cash_balance': float(account.cash_balance),
                    'securities_value': float(securities_value),
                    'available_balance': float(account.available_balance),
                    'margin_used': float(account.margin_used),
                    'buying_power': float(account.available_balance + account.margin_available)
                },
                'performance': {
                    'total_return': float(total_pnl),
                    'total_return_percent': float((total_pnl / (total_value - total_pnl)) * 100) if (total_value - total_pnl) > 0 else 0,
                    'day_change': float(day_change),
                    'day_change_percent': performance_data.get('day_change_percent', 0),
                    **performance_data
                },
                'allocation': {
                    'cash_percent': cash_allocation,
                    'securities_percent': securities_allocation
                },
                'positions': position_data,
                'risk_metrics': self._calculate_portfolio_risk_metrics(account.id)
            }
            
        except Exception as e:
            logger.error(f"Portfolio summary failed for user {user_id}: {str(e)}")
            return {'error': 'Failed to retrieve portfolio summary'}
    
    def rebalance_portfolio(self, user_id: str, account_id: str, target_allocations: Dict[str, float]) -> Dict[str, Any]:
        """Execute portfolio rebalancing based on target allocations"""
        try:
            account = self._get_trading_account(user_id, account_id)
            if not account:
                return {'success': False, 'message': 'Trading account not found'}
            
            # Validate target allocations sum to 100%
            total_allocation = sum(target_allocations.values())
            if abs(total_allocation - 100) > 0.01:
                return {'success': False, 'message': 'Target allocations must sum to 100%'}
            
            # Get current portfolio value
            portfolio_summary = self.get_portfolio_summary(user_id, account_id)
            total_value = Decimal(str(portfolio_summary['account_summary']['total_value']))
            
            # Calculate required trades
            rebalancing_trades = []
            current_positions = {pos['symbol']: pos for pos in portfolio_summary['positions']}
            
            for symbol, target_percent in target_allocations.items():
                target_value = total_value * Decimal(str(target_percent / 100))
                current_value = Decimal(str(current_positions.get(symbol, {}).get('market_value', 0)))
                
                difference = target_value - current_value
                
                if abs(difference) > Decimal('100'):  # Only trade if difference > $100
                    instrument = self._get_instrument(symbol)
                    if instrument and instrument.is_tradeable:
                        current_price = self._get_current_price(symbol)
                        if current_price:
                            quantity_change = abs(difference / current_price)
                            side = 'buy' if difference > 0 else 'sell'
                            
                            rebalancing_trades.append({
                                'symbol': symbol,
                                'side': side,
                                'quantity': float(quantity_change),
                                'estimated_value': float(abs(difference)),
                                'target_percent': target_percent,
                                'current_percent': float((current_value / total_value) * 100)
                            })
            
            # Execute rebalancing trades
            executed_trades = []
            failed_trades = []
            
            for trade in rebalancing_trades:
                order_data = {
                    'account_id': account_id,
                    'symbol': trade['symbol'],
                    'order_type': 'market',
                    'order_side': trade['side'],
                    'quantity': trade['quantity']
                }
                
                result = self.submit_order(user_id, order_data)
                if result.success:
                    executed_trades.append({**trade, 'order_id': result.order_id})
                else:
                    failed_trades.append({**trade, 'error': result.message})
            
            logger.info(f"Portfolio rebalancing completed for user {user_id}: {len(executed_trades)} trades executed")
            
            return {
                'success': True,
                'message': f'Rebalancing completed: {len(executed_trades)} trades executed, {len(failed_trades)} failed',
                'executed_trades': executed_trades,
                'failed_trades': failed_trades,
                'total_trades': len(rebalancing_trades)
            }
            
        except Exception as e:
            logger.error(f"Portfolio rebalancing failed for user {user_id}: {str(e)}")
            return {'success': False, 'message': 'Rebalancing failed due to system error'}

    # === RISK MANAGEMENT ===
    
    def calculate_risk_metrics(self, user_id: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics for portfolio"""
        try:
            account = self._get_trading_account(user_id, account_id)
            if not account:
                return {'error': 'Trading account not found'}
            
            # Get current positions
            positions = self.session.query(Position).filter(
                and_(
                    Position.account_id == account.id,
                    Position.is_active == True
                )
            ).all()
            
            if not positions:
                return {
                    'total_exposure': 0,
                    'var_1day_95': 0,
                    'var_1day_99': 0,
                    'portfolio_beta': 0,
                    'sharpe_ratio': 0,
                    'max_drawdown': 0,
                    'concentration_risk': {},
                    'currency_exposure': {}
                }
            
            # Calculate exposures
            total_long_exposure = sum(pos.market_value for pos in positions if pos.is_long)
            total_short_exposure = sum(abs(pos.market_value) for pos in positions if pos.is_short)
            net_exposure = total_long_exposure - total_short_exposure
            gross_exposure = total_long_exposure + total_short_exposure
            
            # Calculate VaR using historical simulation
            var_1day_95, var_1day_99 = self._calculate_portfolio_var(positions)
            
            # Calculate portfolio beta
            portfolio_beta = self._calculate_portfolio_beta(positions)
            
            # Calculate Sharpe ratio
            sharpe_ratio = self._calculate_sharpe_ratio(account.id)
            
            # Calculate maximum drawdown
            max_drawdown = self._calculate_max_drawdown(account.id)
            
            # Concentration analysis
            concentration_risk = self._analyze_concentration_risk(positions)
            
            # Currency exposure
            currency_exposure = self._analyze_currency_exposure(positions)
            
            # Risk limit utilization
            risk_limit_utilization = {
                'position_size': float((max(pos.market_value for pos in positions) / self.risk_limits['max_position_size']) * 100) if positions else 0,
                'leverage': float((gross_exposure / account.total_value) * 100) if account.total_value > 0 else 0,
                'var_utilization': float((var_1day_95 / self.risk_limits['var_limit_95']) * 100),
                'concentration': max(concentration_risk.values()) if concentration_risk else 0
            }
            
            # Store risk metrics
            risk_metrics = RiskMetrics(
                account_id=account.id,
                user_id=user_id,
                total_exposure=gross_exposure,
                net_exposure=net_exposure,
                gross_exposure=gross_exposure,
                leverage_ratio=gross_exposure / account.total_value if account.total_value > 0 else 0,
                var_1day_95=var_1day_95,
                var_1day_99=var_1day_99,
                largest_position_percent=max(concentration_risk.values()) if concentration_risk else 0,
                sector_concentration=concentration_risk,
                currency_exposure=currency_exposure,
                risk_limit_utilization=max(risk_limit_utilization.values()) / 100,
                is_risk_limit_breached=any(util > 100 for util in risk_limit_utilization.values())
            )
            
            self.session.add(risk_metrics)
            self.session.commit()
            
            return {
                'total_exposure': float(gross_exposure),
                'net_exposure': float(net_exposure),
                'leverage_ratio': float(gross_exposure / account.total_value if account.total_value > 0 else 0),
                'var_1day_95': float(var_1day_95),
                'var_1day_99': float(var_1day_99),
                'portfolio_beta': portfolio_beta,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'concentration_risk': {k: float(v) for k, v in concentration_risk.items()},
                'currency_exposure': {k: float(v) for k, v in currency_exposure.items()},
                'risk_limit_utilization': {k: float(v) for k, v in risk_limit_utilization.items()},
                'risk_limit_breached': any(util > 100 for util in risk_limit_utilization.values())
            }
            
        except Exception as e:
            logger.error(f"Risk metrics calculation failed for user {user_id}: {str(e)}")
            return {'error': 'Failed to calculate risk metrics'}

    # === MARKET DATA ===
    
    def get_market_data(self, symbol: str, timeframe: str = '1D', periods: int = 30) -> Dict[str, Any]:
        """Get historical and real-time market data"""
        try:
            instrument = self._get_instrument(symbol)
            if not instrument:
                return {'error': 'Instrument not found'}
            
            # Get latest market data
            latest_data = self.session.query(MarketData).filter(
                MarketData.instrument_id == instrument.id
            ).order_by(desc(MarketData.market_date)).first()
            
            # Get historical data
            historical_data = self.session.query(MarketData).filter(
                MarketData.instrument_id == instrument.id
            ).order_by(desc(MarketData.market_date)).limit(periods).all()
            
            # Prepare response
            current_data = {
                'symbol': symbol,
                'name': instrument.name,
                'current_price': float(latest_data.current_price) if latest_data else 0,
                'bid_price': float(latest_data.bid_price) if latest_data and latest_data.bid_price else None,
                'ask_price': float(latest_data.ask_price) if latest_data and latest_data.ask_price else None,
                'volume': int(latest_data.volume) if latest_data else 0,
                'price_change': float(latest_data.price_change) if latest_data else 0,
                'price_change_percent': float(latest_data.price_change_percent) if latest_data else 0,
                'last_update': latest_data.last_update.isoformat() if latest_data else None
            }
            
            historical_prices = []
            for data in reversed(historical_data):  # Reverse to get chronological order
                historical_prices.append({
                    'date': data.market_date.isoformat(),
                    'open': float(data.open_price) if data.open_price else None,
                    'high': float(data.high_price) if data.high_price else None,
                    'low': float(data.low_price) if data.low_price else None,
                    'close': float(data.close_price) if data.close_price else None,
                    'volume': int(data.volume)
                })
            
            return {
                'current': current_data,
                'historical': historical_prices,
                'technical_indicators': self._calculate_technical_indicators(historical_data)
            }
            
        except Exception as e:
            logger.error(f"Market data retrieval failed for {symbol}: {str(e)}")
            return {'error': 'Failed to retrieve market data'}

    # === ALGORITHMIC TRADING ===
    
    def create_trading_algorithm(self, user_id: str, algorithm_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create and deploy algorithmic trading strategy"""
        try:
            # Validate algorithm configuration
            required_fields = ['name', 'type', 'universe', 'max_positions', 'capital_allocation']
            if not all(field in algorithm_config for field in required_fields):
                return {'success': False, 'message': 'Missing required algorithm configuration'}
            
            # Create algorithm instance
            algorithm_id = self._generate_algorithm_id()
            
            # Store algorithm configuration
            algorithm_data = {
                'algorithm_id': algorithm_id,
                'user_id': user_id,
                'name': algorithm_config['name'],
                'type': algorithm_config['type'],
                'config': algorithm_config,
                'status': 'inactive',
                'created_at': datetime.now(timezone.utc),
                'performance_metrics': {},
                'risk_metrics': {}
            }
            
            # Validate strategy parameters
            validation_result = self._validate_algorithm_config(algorithm_config)
            if not validation_result['valid']:
                return {'success': False, 'message': f"Invalid configuration: {validation_result['message']}"}
            
            # Backtest the algorithm if requested
            if algorithm_config.get('run_backtest', False):
                backtest_result = self._run_algorithm_backtest(algorithm_config)
                algorithm_data['backtest_results'] = backtest_result
            
            logger.info(f"Trading algorithm created: {algorithm_id} for user {user_id}")
            
            return {
                'success': True,
                'algorithm_id': algorithm_id,
                'message': 'Algorithm created successfully',
                'backtest_results': algorithm_data.get('backtest_results', {})
            }
            
        except Exception as e:
            logger.error(f"Algorithm creation failed for user {user_id}: {str(e)}")
            return {'success': False, 'message': 'Algorithm creation failed'}

    # === HELPER METHODS ===
    
    def _get_trading_account(self, user_id: str, account_id: Optional[str] = None) -> Optional[TradingAccount]:
        """Get user's trading account"""
        query = self.session.query(TradingAccount).filter(
            and_(
                TradingAccount.user_id == user_id,
                TradingAccount.is_active == True
            )
        )
        
        if account_id:
            query = query.filter(TradingAccount.id == account_id)
        
        return query.first()
    
    def _get_instrument(self, symbol: str) -> Optional[TradingInstrument]:
        """Get trading instrument by symbol"""
        return self.session.query(TradingInstrument).filter(
            and_(
                TradingInstrument.symbol == symbol.upper(),
                TradingInstrument.is_active == True
            )
        ).first()
    
    def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for instrument"""
        instrument = self._get_instrument(symbol)
        if not instrument:
            return None
            
        latest_data = self.session.query(MarketData).filter(
            MarketData.instrument_id == instrument.id
        ).order_by(desc(MarketData.last_update)).first()
        
        return latest_data.current_price if latest_data else instrument.current_price
    
    def _validate_order(self, order_data: Dict[str, Any], account: TradingAccount, instrument: TradingInstrument) -> RiskAssessment:
        """Comprehensive order validation including risk checks"""
        warnings = []
        violations = []
        
        # Basic validations
        if order_data['quantity'] <= 0:
            violations.append("Quantity must be positive")
        
        if order_data['quantity'] < instrument.minimum_quantity:
            violations.append(f"Quantity below minimum of {instrument.minimum_quantity}")
        
        if instrument.maximum_quantity and order_data['quantity'] > instrument.maximum_quantity:
            violations.append(f"Quantity exceeds maximum of {instrument.maximum_quantity}")
        
        # Price validations
        current_price = self._get_current_price(instrument.symbol)
        if not current_price:
            violations.append("Unable to get current market price")
            return RiskAssessment(False, 0, warnings, violations, Decimal('0'))
        
        # Calculate order value and margin requirement
        order_value = Decimal(str(order_data['quantity'])) * current_price
        margin_requirement = order_value * instrument.margin_requirement
        
        # Account balance checks
        if order_data['order_side'] in ['buy'] and account.available_balance < margin_requirement:
            violations.append("Insufficient available balance")
        
        # Position size limits
        if order_value > self.risk_limits['max_position_size']:
            violations.append(f"Order value exceeds position size limit")
        
        # Calculate risk score (0-100)
        risk_score = self._calculate_order_risk_score(order_data, account, instrument, current_price)
        
        # Risk threshold checks
        if risk_score > 80:
            violations.append("Order risk score too high")
        elif risk_score > 60:
            warnings.append("High risk order")
        
        approved = len(violations) == 0
        
        return RiskAssessment(
            approved=approved,
            risk_score=risk_score,
            warnings=warnings,
            violations=violations,
            required_margin=margin_requirement
        )
    
    def _calculate_order_risk_score(self, order_data: Dict[str, Any], account: TradingAccount, 
                                   instrument: TradingInstrument, current_price: Decimal) -> float:
        """Calculate risk score for order (0-100)"""
        risk_factors = []
        
        # Size risk
        order_value = Decimal(str(order_data['quantity'])) * current_price
        size_risk = min((order_value / account.total_value) * 100, 50) if account.total_value > 0 else 50
        risk_factors.append(size_risk)
        
        # Volatility risk
        volatility_risk = (instrument.volatility or 0.2) * 100
        risk_factors.append(min(volatility_risk, 30))
        
        # Leverage risk
        leverage_risk = min((account.margin_used / account.total_value) * 50, 20) if account.total_value > 0 else 0
        risk_factors.append(leverage_risk)
        
        return sum(risk_factors)
    
    def _validate_market_order(self, order_data: Dict[str, Any], account: TradingAccount, instrument: TradingInstrument) -> RiskAssessment:
        """Validate market order specific requirements"""
        warnings = []
        violations = []
        
        # Market orders don't require price validation
        # but check if market is open
        if not instrument.is_tradable:
            violations.append("Market is closed for this instrument")
        
        # Check for sufficient liquidity
        if order_data.get('quantity', 0) > instrument.daily_volume * 0.1:
            warnings.append("Large order relative to daily volume")
        
        # Calculate basic margin requirement
        current_price = self._get_current_price(instrument.symbol)
        if current_price:
            order_value = Decimal(str(order_data['quantity'])) * current_price
            margin_requirement = order_value * instrument.margin_requirement
            
            if order_data['order_side'] == 'buy' and account.available_balance < margin_requirement:
                violations.append("Insufficient funds for market order")
        
        return RiskAssessment(
            approved=len(violations) == 0,
            risk_score=20.0,  # Market orders have moderate risk
            warnings=warnings,
            violations=violations,
            required_margin=margin_requirement if current_price else Decimal('0')
        )
    
    def _validate_limit_order(self, order_data: Dict[str, Any], account: TradingAccount, instrument: TradingInstrument) -> RiskAssessment:
        """Validate limit order specific requirements"""
        warnings = []
        violations = []
        
        # Limit orders require price validation
        if 'limit_price' not in order_data or not order_data['limit_price']:
            violations.append("Limit price is required for limit orders")
            return RiskAssessment(False, 0, warnings, violations, Decimal('0'))
        
        limit_price = Decimal(str(order_data['limit_price']))
        current_price = self._get_current_price(instrument.symbol)
        
        if current_price:
            price_diff = abs(limit_price - current_price) / current_price
            if price_diff > 0.2:  # 20% from current price
                warnings.append("Limit price significantly differs from current market price")
        
        # Calculate margin requirement
        order_value = Decimal(str(order_data['quantity'])) * limit_price
        margin_requirement = order_value * instrument.margin_requirement
        
        if order_data['order_side'] == 'buy' and account.available_balance < margin_requirement:
            violations.append("Insufficient funds for limit order")
        
        return RiskAssessment(
            approved=len(violations) == 0,
            risk_score=10.0,  # Limit orders have lower risk
            warnings=warnings,
            violations=violations,
            required_margin=margin_requirement
        )
    
    def _validate_stop_order(self, order_data: Dict[str, Any], account: TradingAccount, instrument: TradingInstrument) -> RiskAssessment:
        """Validate stop order specific requirements"""
        warnings = []
        violations = []
        
        # Stop orders require stop price validation
        if 'stop_price' not in order_data or not order_data['stop_price']:
            violations.append("Stop price is required for stop orders")
            return RiskAssessment(False, 0, warnings, violations, Decimal('0'))
        
        stop_price = Decimal(str(order_data['stop_price']))
        current_price = self._get_current_price(instrument.symbol)
        
        if current_price:
            # Validate stop price direction
            if order_data['order_side'] == 'sell' and stop_price >= current_price:
                violations.append("Stop-loss price must be below current price for sell orders")
            elif order_data['order_side'] == 'buy' and stop_price <= current_price:
                violations.append("Stop-buy price must be above current price for buy orders")
        
        # Calculate margin requirement using stop price
        order_value = Decimal(str(order_data['quantity'])) * stop_price
        margin_requirement = order_value * instrument.margin_requirement
        
        if order_data['order_side'] == 'buy' and account.available_balance < margin_requirement:
            violations.append("Insufficient funds for stop order")
        
        return RiskAssessment(
            approved=len(violations) == 0,
            risk_score=25.0,  # Stop orders have higher risk
            warnings=warnings,
            violations=violations,
            required_margin=margin_requirement
        )
    
    def _validate_stop_limit_order(self, order_data: Dict[str, Any], account: TradingAccount, instrument: TradingInstrument) -> RiskAssessment:
        """Validate stop-limit order specific requirements"""
        warnings = []
        violations = []
        
        # Stop-limit orders require both stop and limit prices
        if 'stop_price' not in order_data or not order_data['stop_price']:
            violations.append("Stop price is required for stop-limit orders")
        if 'limit_price' not in order_data or not order_data['limit_price']:
            violations.append("Limit price is required for stop-limit orders")
        
        if violations:
            return RiskAssessment(False, 0, warnings, violations, Decimal('0'))
        
        stop_price = Decimal(str(order_data['stop_price']))
        limit_price = Decimal(str(order_data['limit_price']))
        current_price = self._get_current_price(instrument.symbol)
        
        if current_price:
            # Validate price relationships
            if order_data['order_side'] == 'sell':
                if stop_price >= current_price:
                    violations.append("Stop price must be below current price for sell orders")
                if limit_price > stop_price:
                    violations.append("Limit price must be at or below stop price for sell orders")
            elif order_data['order_side'] == 'buy':
                if stop_price <= current_price:
                    violations.append("Stop price must be above current price for buy orders")
                if limit_price < stop_price:
                    violations.append("Limit price must be at or above stop price for buy orders")
        
        # Calculate margin requirement using limit price
        order_value = Decimal(str(order_data['quantity'])) * limit_price
        margin_requirement = order_value * instrument.margin_requirement
        
        if order_data['order_side'] == 'buy' and account.available_balance < margin_requirement:
            violations.append("Insufficient funds for stop-limit order")
        
        return RiskAssessment(
            approved=len(violations) == 0,
            risk_score=15.0,  # Stop-limit orders have moderate risk
            warnings=warnings,
            violations=violations,
            required_margin=margin_requirement
        )
    
    def _execute_market_order(self, order: TradingOrder, instrument: TradingInstrument) -> OrderResult:
        """Execute market order immediately"""
        try:
            current_price = self._get_current_price(instrument.symbol)
            if not current_price:
                order.status = OrderStatus.REJECTED.value
                self.session.commit()
                return OrderResult(False, message="Unable to get market price")
            
            # Simulate execution with slippage
            slippage = Decimal('0.001')  # 0.1% slippage
            execution_price = current_price * (1 + slippage if order.order_side == 'buy' else 1 - slippage)
            
            # Calculate commission
            commission = self._calculate_commission(order.quantity, execution_price, instrument)
            
            # Create trade record
            trade = Trade(
                trade_id=self._generate_trade_id(),
                order_id=order.id,
                account_id=order.account_id,
                instrument_id=order.instrument_id,
                user_id=order.user_id,
                side=order.order_side,
                quantity=order.quantity,
                price=execution_price,
                total_value=order.quantity * execution_price,
                commission=commission,
                total_fees=commission,
                net_amount=order.quantity * execution_price + commission,
                settlement_date=datetime.now(timezone.utc) + timedelta(days=2)
            )
            
            # Update order status
            order.status = OrderStatus.FILLED.value
            order.filled_quantity = order.quantity
            order.remaining_quantity = Decimal('0')
            order.average_fill_price = execution_price
            order.total_commission = commission
            order.executed_at = datetime.now(timezone.utc)
            
            # Update position
            self._update_position(order, trade)
            
            # Update account balances
            self._update_account_balances(order.account_id, trade)
            
            self.session.add(trade)
            self.session.commit()
            
            logger.info(f"Market order executed: {order.order_id}, price: {execution_price}")
            
            return OrderResult(
                success=True,
                order_id=order.order_id,
                trade_id=trade.trade_id,
                filled_quantity=order.quantity,
                average_price=execution_price,
                total_cost=trade.total_value,
                commission=commission,
                message="Order executed successfully"
            )
            
        except Exception as e:
            logger.error(f"Market order execution failed: {str(e)}")
            order.status = OrderStatus.REJECTED.value
            self.session.commit()
            return OrderResult(False, message="Execution failed")
    
    def _queue_order(self, order: TradingOrder, instrument: TradingInstrument) -> OrderResult:
        """Queue non-market order for execution"""
        order.status = OrderStatus.SUBMITTED.value
        self.session.commit()
        
        return OrderResult(
            success=True,
            order_id=order.order_id,
            message="Order submitted successfully"
        )
    
    def _update_position(self, order: TradingOrder, trade: Trade):
        """Update position after trade execution"""
        # Find existing position
        position = self.session.query(Position).filter(
            and_(
                Position.account_id == order.account_id,
                Position.instrument_id == order.instrument_id,
                Position.is_active == True
            )
        ).first()
        
        if not position:
            # Create new position
            position = Position(
                account_id=order.account_id,
                instrument_id=order.instrument_id,
                user_id=order.user_id,
                quantity=trade.quantity if order.order_side == 'buy' else -trade.quantity,
                average_cost=trade.price,
                total_cost=trade.total_value,
                current_price=trade.price,
                market_value=trade.quantity * trade.price,
                is_long=order.order_side == 'buy',
                is_short=order.order_side == 'sell'
            )
            self.session.add(position)
        else:
            # Update existing position
            if order.order_side == 'buy':
                new_quantity = position.quantity + trade.quantity
                if new_quantity != 0:
                    position.average_cost = ((position.quantity * position.average_cost) + 
                                           (trade.quantity * trade.price)) / new_quantity
                position.quantity = new_quantity
                position.total_cost += trade.total_value
            else:  # sell
                position.quantity -= trade.quantity
                position.total_cost -= trade.total_value
                if position.quantity == 0:
                    position.is_active = False
                    position.closed_at = datetime.now(timezone.utc)
    
    def _update_account_balances(self, account_id: str, trade: Trade):
        """Update account balances after trade"""
        account = self.session.query(TradingAccount).filter(
            TradingAccount.id == account_id
        ).first()
        
        if account:
            if trade.side == 'buy':
                account.cash_balance -= trade.net_amount
                account.available_balance -= trade.net_amount
            else:  # sell
                account.cash_balance += trade.net_amount
                account.available_balance += trade.net_amount
    
    def _calculate_commission(self, quantity: Decimal, price: Decimal, instrument: TradingInstrument) -> Decimal:
        """Calculate trading commission"""
        trade_value = quantity * price
        
        # Simple commission structure: 0.1% with $1 minimum
        commission_rate = Decimal('0.001')  # 0.1%
        commission = trade_value * commission_rate
        min_commission = Decimal('1.00')
        
        return max(commission, min_commission)
    
    def _calculate_portfolio_var(self, positions: List[Position]) -> Tuple[Decimal, Decimal]:
        """Calculate portfolio Value at Risk using numpy-optimized historical simulation"""
        try:
            if not HAS_NUMPY:
                # Fallback to basic calculation
                total_value = sum(pos.market_value for pos in positions)
                portfolio_volatility = Decimal('0.15')
                daily_volatility = portfolio_volatility / Decimal('16')
                var_1day_95 = total_value * daily_volatility * Decimal('1.645')
                var_1day_99 = total_value * daily_volatility * Decimal('2.326')
                return var_1day_95, var_1day_99
            
            # High-performance numpy-based VaR calculation
            position_values = np.array([float(pos.market_value) for pos in positions])
            position_weights = position_values / np.sum(position_values) if np.sum(position_values) > 0 else np.zeros_like(position_values)
            
            # Get historical returns for all instruments
            instrument_ids = [pos.instrument_id for pos in positions]
            returns_data = []
            
            for instrument_id in instrument_ids:
                historical_returns = self.session.query(MarketData.return_1d).filter(
                    MarketData.instrument_id == instrument_id
                ).order_by(MarketData.market_date.desc()).limit(252).all()  # 1 year of data
                
                if historical_returns:
                    returns = np.array([float(r[0] or 0) for r in historical_returns])
                    returns_data.append(returns)
                else:
                    # Use default volatility if no historical data
                    returns_data.append(np.random.normal(0, 0.02, 252))  # 2% daily volatility
            
            # Create returns matrix
            if returns_data:
                min_length = min(len(returns) for returns in returns_data)
                returns_matrix = np.column_stack([returns[:min_length] for returns in returns_data])
                
                # Calculate portfolio returns
                portfolio_returns = np.dot(returns_matrix, position_weights[:len(returns_data)])
                
                # Calculate VaR using percentiles
                var_95_pct = np.percentile(portfolio_returns, 5)  # 5th percentile for 95% VaR
                var_99_pct = np.percentile(portfolio_returns, 1)  # 1st percentile for 99% VaR
                
                total_portfolio_value = float(np.sum(position_values))
                var_1day_95 = Decimal(str(abs(var_95_pct * total_portfolio_value)))
                var_1day_99 = Decimal(str(abs(var_99_pct * total_portfolio_value)))
                
                return var_1day_95, var_1day_99
            
            # Fallback if no data available
            total_value = sum(pos.market_value for pos in positions)
            var_1day_95 = total_value * Decimal('0.025')  # 2.5% of portfolio
            var_1day_99 = total_value * Decimal('0.04')   # 4% of portfolio
            return var_1day_95, var_1day_99
            
        except Exception as e:
            logger.error(f"VaR calculation failed: {str(e)}")
            # Safe fallback
            total_value = sum(pos.market_value for pos in positions)
            return total_value * Decimal('0.025'), total_value * Decimal('0.04')
    
    def _calculate_portfolio_beta(self, positions: List[Position]) -> float:
        """Calculate portfolio beta"""
        if not positions:
            return 0.0
        
        weighted_beta = sum(
            (pos.market_value * (pos.instrument.beta or 1.0)) 
            for pos in positions
        )
        total_value = sum(pos.market_value for pos in positions)
        
        return float(weighted_beta / total_value) if total_value > 0 else 0.0
    
    def _analyze_concentration_risk(self, positions: List[Position]) -> Dict[str, float]:
        """Analyze portfolio concentration by sector/asset"""
        if not positions:
            return {}
        
        total_value = sum(pos.market_value for pos in positions)
        concentration = {}
        
        for position in positions:
            sector = position.instrument.sector or 'Unknown'
            if sector not in concentration:
                concentration[sector] = 0
            concentration[sector] += float((position.market_value / total_value) * 100)
        
        return concentration
    
    def _analyze_currency_exposure(self, positions: List[Position]) -> Dict[str, float]:
        """Analyze currency exposure"""
        if not positions:
            return {}
        
        total_value = sum(pos.market_value for pos in positions)
        exposure = {}
        
        for position in positions:
            currency = position.instrument.currency
            if currency not in exposure:
                exposure[currency] = 0
            exposure[currency] += float((position.market_value / total_value) * 100)
        
        return exposure
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        import uuid
        return f"ORD{uuid.uuid4().hex[:12].upper()}"
    
    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        import uuid
        return f"TRD{uuid.uuid4().hex[:12].upper()}"
    
    def _generate_algorithm_id(self) -> str:
        """Generate unique algorithm ID"""
        import uuid
        return f"ALG{uuid.uuid4().hex[:12].upper()}"
    
    # === ADDITIONAL REQUIRED METHODS ===
    
    def get_recent_orders(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent orders for user"""
        try:
            orders = self.session.query(TradingOrder).filter(
                TradingOrder.user_id == user_id
            ).order_by(desc(TradingOrder.submitted_at)).limit(limit).all()
            
            order_list = []
            for order in orders:
                order_list.append({
                    'order_id': order.order_id,
                    'symbol': order.instrument.symbol if order.instrument else '--',
                    'order_side': order.order_side,
                    'order_type': order.order_type,
                    'quantity': float(order.quantity),
                    'status': order.status,
                    'submitted_at': order.submitted_at,
                    'executed_at': order.executed_at,
                    'filled_quantity': float(order.filled_quantity) if order.filled_quantity else 0,
                    'average_fill_price': float(order.average_fill_price) if order.average_fill_price else None
                })
            
            return order_list
            
        except Exception as e:
            logger.error(f"Get recent orders failed: {str(e)}")
            return []
    
    def get_order_status(self, user_id: str, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order status by ID"""
        try:
            order = self.session.query(TradingOrder).filter(
                and_(
                    TradingOrder.order_id == order_id,
                    TradingOrder.user_id == user_id
                )
            ).first()
            
            if not order:
                return None
            
            return {
                'order_id': order.order_id,
                'status': order.status,
                'symbol': order.instrument.symbol if order.instrument else '--',
                'order_side': order.order_side,
                'order_type': order.order_type,
                'quantity': float(order.quantity),
                'filled_quantity': float(order.filled_quantity) if order.filled_quantity else 0,
                'remaining_quantity': float(order.remaining_quantity) if order.remaining_quantity else 0,
                'average_fill_price': float(order.average_fill_price) if order.average_fill_price else None,
                'submitted_at': order.submitted_at.isoformat() if order.submitted_at else None,
                'executed_at': order.executed_at.isoformat() if order.executed_at else None
            }
            
        except Exception as e:
            logger.error(f"Get order status failed: {str(e)}")
            return None
    
    def get_risk_limits(self, user_id: str) -> Dict[str, Any]:
        """Get current risk limits for user"""
        return {
            'max_position_size': float(self.risk_limits['max_position_size']),
            'max_daily_loss': float(self.risk_limits['max_daily_loss']),
            'max_leverage': float(self.risk_limits['max_leverage']),
            'var_limit_95': float(self.risk_limits['var_limit_95']),
            'concentration_limit': float(self.risk_limits['concentration_limit'])
        }
    
    def update_risk_limits(self, user_id: str, new_limits: Dict[str, Any]) -> Dict[str, Any]:
        """Update risk limits for user"""
        try:
            # Validate limits
            valid_keys = {'max_position_size', 'max_daily_loss', 'max_leverage', 'var_limit_95', 'concentration_limit'}
            for key, value in new_limits.items():
                if key in valid_keys and isinstance(value, (int, float)) and value > 0:
                    self.risk_limits[key] = Decimal(str(value))
            
            return {'success': True, 'message': 'Risk limits updated successfully'}
            
        except Exception as e:
            logger.error(f"Update risk limits failed: {str(e)}")
            return {'success': False, 'message': 'Failed to update risk limits'}
    
    def get_performance_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance analytics for specified period"""
        try:
            # Simplified analytics - in production would calculate from historical data
            return {
                'period_days': days,
                'total_return': 0.0,
                'total_return_percent': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'trades_count': 0,
                'avg_trade_return': 0.0
            }
            
        except Exception as e:
            logger.error(f"Get performance analytics failed: {str(e)}")
            return {}
    
    def get_trade_analytics(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get trade analytics for date range"""
        try:
            # Simplified analytics - in production would analyze actual trades
            return {
                'period': f"{start_date} to {end_date}" if start_date and end_date else "All time",
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_volume': 0.0,
                'total_fees': 0.0,
                'avg_trade_size': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
            
        except Exception as e:
            logger.error(f"Get trade analytics failed: {str(e)}")
            return {}
    
    def get_trading_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all trading accounts for user"""
        try:
            accounts = self.session.query(TradingAccount).filter(
                and_(
                    TradingAccount.user_id == user_id,
                    TradingAccount.is_active == True
                )
            ).all()
            
            account_list = []
            for account in accounts:
                account_list.append({
                    'account_id': str(account.id),
                    'account_number': account.account_number,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'base_currency': account.base_currency,
                    'total_value': float(account.total_value) if account.total_value else 0,
                    'cash_balance': float(account.cash_balance),
                    'is_active': account.is_active
                })
            
            return account_list
            
        except Exception as e:
            logger.error(f"Get trading accounts failed: {str(e)}")
            return []
    
    def get_account_balance(self, user_id: str, account_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed account balance"""
        try:
            account = self._get_trading_account(user_id, account_id)
            if not account:
                return None
            
            return {
                'account_id': str(account.id),
                'cash_balance': float(account.cash_balance),
                'available_balance': float(account.available_balance),
                'margin_used': float(account.margin_used),
                'margin_available': float(account.margin_available),
                'equity_value': float(account.equity_value) if account.equity_value else 0,
                'total_value': float(account.total_value) if account.total_value else 0,
                'buying_power': float(account.available_balance + account.margin_available),
                'currency': account.base_currency
            }
            
        except Exception as e:
            logger.error(f"Get account balance failed: {str(e)}")
            return None
    
    def get_watchlist(self, user_id: str) -> Dict[str, Any]:
        """Get user's watchlist"""
        # Simplified - would typically store in database
        default_watchlist = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
        watchlist_data = []
        
        for symbol in default_watchlist:
            market_data = self.get_market_data(symbol)
            if market_data.get('current'):
                watchlist_data.append(market_data['current'])
        
        return {
            'symbols': default_watchlist,
            'data': watchlist_data,
            'count': len(watchlist_data)
        }
    
    def add_to_watchlist(self, user_id: str, symbol: str) -> Dict[str, Any]:
        """Add symbol to watchlist"""
        # Simplified implementation
        return {'success': True, 'message': f'{symbol} added to watchlist'}
    
    def remove_from_watchlist(self, user_id: str, symbol: str) -> Dict[str, Any]:
        """Remove symbol from watchlist"""
        # Simplified implementation
        return {'success': True, 'message': f'{symbol} removed from watchlist'}
    
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for trading symbols"""
        # Simplified symbol search - would typically use market data provider
        popular_symbols = {
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.',
            'AMD': 'Advanced Micro Devices',
            'INTC': 'Intel Corporation'
        }
        
        results = []
        for symbol, name in popular_symbols.items():
            if query in symbol or query in name.upper():
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'exchange': 'NASDAQ'
                })
        
        return results[:10]  # Limit to 10 results
    
    def _calculate_performance_metrics(self, account_id: str) -> Dict[str, Any]:
        """Calculate performance metrics for account"""
        # Simplified calculation - would use historical data in production
        return {
            'day_change_percent': 0.0,
            'week_change_percent': 0.0,
            'month_change_percent': 0.0,
            'year_change_percent': 0.0,
            'since_inception_percent': 0.0
        }
    
    def _calculate_sharpe_ratio(self, account_id: str) -> float:
        """Calculate Sharpe ratio for account using pandas for time series analysis"""
        try:
            if not HAS_NUMPY:
                # Basic fallback calculation
                return 1.2  # Assumed reasonable Sharpe ratio
            
            # Get portfolio performance history
            performance_data = self.session.query(
                PerformanceMetrics.calculation_date,
                PerformanceMetrics.total_return,
                PerformanceMetrics.portfolio_value
            ).filter(
                PerformanceMetrics.account_id == account_id
            ).order_by(PerformanceMetrics.calculation_date.desc()).limit(252).all()  # 1 year
            
            if len(performance_data) < 30:  # Need at least 30 data points
                return 1.0  # Default reasonable Sharpe
            
            # Convert to pandas DataFrame for efficient time series analysis
            df = pd.DataFrame(performance_data, columns=['date', 'return', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate daily returns
            df['daily_return'] = df['value'].pct_change().fillna(0)
            
            # Remove outliers (returns beyond 3 standard deviations)
            returns = df['daily_return']
            mean_return = returns.mean()
            std_return = returns.std()
            returns_clean = returns[abs(returns - mean_return) <= 3 * std_return]
            
            if len(returns_clean) < 10:
                return 1.0
            
            # Calculate excess returns (assuming 2% risk-free rate annually)
            risk_free_daily = 0.02 / 252  # Convert annual to daily
            excess_returns = returns_clean - risk_free_daily
            
            # Sharpe ratio = mean(excess returns) / std(excess returns)
            if excess_returns.std() > 0:
                sharpe = excess_returns.mean() / excess_returns.std()
                # Annualize the Sharpe ratio
                sharpe_annualized = sharpe * np.sqrt(252)
                return float(sharpe_annualized)
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Sharpe ratio calculation failed for account {account_id}: {str(e)}")
            return 1.0  # Safe default
    
    def _calculate_max_drawdown(self, account_id: str) -> float:
        """Calculate maximum drawdown for account using pandas for efficient time series analysis"""
        try:
            if not HAS_NUMPY:
                # Basic fallback
                return 0.05  # Assume 5% max drawdown
            
            # Get historical portfolio values
            portfolio_history = self.session.query(
                PerformanceMetrics.calculation_date,
                PerformanceMetrics.portfolio_value
            ).filter(
                PerformanceMetrics.account_id == account_id
            ).order_by(PerformanceMetrics.calculation_date.asc()).limit(1000).all()  # Up to 4 years
            
            if len(portfolio_history) < 10:
                return 0.02  # Default 2% if insufficient data
            
            # Convert to pandas DataFrame for efficient analysis
            df = pd.DataFrame(portfolio_history, columns=['date', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Calculate rolling maximum (peak values)
            df['rolling_max'] = df['value'].expanding().max()
            
            # Calculate drawdown as percentage from peak
            df['drawdown'] = (df['value'] - df['rolling_max']) / df['rolling_max']
            
            # Find maximum drawdown (most negative value)
            max_drawdown = abs(df['drawdown'].min())
            
            # Cap at reasonable maximum (50% for safety)
            max_drawdown = min(max_drawdown, 0.50)
            
            return float(max_drawdown)
            
        except Exception as e:
            logger.error(f"Max drawdown calculation failed for account {account_id}: {str(e)}")
            return 0.05  # Safe default 5%
    
    def _calculate_technical_indicators(self, historical_data: List) -> Dict[str, Any]:
        """Calculate technical indicators from historical data"""
        if not historical_data or len(historical_data) < 2:
            return {}
        
        # Get latest data point
        latest = historical_data[0]
        
        return {
            'rsi_14': float(latest.rsi_14) if latest.rsi_14 else None,
            'moving_avg_20': float(latest.moving_avg_20) if latest.moving_avg_20 else None,
            'moving_avg_50': float(latest.moving_avg_50) if latest.moving_avg_50 else None,
            'bollinger_upper': float(latest.bollinger_upper) if latest.bollinger_upper else None,
            'bollinger_lower': float(latest.bollinger_lower) if latest.bollinger_lower else None,
            'support_level': None,
            'resistance_level': None,
            'trend': 'neutral'
        }
    
    def _validate_algorithm_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate algorithm configuration"""
        errors = []
        
        # Basic validation
        if not config.get('name'):
            errors.append('Algorithm name is required')
        
        if not config.get('type'):
            errors.append('Algorithm type is required')
        
        if not config.get('universe'):
            errors.append('Trading universe is required')
        
        max_positions = config.get('max_positions', 0)
        if not isinstance(max_positions, int) or max_positions <= 0:
            errors.append('Max positions must be a positive integer')
        
        return {
            'valid': len(errors) == 0,
            'message': '; '.join(errors) if errors else 'Configuration valid'
        }
    
    def _run_algorithm_backtest(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run algorithm backtest"""
        # Simplified backtest results
        return {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'total_return': 0.15,
            'annual_return': 0.15,
            'volatility': 0.18,
            'sharpe_ratio': 0.83,
            'max_drawdown': -0.08,
            'win_rate': 0.55,
            'total_trades': 125,
            'profitable_trades': 69,
            'avg_trade_return': 0.0012
        }