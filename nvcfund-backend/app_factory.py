"""
Flask Application Factory for Pure Modular Architecture
NVC Banking Platform - Enterprise-grade modular application factory
"""

import os
import logging
from flask import Flask, request, g, render_template
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
    Create and configure Flask application with modular architecture
    
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
    
    # Configure static file serving
    configure_static_files(app)
    
    # Configure template loader for modular architecture
    configure_modular_templates(app)
    
    # Register modular blueprints
    register_all_modules(app)
    
    # Add basic root route with server-side authentication
    @app.route('/')
    def root():
        from flask_login import current_user
        from flask import render_template, redirect, url_for
        
        # Check if user is authenticated
        if current_user.is_authenticated:
            # User is logged in, redirect to dashboard
            return redirect(url_for('dashboard.main'))
        else:
            # User is not logged in, redirect to public home
            return redirect(url_for('public.index'))
    
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
    
    logger.info("NVC Banking Platform initialized with Pure Modular Architecture")
    
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
    
    # Custom unauthorized handler for direct URL redirect
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import redirect, request, session
        session['next_url'] = request.url
        return redirect('/auth/login')
    
    # Add user loader function
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
    
    # Register template context processors AFTER Flask-Login is initialized
    # This ensures Flask-Login's current_user is available before our custom processors
    from modules.core.template_context import register_template_context
    register_template_context(app)
    
    # Ensure current_user is always available in templates with security filtering
    @app.context_processor
    def inject_current_user():
        """Ensure current_user is always available in template context with security filtering"""
        try:
            from flask_login import current_user

            # Create a template-safe user proxy that only exposes safe attributes
            class TemplateUser:
                def __init__(self, user):
                    self._user = user

                @property
                def is_authenticated(self):
                    try:
                        return self._user.is_authenticated if self._user else False
                    except:
                        return False

                @property
                def is_active(self):
                    try:
                        return self._user.is_active if self._user else False
                    except:
                        return False

                @property
                def is_anonymous(self):
                    try:
                        return self._user.is_anonymous if self._user else True
                    except:
                        return True

                @property
                def username(self):
                    try:
                        return self._user.username if self._user and self._user.is_authenticated else 'Guest'
                    except:
                        return 'Guest'

                @property
                def role(self):
                    try:
                        return self._user.role if self._user and self._user.is_authenticated else None
                    except:
                        return None

                @property
                def id(self):
                    try:
                        return self._user.id if self._user and self._user.is_authenticated else None
                    except:
                        return None

                @property
                def first_name(self):
                    try:
                        return self._user.first_name if self._user and self._user.is_authenticated else None
                    except:
                        return None

                @property
                def last_name(self):
                    try:
                        return self._user.last_name if self._user and self._user.is_authenticated else None
                    except:
                        return None

                def __bool__(self):
                    try:
                        return bool(self._user and self._user.is_authenticated)
                    except:
                        return False

                def __str__(self):
                    try:
                        return f"<TemplateUser {self.username}>" if self.is_authenticated else "<TemplateUser Anonymous>"
                    except:
                        return "<TemplateUser Anonymous>"

            template_user = TemplateUser(current_user)
            return {
                'current_user': template_user
            }
        except Exception as e:
            # Fallback: provide a safe anonymous user
            logger.error(f"Error in inject_current_user context processor: {e}")
            class AnonymousTemplateUser:
                is_authenticated = False
                is_active = False
                is_anonymous = True
                username = 'Guest'
                role = None
                id = None
                first_name = None
                last_name = None

                def __bool__(self):
                    return False

                def __str__(self):
                    return "<TemplateUser Anonymous>"

            return {
                'current_user': AnonymousTemplateUser(),
            }
    
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

