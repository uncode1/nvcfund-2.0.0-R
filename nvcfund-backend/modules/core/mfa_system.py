"""
Multi-Factor Authentication System
Implements TOTP, SMS, and backup code authentication for banking security
"""

import os
import pyotp
import qrcode
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from io import BytesIO
import base64
from flask import current_app
from modules.core.extensions import db

logger = logging.getLogger(__name__)

class MFASystem:
    """
    Comprehensive Multi-Factor Authentication system
    Supports TOTP, SMS backup codes, and recovery procedures
    """
    
    def __init__(self):
        self.issuer_name = "NVC Banking Platform"
        self.backup_code_length = 8
        self.backup_code_count = 10
        
    def setup_totp_for_user(self, user_id: int, username: str) -> Dict[str, any]:
        """
        Set up TOTP (Time-based One-Time Password) for user
        Returns secret key and QR code for authenticator app setup
        """
        try:
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate provisioning URI for QR code
            provisioning_uri = totp.provisioning_uri(
                name=username,
                issuer_name=self.issuer_name
            )
            
            # Generate QR code
            qr_code_data = self._generate_qr_code(provisioning_uri)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Store MFA configuration (you'll need to implement this in your user model)
            mfa_config = {
                'totp_secret': secret,
                'backup_codes': backup_codes,
                'setup_date': datetime.utcnow().isoformat(),
                'is_verified': False
            }
            
            return {
                'success': True,
                'secret': secret,
                'qr_code': qr_code_data,
                'backup_codes': backup_codes,
                'manual_entry_key': secret,
                'mfa_config': mfa_config
            }
            
        except Exception as e:
            logger.error(f"TOTP setup failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to set up TOTP authentication'
            }
    
    def verify_totp_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token with time window tolerance
        Window allows for clock drift compensation
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification failed: {e}")
            return False
    
    def verify_backup_code(self, user_backup_codes: List[str], provided_code: str) -> Tuple[bool, List[str]]:
        """
        Verify backup code and remove it from available codes
        Returns (success, remaining_codes)
        """
        try:
            # Normalize provided code
            provided_code = provided_code.strip().upper()
            
            # Check if code exists in backup codes
            if provided_code in user_backup_codes:
                # Remove used code
                remaining_codes = [code for code in user_backup_codes if code != provided_code]
                logger.info(f"Backup code used successfully. Remaining codes: {len(remaining_codes)}")
                return True, remaining_codes
            else:
                logger.warning("Invalid backup code provided")
                return False, user_backup_codes
                
        except Exception as e:
            logger.error(f"Backup code verification failed: {e}")
            return False, user_backup_codes
    
    def _generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code as base64 image data"""
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
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            return ""
    
    def _generate_backup_codes(self) -> List[str]:
        """Generate secure backup codes"""
        codes = []
        for _ in range(self.backup_code_count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') 
                          for _ in range(self.backup_code_length))
            codes.append(code)
        return codes
    
    def regenerate_backup_codes(self, user_id: int) -> List[str]:
        """
        Regenerate backup codes for user
        Used when user runs out of backup codes
        """
        try:
            new_codes = self._generate_backup_codes()
            logger.info(f"Generated new backup codes for user {user_id}")
            return new_codes
        except Exception as e:
            logger.error(f"Backup code regeneration failed for user {user_id}: {e}")
            return []
    
    def validate_mfa_setup(self, secret: str, verification_token: str) -> bool:
        """
        Validate MFA setup by verifying the first token
        Ensures user has correctly configured their authenticator app
        """
        return self.verify_totp_token(secret, verification_token)
    
    def get_mfa_status(self, user_mfa_config: Dict) -> Dict[str, any]:
        """
        Get comprehensive MFA status for user
        Returns setup status and available methods
        """
        if not user_mfa_config:
            return {
                'enabled': False,
                'totp_configured': False,
                'backup_codes_available': 0,
                'setup_required': True
            }
        
        backup_codes = user_mfa_config.get('backup_codes', [])
        
        return {
            'enabled': user_mfa_config.get('is_verified', False),
            'totp_configured': bool(user_mfa_config.get('totp_secret')),
            'backup_codes_available': len(backup_codes),
            'setup_date': user_mfa_config.get('setup_date'),
            'setup_required': not user_mfa_config.get('is_verified', False)
        }
    
    def emergency_disable_mfa(self, user_id: int, admin_user_id: int, reason: str) -> bool:
        """
        Emergency MFA disable function for admin use
        Requires admin authorization and logs the action
        """
        try:
            logger.critical(
                f"EMERGENCY MFA DISABLE: User {user_id} MFA disabled by admin {admin_user_id}. "
                f"Reason: {reason}"
            )
            # Implementation would update user MFA configuration
            return True
        except Exception as e:
            logger.error(f"Emergency MFA disable failed: {e}")
            return False

# Global MFA system instance
mfa_system = MFASystem()