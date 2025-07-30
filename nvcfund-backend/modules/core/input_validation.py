"""
NVC Banking Platform - Enhanced Input Validation System
Comprehensive input validation and sanitization for banking operations
"""

import re
import html
import bleach
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from modules.core.enhanced_error_handler import BankingError


class InputValidator:
    """Comprehensive input validation for banking operations"""
    
    # Banking-specific patterns
    ACCOUNT_NUMBER_PATTERN = re.compile(r'^[0-9]{8,20}$')
    ROUTING_NUMBER_PATTERN = re.compile(r'^[0-9]{9}$')
    SSN_PATTERN = re.compile(r'^\d{3}-\d{2}-\d{4}$')
    PHONE_PATTERN = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Security patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT|JAVASCRIPT)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\')(.*)(--|\#)",
        r"(\')(.*)(UNION|SELECT|INSERT|UPDATE|DELETE)"
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*="
    ]
    
    @classmethod
    def sanitize_input(cls, input_value: str, strict: bool = False) -> str:
        """Sanitize input string to prevent XSS and injection attacks"""
        
        if not isinstance(input_value, str):
            input_value = str(input_value)
        
        # HTML escape
        sanitized = html.escape(input_value)
        
        # Use bleach for additional sanitization
        if strict:
            # Strip all HTML tags
            sanitized = bleach.clean(sanitized, tags=[], strip=True)
        else:
            # Allow only safe HTML tags
            allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
            sanitized = bleach.clean(sanitized, tags=allowed_tags, strip=True)
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise BankingError(
                    message="Invalid input detected",
                    error_code="INVALID_INPUT",
                    status_code=400
                )
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise BankingError(
                    message="Invalid input detected",
                    error_code="INVALID_INPUT", 
                    status_code=400
                )
        
        return sanitized.strip()
    
    @classmethod
    def validate_amount(cls, amount: Union[str, int, float, Decimal], 
                       min_amount: float = 0.01, 
                       max_amount: Optional[float] = None,
                       allow_negative: bool = False) -> Decimal:
        """Validate monetary amounts with proper decimal handling"""
        
        try:
            if isinstance(amount, str):
                # Remove currency symbols and commas
                amount = re.sub(r'[$,\s]', '', amount)
            
            decimal_amount = Decimal(str(amount))
            
            # Check for negative amounts
            if not allow_negative and decimal_amount < 0:
                raise BankingError(
                    message="Amount cannot be negative",
                    error_code="NEGATIVE_AMOUNT",
                    status_code=400
                )
            
            # Check minimum amount
            if decimal_amount < Decimal(str(min_amount)):
                raise BankingError(
                    message=f"Amount must be at least ${min_amount}",
                    error_code="AMOUNT_TOO_LOW",
                    details={'min_amount': min_amount},
                    status_code=400
                )
            
            # Check maximum amount
            if max_amount and decimal_amount > Decimal(str(max_amount)):
                raise BankingError(
                    message=f"Amount exceeds maximum limit of ${max_amount}",
                    error_code="AMOUNT_TOO_HIGH",
                    details={'max_amount': max_amount},
                    status_code=400
                )
            
            # Check for reasonable precision (max 2 decimal places for currency)
            if decimal_amount.as_tuple().exponent < -2:
                raise BankingError(
                    message="Amount cannot have more than 2 decimal places",
                    error_code="INVALID_PRECISION",
                    status_code=400
                )
            
            return decimal_amount
            
        except (ValueError, InvalidOperation):
            raise BankingError(
                message="Invalid amount format",
                error_code="INVALID_AMOUNT_FORMAT",
                status_code=400
            )
    
    @classmethod
    def validate_account_number(cls, account_number: str) -> str:
        """Validate bank account number format"""
        
        account_number = cls.sanitize_input(account_number, strict=True)
        
        if not cls.ACCOUNT_NUMBER_PATTERN.match(account_number):
            raise BankingError(
                message="Invalid account number format",
                error_code="INVALID_ACCOUNT_NUMBER",
                status_code=400
            )
        
        return account_number
    
    @classmethod
    def validate_routing_number(cls, routing_number: str) -> str:
        """Validate bank routing number with checksum"""
        
        routing_number = cls.sanitize_input(routing_number, strict=True)
        
        if not cls.ROUTING_NUMBER_PATTERN.match(routing_number):
            raise BankingError(
                message="Invalid routing number format",
                error_code="INVALID_ROUTING_NUMBER", 
                status_code=400
            )
        
        # Validate routing number checksum
        if not cls._validate_routing_checksum(routing_number):
            raise BankingError(
                message="Invalid routing number checksum",
                error_code="INVALID_ROUTING_CHECKSUM",
                status_code=400
            )
        
        return routing_number
    
    @classmethod
    def validate_ssn(cls, ssn: str) -> str:
        """Validate Social Security Number format"""
        
        ssn = cls.sanitize_input(ssn, strict=True)
        
        if not cls.SSN_PATTERN.match(ssn):
            raise BankingError(
                message="Invalid SSN format. Use XXX-XX-XXXX format",
                error_code="INVALID_SSN_FORMAT",
                status_code=400
            )
        
        # Check for invalid SSN patterns
        parts = ssn.split('-')
        if parts[0] in ['000', '666'] or parts[0].startswith('9'):
            raise BankingError(
                message="Invalid SSN number",
                error_code="INVALID_SSN",
                status_code=400
            )
        
        if parts[1] == '00' or parts[2] == '0000':
            raise BankingError(
                message="Invalid SSN number",
                error_code="INVALID_SSN",
                status_code=400
            )
        
        return ssn
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email address format"""
        
        email = cls.sanitize_input(email, strict=True).lower()
        
        if not cls.EMAIL_PATTERN.match(email):
            raise BankingError(
                message="Invalid email address format",
                error_code="INVALID_EMAIL",
                status_code=400
            )
        
        # Check for disposable email domains
        disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com'
        ]
        
        domain = email.split('@')[1]
        if domain in disposable_domains:
            raise BankingError(
                message="Disposable email addresses are not allowed",
                error_code="DISPOSABLE_EMAIL",
                status_code=400
            )
        
        return email
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate phone number format"""
        
        phone = cls.sanitize_input(phone, strict=True)
        
        if not cls.PHONE_PATTERN.match(phone):
            raise BankingError(
                message="Invalid phone number format",
                error_code="INVALID_PHONE",
                status_code=400
            )
        
        # Extract digits only
        digits_only = re.sub(r'[^0-9]', '', phone)
        
        # Format as standard US phone number
        if len(digits_only) == 10:
            formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            formatted = f"({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            raise BankingError(
                message="Invalid phone number length",
                error_code="INVALID_PHONE_LENGTH",
                status_code=400
            )
        
        return formatted
    
    @classmethod
    def validate_date(cls, date_str: str, date_format: str = '%Y-%m-%d') -> date:
        """Validate date format and reasonable ranges"""
        
        date_str = cls.sanitize_input(date_str, strict=True)
        
        try:
            parsed_date = datetime.strptime(date_str, date_format).date()
            
            # Check reasonable date ranges
            min_date = date(1900, 1, 1)
            max_date = date(2100, 12, 31)
            
            if parsed_date < min_date or parsed_date > max_date:
                raise BankingError(
                    message="Date is outside acceptable range",
                    error_code="DATE_OUT_OF_RANGE",
                    status_code=400
                )
            
            return parsed_date
            
        except ValueError:
            raise BankingError(
                message=f"Invalid date format. Expected {date_format}",
                error_code="INVALID_DATE_FORMAT",
                status_code=400
            )
    
    @classmethod
    def validate_required_fields(cls, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validate that all required fields are present and not empty"""
        
        missing_fields = []
        sanitized_data = {}
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
            elif isinstance(data[field], str) and not data[field].strip():
                missing_fields.append(field)
            else:
                # Sanitize string inputs
                if isinstance(data[field], str):
                    sanitized_data[field] = cls.sanitize_input(data[field])
                else:
                    sanitized_data[field] = data[field]
        
        if missing_fields:
            raise BankingError(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                error_code="MISSING_REQUIRED_FIELDS",
                details={'missing_fields': missing_fields},
                status_code=400
            )
        
        # Add non-required fields (sanitized if strings)
        for field, value in data.items():
            if field not in sanitized_data:
                if isinstance(value, str):
                    sanitized_data[field] = cls.sanitize_input(value)
                else:
                    sanitized_data[field] = value
        
        return sanitized_data
    
    @classmethod
    def _validate_routing_checksum(cls, routing_number: str) -> bool:
        """Validate routing number using checksum algorithm"""
        
        if len(routing_number) != 9:
            return False
        
        # ABA routing number checksum algorithm
        weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
        total = sum(int(digit) * weight for digit, weight in zip(routing_number, weights))
        
        return total % 10 == 0


# Global validator instance
input_validator = InputValidator()