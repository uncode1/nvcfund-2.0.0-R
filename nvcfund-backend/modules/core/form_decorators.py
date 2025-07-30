"""
Form Processing Decorators for NVC Banking Platform
Decorators for handling CSRF-protected form submissions
"""

import json
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify, render_template, redirect, url_for, flash
from flask_login import current_user

from .form_processor import form_processor
from .enterprise_logging import get_enterprise_logger

logger = get_enterprise_logger('form_decorators')

def process_form(form_type: str, module_name: str, success_template: Optional[str] = None,
                error_template: Optional[str] = None, redirect_url: Optional[str] = None,
                json_response: bool = False):
    """
    Decorator for processing forms with CSRF protection and database storage
    
    Args:
        form_type: Type of form being processed
        module_name: Module name for the form
        success_template: Template to render on success
        error_template: Template to render on error
        redirect_url: URL to redirect to on success
        json_response: Whether to return JSON response
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                # Extract form data
                form_data = {}
                for key, value in request.form.items():
                    if key != 'csrf_token':  # Exclude CSRF token from form data
                        form_data[key] = value
                
                # Process the form
                result = form_processor.process_form(
                    form_type=form_type,
                    module_name=module_name,
                    form_data=form_data,
                    user_id=current_user.id if current_user.is_authenticated else None
                )
                
                if json_response:
                    return jsonify(result)
                
                if result['success']:
                    flash(f'{form_type.title()} submitted successfully', 'success')
                    if redirect_url:
                        return redirect(redirect_url)
                    elif success_template:
                        return render_template(success_template, result=result)
                else:
                    flash(f'Error processing {form_type}: {result.get("error", "Unknown error")}', 'error')
                    if error_template:
                        return render_template(error_template, error=result)
            
            # Call original function for GET requests or fallback
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def banking_form(form_type: str, success_redirect: Optional[str] = None):
    """Decorator specifically for banking forms"""
    return process_form(
        form_type=form_type,
        module_name='banking',
        redirect_url=success_redirect or 'banking.dashboard'
    )

def treasury_form(form_type: str, success_redirect: Optional[str] = None):
    """Decorator specifically for treasury forms"""
    return process_form(
        form_type=form_type,
        module_name='treasury',
        redirect_url=success_redirect or 'treasury.dashboard'
    )

def trading_form(form_type: str, success_redirect: Optional[str] = None):
    """Decorator specifically for trading forms"""
    return process_form(
        form_type=form_type,
        module_name='trading',
        redirect_url=success_redirect or 'trading.dashboard'
    )

def payment_form(form_type: str, success_redirect: Optional[str] = None):
    """Decorator specifically for payment forms"""
    return process_form(
        form_type=form_type,
        module_name='cards_payments',
        redirect_url=success_redirect or 'cards_payments.dashboard'
    )

def admin_form(form_type: str, success_redirect: Optional[str] = None):
    """Decorator specifically for admin forms"""
    return process_form(
        form_type=form_type,
        module_name='admin_management',
        redirect_url=success_redirect or 'admin_management.dashboard'
    )

def require_post_data(required_fields: list):
    """Decorator to require specific POST fields"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                missing_fields = []
                for field in required_fields:
                    if field not in request.form or not request.form[field].strip():
                        missing_fields.append(field)
                
                if missing_fields:
                    flash(f'Missing required fields: {", ".join(missing_fields)}', 'error')
                    return redirect(request.url)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_form_data(validation_rules: Dict[str, Callable]):
    """Decorator to validate form data"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                validation_errors = []
                
                for field, validator in validation_rules.items():
                    if field in request.form:
                        try:
                            validator(request.form[field])
                        except ValueError as e:
                            validation_errors.append(f'{field}: {str(e)}')
                
                if validation_errors:
                    flash(f'Validation errors: {"; ".join(validation_errors)}', 'error')
                    return redirect(request.url)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator