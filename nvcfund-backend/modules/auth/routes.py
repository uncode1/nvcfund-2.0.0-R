"""
NVC Banking Platform - Authentication Module Routes
Professional authentication system with enhanced security and user experience
Version: 2.0.0 - Complete redesign for professional banking interface
"""

from flask import Blueprint, request, render_template, redirect, flash, session, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging
import random
import string
import re

from .config import AuthConfig
from .services import AuthService
from .models import User
from modules.core.extensions import db, csrf, login_manager
from modules.services.communications.services import EmailService, PersonalizedMessageService

# Enhanced security imports with error handling
try:
    from modules.core.enhanced_security import enhanced_security
    from modules.core.mfa_system import mfa_system
    from modules.core.centralized_audit_logger import centralized_audit_logger, AuditEventType, AuditSeverity
    ENHANCED_SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced security modules not available: {e}")
    ENHANCED_SECURITY_AVAILABLE = False
    # Create dummy objects to prevent errors
    class DummyLogger:
        def log_event(self, *args, **kwargs):
            pass
    centralized_audit_logger = DummyLogger()
    class DummyEventType:
        LOGIN = "login"
        LOGIN_FAILED = "login_failed"
        SECURITY_INCIDENT = "security_incident"
    AuditEventType = DummyEventType()
    class DummySeverity:
        MEDIUM = "medium"
        HIGH = "high"
    AuditSeverity = DummySeverity()

# Configure logging
logger = logging.getLogger(__name__)

# ===== UTILITY FUNCTIONS =====

def handle_auth_error(route_name: str, error: Exception, status_code: int = 500) -> tuple:
    """Centralized error handling for authentication routes"""
    logger.error(f"Error in {route_name}: {error}")
    flash('Authentication service temporarily unavailable. Please try again later.', 'error')
    return redirect(url_for('auth.login')), status_code

def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength requirements"""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'

    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'

    return True, None

def validate_email_format(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_pattern, email) is not None

# ===== SECURITY DECORATORS =====

def require_session_security(max_age_minutes=30):
    """Decorator to require session security checks"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # Check session age
            if 'session_start' in session:
                session_age = datetime.now() - datetime.fromisoformat(session['session_start'])
                if session_age > timedelta(minutes=max_age_minutes):
                    flash('Session expired for security reasons', 'warning')
                    return redirect(url_for('auth.login'))
            else:
                session['session_start'] = datetime.now().isoformat()

            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# ===== BLUEPRINT AND SERVICE INITIALIZATION =====

# Create Auth Module Blueprint (URL prefix handled in registration)
auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Initialize auth service
auth_service = AuthService()

# ===== FORMS =====

