"""
Flask Extensions for NVC Banking Platform
Centralized initialization of Flask extensions
"""

from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

# Initialize extensions
login_manager = LoginManager()
socketio = SocketIO()
db = SQLAlchemy()
csrf = CSRFProtect()
cache = Cache()
rate_limiter = Limiter(key_func=get_remote_address)
session_interface = Session()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'