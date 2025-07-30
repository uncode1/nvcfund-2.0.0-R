"""
Communications Module
NVC Banking Platform - Enterprise Communications System

This module provides comprehensive communication capabilities including:
- Email notifications and alerts
- SMS messaging (optional)
- Automated personalized communications
- Transaction receipts and statements
- Birthday and holiday messages
- Login notifications
- Marketing communications

Features:
- SendGrid integration for reliable email delivery
- Template-based messaging with personalization
- Automated scheduling with Celery
- Audit logging for all communications
- Compliance with banking communication standards
"""

from flask import Blueprint

# Create Communications blueprint
communications_bp = Blueprint('communications', __name__, url_prefix='/communications', template_folder='templates')

# Import routes to register them
from . import routes

# Module metadata
__version__ = '1.0.0'
__author__ = 'NVC Banking Platform'
__description__ = 'Enterprise Communications and Messaging Module'