class LoginForm(FlaskForm):
    """Professional login form with CSRF protection"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# ===== LOGIN MANAGER CONFIGURATION =====

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        return User.query.get(user_id)
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

# ===== MAIN AUTHENTICATION ROUTES =====

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Professional login route with enhanced security and user experience
    Handles user authentication with role-based dashboard redirection
    """
    logger.info("🔐 Auth Module: Login route accessed - Method: %s", request.method)

    # Security check: Block credentials in URL parameters
    if request.method == 'GET':
        username_param = request.args.get('username')
        password_param = request.args.get('password')

        if username_param or password_param:
            logger.critical("🚨 SECURITY VIOLATION: Credentials detected in URL parameters")
            flash('Security violation detected. Credentials must not be sent in URL.', 'error')
            return redirect(url_for('auth.login')), 400

    # Redirect authenticated users
    if current_user.is_authenticated:
        logger.info("🔐 Auth Module: User already authenticated, redirecting to dashboard")
        return redirect(url_for('dashboard.main_dashboard'))

    # Initialize CSRF protection
    from flask import session as flask_session
    from flask_wtf.csrf import generate_csrf

    if '_csrf_token' not in flask_session:
        flask_session['_csrf_token'] = generate_csrf()
        flask_session.permanent = True

    # Create form with CSRF protection
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember_me.data

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/modular_auth_login.html', form=form)

        try:
            # Authenticate user
            user = User.query.filter_by(username=username).first()

            if user and user.is_active and check_password_hash(user.password_hash, password):
                # Reset failed login attempts
                user.failed_login_attempts = 0
                user.account_locked_until = None

                # Check for MFA requirement
                if (ENHANCED_SECURITY_AVAILABLE and
                    getattr(user, 'mfa_enabled', False) and
                    getattr(user, 'mfa_config', None)):

                    # Store user ID for MFA verification
                    session['mfa_user_id'] = user.id
                    session['remember_me'] = remember_me

                    # Log MFA required
                    centralized_audit_logger.log_event(
                        AuditEventType.LOGIN,
                        AuditSeverity.MEDIUM,
                        f"MFA verification required for user {username}",
                        resource="authentication",
                        resource_id=str(user.id)
                    )

                    logger.info("✅ Auth Module: User %s requires MFA verification", username)
                    return redirect(url_for('enhanced_auth.mfa_verify'))
                else:
                    # Standard login without MFA - use centralized login completion
                    login_result = auth_service.complete_login(user, login_method='password', remember_me=remember_me)

                    if login_result['success']:
                        # Log successful login
                        centralized_audit_logger.log_event(
                            AuditEventType.LOGIN,
                            AuditSeverity.MEDIUM,
                            f"Successful login for user {username}",
                            resource="authentication",
                            resource_id=str(user.id)
                        )

                        logger.info("✅ Auth Module: Successful login for user: %s (Role: %s)",
                                  username, user.role)

                        # Role-based dashboard redirection
                        dashboard_url = auth_service.determine_dashboard_redirect(username, user.role)
                        logger.info("🔀 Auth Module: Redirecting user %s to: %s", username, dashboard_url)

                        return redirect(dashboard_url)
                    else:
                        flash('Error completing login. Please try again.', 'error')
                        logger.error("❌ Auth Module: Login completion failed for user: %s", username)

            else:
                # Handle failed login attempt
                if user:
                    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

                    # Lock account after 5 failed attempts
                    if user.failed_login_attempts >= 5:
                        user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
                        db.session.commit()

                        # Log security incident
                        centralized_audit_logger.log_event(
                            AuditEventType.SECURITY_INCIDENT,
                            AuditSeverity.HIGH,
                            f"Account locked due to {user.failed_login_attempts} failed attempts",
                            resource="authentication",
                            resource_id=str(user.id)
                        )

                        flash('Account temporarily locked due to multiple failed login attempts. '
                              'Try again in 30 minutes.', 'error')
                    else:
                        db.session.commit()
                        flash('Invalid username or password', 'error')
                else:
                    # Log failed login attempt for non-existent user
                    centralized_audit_logger.log_event(
                        AuditEventType.LOGIN_FAILED,
                        AuditSeverity.MEDIUM,
                        f"Failed login attempt for non-existent username: {username}",
                        resource="authentication"
                    )
                    flash('Invalid username or password', 'error')

                logger.warning("❌ Auth Module: Failed login attempt for username: %s", username)

        except Exception as e:
            logger.error("❌ Auth Module: Authentication error: %s", str(e))
            flash('Authentication service unavailable. Please try again later.', 'error')

    return render_template('auth/modular_auth_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Professional logout route with secure session cleanup and tracking
    """
    username = current_user.username if current_user.is_authenticated else 'Unknown'
    logger.info("🚪 Auth Module: Logout requested for user: %s", username)

    # Complete logout tracking before clearing session
    if current_user.is_authenticated:
        auth_service = AuthService()
        logout_result = auth_service.complete_logout(current_user, logout_reason='user_logout')

        if logout_result['success']:
            logger.info("✅ Auth Module: Logout tracking completed for user: %s", username)

    logout_user()
    session.clear()

    flash('You have been successfully logged out', 'success')
    logger.info("✅ Auth Module: User %s successfully logged out", username)

    return redirect(AuthConfig.POST_LOGOUT_REDIRECT)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Professional registration route with enhanced validation and KYC compliance
    """
    logger.info("📝 Auth Module: Registration route accessed - Method: %s", request.method)

    # Redirect authenticated users
    if current_user.is_authenticated:
        logger.info("📝 Auth Module: User already authenticated, redirecting to dashboard")
        return redirect(url_for('dashboard.main_dashboard'))

    if request.method == 'POST':
        try:
            # Extract and validate registration data
            registration_data = {
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip().lower(),
                'password': request.form.get('password', ''),
                'confirm_password': request.form.get('confirm_password', ''),
                'first_name': request.form.get('first_name', '').strip(),
                'last_name': request.form.get('last_name', '').strip(),
                'phone_number': request.form.get('phone_number', '').strip(),
                'date_of_birth': request.form.get('date_of_birth', ''),
                'account_type': request.form.get('account_type', 'USER')
            }

            # Enhanced validation
            validation_errors = []

            # Required fields validation
            required_fields = ['username', 'email', 'password', 'confirm_password',
                             'first_name', 'last_name']
            for field in required_fields:
                if not registration_data.get(field):
                    validation_errors.append(f'{field.replace("_", " ").title()} is required')

            # Email format validation
            if registration_data['email'] and not validate_email_format(registration_data['email']):
                validation_errors.append('Please enter a valid email address')

            # Password validation
            if registration_data['password']:
                is_valid, error_msg = validate_password_strength(registration_data['password'])
                if not is_valid:
                    validation_errors.append(error_msg)

            # Password confirmation
            if (registration_data['password'] and registration_data['confirm_password'] and
                registration_data['password'] != registration_data['confirm_password']):
                validation_errors.append('Passwords do not match')

            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('auth/modular_auth_register.html')

            # Create new user
            user_result = auth_service.create_user(registration_data)
            if user_result['success']:
                logger.info("✅ Auth Module: New user registered: %s", registration_data['username'])
                flash('Registration successful! Please log in with your new account.', 'success')
                return redirect(AuthConfig.POST_REGISTER_REDIRECT)
            else:
                flash(user_result['error'], 'error')

        except Exception as e:
            logger.error("❌ Auth Module: Registration error: %s", str(e))
            flash('Registration service unavailable. Please try again later.', 'error')

    return render_template('auth/modular_auth_register.html')

# ===== PASSWORD RECOVERY ROUTES =====

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Professional forgot password route with enhanced validation
    """
    logger.info("🔄 Auth Module: Forgot password route accessed - Method: %s", request.method)

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Email address is required', 'error')
            return render_template('auth/modular_auth_forgot_password.html')

        if not validate_email_format(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/modular_auth_forgot_password.html')

        try:
            result = auth_service.initiate_password_reset(email)
            if result['success']:
                flash('Password reset instructions have been sent to your email', 'success')
                logger.info("✅ Auth Module: Password reset initiated for email: %s", email)
            else:
                flash(result['error'], 'error')

        except Exception as e:
            logger.error("❌ Auth Module: Forgot password error: %s", str(e))
            flash('Password reset service unavailable. Please try again later.', 'error')

    return render_template('auth/modular_auth_forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Professional password reset route with enhanced validation
    """
    logger.info("🔐 Auth Module: Reset password route accessed for token: %s", token[:8] + "...")

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not new_password or not confirm_password:
            flash('Both password fields are required', 'error')
            return render_template('auth/modular_auth_reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/modular_auth_reset_password.html', token=token)

        # Validate password strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('auth/modular_auth_reset_password.html', token=token)

        try:
            result = auth_service.reset_password_with_token(token, new_password)
            if result['success']:
                flash('Password successfully reset! Please log in with your new password.', 'success')
                logger.info("✅ Auth Module: Password reset completed for token: %s",
                          token[:8] + "...")
                return redirect(AuthConfig.LOGIN_URL)
            else:
                flash(result['error'], 'error')

        except Exception as e:
            logger.error("❌ Auth Module: Password reset error: %s", str(e))
            flash('Password reset service unavailable. Please try again later.', 'error')

    return render_template('auth/modular_auth_reset_password.html', token=token)

# ===== ENHANCED AUTHENTICATION FEATURES =====

@auth_bp.route('/mfa-verify')
@login_required
def mfa_verify():
    """Multi-factor authentication verification page"""
    try:
        return render_template('auth/mfa_verify.html',
                             page_title='Multi-Factor Authentication')
    except Exception as e:
        logger.error(f"MFA verify error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/setup-mfa')
@login_required
def setup_mfa():
    """Multi-factor authentication setup page"""
    try:
        return render_template('auth/setup_mfa.html',
                             page_title='Setup Multi-Factor Authentication')
    except Exception as e:
        logger.error(f"Setup MFA error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

# ===== KYC AND ONBOARDING ROUTES =====

@auth_bp.route('/kyc/onboarding', methods=['GET'])
@login_required
def kyc_onboarding():
    """KYC onboarding and identity verification page"""
    try:
        # Check existing KYC status (when KYC models are available)
        existing_kyc = None
        try:
            from .kyc_models import PlaidKYCVerification
            existing_kyc = PlaidKYCVerification.query.filter_by(
                user_id=current_user.id
            ).first()
        except ImportError:
            logger.info("KYC models not available, proceeding without existing KYC check")

        return render_template('auth/kyc_onboarding.html',
                             page_title='Identity Verification',
                             existing_kyc=existing_kyc)
    except Exception as e:
        logger.error(f"KYC onboarding error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/api/kyc/submit', methods=['POST'])
@login_required
@require_session_security(max_age_minutes=30)
def submit_kyc():
    """Submit KYC information for verification"""
    try:
        from .kyc_service import KYCOnboardingService

        kyc_service = KYCOnboardingService()
        result = kyc_service.process_submission(request.json, current_user.id)

        return jsonify({
            'status': 'success',
            'verification_id': result.id,
            'next_steps': ['document_upload', 'identity_verification']
        })
    except ImportError:
        logger.warning("KYC service not available")
        return jsonify({
            'status': 'error',
            'message': 'KYC service temporarily unavailable'
        }), 503
    except Exception as e:
        logger.error(f"KYC submission error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to process KYC submission'
        }), 500

# ===== MODULE INFORMATION =====

MODULE_INFO = {
    'name': 'NVC Banking Platform - Authentication Module',
    'version': '2.0.0',
    'description': 'Professional authentication system with enhanced security and user experience',
    'routes': [
        '/login',
        '/logout',
        '/register',
        '/forgot-password',
        '/reset-password/<token>',
        '/mfa-verify',
        '/setup-mfa',
        '/kyc/onboarding'
    ],
    'api_endpoints': [
        '/api/kyc/submit'
    ],
    'features': [
        'Professional login/logout system',
        'Enhanced user registration with validation',
        'Secure password recovery',
        'Multi-factor authentication support',
        'KYC onboarding integration',
        'Role-based dashboard redirection',
        'Account lockout protection',
        'Session security management'
    ],
    'dependencies': [
        'modules.auth.services.AuthService',
        'modules.auth.models.User',
        'modules.core.extensions',
        'flask_login',
        'flask_wtf'
    ],
    'status': 'active',
    'last_updated': '2025-01-25'
}

def get_module_info() -> Dict[str, Any]:
    """Get comprehensive module information"""
    return MODULE_INFO
