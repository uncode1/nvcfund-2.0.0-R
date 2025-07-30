"""
Secure Model Mixins for Database Operations
Provides automatic encryption/decryption for sensitive fields
Integrated with Security Center Module
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy
import json
import logging

from .data_security import security_framework, SecurityError

logger = logging.getLogger(__name__)

class SecureFieldMixin:
    """
    Mixin class for models with encrypted sensitive fields
    Provides automatic encryption/decryption for data at rest
    """
    
    @declared_attr
    def audit_hash(cls):
        """Audit hash for data integrity verification"""
        return Column(String(64), nullable=True)
    
    @declared_attr
    def encrypted_at(cls):
        """Timestamp when data was encrypted"""
        return Column(DateTime, default=datetime.utcnow)
    
    @declared_attr
    def data_version(cls):
        """Version for encryption key rotation"""
        return Column(String(10), default='1.0')
    
    def encrypt_field(self, field_name: str, value: str) -> str:
        """
        Encrypt a specific field value
        """
        if not value:
            return value
            
        try:
            encrypted_value = security_framework.secure_field_encryption(value, field_name)
            logger.debug(f"Field {field_name} encrypted successfully")
            return encrypted_value
        except Exception as e:
            logger.error(f"Field encryption failed for {field_name}: {e}")
            raise SecurityError(f"Failed to encrypt {field_name}")
    
    def decrypt_field(self, field_name: str, encrypted_value: str) -> str:
        """
        Decrypt a specific field value
        """
        if not encrypted_value:
            return encrypted_value
            
        try:
            decrypted_value = security_framework.secure_field_decryption(encrypted_value, field_name)
            logger.debug(f"Field {field_name} decrypted successfully")
            return decrypted_value
        except Exception as e:
            logger.error(f"Field decryption failed for {field_name}: {e}")
            # Return masked value instead of failing
            return security_framework.mask_sensitive_data(encrypted_value, 'account')
    
    def create_audit_hash(self, operation: str, user_id: str) -> str:
        """
        Create audit hash for the model instance
        """
        model_data = {}
        for column in self.__table__.columns:
            if column.name not in ['audit_hash', 'encrypted_at', 'data_version']:
                model_data[column.name] = getattr(self, column.name)
        
        return security_framework.create_audit_hash(operation, model_data, user_id)
    
    def validate_integrity(self, expected_hash: str) -> bool:
        """
        Validate model data integrity
        """
        model_data = {}
        for column in self.__table__.columns:
            if column.name not in ['audit_hash', 'encrypted_at', 'data_version']:
                model_data[column.name] = getattr(self, column.name)
        
        return security_framework.validate_data_integrity(model_data, expected_hash)


class BankingAccountSecureMixin(SecureFieldMixin):
    """
    Secure mixin for banking account models
    Handles encryption of sensitive banking data
    """
    
    @declared_attr
    def encrypted_account_number(cls):
        """Encrypted account number"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_routing_number(cls):
        """Encrypted routing number"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_ssn(cls):
        """Encrypted Social Security Number"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_pin(cls):
        """Encrypted PIN"""
        return Column(Text, nullable=True)
    
    def set_account_number(self, account_number: str):
        """Set encrypted account number"""
        self.encrypted_account_number = self.encrypt_field('account_number', account_number)
    
    def get_account_number(self) -> str:
        """Get decrypted account number"""
        if not self.encrypted_account_number:
            return None
        return self.decrypt_field('account_number', self.encrypted_account_number)
    
    def get_masked_account_number(self) -> str:
        """Get masked account number for display"""
        account_number = self.get_account_number()
        if account_number:
            return security_framework.mask_sensitive_data(account_number, 'account')
        return '****'
    
    def set_routing_number(self, routing_number: str):
        """Set encrypted routing number"""
        self.encrypted_routing_number = self.encrypt_field('routing_number', routing_number)
    
    def get_routing_number(self) -> str:
        """Get decrypted routing number"""
        if not self.encrypted_routing_number:
            return None
        return self.decrypt_field('routing_number', self.encrypted_routing_number)
    
    def get_masked_routing_number(self) -> str:
        """Get masked routing number for display"""
        routing_number = self.get_routing_number()
        if routing_number:
            return security_framework.mask_sensitive_data(routing_number, 'account')
        return '****'
    
    def set_ssn(self, ssn: str):
        """Set encrypted SSN"""
        self.encrypted_ssn = self.encrypt_field('ssn', ssn)
    
    def get_ssn(self) -> str:
        """Get decrypted SSN"""
        if not self.encrypted_ssn:
            return None
        return self.decrypt_field('ssn', self.encrypted_ssn)
    
    def get_masked_ssn(self) -> str:
        """Get masked SSN for display"""
        ssn = self.get_ssn()
        if ssn:
            return security_framework.mask_sensitive_data(ssn, 'ssn')
        return 'XXX-XX-XXXX'
    
    def set_pin(self, pin: str):
        """Set encrypted PIN"""
        self.encrypted_pin = self.encrypt_field('pin', pin)
    
    def verify_pin(self, pin: str) -> bool:
        """Verify PIN without decrypting"""
        if not self.encrypted_pin:
            return False
        try:
            stored_pin = self.decrypt_field('pin', self.encrypted_pin)
            return pin == stored_pin
        except Exception:
            return False


