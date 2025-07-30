"""
JWT Authentication System
NVC Banking Platform - Enterprise JWT Token Management

Implements banking-grade JWT authentication with:
- Secure token generation and validation
- Role-based access control integration
- Token refresh mechanisms
- Security event logging
"""

import jwt
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional, Any
from flask import request, jsonify, current_app, g
from flask_login import current_user
import logging

from .rbac import get_user_role
from modules.auth.models import User

logger = logging.getLogger(__name__)

class JWTManager:
    """Enterprise JWT token management for banking platform"""
    
    def __init__(self):
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 15  # Short-lived for security
        self.refresh_token_expire_days = 7     # Longer for user experience
        
    def _get_secret_key(self) -> str:
        """Get JWT secret key from app config"""
        secret = current_app.config.get('JWT_SECRET_KEY') or current_app.secret_key
        if isinstance(secret, bytes):
            return secret.decode('utf-8')
        return str(secret) if secret else 'fallback-secret-key'
    
    def generate_access_token(self, user_id, username: str, role: str) -> str:
        """Generate secure JWT access token"""
        try:
            now = datetime.utcnow()
            payload = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'iat': now,
                'exp': now + timedelta(minutes=self.access_token_expire_minutes),
                'type': 'access',
                'jti': secrets.token_hex(16)  # Unique token ID for revocation
            }
            
            token = jwt.encode(payload, self._get_secret_key(), algorithm=self.algorithm)
            
            logger.info(f"JWT access token generated for user {username}", extra={
                'user_id': user_id,
                'role': role,
                'action': 'JWT_TOKEN_GENERATED',
                'token_type': 'access'
            })
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}", extra={
                'user_id': user_id,
                'error': str(e),
                'action': 'JWT_TOKEN_GENERATION_FAILED'
            })
            raise
    
    def generate_refresh_token(self, user_id, username: str) -> str:
        """Generate secure JWT refresh token"""
        try:
            now = datetime.utcnow()
            payload = {
                'user_id': user_id,
                'username': username,
                'iat': now,
                'exp': now + timedelta(days=self.refresh_token_expire_days),
                'type': 'refresh',
                'jti': secrets.token_hex(16)
            }
            
            token = jwt.encode(payload, self._get_secret_key(), algorithm=self.algorithm)
            
            logger.info(f"JWT refresh token generated for user {username}", extra={
                'user_id': user_id,
                'action': 'JWT_REFRESH_TOKEN_GENERATED'
            })
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate refresh token: {e}", extra={
                'user_id': user_id,
                'error': str(e),
                'action': 'JWT_REFRESH_TOKEN_GENERATION_FAILED'
            })
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self._get_secret_key(), 
                algorithms=[self.algorithm]
            )
            
            # Validate token type
            if payload.get('type') not in ['access', 'refresh']:
                logger.warning(f"Invalid token type: {payload.get('type')}")
                return None
            
            # Check expiration
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning(f"Expired token for user {payload.get('username')}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT token verification failed: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get('type') != 'refresh':
                return None
            
            # Get fresh user data
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                logger.warning(f"User {payload['user_id']} not found or inactive during token refresh")
                return None
            
            # Generate new access token
            user_role = get_user_role(user)
            return self.generate_access_token(user.id, user.username, user_role.value)
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

# Global JWT manager instance
jwt_manager = JWTManager()

def jwt_required(optional: bool = False, roles: Optional[list] = None):
    """
    JWT authentication decorator for API routes
    
    Args:
        optional: If True, allows unauthenticated access but sets g.current_user if token present
        roles: List of required roles (e.g., ['admin', 'treasury'])
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None
            
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            # Extract token from request body for form submissions
            if not token and request.is_json:
                token = request.json.get('access_token')
            
            # Extract token from form data
            if not token and request.form:
                token = request.form.get('access_token')
            
            if not token:
                if optional:
                    g.current_user = None
                    g.jwt_payload = None
                    return f(*args, **kwargs)
                else:
                    logger.warning(f"Missing JWT token for protected route {request.endpoint}")
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'Missing or invalid authentication token'
                    }), 401
            
            # Verify token
            payload = jwt_manager.verify_token(token)
            if not payload:
                logger.warning(f"Invalid JWT token for route {request.endpoint}")
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'Authentication token is invalid or expired'
                }), 401
            
            # Get user from database
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                logger.warning(f"User {payload['user_id']} not found or inactive for JWT auth")
                return jsonify({
                    'error': 'User not found',
                    'message': 'Authentication failed'
                }), 401
            
            # Check role requirements
            if roles:
                user_role = payload.get('role', '').lower()
                if user_role not in [role.lower() for role in roles]:
                    logger.warning(f"Insufficient role {user_role} for route {request.endpoint}, required: {roles}")
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'message': f'Required role: {", ".join(roles)}'
                    }), 403
            
            # Set user context
            g.current_user = user
            g.jwt_payload = payload
            
            logger.info(f"JWT authentication successful", extra={
                'user_id': user.id,
                'username': user.username,
                'role': payload.get('role'),
                'endpoint': request.endpoint,
                'action': 'JWT_AUTH_SUCCESS'
            })
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator

def get_jwt_user() -> Optional[User]:
    """Get current JWT authenticated user"""
    return getattr(g, 'current_user', None)

def get_jwt_payload() -> Optional[Dict[str, Any]]:
    """Get current JWT token payload"""
    return getattr(g, 'jwt_payload', None)

def create_token_response(user: User) -> Dict[str, Any]:
    """Create standardized JWT token response"""
    try:
        user_role = get_user_role(user)
        access_token = jwt_manager.generate_access_token(user.id, user.username, user_role.value)
        refresh_token = jwt_manager.generate_refresh_token(user.id, user.username)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': jwt_manager.access_token_expire_minutes * 60,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user_role.value,
                'email': user.email
            }
        }
    except Exception as e:
        logger.error(f"Failed to create token response for user {user.id}: {e}")
        raise