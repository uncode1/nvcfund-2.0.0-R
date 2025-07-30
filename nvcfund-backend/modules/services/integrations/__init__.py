"""
Integrations Module
NVC Banking Platform - External Service Integration Management

This module provides centralized management for all external integrations:
- Payment gateways (PayPal, Stripe, Flutterwave, Mojaloop, Mobile)
- Blockchain services (Binance, Etherscan, Polygonscan)
- Communication services (SendGrid, Twilio)
- Financial data providers (Plaid, banking APIs)
- Analytics and monitoring services

Sub-modules:
- payment_gateways: Payment processing integrations
- blockchain: Blockchain and cryptocurrency integrations
- communications: Email and messaging service integrations
- financial_data: Banking and financial data provider integrations
- analytics: External analytics and monitoring integrations
"""

from .routes import integrations_bp
from .payment_gateways.routes import payment_gateways_bp
from .payment_gateways.paypal.routes import paypal_bp
from .payment_gateways.stripe.routes import stripe_bp
from .payment_gateways.flutterwave.routes import flutterwave_bp
from .payment_gateways.ach_network.routes import ach_network_bp
from .blockchain.routes import blockchain_bp
from .blockchain.analytics.routes import blockchain_analytics_bp
from .communications.routes import communications_integration_bp
from .communications.sendgrid.routes import sendgrid_bp
from .communications.twilio.routes import twilio_bp
from .financial_data.routes import financial_data_bp
from .financial_data.plaid.routes import plaid_bp

__all__ = ['integrations_bp', 'payment_gateways_bp', 'paypal_bp', 'stripe_bp', 'flutterwave_bp', 'ach_network_bp', 'blockchain_bp', 'blockchain_analytics_bp', 'communications_integration_bp', 'sendgrid_bp', 'twilio_bp', 'financial_data_bp', 'plaid_bp']