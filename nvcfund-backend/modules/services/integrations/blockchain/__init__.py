"""
Blockchain Integration Sub-module
Part of the Integrations Module - NVC Banking Platform

This sub-module provides:
- Binance API integration for cryptocurrency trading
- Etherscan integration for Ethereum blockchain data
- Polygonscan integration for Polygon blockchain data
- NVCT stablecoin network integration
- Smart contract interaction services
"""

from .services import BlockchainIntegrationService
from .routes import blockchain_bp
from .analytics.routes import blockchain_analytics_bp

__all__ = ['BlockchainIntegrationService', 'blockchain_bp', 'blockchain_analytics_bp']