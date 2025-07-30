"""
API Module - RESTful API Services
Unified API layer for NVC Banking Platform
"""

from flask import Blueprint
from modules.core.extensions import db

# Import existing models to avoid table conflicts
from modules.auth.models import User
from modules.banking.models import BankAccount as Account
from modules.banking.models import Transaction

from .routes import api_bp
from .realtime_handlers import init_socketio_handlers

def init_api_module(app, socketio=None):
    """Initialize the API module"""
    try:
        # Register the API blueprint
        app.register_blueprint(api_bp, url_prefix='/api')

        # Initialize real-time handlers if SocketIO is available
        if socketio:
            init_socketio_handlers(socketio)

        return True
    except Exception as e:
        print(f"Error initializing API module: {e}")
        return False

__all__ = ['api_bp', 'init_api_module', 'init_socketio_handlers']