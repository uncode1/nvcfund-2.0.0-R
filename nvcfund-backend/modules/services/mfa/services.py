"""
MFA Services
NVC Banking Platform - Multi-Factor Authentication Business Logic

This module provides comprehensive MFA services including:
- TOTP generation and verification
- QR code generation for authenticator apps
- Backup code management
- MFA enforcement logic
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime
from flask import request, session
from modules.core.extensions import db
from modules.services.mfa.models import MFAConfiguration, MFABackupCode, MFAAuditLog
import logging

logger = logging.getLogger(__name__)


class MFAService:
    """
    Multi-Factor Authentication Service
    Handles all MFA operations with enterprise-grade security
    """
    
    @staticmethod
    def get_or_create_mfa_config(user_id):
        """Get or create MFA configuration for a user"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            
            if not mfa_config:
                mfa_config = MFAConfiguration(user_id=user_id)
                db.session.add(mfa_config)
                db.session.commit()
                
                # Log configuration creation
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='config_created',
                    event_description='MFA configuration created for user',
                    event_result='success',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None
                )
            
            return mfa_config
            
        except Exception as e:
            logger.error(f"Error getting/creating MFA config for user {user_id}: {str(e)}")
            db.session.rollback()
            return None
    
    @staticmethod
    def generate_totp_secret():
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()
    
    @staticmethod
    def setup_totp(user_id, app_name="NVC Banking Platform"):
        """Set up TOTP for a user and generate QR code"""
        try:
            mfa_config = MFAService.get_or_create_mfa_config(user_id)
            if not mfa_config:
                return None, None, "Failed to create MFA configuration"
            
            # Generate new secret if not exists
            if not mfa_config.totp_secret:
                mfa_config.totp_secret = MFAService.generate_totp_secret()
                db.session.commit()
            
            # Create TOTP object
            totp = pyotp.TOTP(mfa_config.totp_secret)
            
            # Generate provisioning URI for QR code
            # Use user_id as the account name since we don't have email in scope
            provisioning_uri = totp.provisioning_uri(
                name=f"User-{user_id}",
                issuer_name=app_name
            )
            
            # Generate QR code
            qr_code_base64 = MFAService.generate_qr_code(provisioning_uri)
            
            # Log setup initiation
            MFAAuditLog.log_event(
                mfa_config_id=mfa_config.id,
                event_type='totp_setup_initiated',
                event_description='TOTP setup process started',
                event_result='success',
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                session_id=session.get('session_id') if session else None
            )
            
            return mfa_config.totp_secret, qr_code_base64, None
            
        except Exception as e:
            logger.error(f"Error setting up TOTP for user {user_id}: {str(e)}")
            return None, None, f"Setup failed: {str(e)}"
    
    @staticmethod
    def generate_qr_code(provisioning_uri):
        """Generate QR code from provisioning URI"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for HTML embedding
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return img_base64
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            return None
    
    @staticmethod
    def verify_totp_setup(user_id, totp_code):
        """Verify TOTP code during setup process"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config or not mfa_config.totp_secret:
                return False, "MFA configuration not found"
            
            # Create TOTP object
            totp = pyotp.TOTP(mfa_config.totp_secret)
            
            # Verify the code (with 30-second window tolerance)
            is_valid = totp.verify(totp_code, valid_window=1)
            
            if is_valid:
                # Enable TOTP for the user
                mfa_config.totp_enabled = True
                mfa_config.totp_verified = True
                mfa_config.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Generate backup codes
                backup_codes = mfa_config.generate_backup_codes()
                
                # Log successful setup
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='totp_setup_completed',
                    event_description='TOTP setup successfully completed',
                    event_result='success',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None,
                    additional_data={'backup_codes_generated': len(backup_codes)}
                )
                
                return True, backup_codes
            else:
                # Log failed verification
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='totp_setup_verification',
                    event_description='TOTP verification failed during setup',
                    event_result='failure',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None
                )
                
                return False, "Invalid verification code"
                
        except Exception as e:
            logger.error(f"Error verifying TOTP setup for user {user_id}: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    @staticmethod
    def verify_totp_login(user_id, totp_code):
        """Verify TOTP code during login process"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config or not mfa_config.totp_enabled or not mfa_config.totp_secret:
                return False, "MFA not enabled for this user"
            
            # Create TOTP object
            totp = pyotp.TOTP(mfa_config.totp_secret)
            
            # Verify the code (with 30-second window tolerance)
            is_valid = totp.verify(totp_code, valid_window=1)
            
            if is_valid:
                # Update last used timestamp
                mfa_config.last_used_at = datetime.utcnow()
                db.session.commit()
                
                # Log successful verification
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='totp_login_verification',
                    event_description='TOTP login verification successful',
                    event_result='success',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None
                )
                
                return True, "Verification successful"
            else:
                # Log failed verification
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='totp_login_verification',
                    event_description='TOTP login verification failed',
                    event_result='failure',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None
                )
                
                return False, "Invalid verification code"
                
        except Exception as e:
            logger.error(f"Error verifying TOTP login for user {user_id}: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    @staticmethod
    def verify_backup_code(user_id, backup_code):
        """Verify backup code for account recovery"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config:
                return False, "MFA configuration not found"
            
            # Verify backup code
            is_valid = mfa_config.verify_backup_code(backup_code.upper().strip())
            
            if is_valid:
                # Log successful backup code usage
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='backup_code_used',
                    event_description='Backup code successfully used for authentication',
                    event_result='success',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None,
                    additional_data={'remaining_codes': mfa_config.get_unused_backup_codes_count()}
                )
                
                return True, "Backup code verified successfully"
            else:
                # Log failed backup code attempt
                MFAAuditLog.log_event(
                    mfa_config_id=mfa_config.id,
                    event_type='backup_code_verification',
                    event_description='Invalid backup code attempted',
                    event_result='failure',
                    ip_address=request.remote_addr if request else None,
                    user_agent=request.headers.get('User-Agent') if request else None,
                    session_id=session.get('session_id') if session else None
                )
                
                return False, "Invalid or already used backup code"
                
        except Exception as e:
            logger.error(f"Error verifying backup code for user {user_id}: {str(e)}")
            return False, f"Verification failed: {str(e)}"
    
    @staticmethod
    def disable_mfa(user_id):
        """Disable MFA for a user"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config:
                return False, "MFA configuration not found"
            
            # Disable MFA
            mfa_config.totp_enabled = False
            mfa_config.totp_verified = False
            mfa_config.totp_secret = None  # Clear secret for security
            mfa_config.backup_codes_generated = False
            mfa_config.backup_codes_count = 0
            mfa_config.updated_at = datetime.utcnow()
            
            # Remove all backup codes
            for backup_code in mfa_config.backup_codes:
                db.session.delete(backup_code)
            
            db.session.commit()
            
            # Log MFA disable
            MFAAuditLog.log_event(
                mfa_config_id=mfa_config.id,
                event_type='mfa_disabled',
                event_description='MFA disabled for user account',
                event_result='success',
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                session_id=session.get('session_id') if session else None
            )
            
            return True, "MFA disabled successfully"
            
        except Exception as e:
            logger.error(f"Error disabling MFA for user {user_id}: {str(e)}")
            db.session.rollback()
            return False, f"Failed to disable MFA: {str(e)}"
    
    @staticmethod
    def get_mfa_status(user_id):
        """Get MFA status for a user"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config:
                return {
                    'enabled': False,
                    'verified': False,
                    'backup_codes_count': 0,
                    'setup_required': False,
                    'is_enforced': False
                }
            
            return {
                'enabled': mfa_config.totp_enabled,
                'verified': mfa_config.totp_verified,
                'backup_codes_count': mfa_config.get_unused_backup_codes_count(),
                'setup_required': mfa_config.setup_required,
                'is_enforced': mfa_config.is_enforced,
                'last_used': mfa_config.last_used_at.isoformat() if mfa_config.last_used_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting MFA status for user {user_id}: {str(e)}")
            return {
                'enabled': False,
                'verified': False,
                'backup_codes_count': 0,
                'setup_required': False,
                'is_enforced': False,
                'error': str(e)
            }
    
    @staticmethod
    def regenerate_backup_codes(user_id):
        """Regenerate backup codes for a user"""
        try:
            mfa_config = MFAConfiguration.query.filter_by(user_id=user_id).first()
            if not mfa_config or not mfa_config.totp_enabled:
                return None, "MFA is not enabled for this user"
            
            # Generate new backup codes
            backup_codes = mfa_config.generate_backup_codes()
            
            # Log backup codes regeneration
            MFAAuditLog.log_event(
                mfa_config_id=mfa_config.id,
                event_type='backup_codes_regenerated',
                event_description='Backup codes regenerated by user',
                event_result='success',
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                session_id=session.get('session_id') if session else None,
                additional_data={'new_codes_count': len(backup_codes)}
            )
            
            return backup_codes, "Backup codes regenerated successfully"
            
        except Exception as e:
            logger.error(f"Error regenerating backup codes for user {user_id}: {str(e)}")
            return None, f"Failed to regenerate backup codes: {str(e)}"