"""
Banking Module - Self-Contained Banking Operations
Enterprise-grade banking module with account management, transfers, cards, and payments

Module Features:
- Account Management (Checking, Savings, Business, Investment)
- Money Transfers (Domestic, International, Wire, ACH)
- Card Services (Debit, Credit, Prepaid)
- Payment Processing (PayPal, Stripe, Apple Pay, Google Pay)
- Transaction History and Statements
- KYC-Compliant Account Opening
- Multi-currency Support
"""

from flask import Blueprint
from .routes import banking_bp
from .services import BankingService

# Module Registry Information
MODULE_INFO = {
    'name': 'Banking Module',
    'version': '1.0.0',
    'description': 'Comprehensive banking operations and account management',
    'author': 'NVC Banking Platform',
    'routes_prefix': '/banking',
    'blueprint_name': 'banking',
    'dependencies': ['auth', 'utils'],
    'features': [
        'account_management',
        'money_transfers', 
        'card_services',
        'payment_processing',
        'transaction_history',
        'multi_currency',
        'kyc_compliance',
        'statements_generation'
    ],
    'api_endpoints': [
        '/banking/accounts',
        '/banking/transfers',
        '/banking/cards',
        '/banking/payments',
        '/banking/history',
        '/banking/statements'
    ]
}

# Initialize banking service
banking_service = BankingService()

def init_banking_module(app):
    """Initialize Banking Module with Flask app"""
    app.register_blueprint(banking_bp, url_prefix='/banking')
    app.banking_service = banking_service
    
    # Module health check
    @app.route('/banking/api/health')
    def banking_health():
        return {'status': 'healthy', 'app_module': 'banking'}
    
    return MODULE_INFO

__all__ = ['banking_bp', 'banking_service', 'init_banking_module', 'MODULE_INFO']