"""
Financial Data Integration Sub-module
Part of the Integrations Module - NVC Banking Platform

This sub-module provides:
- Financial data provider integrations (Plaid, Federal Reserve, SWIFT, Clearing House)
- Banking and economic data access
- Financial data processing and analysis
- Provider health monitoring
"""

from .routes import financial_data_bp
from .plaid.routes import plaid_bp

__all__ = ['financial_data_bp', 'plaid_bp']