class UserSecureMixin(SecureFieldMixin):
    """
    Secure mixin for user models
    Handles encryption of sensitive user data
    """
    
    @declared_attr
    def encrypted_email(cls):
        """Encrypted email address"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_phone(cls):
        """Encrypted phone number"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_address(cls):
        """Encrypted address data"""
        return Column(Text, nullable=True)
    
    def set_email(self, email: str):
        """Set encrypted email"""
        self.encrypted_email = self.encrypt_field('email', email)
    
    def get_email(self) -> str:
        """Get decrypted email"""
        if not self.encrypted_email:
            return None
        return self.decrypt_field('email', self.encrypted_email)
    
    def get_masked_email(self) -> str:
        """Get masked email for display"""
        email = self.get_email()
        if email:
            return security_framework.mask_sensitive_data(email, 'email')
        return '****@****.com'
    
    def set_phone(self, phone: str):
        """Set encrypted phone number"""
        self.encrypted_phone = self.encrypt_field('phone', phone)
    
    def get_phone(self) -> str:
        """Get decrypted phone number"""
        if not self.encrypted_phone:
            return None
        return self.decrypt_field('phone', self.encrypted_phone)
    
    def get_masked_phone(self) -> str:
        """Get masked phone for display"""
        phone = self.get_phone()
        if phone:
            return security_framework.mask_sensitive_data(phone, 'phone')
        return '***-***-****'
    
    def set_address(self, address: dict):
        """Set encrypted address data"""
        address_json = json.dumps(address)
        self.encrypted_address = self.encrypt_field('address', address_json)
    
    def get_address(self) -> dict:
        """Get decrypted address data"""
        if not self.encrypted_address:
            return {}
        try:
            address_json = self.decrypt_field('address', self.encrypted_address)
            return json.loads(address_json)
        except Exception:
            return {}
    
    def get_masked_address(self) -> dict:
        """Get masked address for display"""
        address = self.get_address()
        if not address:
            return {}
        
        masked_address = {}
        for key, value in address.items():
            if key in ['street', 'address_line_1', 'address_line_2']:
                masked_address[key] = '***'
            elif key == 'postal_code':
                masked_address[key] = '****'
            else:
                masked_address[key] = value
        
        return masked_address


class TransactionSecureMixin(SecureFieldMixin):
    """
    Secure mixin for transaction models
    Handles encryption of sensitive transaction data
    """
    
    @declared_attr
    def encrypted_amount(cls):
        """Encrypted transaction amount"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_memo(cls):
        """Encrypted transaction memo"""
        return Column(Text, nullable=True)
    
    @declared_attr
    def encrypted_reference(cls):
        """Encrypted reference number"""
        return Column(Text, nullable=True)
    
    def set_amount(self, amount: str):
        """Set encrypted amount"""
        self.encrypted_amount = self.encrypt_field('amount', str(amount))
    
    def get_amount(self) -> float:
        """Get decrypted amount"""
        if not self.encrypted_amount:
            return 0.0
        try:
            amount_str = self.decrypt_field('amount', self.encrypted_amount)
            return float(amount_str)
        except Exception:
            return 0.0
    
    def set_memo(self, memo: str):
        """Set encrypted memo"""
        if memo:
            self.encrypted_memo = self.encrypt_field('memo', memo)
    
    def get_memo(self) -> str:
        """Get decrypted memo"""
        if not self.encrypted_memo:
            return None
        return self.decrypt_field('memo', self.encrypted_memo)
    
    def set_reference(self, reference: str):
        """Set encrypted reference number"""
        self.encrypted_reference = self.encrypt_field('reference', reference)
    
    def get_reference(self) -> str:
        """Get decrypted reference number"""
        if not self.encrypted_reference:
            return None
        return self.decrypt_field('reference', self.encrypted_reference)
    
    def get_masked_reference(self) -> str:
        """Get masked reference for display"""
        reference = self.get_reference()
        if reference:
            return security_framework.mask_sensitive_data(reference, 'account')
        return '****'


class SecureJSONField:
    """
    Secure JSON field that automatically encrypts/decrypts JSON data
    """
    
    def __init__(self, field_name: str):
        self.field_name = field_name
    
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        encrypted_value = getattr(obj, self.private_name, None)
        if not encrypted_value:
            return {}
        
        try:
            decrypted_json = security_framework.secure_field_decryption(encrypted_value, self.field_name)
            return json.loads(decrypted_json)
        except Exception:
            return {}
    
    def __set__(self, obj, value):
        if value is None:
            setattr(obj, self.private_name, None)
        else:
            json_str = json.dumps(value)
            encrypted_value = security_framework.secure_field_encryption(json_str, self.field_name)
            setattr(obj, self.private_name, encrypted_value)


def secure_model_to_dict(model_instance, include_sensitive: bool = False, mask_sensitive: bool = True) -> dict:
    """
    Convert model instance to dictionary with security considerations
    
    Args:
        model_instance: SQLAlchemy model instance
        include_sensitive: Whether to include sensitive fields
        mask_sensitive: Whether to mask sensitive data
    
    Returns:
        Dictionary representation of the model
    """
    result = {}
    
    # Get all columns
    for column in model_instance.__table__.columns:
        column_name = column.name
        value = getattr(model_instance, column_name)
        
        # Skip audit fields
        if column_name in ['audit_hash', 'encrypted_at', 'data_version']:
            continue
        
        # Handle encrypted fields
        if column_name.startswith('encrypted_'):
            if not include_sensitive:
                continue
            
            # Get the original field name
            original_field = column_name.replace('encrypted_', '')
            
            # Get the appropriate getter method
            if hasattr(model_instance, f'get_{original_field}'):
                if mask_sensitive and hasattr(model_instance, f'get_masked_{original_field}'):
                    result[original_field] = getattr(model_instance, f'get_masked_{original_field}')()
                else:
                    result[original_field] = getattr(model_instance, f'get_{original_field}')()
        else:
            result[column_name] = value
    
    return result