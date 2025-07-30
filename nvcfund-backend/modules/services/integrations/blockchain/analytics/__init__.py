"""
Blockchain Analytics Module for NVC Banking Platform
Provides Etherscan API integration for real-time token analytics
"""

from flask import Blueprint
from .routes import blockchain_analytics_bp

def register_blockchain_analytics_module(app):
    """Register the Blockchain Analytics module with the Flask application"""
    app.register_blueprint(blockchain_analytics_bp)
    return True