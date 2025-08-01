"""
Flask Application Factory for a Pure API Architecture
NVC Banking Platform - Enterprise-grade modular API factory
"""

import os
import logging
from flask import Flask, request, g, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Import core extensions
from modules.core.extensions import (
    db, login_manager, csrf, socketio, 
    cache, rate_limiter, session_interface
)

# Import modular blueprint registration
from modules.core.modular_blueprint_registration import register_all_modules

# Import enterprise logging system
from modules.core.enterprise_logging import get_enterprise_logger, EnterpriseLogger

# Import global security middleware
from modules.core.global_security_middleware import register_global_security

# SASS compilation removed - no longer using SASS in the application



# Configure logging only if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# Initialize enterprise logging system
enterprise_logger = EnterpriseLogger()

# Initialize enterprise error logger
error_logger = get_enterprise_logger("errors")

def create_app(config_name=None):
    """
    Create and configure the Flask application as a pure API service.
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Configure application
    configure_app(app, config_name)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure security headers for all responses
    configure_security_headers(app)
    
    # Register modular blueprints
    register_all_modules(app)
    
    # Add a basic root route for health checks and API discovery
    @app.route('/')
    def root():
        return jsonify({
            'status': 'ok',
            'message': 'Welcome to the NVC Banking Platform API'
        })
    
    # Test route for error logging
    @app.route('/test-error')
    def test_error():
        if app.debug:
            # Force a division by zero error to test logging
            result = 1 / 0
            return {'result': result}
        return "This route is only available in debug mode.", 404
    
    # Configure error handlers
    configure_error_handlers(app)
    
    # Configure middleware
    configure_middleware(app)
    
    # Initialize enterprise-grade global security middleware
    register_global_security(app)
    logger.info("Global Security Middleware initialized with enterprise-grade protection")
    
    # SASS compilation removed - application now uses direct CSS without SASS preprocessing
    
    logger.info("NVC Banking Platform API initialized with Pure API Architecture")
    
    return app

def initialize_dynamic_websocket_handlers(app, socketio):
    """Dynamically discover and initialize WebSocket handlers from all modules."""
    import os
    import importlib.util
    
    modules_dir = os.path.join(app.root_path, 'modules')
    if not os.path.exists(modules_dir):
        logger.warning("Modules directory not found, skipping dynamic WebSocket handler loading.")
        return

    for module_name in os.listdir(modules_dir):
        module_path = os.path.join(modules_dir, module_name)
        if os.path.isdir(module_path):
            # Convention: Look for a 'websocket_handlers.py' file in each module
            handler_file_path = os.path.join(module_path, 'websocket_handlers.py')
            if os.path.exists(handler_file_path):
                try:
                    # Dynamically import the module
                    spec = importlib.util.spec_from_file_location(
                        f"modules.{module_name}.websocket_handlers", handler_file_path
                    )
                    handler_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(handler_module)
                    
                    # Convention: Look for a function named 'register_handlers'
                    if hasattr(handler_module, 'register_handlers'):
                        handler_module.register_handlers(socketio)
                        logger.info(f"Initialized WebSocket handlers for module: {module_name}")
                except Exception as e:
                    logger.error(f"Error initializing WebSocket handlers for module '{module_name}': {e}")

def configure_app(app, config_name):
    """Configure Flask application settings"""
    
    # Import configuration classes
    from config import config
    
    # Load appropriate configuration
    config_obj = config.get(config_name or 'development')
    app.config.from_object(config_obj)
    
    # Static file configuration - disable ETags and caching to prevent 304 responses
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['USE_X_SENDFILE'] = False
    
    # ProxyFix for Replit deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def initialize_extensions(app):
    """Initialize Flask extensions"""

    # Initialize enterprise logging system FIRST
    enterprise_logger.init_app(app)



    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Authentication required', 'message': 'Please log in to access this resource.'}), 401
    @login_manager.user_loader
    def load_user(user_id):
        # Import here to avoid circular imports
        from modules.auth.models import User
        try:
            logger.info(f"Loading user with ID: {user_id}")
            user = User.query.get(int(user_id))
            if user:
                logger.info(f"Successfully loaded user: {user.username}")
            else:
                logger.warning(f"No user found with ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    # Initialize CSRF protection with enhanced settings
    # Enable CSRF protection for enhanced security
    app.config['WTF_CSRF_ENABLED'] = True
    csrf.init_app(app)
    
    # Configure additional CSRF settings
    app.config.setdefault('WTF_CSRF_TIME_LIMIT', 3600)
    app.config.setdefault('WTF_CSRF_SSL_STRICT', False)
    app.config.setdefault('WTF_CSRF_CHECK_DEFAULT', True)
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    # Dynamically initialize WebSocket handlers for all modules
    initialize_dynamic_websocket_handlers(app, socketio)
    
    # Initialize cache
    cache.init_app(app)
    
    # Initialize rate limiter
    rate_limiter.init_app(app)
    
    # Initialize session interface
    session_interface.init_app(app)
    
    # Initialize CORS with global access configuration
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    if isinstance(cors_origins, str) and cors_origins != '*':
        cors_origins = [origin.strip() for origin in cors_origins.split(',')]

    # Configure CORS for global access
    CORS(app,
         origins=cors_origins,
         supports_credentials=True,  # Allow cookies/sessions across origins
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-CSRF-Token'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
    
    # Create database tables and apply migrations
    with app.app_context():
        try:
            # Create new tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Apply automatic migrations for existing tables
            try:
                from modules.core.database_migration import database_migration
                migration_success = database_migration.check_and_apply_migrations()
                
                if migration_success:
                    logger.info("Database migrations applied successfully")
                else:
                    logger.warning("Some database migrations failed - check logs")
            except ImportError:
                logger.info("Database migration module not available - skipping migrations")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            logger.info("Continuing without database - some features may not work")

def configure_security_headers(app):
    """Configure security headers for all API responses"""
    
    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        # Add enhanced security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy for a pure API.
        # This policy is very restrictive as it does not need to allow scripts, styles, etc.
        csp_policy = (
            "default-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS for production
        if app.config.get('PREFERRED_URL_SCHEME') == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

def configure_error_handlers(app):
    """Configure comprehensive error handlers with enterprise logging"""
    
    @app.errorhandler(404)
    def not_found(error):
        error_logger.warning(f"404 Not Found: {request.method} {request.path} from {request.remote_addr}")
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log to both standard logger and enterprise error logger
        logger.error(f"Internal server error: {error}")
        error_logger.error(f"500 Internal Server Error: {request.method} {request.path} from {request.remote_addr} - {str(error)}")
        # Rollback the session to prevent corrupted data from failed transactions
        try:
            db.session.rollback()
            logger.info("Database session rolled back after internal error.")
        except Exception as e:
            logger.error(f"Error during session rollback: {e}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        error_logger.warning(f"403 Forbidden: {request.method} {request.path} from {request.remote_addr}")
        return {'error': 'Access forbidden'}, 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        error_logger.warning(f"401 Unauthorized: {request.method} {request.path} from {request.remote_addr}")
        return {'error': 'Authentication required'}, 401
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Catch all unhandled exceptions"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'request_path': request.path,
            'request_method': request.method,
            'user_ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        logger.error(f"Unhandled exception: {error}")
        error_logger.critical(f"Unhandled Exception: {type(error).__name__} - {str(error)} - Context: {error_details}")
        # Rollback the session to prevent corrupted data from failed transactions
        try:
            db.session.rollback()
            logger.info("Database session rolled back after unhandled exception.")
        except Exception as e:
            logger.error(f"Error during session rollback: {e}")
        return {'error': 'An unexpected error occurred'}, 500

def configure_middleware(app):
    """Configure middleware"""
    
    # Proxy fix for proper HTTPS handling (only if behind a proxy)
    if app.config.get('BEHIND_PROXY', False):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests"""
        logger.info(f"Request: {request.method} {request.path}")
    
    @app.after_request
    def log_response(response):
        """Log outgoing responses"""
        logger.info(f"Response: {response.status_code}")
        return response

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)