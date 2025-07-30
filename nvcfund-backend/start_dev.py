#!/usr/bin/env python3
"""
Development Startup Script for NVC Banking Platform
Automatically sets up environment variables for local development
"""

import os
import sys
from pathlib import Path

def setup_development_environment():
    """Set up environment variables for development"""

    # IMPORTANT: Set encryption key FIRST before any imports
    if not os.environ.get('DATA_ENCRYPTION_KEY'):
        # Generate a proper Fernet key for development
        from cryptography.fernet import Fernet
        dev_key = Fernet.generate_key().decode()
        os.environ['DATA_ENCRYPTION_KEY'] = dev_key

    # Set development environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'

    # Set Vault URL for local development
    os.environ['VAULT_URL'] = 'http://127.0.0.1:8200'

    # Set database URL for development (using existing PostgreSQL)
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://nvcfund_web1@localhost:5432/nvcfund_db'

    # Set session secret for development (will be overridden by Vault if available)
    if not os.environ.get('SESSION_SECRET'):
        os.environ['SESSION_SECRET'] = 'dev-session-secret-change-in-production'
    
    print("🔧 Development environment configured:")
    print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"   VAULT_URL: {os.environ.get('VAULT_URL')}")
    print(f"   DATABASE_URL: postgresql://***@***/nvcfund_db")
    print(f"   SESSION_SECRET: {'Set from Vault' if 'VAULT_TOKEN' in os.environ else 'Development default'}")
    print(f"   DATA_ENCRYPTION_KEY: {'Set from Vault' if 'VAULT_TOKEN' in os.environ else 'Development default'}")
    print()

def check_css_assets():
    """Check that CSS assets are available"""
    css_dir = Path(__file__).parent / 'static' / 'css'
    if css_dir.exists() and any(css_dir.glob('*.css')):
        print("✅ CSS assets found and ready")
    else:
        print("⚠️  No CSS assets found in static/css directory")

def main():
    """Main development startup function"""
    print("🏦 NVC Banking Platform - Development Startup")
    print("=" * 50)
    
    # Setup environment
    setup_development_environment()
    
    # Check CSS assets
    check_css_assets()
    
    # Import and create app
    try:
        from app_factory import create_app
        app = create_app()
        
        print("✅ Application created successfully")
        print("🚀 Starting development server...")
        print("📱 Access the application at: http://localhost:5000")
        print("🔐 Registration page: http://localhost:5000/auth/register")
        print("🔑 Login page: http://localhost:5000/auth/login")
        print()
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent double initialization
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
