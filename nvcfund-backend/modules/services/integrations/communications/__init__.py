"""
Communications Integration Sub-module
Part of the Integrations Module - NVC Banking Platform

This sub-module provides:
- Communication service integrations (SendGrid, Twilio, Push Notifications)
- Email and SMS processing services
- Notification management and delivery
- Communication analytics and monitoring
"""

from .routes import communications_integration_bp
from .sendgrid.routes import sendgrid_bp
from .twilio.routes import twilio_bp

__all__ = ['communications_integration_bp', 'sendgrid_bp', 'twilio_bp']