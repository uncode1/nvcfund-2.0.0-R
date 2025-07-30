"""
Exchange Module
NVC Banking Platform - Complete Exchange Operations

Provides comprehensive exchange functionality:
- Internal exchange between fiat and digital assets
- External exchange via Binance integration  
- Liquidity pool management
- Real-time exchange rates
- Transaction processing and compliance
"""

from .routes import exchange_bp
from .services import ExchangeService

__version__ = "1.0.0"
__author__ = "NVC Banking Platform"

# Module metadata
MODULE_NAME = "exchange"
MODULE_DESCRIPTION = "Complete exchange operations with internal and external trading"
MODULE_VERSION = __version__
MODULE_FEATURES = [
    "internal_exchange",
    "external_binance_integration", 
    "liquidity_pool_management",
    "real_time_rates",
    "exchange_history",
    "admin_exchange_management"
]

# Export main components
__all__ = [
    'exchange_bp',
    'ExchangeService',
    'MODULE_NAME',
    'MODULE_DESCRIPTION', 
    'MODULE_VERSION',
    'MODULE_FEATURES'
]