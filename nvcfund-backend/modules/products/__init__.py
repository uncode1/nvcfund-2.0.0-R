"""
NVC Banking Platform - Products Module
Centralized product management and integration system
"""

from flask import Blueprint
from .routes import products_bp

# Import sub-module blueprints
try:
    from .cards_payments.routes import cards_payments_bp
except ImportError:
    cards_payments_bp = None

try:
    from .insurance.routes import insurance_bp
except ImportError:
    insurance_bp = None

try:
    from .investments.routes import investments_bp
except ImportError:
    investments_bp = None

try:
    from .trading.routes import trading_bp
except ImportError:
    trading_bp = None

try:
    from .islamic_banking.routes import islamic_banking_bp
except ImportError:
    islamic_banking_bp = None

try:
    from .loans.routes import loans_bp
except ImportError:
    loans_bp = None

# Export the blueprint for registration
__all__ = [
    'products_bp', 'cards_payments_bp', 'insurance_bp', 'investments_bp',
    'trading_bp', 'islamic_banking_bp', 'loans_bp'
]