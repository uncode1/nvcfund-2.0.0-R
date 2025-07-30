#!/usr/bin/env python3
"""
Production Startup Script for NVC Banking Platform
Demonstrates AWS Secrets Manager with HashiCorp Vault fallback
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_secrets_manager():
    """Test the secrets manager functionality"""
    try:
        from modules.core.secrets_manager import secrets_manager
        
        logger.info("🔐 Testing Secrets Manager...")
        
        # Test AWS Secrets Manager connectivity
        if secrets_manager.aws_client:
            logger.info("✅ AWS Secrets Manager client available")
        else:
            logger.warning("⚠️  AWS Secrets Manager not available")
        
        # Test Vault connectivity
        if secrets_manager.vault_client:
            logger.info("✅ HashiCorp Vault client available")
        else:
            logger.warning("⚠️  HashiCorp Vault not available")
        
        # Test secret retrieval
        db_url = secrets_manager.get_database_url()
        if db_url:
            logger.info("✅ Database URL retrieved successfully")
            # Mask the URL for security - show only protocol and last part
            if db_url.startswith('postgresql://'):
                masked_url = "postgresql://***@***/" + db_url.split('/')[-1]
            else:
                masked_url = "***"
            logger.info(f"   Database URL: {masked_url}")
        else:
            logger.error("❌ Failed to retrieve database URL")

        session_secret = secrets_manager.get_session_secret()
        if session_secret:
            logger.info("✅ Session secret retrieved successfully")
        else:
            logger.error("❌ Failed to retrieve session secret")
        
        app_secrets = secrets_manager.get_application_secrets()
        if app_secrets:
            logger.info(f"✅ Retrieved {len(app_secrets)} application secrets")
            for key in app_secrets.keys():
                logger.info(f"   - {key}")
        else:
            logger.warning("⚠️  No application secrets retrieved")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Secrets manager test failed: {e}")
        return False

def validate_production_config():
    """Validate production configuration"""
    try:
        from config import ProductionConfig
        
        logger.info("🔧 Validating Production Configuration...")
        
        # Create production config instance
        config = ProductionConfig()
        
        # Test database URL
        db_url = config.SQLALCHEMY_DATABASE_URI
        if db_url and db_url != 'postgresql://user:pass@localhost/nvc_banking_prod':
            logger.info("✅ Production database URL configured")
        else:
            logger.error("❌ Production database URL not properly configured")
            return False
        
        # Test secret key
        secret_key = config.SECRET_KEY
        if secret_key and secret_key != 'dev-secret-key-change-in-production':
            logger.info("✅ Production secret key configured")
        else:
            logger.error("❌ Production secret key not properly configured")
            return False
        
        # Test validation method
        try:
            ProductionConfig.validate_production_requirements()
            logger.info("✅ Production requirements validation passed")
        except ValueError as e:
            logger.error(f"❌ Production requirements validation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Production config validation failed: {e}")
        return False

def create_app_with_secrets():
    """Create Flask app with secrets manager"""
    try:
        from app_factory import create_app
        
        logger.info("🚀 Creating Flask application with secrets manager...")
        
        # Set production environment
        os.environ['FLASK_ENV'] = 'production'
        
        # Create app
        app = create_app('production')
        
        logger.info("✅ Flask application created successfully")
        
        # Test app context
        with app.app_context():
            from modules.core.database import db
            
            # Test database connection
            try:
                db.engine.execute("SELECT 1")
                logger.info("✅ Database connection successful")
            except Exception as e:
                logger.error(f"❌ Database connection failed: {e}")
                return None
        
        return app
        
    except Exception as e:
        logger.error(f"❌ Flask app creation failed: {e}")
        return None

def main():
    """Main startup function"""
    logger.info("🏦 NVC Banking Platform - Production Startup")
    logger.info("=" * 60)
    
    # Test secrets manager
    if not test_secrets_manager():
        logger.error("❌ Secrets manager test failed - cannot proceed")
        sys.exit(1)
    
    logger.info("-" * 60)
    
    # Validate production config
    if not validate_production_config():
        logger.error("❌ Production config validation failed - cannot proceed")
        sys.exit(1)
    
    logger.info("-" * 60)
    
    # Create Flask app
    app = create_app_with_secrets()
    if not app:
        logger.error("❌ Flask app creation failed - cannot proceed")
        sys.exit(1)
    
    logger.info("-" * 60)
    logger.info("✅ Production startup validation completed successfully!")
    logger.info("🚀 Ready to start production server")
    
    # Example of how to start with Gunicorn
    logger.info("\n📋 To start the production server:")
    logger.info("   gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app")
    logger.info("\n🔐 Secrets Management Status:")
    logger.info("   - AWS Secrets Manager: Primary")
    logger.info("   - HashiCorp Vault: Fallback")
    logger.info("   - Environment Variables: Final fallback")
    
    return app

if __name__ == "__main__":
    main()