def configure_static_files(app):
    """Configure static file serving with proper cache control"""
    
    @app.after_request
    def after_request(response):
        """Add cache control headers to prevent 304 responses"""
        # For static files, disable caching to force fresh content
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            # Remove ETag to prevent 304 responses
            response.headers.pop('ETag', None)
            # Always return 200 for static files
            if response.status_code == 304:
                response.status_code = 200
        
        # Add enhanced security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy for XSS prevention.
        # WARNING: 'unsafe-inline' is used for styles, which is not ideal for production.
        # Consider using a nonce-based or hash-based approach for better security.
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
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
    
    def is_api_request():
        """Check if this is an API request that should return JSON"""
        # API endpoints should return JSON
        if request.path.startswith('/api/'):
            return True
        
        # If the request explicitly asks for JSON
        if request.headers.get('Content-Type') == 'application/json':
            return True
            
        # Check Accept header for JSON preference (but not if HTML is preferred)
        accept_header = request.headers.get('Accept', '')
        # Only return JSON if specifically asking for JSON and NOT asking for HTML
        if accept_header and 'application/json' in accept_header and 'text/html' not in accept_header:
            return True
            
        # For anything else (including browsers), return HTML
        return False
    
    @app.errorhandler(404)
    def not_found(error):
        error_logger.warning(f"404 Not Found: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Resource not found'}, 404
        
        try:
            return render_template('errors/404.html'), 404
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Page Not Found</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>404 - Page Not Found</h1>
            <p>The page you're looking for doesn't exist.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log to both standard logger and enterprise error logger
        logger.error(f"Internal server error: {error}")
        error_logger.error(f"500 Internal Server Error: {request.method} {request.path} from {request.remote_addr} - {str(error)}")
        
        if is_api_request():
            return {'error': 'Internal server error'}, 500
        
        try:
            return render_template('errors/500.html'), 500
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Service Temporarily Unavailable</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>Service Temporarily Unavailable</h1>
            <p>We're experiencing technical difficulties. Our team has been notified.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        error_logger.warning(f"403 Forbidden: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Access forbidden'}, 403
            
        try:
            return render_template('errors/error_page.html', error_code=403), 403
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Access Forbidden</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>403 - Access Forbidden</h1>
            <p>You don't have permission to access this resource.</p>
            <a href="/auth/login" style="color: #66ccff;">Login</a>
            </body></html>
            """, 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        error_logger.warning(f"401 Unauthorized: {request.method} {request.path} from {request.remote_addr}")
        
        if is_api_request():
            return {'error': 'Authentication required'}, 401
            
        try:
            return render_template('errors/error_page.html', error_code=401), 401
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Authentication Required</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>401 - Authentication Required</h1>
            <p>You need to log in to access this page.</p>
            <a href="/auth/login" style="color: #66ccff;">Login</a>
            </body></html>
            """, 401
    
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
        
        if is_api_request():
            return {'error': 'An unexpected error occurred'}, 500
        
        try:
            return render_template('errors/error_page.html', error_code=500), 500
        except:
            # Fallback to plain HTML if template fails
            return """
            <html><head><title>Unexpected Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px; background: #0a2447; color: white;">
            <h1>Unexpected Error</h1>
            <p>Something went wrong. Our technical team has been notified.</p>
            <a href="/" style="color: #66ccff;">Return to Homepage</a>
            </body></html>
            """, 500

def configure_modular_templates(app):
    """Configure template loader to support modular architecture with shared components"""
    import os
    from jinja2 import FileSystemLoader, ChoiceLoader
    
    # Get the main template directory
    main_template_dir = os.path.join(app.root_path, 'templates')
    
    # Create a choice loader that searches multiple directories
    # This allows modules to access shared templates while maintaining their own templates
    template_dirs = [main_template_dir]
    
    # Add module template directories
    modules_dir = os.path.join(app.root_path, 'modules')
    if os.path.exists(modules_dir):
        for module_name in os.listdir(modules_dir):
            module_template_dir = os.path.join(modules_dir, module_name, 'templates')
            if os.path.exists(module_template_dir):
                template_dirs.append(module_template_dir)
    
    # Create loaders for each directory
    loaders = [FileSystemLoader(template_dir) for template_dir in template_dirs]
    
    # Set up the choice loader
    app.jinja_loader = ChoiceLoader(loaders)
    
    logger.info(f"Configured modular template loader with directories: {template_dirs}")

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