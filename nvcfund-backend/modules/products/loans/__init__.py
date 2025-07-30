"""
Loans Module - Loan Management System
Handles loan applications, approvals, and portfolio management
"""

from flask import Blueprint

# Create loans blueprint
loans_bp = Blueprint(
    'loans',
    __name__,
    url_prefix='/loans',
    template_folder='templates',
    static_folder='static'
)

# Import routes after blueprint creation to avoid circular imports
from . import routes

# Module information for registry
MODULE_INFO = {
    'name': 'Loans Module',
    'version': '1.0.0',
    'description': 'Loan management and portfolio tracking',
    'author': 'NVC Banking Platform',
    'routes_prefix': '/loans',
    'blueprint_name': 'loans',
    'dependencies': ['auth', 'banking'],
    'features': [
        'loan_applications',
        'loan_approvals',
        'portfolio_management',
        'credit_analysis',
        'risk_assessment'
    ],
    'api_endpoints': [
        '/loans/applications',
        '/loans/portfolio',
        '/loans/reports'
    ]
}
