"""
Configuration Classes for NVC Banking Platform
Supports development, testing, and production environments
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings"""
    
    # Security
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Data Encryption Key (for development - use proper key management in production)
    # CRITICAL: This key MUST be set in the environment.
    # The application will not start without it.
    DATA_ENCRYPTION_KEY = os.environ.get('DATA_ENCRYPTION_KEY')
    if not DATA_ENCRYPTION_KEY:
        raise ValueError("CRITICAL: DATA_ENCRYPTION_KEY is not set in the environment.")
    
    # Database - PostgreSQL only
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://nvcfund_web1@localhost:5432/nvcfund_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Session Management
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'flask_session'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'nvc_banking:'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)

    # Session Cookie Configuration
    # In production, this will be set to .nvcfund.com for domain-wide cookies
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', None)
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = '1000 per hour'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CORS - Production domain configuration
    # Allow access from production domain and development environments
    default_origins = 'https://www.nvcfund.com,https://nvcfund.com,http://localhost:5000,http://127.0.0.1:5000'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', default_origins).split(',')
    
    # Proxy configuration
    BEHIND_PROXY = os.environ.get('BEHIND_PROXY', 'false').lower() == 'true'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Plaid Configuration
    PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
    PLAID_SECRET = os.environ.get('PLAID_SECRET')
    PLAID_ENV = os.environ.get('PLAID_ENV', 'sandbox')
    
    # Binance Configuration
    BINANCE_CLIENT_ID = os.environ.get('BINANCE_CLIENT_ID')
    BINANCE_CLIENT_SECRET = os.environ.get('BINANCE_CLIENT_SECRET')


class DevelopmentConfig(Config):
    """Development configuration for sandbox environment"""

    DEBUG = True
    TESTING = False

    # Database - Use PostgreSQL with vault-managed credentials
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://nvcfund_web1@localhost:5432/nvcfund_db')
    
    # Enhanced CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = False  # Allow non-SSL in development
    WTF_CSRF_CHECK_DEFAULT = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # PostgreSQL settings for development
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "echo": False  # Set to True for SQL query debugging
    }
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Session timeout (30 minutes for development - secure but reasonable)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Development session configuration - Allow cross-IP access
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SESSION_COOKIE_DOMAIN = None   # Allow any domain/IP in development
    SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cross-origin requests


class TestingConfig(Config):
    """Testing configuration with optimized settings for automated tests"""

    TESTING = True
    DEBUG = False

    # Use PostgreSQL test database with vault-managed credentials
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    
    # Disable CSRF for easier testing of POST requests
    WTF_CSRF_ENABLED = False
    
    # Use simple cache for testing
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10  # Short timeout for testing
    
    # Use in-memory rate limit storage for testing
    RATELIMIT_STORAGE_URI = 'memory://'
    RATELIMIT_DEFAULT = '10000 per hour'  # High limit for testing
    
    # Disable email sending in tests
    MAIL_SUPPRESS_SEND = True
    
    # Session configuration for testing
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'test_sessions'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Logging
    LOG_LEVEL = 'WARNING'  # Reduce log noise during tests
    
    # Test-specific settings
    SERVER_NAME = 'localhost.localdomain'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    
    # Security settings for testing
    SECRET_KEY = 'test-secret-key-for-testing-only'
    
    # API Configuration for testing
    PLAID_ENV = 'sandbox'
    
    # Disable external API calls during testing
    EXTERNAL_API_ENABLED = False


class ProductionConfig(Config):
    """Production configuration with security hardening"""

    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__()
        # Initialize secrets manager for production
        try:
            from modules.core.secrets_manager import secrets_manager
            self._secrets_manager = secrets_manager
        except ImportError:
            self._secrets_manager = None

        # Production-specific session configuration
        self.SESSION_COOKIE_DOMAIN = '.nvcfund.com'  # Allow subdomains
        self.SESSION_COOKIE_SECURE = True  # HTTPS only in production
        self.PREFERRED_URL_SCHEME = 'https'

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Get database URI from AWS Secrets Manager with Vault fallback"""
        if self._secrets_manager:
            db_url = self._secrets_manager.get_database_url()
            if db_url:
                return db_url

        # Fallback to environment variable
        return os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/nvc_banking_prod')

    @property
    def SECRET_KEY(self):
        """Get secret key from AWS Secrets Manager with Vault fallback"""
        if self._secrets_manager:
            session_secret = self._secrets_manager.get_session_secret()
            if session_secret:
                return session_secret

        # Fallback to environment variable or base config
        return os.environ.get('SESSION_SECRET') or super().SECRET_KEY

    def get_application_secrets(self):
        """Get all application secrets for production"""
        if self._secrets_manager:
            return self._secrets_manager.get_application_secrets()
        return {}

    # Enable proxy fix in production (typically behind nginx/apache)
    BEHIND_PROXY = True
    
    # Enhanced security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Shorter session timeout for production
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # Rate limiting - more restrictive in production
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # CORS - more restrictive in production (should be set via environment)
    CORS_ORIGINS = []
    
    # SSL/TLS
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def validate_production_requirements(cls):
        """Validate secrets management for production"""
        try:
            from modules.core.secrets_manager import secrets_manager

            # Test secrets manager connectivity
            db_url = secrets_manager.get_database_url()
            session_secret = secrets_manager.get_session_secret()

            if not db_url:
                raise ValueError("DATABASE_URL not available from AWS Secrets Manager, Vault, or environment")

            if not session_secret:
                raise ValueError("SESSION_SECRET not available from AWS Secrets Manager, Vault, or environment")

            return True

        except ImportError:
            # Fallback to environment variable validation
            required_vars = ['DATABASE_URL', 'SESSION_SECRET']
            missing_vars = [var for var in required_vars if not os.environ.get(var)]

            if missing_vars:
                raise ValueError(
                    f"Secrets manager not available. Required environment variables: {', '.join(missing_vars)}"
                )
    
    # Production API settings
    PLAID_ENV = 'production'
    EXTERNAL_API_ENABLED = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}