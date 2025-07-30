#!/usr/bin/env python3
"""
NVC Banking Platform - Main Entry Point
Production-ready banking and financial services platform
"""

import os

def setup_environment():
    """Set up environment variables if not already configured"""
    
    # IMPORTANT: Set encryption key FIRST before any imports
    if not os.environ.get('DATA_ENCRYPTION_KEY'):
        # Generate a proper Fernet key for development
        from cryptography.fernet import Fernet
        dev_key = Fernet.generate_key().decode()
        os.environ['DATA_ENCRYPTION_KEY'] = dev_key

    # Set database URL for development if not provided
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://nvcfund_web1@localhost:5432/nvcfund_db'

    # Set session secret if not provided
    if not os.environ.get('SESSION_SECRET'):
        os.environ['SESSION_SECRET'] = 'dev-session-secret-change-in-production'
    
    # Set Vault URL for local development if not provided
    if not os.environ.get('VAULT_URL'):
        os.environ['VAULT_URL'] = 'http://127.0.0.1:8200'

# Setup environment before importing app
setup_environment()

from app_factory import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    print("Starting NVC Banking Platform...")
    print(f"Environment: {'Production' if not app.debug else 'Development'}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )