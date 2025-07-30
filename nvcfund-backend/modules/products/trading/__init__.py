"""
Trading Platform Module
Complete trading module with models, forms, routes, services, API endpoints, and templates
"""

from flask import Blueprint
import logging

from .routes import trading_bp
from .api.endpoints import trading_api_bp

logger = logging.getLogger(__name__)

def register_trading_module(app):
    """Register the Trading Module with the main application"""
    try:
        # Register main trading routes
        app.register_blueprint(trading_bp)
        
        # Register trading API endpoints
        app.register_blueprint(trading_api_bp)
        
        logger.info("✅ Trading module registered successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Trading module registration failed: {str(e)}")
        return False

def get_module_info():
    """Get module information"""
    return {
        'name': 'trading',
        'version': '1.0.0',
        'description': 'Advanced Trading Platform Module',
        'routes': [
            '/trading/',
            '/trading/securities',
            '/trading/forex', 
            '/trading/commodities',
            '/trading/derivatives',
            '/trading/portfolio',
            '/trading/risk',
            '/trading/orders',
            '/trading/algorithms',
            '/trading/analytics'
        ],
        'api_endpoints': [
            '/trading/api/market-data/<symbol>',
            '/trading/api/portfolio/summary',
            '/trading/api/orders/recent',
            '/trading/api/risk/metrics',
            '/trading/api/health'
        ],
        'features': [
            'Multi-asset trading (Equities, FX, Commodities, Derivatives)',
            'Advanced order types (Market, Limit, Stop, Algorithmic)',
            'Portfolio management and rebalancing',
            'Risk management and VaR calculations',
            'Real-time market data and quotes',
            'Algorithmic trading strategies',
            'Performance analytics and reporting'
        ],
        'models': [
            'TradingInstrument',
            'TradingAccount', 
            'TradingOrder',
            'Trade',
            'Position',
            'Portfolio',
            'RiskMetrics',
            'MarketData'
        ],
        'forms': [
            'EquityOrderForm',
            'ForexOrderForm',
            'CommodityOrderForm',
            'DerivativeOrderForm',
            'PortfolioRebalanceForm',
            'RiskLimitForm',
            'TradingAlgorithmForm'
        ],
        'permissions': [
            'trading_dashboard',
            'securities_trading',
            'forex_trading',
            'commodities_trading',
            'derivatives_trading',
            'portfolio_management',
            'risk_management',
            'trading_analytics'
        ]
    }