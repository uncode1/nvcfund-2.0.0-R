"""
Data Security Framework for NVC Banking Platform
Comprehensive security for data in transit and data at rest
Integrated with Security Center Module
"""

import os
import hashlib
import hmac
import json
import base64
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

class DataSecurityFramework:
    """
    Comprehensive data security framework for banking-grade applications
    Handles encryption, hashing, secure transmission, and data protection
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.backend = default_backend()
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key from environment or generate new one"""
        env_key = os.environ.get('DATA_ENCRYPTION_KEY')
        if env_key:
            try:
                # Try to use the key directly if it's already a Fernet key
                if isinstance(env_key, str) and len(env_key) == 44:
                    # This is likely a Fernet key string, encode it to bytes
                    return env_key.encode('utf-8')
                else:
                    # Try to decode as base64
                    return base64.urlsafe_b64decode(env_key)
            except Exception as e:
                logger.warning(f"Invalid encryption key format: {e}, generating new key")

        # Generate new key for development
        key = Fernet.generate_key()
        logger.warning("Generated new encryption key - set DATA_ENCRYPTION_KEY in production")
        return key
    
    def encrypt_sensitive_data(self, data: Union[str, dict, bytes, int, float]) -> str:
        """
        Encrypt sensitive data for storage (data at rest)
        Returns base64-encoded encrypted string
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data, default=str)
            elif isinstance(data, (int, float)):
                data = str(data)
            elif isinstance(data, str):
                pass  # Already a string
            elif isinstance(data, bytes):
                data = data.decode('utf-8')
            else:
                data = str(data)
            
            # Ensure data is bytes for encryption
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted = self.fernet.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise SecurityError("Failed to encrypt sensitive data")
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Union[str, dict, int, float]:
        """
        Decrypt sensitive data from storage (data at rest)
        Returns original data format
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.fernet.decrypt(encrypted_bytes)
            decrypted_str = decrypted.decode('utf-8')
            
            # Try to parse as JSON first
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                # Try to parse as number
                try:
                    if '.' in decrypted_str:
                        return float(decrypted_str)
                    else:
                        return int(decrypted_str)
                except ValueError:
                    return decrypted_str
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise SecurityError("Failed to decrypt sensitive data")
    
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """
        Hash password with salt for secure storage
        Returns (hash, salt) tuple
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        
        password_hash = kdf.derive(password.encode('utf-8'))
        return base64.urlsafe_b64encode(password_hash).decode('utf-8'), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: bytes) -> bool:
        """Verify password against stored hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(stored_hash, computed_hash)
        except Exception:
            return False
    
    def secure_token_generation(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def create_secure_session_token(self, user_id: str, expires_in: int = 900) -> dict:
        """
        Create secure session token with expiration
        Returns token data for secure transmission
        """
        token_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
            'token_id': self.secure_token_generation()
        }
        
        encrypted_token = self.encrypt_sensitive_data(token_data)
        return {
            'token': encrypted_token,
            'expires_in': expires_in,
            'token_type': 'Bearer'
        }
    
    def validate_secure_token(self, token: str) -> Optional[dict]:
        """Validate and decrypt secure token"""
        try:
            token_data = self.decrypt_sensitive_data(token)
            
            # Check expiration
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.utcnow() > expires_at:
                return None
                
            return token_data
            
        except Exception:
            return None
    
    def secure_data_transmission(self, data: dict, recipient_context: str = None) -> dict:
        """
        Prepare data for secure transmission (data in transit)
        Adds integrity checks and encryption
        """
        transmission_data = {
            'payload': self.encrypt_sensitive_data(data),
            'timestamp': datetime.utcnow().isoformat(),
            'integrity_hash': self._calculate_integrity_hash(data),
            'transmission_id': self.secure_token_generation(16)
        }
        
        if recipient_context:
            transmission_data['context'] = recipient_context
            
        return transmission_data
    
    def verify_transmitted_data(self, transmission_data: dict) -> Optional[dict]:
        """
        Verify and decrypt transmitted data
        Returns original data if verification succeeds
        """
        try:
            # Decrypt payload
            decrypted_data = self.decrypt_sensitive_data(transmission_data['payload'])
            
            # Verify integrity
            calculated_hash = self._calculate_integrity_hash(decrypted_data)
            if not hmac.compare_digest(transmission_data['integrity_hash'], calculated_hash):
                logger.error("Data integrity verification failed")
                return None
                
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data transmission verification failed: {e}")
            return None
    
    def _calculate_integrity_hash(self, data: dict) -> str:
        """Calculate HMAC for data integrity"""
        data_string = json.dumps(data, sort_keys=True)
        return hmac.new(
            self.encryption_key,
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def secure_field_encryption(self, field_value: str, field_name: str) -> str:
        """
        Encrypt specific database fields
        Adds field context for additional security
        """
        field_data = {
            'value': field_value,
            'field': field_name,
            'encrypted_at': datetime.utcnow().isoformat()
        }
        return self.encrypt_sensitive_data(field_data)
    
    def secure_field_decryption(self, encrypted_field: str, expected_field: str) -> str:
        """
        Decrypt specific database fields with validation
        """
        try:
            field_data = self.decrypt_sensitive_data(encrypted_field)
            
            # Validate field context
            if field_data.get('field') != expected_field:
                raise SecurityError(f"Field context mismatch: expected {expected_field}")
                
            return field_data['value']
            
        except Exception as e:
            logger.error(f"Field decryption failed for {expected_field}: {e}")
            raise SecurityError("Failed to decrypt field data")
    
    def sanitize_input_data(self, data: Union[str, dict]) -> Union[str, dict]:
        """
        Sanitize input data to prevent injection attacks
        """
        if isinstance(data, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', 'javascript:', 'data:', 'vbscript:']
            sanitized = data
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
            return sanitized.strip()
            
        elif isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                sanitized_key = self.sanitize_input_data(key)
                sanitized_value = self.sanitize_input_data(value) if isinstance(value, (str, dict)) else value
                sanitized[sanitized_key] = sanitized_value
            return sanitized
            
        return data
    
    def create_audit_hash(self, operation: str, data: dict, user_id: str) -> str:
        """
        Create audit hash for banking operations
        Ensures data integrity for compliance
        """
        audit_data = {
            'operation': operation,
            'data_hash': self._calculate_integrity_hash(data),
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self._calculate_integrity_hash(audit_data)
    
    def mask_sensitive_data(self, data: str, mask_type: str = 'account') -> str:
        """
        Mask sensitive data for display purposes
        """
        if not data:
            return data
            
        if mask_type == 'account':
            # Show last 4 digits of account numbers
            return '*' * (len(data) - 4) + data[-4:] if len(data) > 4 else '****'
        elif mask_type == 'ssn':
            # Show last 4 digits of SSN
            return 'XXX-XX-' + data[-4:] if len(data) >= 4 else 'XXX-XX-XXXX'
        elif mask_type == 'email':
            # Show first char and domain
            if '@' in data:
                local, domain = data.split('@')
                return local[0] + '*' * (len(local) - 1) + '@' + domain
            return data
        elif mask_type == 'phone':
            # Show last 4 digits of phone
            return '***-***-' + data[-4:] if len(data) >= 4 else '***-***-****'
        else:
            # Generic masking
            return '*' * len(data)
    
    def validate_data_integrity(self, data: dict, expected_hash: str) -> bool:
        """
        Validate data integrity using hash comparison
        """
        calculated_hash = self._calculate_integrity_hash(data)
        return hmac.compare_digest(expected_hash, calculated_hash)


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class SecureDataTransmission:
    """
    Decorator and utility class for secure data transmission
    """
    
    def __init__(self, security_framework: DataSecurityFramework):
        self.security = security_framework
        
    def secure_route_data(self, func):
        """
        Decorator to automatically secure route data transmission
        """
        def wrapper(*args, **kwargs):
            try:
                # Execute original function
                result = func(*args, **kwargs)
                
                # If result is a dict (JSON response), secure it
                if isinstance(result, dict):
                    return self.security.secure_data_transmission(result)
                    
                return result
                
            except Exception as e:
                logger.error(f"Secure route execution failed: {e}")
                raise
                
        return wrapper
    
    def secure_database_write(self, data: dict, table_name: str, user_id: str) -> dict:
        """
        Secure database write operation with audit trail
        """
        # Create audit hash
        audit_hash = self.security.create_audit_hash('INSERT', data, user_id)
        
        # Encrypt sensitive fields
        secured_data = {}
        sensitive_fields = ['ssn', 'account_number', 'routing_number', 'password', 'pin']
        
        for key, value in data.items():
            if key.lower() in sensitive_fields:
                secured_data[key] = self.security.secure_field_encryption(str(value), key)
            else:
                secured_data[key] = value
                
        # Add audit information
        secured_data['audit_hash'] = audit_hash
        secured_data['created_at'] = datetime.utcnow().isoformat()
        
        return secured_data
    
    def secure_database_read(self, data: dict, expected_fields: list = None) -> dict:
        """
        Secure database read operation with field decryption
        """
        if not expected_fields:
            expected_fields = ['ssn', 'account_number', 'routing_number', 'password', 'pin']
            
        decrypted_data = {}
        
        for key, value in data.items():
            if key.lower() in expected_fields and value:
                try:
                    decrypted_data[key] = self.security.secure_field_decryption(value, key)
                except SecurityError:
                    # If decryption fails, it might be plain text (migration scenario)
                    decrypted_data[key] = value
            else:
                decrypted_data[key] = value
                
        return decrypted_data


# Global security framework instance
security_framework = DataSecurityFramework()
secure_transmission = SecureDataTransmission(security_framework)

# Export commonly used functions
def encrypt_data(data: Union[str, dict]) -> str:
    """Quick access to data encryption"""
    return security_framework.encrypt_sensitive_data(data)

def decrypt_data(encrypted_data: str) -> Union[str, dict]:
    """Quick access to data decryption"""
    return security_framework.decrypt_sensitive_data(encrypted_data)

def secure_hash(password: str, salt: bytes = None) -> tuple:
    """Quick access to password hashing"""
    return security_framework.hash_password(password, salt)

def verify_hash(password: str, stored_hash: str, salt: bytes) -> bool:
    """Quick access to password verification"""
    return security_framework.verify_password(password, stored_hash, salt)

def generate_secure_token(length: int = 32) -> str:
    """Quick access to secure token generation"""
    return security_framework.secure_token_generation(length)

def mask_sensitive(data: str, mask_type: str = 'account') -> str:
    """Quick access to data masking"""
    return security_framework.mask_sensitive_data(data, mask_type)

def sanitize_input(data: Union[str, dict]) -> Union[str, dict]:
    """Quick access to input sanitization"""
    return security_framework.sanitize_input_data(data)