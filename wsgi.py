
"""
WSGI Entry Point for NVC Banking Platform
Production-ready WSGI application entry point for Gunicorn
"""

import os
import sys
import logging
from pathlib import Path

# Add the application directory to Python path
app_dir = Path(__file__).parent / "nvcfund-backend"
sys.path.insert(0, str(app_dir))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the application
try:
    from app_factory import create_app
    
    # Create the application instance
    application = create_app(os.getenv('FLASK_ENV', 'production'))
    
    # Ensure the application is ready
    with application.app_context():
        application.logger.info("WSGI application initialized successfully")
        
except Exception as e:
    logging.error(f"Failed to initialize WSGI application: {e}")
    raise

# Export for Gunicorn
app = application

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    app.run(host='0.0.0.0', port=5000, debug=False)
