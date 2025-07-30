"""
Binance Integration API Module
RESTful API endpoints for Binance integration health checks and status monitoring
"""

from .endpoints import binance_api_bp

__all__ = ['binance_api_bp']