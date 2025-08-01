"""
Communications Services
NVC Banking Platform - Email and Messaging Service

This module provides comprehensive communication services including:
- Email sending via SendGrid
- Template-based messaging
- Personalized content generation
- Automated communication scheduling
- Audit logging for compliance
"""

import os
import logging
from datetime import datetime, date
from typing import Dict, List, Any
from flask import render_template, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from modules.core.extensions import db
import base64

logger = logging.getLogger(__name__)


class EmailService:
    """
    Enterprise Email Service using SendGrid
    Handles all email communications with audit logging
    """
    
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        if not self.api_key:
            logger.warning("SendGrid API key not found in environment variables")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)
        
        # Banking-specific templates for comprehensive communication
        self.email_templates = {
            'welcome': self._get_welcome_template(),
            'signup_verification': self._get_signup_verification_template(),
            'kyc_verification': self._get_kyc_verification_template(),
            'password_reset': self._get_password_reset_template(),
            'transaction_alert': self._get_transaction_alert_template(),
            'security_alert': self._get_security_alert_template(),
            'two_factor_code': self._get_2fa_code_template(),
            'account_statement': self._get_account_statement_template(),
            'loan_approval': self._get_loan_approval_template(),
            'card_application': self._get_card_application_template(),
            'compliance_notification': self._get_compliance_template()
        }
    
    def send_email(self, 
                   to_email: str,
                   subject: str,
                   html_content: str,
                   from_email: str = None,
                   attachments: List[Dict] = None,
                   template_name_for_log: str = 'custom',
                   context_for_log: Dict[str, Any] = None) -> bool:
        """
        Send email using SendGrid with pre-rendered HTML content.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: The HTML body of the email.
            from_email: Sender email (defaults to bank's official email)
            attachments: List of attachment dictionaries.
            template_name_for_log: The name of the template used, for logging.
            context_for_log: The context dictionary used, for logging.
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not self.client:
                logger.error("SendGrid client not initialized - missing API key")
                return False
            
            # Set default sender email
            if not from_email:
                from_email = "noreply@nvcfund.com"
            
            # Create email message
            message = Mail(
                from_email=Email(from_email, "NVC Banking Platform"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Add attachments if provided
            if attachments:
                for attachment_data in attachments:
                    attachment = Attachment()
                    attachment.file_content = attachment_data.get('content')
                    attachment.file_type = attachment_data.get('type', 'application/pdf')
                    attachment.file_name = attachment_data.get('filename', 'attachment.pdf')
                    attachment.disposition = attachment_data.get('disposition', 'attachment')
                    message.attachment = attachment
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email} using template {template_name_for_log}")
                
                # Log communication for audit
                self._log_communication(
                    to_email=to_email,
                    subject=subject,
                    template_name=template_name_for_log,
                    status='sent',
                    context=context_for_log
                )
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def _log_communication(self, 
                          to_email: str,
                          subject: str,
                          template_name: str,
                          status: str,
                          context: Dict[str, Any] = None):
        """Log communication for audit purposes"""
        try:
            # Import here to avoid circular imports
            from modules.services.communications.models import CommunicationLog
            
            log_entry = CommunicationLog(
                recipient_email=to_email,
                subject=subject,
                template_name=template_name,
                status=status,
                sent_at=datetime.utcnow(),
                context_data=context
            )
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging communication: {str(e)}")


class PersonalizedMessageService:
    """
    Service for generating personalized messages and communications
    """
    
    @staticmethod
    def generate_welcome_email_context(user) -> Dict[str, Any]:
        """Generate context for welcome email"""
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'last_name': getattr(user, 'last_name', ''),
            'email': getattr(user, 'email', ''),
            'account_number': getattr(user, 'account_number', 'Not Available'),
            'signup_date': datetime.utcnow().strftime('%B %d, %Y'),
            'login_url': current_app.config.get('BASE_URL', '') + '/auth/login',
            'support_email': 'support@nvcfund.com',
            'current_year': datetime.utcnow().year
        }
    
    @staticmethod
    def generate_login_notification_context(user, ip_address: str = None) -> Dict[str, Any]:
        """Generate context for login notification email"""
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'login_time': datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC'),
            'ip_address': ip_address or 'Unknown',
            'location': 'Unknown Location',  # Could integrate with IP geolocation service
            'device_info': 'Unknown Device',  # Could parse user agent
            'security_url': current_app.config.get('BASE_URL', '') + '/security',
            'support_email': 'security@nvcfund.com',
            'current_year': datetime.utcnow().year
        }
    
    @staticmethod
    def generate_transaction_receipt_context(transaction, user) -> Dict[str, Any]:
        """Generate context for transaction receipt email"""
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'transaction_id': getattr(transaction, 'id', 'N/A'),
            'transaction_type': getattr(transaction, 'transaction_type', 'Transaction'),
            'amount': f"${getattr(transaction, 'amount', 0):,.2f}",
            'transaction_date': getattr(transaction, 'created_at', datetime.utcnow()).strftime('%B %d, %Y at %I:%M %p'),
            'description': getattr(transaction, 'description', 'Banking transaction'),
            'account_balance': f"${getattr(user, 'account_balance', 0):,.2f}",
            'reference_number': getattr(transaction, 'reference_number', 'N/A'),
            'support_email': 'support@nvcfund.com',
            'current_year': datetime.utcnow().year
        }
    
    @staticmethod
    def generate_birthday_message_context(user) -> Dict[str, Any]:
        """Generate context for birthday message"""
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'birthday_year': datetime.utcnow().year,
            'special_offers': [
                {'title': 'Birthday Bonus', 'description': '0.5% extra interest on savings for 30 days'},
                {'title': 'Free Wire Transfers', 'description': 'No fees on international transfers this month'},
                {'title': 'Premium Support', 'description': 'Priority customer service access'}
            ],
            'customer_since': getattr(user, 'created_at', datetime.utcnow()).strftime('%Y'),
            'support_email': 'support@nvcfund.com',
            'current_year': datetime.utcnow().year
        }
    
    @staticmethod
    def generate_holiday_message_context(user, holiday_name: str) -> Dict[str, Any]:
        """Generate context for holiday message"""
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'holiday_name': holiday_name,
            'holiday_year': datetime.utcnow().year,
            'holiday_message': f"Wishing you and your family a wonderful {holiday_name}!",
            'special_hours': 'Our branches will have modified hours during the holiday. Please check our website for details.',
            'emergency_contact': '+1-800-NVC-BANK',
            'support_email': 'support@nvcfund.com',
            'current_year': datetime.utcnow().year
        }
    
    @staticmethod
    def generate_monthly_statement_context(user, account, transactions) -> Dict[str, Any]:
        """Generate context for monthly statement"""
        total_deposits = sum(t.amount for t in transactions if t.amount > 0)
        total_withdrawals = abs(sum(t.amount for t in transactions if t.amount < 0))
        
        return {
            'first_name': getattr(user, 'first_name', 'Valued Customer'),
            'last_name': getattr(user, 'last_name', ''),
            'account_number': getattr(account, 'account_number', 'N/A'),
            'statement_period': datetime.utcnow().strftime('%B %Y'),
            'opening_balance': f"${getattr(account, 'opening_balance', 0):,.2f}",
            'closing_balance': f"${getattr(account, 'balance', 0):,.2f}",
            'total_deposits': f"${total_deposits:,.2f}",
            'total_withdrawals': f"${total_withdrawals:,.2f}",
            'transaction_count': len(transactions),
            'transactions': [{
                'date': t.created_at.strftime('%m/%d/%Y'),
                'description': t.description,
                'amount': f"${t.amount:,.2f}" if t.amount > 0 else f"-${abs(t.amount):,.2f}",
                'balance': f"${t.running_balance:,.2f}" if hasattr(t, 'running_balance') else 'N/A'
            } for t in transactions],
            'support_email': 'support@nvcfund.com',
            'current_year': datetime.utcnow().year
        }


class CommunicationScheduler:
    """
    Service for scheduling automated communications
    """
    
    @staticmethod
    def schedule_birthday_messages():
        """Schedule birthday messages for users with today's birthday"""
        try:
            from modules.auth.models import User
            
            today = date.today()
            # Find users with birthday today
            birthday_users = User.query.filter(
                db.extract('month', User.date_of_birth) == today.month,
                db.extract('day', User.date_of_birth) == today.day
            ).all()
            
            email_service = EmailService()
            message_service = PersonalizedMessageService()
            
            for user in birthday_users:
                try:
                    context = message_service.generate_birthday_message_context(user)
                    success = email_service.send_email(
                        to_email=user.email,
                        subject=f"Happy Birthday, {user.first_name}! 🎉",
                        template_name="birthday_message",
                        context=context
                    )
                    
                    if success:
                        logger.info(f"Birthday message sent to {user.email}")
                    else:
                        logger.error(f"Failed to send birthday message to {user.email}")
                        
                except Exception as e:
                    logger.error(f"Error sending birthday message to user {user.id}: {str(e)}")
            
            return len(birthday_users)
            
        except Exception as e:
            logger.error(f"Error scheduling birthday messages: {str(e)}")
            return 0
    
    @staticmethod
    def schedule_holiday_messages(holiday_name: str, target_users: List = None):
        """Schedule holiday messages for all users or specified users"""
        try:
            from modules.auth.models import User
            
            if target_users is None:
                # Send to all active users
                users = User.query.filter_by(is_active=True).all()
            else:
                users = target_users
            
            email_service = EmailService()
            message_service = PersonalizedMessageService()
            
            sent_count = 0
            for user in users:
                try:
                    context = message_service.generate_holiday_message_context(user, holiday_name)
                    success = email_service.send_email(
                        to_email=user.email,
                        subject=f"Happy {holiday_name} from NVC Banking!",
                        template_name="holiday_message",
                        context=context
                    )
                    
                    if success:
                        sent_count += 1
                        logger.info(f"Holiday message sent to {user.email}")
                    else:
                        logger.error(f"Failed to send holiday message to {user.email}")
                        
                except Exception as e:
                    logger.error(f"Error sending holiday message to user {user.id}: {str(e)}")
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error scheduling holiday messages: {str(e)}")
            return 0
    
    @staticmethod
    def schedule_monthly_statements():
        """Generate and send monthly statements for all users"""
        try:
            from modules.auth.models import User
            from modules.banking.models import BankAccount, Transaction
            
            # Get all active users with bank accounts
            users_with_accounts = db.session.query(User).join(BankAccount).filter(
                User.is_active == True,
                BankAccount.is_active == True
            ).all()
            
            email_service = EmailService()
            message_service = PersonalizedMessageService()
            
            sent_count = 0
            for user in users_with_accounts:
                try:
                    # Get user's primary account
                    account = BankAccount.query.filter_by(
                        user_id=user.id, 
                        is_primary=True
                    ).first()
                    
                    if not account:
                        account = BankAccount.query.filter_by(user_id=user.id).first()
                    
                    if account:
                        # Get last month's transactions
                        last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
                        first_day_last_month = last_month.replace(day=1)
                        
                        transactions = Transaction.query.filter(
                            Transaction.account_id == account.id,
                            Transaction.created_at >= first_day_last_month,
                            Transaction.created_at < datetime.utcnow().replace(day=1)
                        ).order_by(Transaction.created_at).all()
                        
                        context = message_service.generate_monthly_statement_context(
                            user, account, transactions
                        )
                        
                        success = email_service.send_email(
                            to_email=user.email,
                            subject=f"Monthly Statement - {last_month.strftime('%B %Y')}",
                            template_name="monthly_statement",
                            context=context
                        )
                        
                        if success:
                            sent_count += 1
                            logger.info(f"Monthly statement sent to {user.email}")
                        else:
                            logger.error(f"Failed to send monthly statement to {user.email}")
                            
                except Exception as e:
                    logger.error(f"Error sending monthly statement to user {user.id}: {str(e)}")
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error scheduling monthly statements: {str(e)}")
            return 0
    
    # Banking-specific email template methods for comprehensive communication
    def send_signup_verification_email(self, to_email: str, user_name: str, verification_token: str) -> bool:
        """Send signup verification email with secure token"""
        try:
            verification_link = f"{current_app.config.get('BASE_URL', '')}/auth/verify-email?token={verification_token}"
            
            template_data = {
                'user_name': user_name,
                'verification_link': verification_link,
                'support_email': 'support@nvcfund.com',
                'expires_in': '24 hours',
                'platform_name': 'NVC Banking Platform'
            }
            
            html_content = self.email_templates.get('signup_verification', '').format(**template_data)
            
            return self.send_email(
                to_email=to_email,
                subject="Please Verify Your Email - NVC Banking Platform",
                html_content=html_content,
                template_name_for_log="signup_verification",
                context_for_log=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending signup verification email: {str(e)}")
            return False
    
    def send_mfa_code_email(self, to_email: str, user_name: str, verification_code: str) -> bool:
        """Send two-factor authentication code via email"""
        try:
            template_data = {
                'user_name': user_name,
                'verification_code': verification_code,
                'expires_in': '10 minutes',
                'platform_name': 'NVC Banking Platform'
            }
            
            html_content = self.email_templates.get('two_factor_code', '').format(**template_data)
            
            return self.send_email(
                to_email=to_email,
                subject=f"Your NVC Banking Verification Code: {verification_code}",
                html_content=html_content,
                template_name_for_log="two_factor_code",
                context_for_log=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending MFA code email: {str(e)}")
            return False
    
    def send_transaction_alert_email(self, to_email: str, user_name: str, transaction_data: dict) -> bool:
        """Send transaction alert with comprehensive transaction details"""
        try:
            template_data = {
                'user_name': user_name,
                'transaction_amount': f"${transaction_data.get('amount', 0):,.2f}",
                'transaction_type': transaction_data.get('type', 'Transaction'),
                'transaction_date': transaction_data.get('date', datetime.utcnow().strftime('%B %d, %Y at %I:%M %p')),
                'account_number': f"****{str(transaction_data.get('account_number', '0000'))[-4:]}",
                'balance': f"${transaction_data.get('balance', 0):,.2f}",
                'merchant': transaction_data.get('merchant', 'N/A'),
                'location': transaction_data.get('location', 'N/A')
            }
            
            html_content = self.email_templates.get('transaction_alert', '').format(**template_data)
            
            return self.send_email(
                to_email=to_email,
                subject=f"Transaction Alert: {template_data['transaction_type']} - ${transaction_data.get('amount', 0):,.2f}",
                html_content=html_content,
                template_name_for_log="transaction_alert",
                context_for_log=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending transaction alert email: {str(e)}")
            return False
    
    def send_security_alert_email(self, to_email: str, user_name: str, alert_type: str, details: dict) -> bool:
        """Send security alert with detailed security event information"""
        try:
            template_data = {
                'user_name': user_name,
                'alert_type': alert_type,
                'ip_address': details.get('ip_address', 'Unknown'),
                'location': details.get('location', 'Unknown Location'),
                'timestamp': details.get('timestamp', datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')),
                'device_info': details.get('device_info', 'Unknown Device'),
                'action_taken': details.get('action_taken', 'Account monitoring increased'),
                'support_phone': '+1-800-NVC-SECURITY'
            }
            
            html_content = self.email_templates.get('security_alert', '').format(**template_data)
            
            return self.send_email(
                to_email=to_email,
                subject=f"🔒 Security Alert: {alert_type} - Immediate Action Required",
                html_content=html_content,
                template_name_for_log="security_alert",
                context_for_log=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending security alert email: {str(e)}")
            return False
    
    def _get_welcome_template(self) -> str:
        """Banking welcome email template with comprehensive onboarding"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #0a2447; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ background: #66ccff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }}
                .feature-box {{ background: #f8f9fa; border-left: 4px solid #66ccff; padding: 15px; margin: 15px 0; }}
                .highlight {{ color: #0a2447; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to {platform_name}</h1>
                    <p>Your trusted partner in digital banking</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>Welcome to the future of banking! Your account has been successfully created and we're excited to help you achieve your financial goals.</p>
                    
                    <div class="feature-box">
                        <h3>🏦 Your Banking Journey Starts Here</h3>
                        <ul>
                            <li>Complete KYC verification for full access</li>
                            <li>Set up multi-factor authentication</li>
                            <li>Explore our comprehensive banking services</li>
                            <li>Download our mobile banking app</li>
                        </ul>
                    </div>
                    
                    <div class="feature-box">
                        <h3>💼 Banking Services Available</h3>
                        <ul>
                            <li><span class="highlight">Digital Accounts:</span> Checking, Savings, Investment</li>
                            <li><span class="highlight">Payment Solutions:</span> Cards, Transfers, Bill Pay</li>
                            <li><span class="highlight">Investment Options:</span> Portfolio management, Trading</li>
                            <li><span class="highlight">Business Banking:</span> Corporate accounts, Merchant services</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="{login_url}" class="button">Access Your Account</a>
                    </center>
                    
                    <p>Need assistance? Our support team is available 24/7 at <strong>{support_email}</strong></p>
                    
                    <p>Best regards,<br>The NVC Banking Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_signup_verification_template(self) -> str:
        """Signup email verification template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #28a745; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .alert {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .security-note {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verify Your Email Address</h1>
                    <p>Complete your NVC Banking registration</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>Thank you for registering with {platform_name}! To complete your account setup and ensure the security of your banking information, please verify your email address.</p>
                    
                    <div class="alert">
                        <strong>⚠️ Action Required:</strong> Click the button below to verify your email address and activate your banking account.
                    </div>
                    
                    <center>
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </center>
                    
                    <div class="security-note">
                        <h3>🔒 Security Information</h3>
                        <ul>
                            <li>This verification link expires in <strong>{expires_in}</strong></li>
                            <li>Never share this link with anyone</li>
                            <li>If you didn't create this account, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>After verification, you'll be able to:</p>
                    <ul>
                        <li>Complete your KYC verification</li>
                        <li>Access your banking dashboard</li>
                        <li>Set up your banking preferences</li>
                        <li>Begin using our banking services</li>
                    </ul>
                    
                    <p>If you're having trouble with the button above, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_link}</p>
                    
                    <p>Questions? Contact our support team at <strong>{support_email}</strong></p>
                    
                    <p>Best regards,<br>NVC Banking Security Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This verification email was sent to ensure account security.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_kyc_verification_template(self) -> str:
        """KYC verification email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #fd7e14; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ background: #fd7e14; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .requirements {{ background: #f8f9fa; border-left: 4px solid #fd7e14; padding: 20px; margin: 20px 0; }}
                .timeline {{ background: #e7f3ff; border: 1px solid #b3d9ff; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 KYC Verification Required</h1>
                    <p>Complete your identity verification</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>To comply with banking regulations and ensure the security of your account, we need to verify your identity through our Know Your Customer (KYC) process.</p>
                    
                    <div class="timeline">
                        <h3>📅 Verification Timeline</h3>
                        <p><strong>Processing Time:</strong> 1-3 business days<br>
                        <strong>Status Updates:</strong> Real-time notifications<br>
                        <strong>Support Available:</strong> 24/7 assistance</p>
                    </div>
                    
                    <div class="requirements">
                        <h3>📋 Required Documents</h3>
                        <ul>
                            <li><strong>Government-issued Photo ID:</strong> Driver's license, passport, or national ID</li>
                            <li><strong>Proof of Address:</strong> Utility bill or bank statement (dated within 90 days)</li>
                            <li><strong>Income Verification:</strong> Pay stub, tax return, or employment letter</li>
                            <li><strong>Selfie Verification:</strong> Live photo for identity confirmation</li>
                        </ul>
                    </div>
                    
                    <center>
                        <a href="{verification_link}" class="button">Start KYC Verification</a>
                    </center>
                    
                    <p><strong>⏰ Important:</strong> This verification link expires in {expires_in}. Please complete the process promptly to avoid account restrictions.</p>
                    
                    <p><strong>🔒 Security Assurance:</strong> All documents are encrypted and processed according to banking industry standards. Your information is protected and will never be shared with third parties.</p>
                    
                    <p>For KYC assistance, contact our verification team at <strong>{support_email}</strong></p>
                    
                    <p>Best regards,<br>NVC Banking Compliance Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>KYC verification is required by banking regulations for customer protection.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_template(self) -> str:
        """Password reset email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #dc3545; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .security-alert {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .tips {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                    <p>Secure your banking account</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>We received a request to reset your NVC Banking Platform password. If you made this request, click the button below to create a new password.</p>
                    
                    <div class="security-alert">
                        <strong>🚨 Security Notice:</strong> If you did not request this password reset, please contact our security team immediately at <strong>{support_email}</strong>
                    </div>
                    
                    <center>
                        <a href="{reset_link}" class="button">Reset Your Password</a>
                    </center>
                    
                    <p><strong>⏰ Important:</strong> This reset link expires in <strong>{expires_in}</strong> for your security.</p>
                    
                    <div class="tips">
                        <h3>🛡️ Password Security Tips</h3>
                        <ul>
                            <li>Use at least 12 characters with mixed case, numbers, and symbols</li>
                            <li>Don't reuse passwords from other accounts</li>
                            <li>Enable two-factor authentication for extra security</li>
                            <li>Never share your password with anyone</li>
                        </ul>
                    </div>
                    
                    <p>If you're having trouble with the button above, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_link}</p>
                    
                    <p>For immediate security assistance, call our 24/7 security hotline: <strong>+1-800-NVC-SECURITY</strong></p>
                    
                    <p>Best regards,<br>NVC Banking Security Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This security notification was sent to protect your account.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_transaction_alert_template(self) -> str:
        """Transaction alert email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #17a2b8; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .transaction-box {{ background: #e7f3ff; border: 1px solid #b3d9ff; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .amount {{ font-size: 28px; font-weight: bold; color: #17a2b8; text-align: center; margin: 15px 0; }}
                .details {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .security-note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Transaction Alert</h1>
                    <p>Account activity notification</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>A transaction has been processed on your NVC Banking account. Here are the details:</p>
                    
                    <div class="transaction-box">
                        <div class="amount">{transaction_amount}</div>
                        <center>
                            <strong>{transaction_type}</strong><br>
                            {transaction_date}
                        </center>
                    </div>
                    
                    <div class="details">
                        <h3>📋 Transaction Details</h3>
                        <table width="100%" style="border-collapse: collapse;">
                            <tr><td><strong>Account:</strong></td><td>{account_number}</td></tr>
                            <tr><td><strong>Type:</strong></td><td>{transaction_type}</td></tr>
                            <tr><td><strong>Amount:</strong></td><td>{transaction_amount}</td></tr>
                            <tr><td><strong>Date:</strong></td><td>{transaction_date}</td></tr>
                            <tr><td><strong>Merchant:</strong></td><td>{merchant}</td></tr>
                            <tr><td><strong>Location:</strong></td><td>{location}</td></tr>
                            <tr><td><strong>Current Balance:</strong></td><td><strong>{balance}</strong></td></tr>
                        </table>
                    </div>
                    
                    <div class="security-note">
                        <strong>🔒 Security Reminder:</strong> If you did not authorize this transaction, please contact our fraud prevention team immediately at <strong>+1-800-NVC-FRAUD</strong>
                    </div>
                    
                    <p><strong>📱 Manage Your Account:</strong></p>
                    <ul>
                        <li>View detailed transaction history in your online banking</li>
                        <li>Set up custom alerts for different transaction types</li>
                        <li>Enable real-time mobile notifications</li>
                        <li>Review and update your security settings</li>
                    </ul>
                    
                    <p>Thank you for banking with NVC Banking Platform!</p>
                    
                    <p>Best regards,<br>NVC Banking Operations Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This transaction alert helps protect your account security.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_security_alert_template(self) -> str:
        """Security alert email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #dc3545; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .alert-box {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .details {{ background: #e2e3e5; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .actions {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .urgent {{ color: #dc3545; font-weight: bold; font-size: 18px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Security Alert</h1>
                    <p>Immediate attention required</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <div class="alert-box">
                        <div class="urgent">SECURITY EVENT DETECTED</div>
                        <p><strong>Alert Type:</strong> {alert_type}</p>
                        <p>We've detected unusual activity on your NVC Banking account that requires your immediate attention.</p>
                    </div>
                    
                    <div class="details">
                        <h3>🔍 Event Details</h3>
                        <table width="100%" style="border-collapse: collapse;">
                            <tr><td><strong>Event Type:</strong></td><td>{alert_type}</td></tr>
                            <tr><td><strong>Date & Time:</strong></td><td>{timestamp}</td></tr>
                            <tr><td><strong>IP Address:</strong></td><td>{ip_address}</td></tr>
                            <tr><td><strong>Location:</strong></td><td>{location}</td></tr>
                            <tr><td><strong>Device:</strong></td><td>{device_info}</td></tr>
                            <tr><td><strong>Action Taken:</strong></td><td>{action_taken}</td></tr>
                        </table>
                    </div>
                    
                    <div class="actions">
                        <h3>🛡️ Immediate Actions Required</h3>
                        <ol>
                            <li><strong>Change your password immediately</strong> if this wasn't you</li>
                            <li><strong>Enable two-factor authentication</strong> for enhanced security</li>
                            <li><strong>Review recent account activity</strong> for any unauthorized transactions</li>
                            <li><strong>Contact our security team</strong> if you need assistance</li>
                        </ol>
                    </div>
                    
                    <p><strong>🚨 If this was NOT you:</strong></p>
                    <ul>
                        <li>Call our 24/7 security hotline immediately: <strong>{support_phone}</strong></li>
                        <li>Do not delay - account security is time-sensitive</li>
                        <li>Have your account information ready when you call</li>
                    </ul>
                    
                    <p><strong>✅ If this was you:</strong></p>
                    <ul>
                        <li>No further action is required</li>
                        <li>Consider enabling additional security features</li>
                        <li>Always log out completely when using public computers</li>
                    </ul>
                    
                    <p>Your account security is our top priority. We monitor all account activity 24/7 to protect your financial information.</p>
                    
                    <p>Best regards,<br>NVC Banking Security Operations</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This security alert was generated automatically to protect your account.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_2fa_code_template(self) -> str:
        """Two-factor authentication code email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #6f42c1; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; text-align: center; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .code-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: 30px 0; }}
                .code {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; margin: 20px 0; font-family: 'Courier New', monospace; }}
                .timer {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .security-tips {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Your Verification Code</h1>
                    <p>Two-Factor Authentication</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>Use this verification code to complete your login to {platform_name}:</p>
                    
                    <div class="code-box">
                        <p style="margin: 0; font-size: 18px;">Your verification code is:</p>
                        <div class="code">{verification_code}</div>
                        <p style="margin: 0; font-size: 14px;">Enter this code in your banking application</p>
                    </div>
                    
                    <div class="timer">
                        <strong>⏰ Time Sensitive:</strong> This code expires in <strong>{expires_in}</strong>
                    </div>
                    
                    <div class="security-tips">
                        <h3>🛡️ Security Guidelines</h3>
                        <ul>
                            <li>Never share this code with anyone</li>
                            <li>NVC Banking will never ask for this code via phone or email</li>
                            <li>If you didn't request this code, contact security immediately</li>
                            <li>Always verify you're on our official website before entering codes</li>
                        </ul>
                    </div>
                    
                    <p>This extra security step helps protect your account from unauthorized access.</p>
                    
                    <p><strong>Need help?</strong> Contact our security team at <strong>+1-800-NVC-SECURITY</strong></p>
                    
                    <p>Best regards,<br>NVC Banking Security Team</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This verification code was sent to secure your account access.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_account_statement_template(self) -> str:
        """Account statement email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #0a2447; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .statement-info {{ background: #e7f3ff; border: 1px solid #b3d9ff; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .highlight {{ color: #0a2447; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Monthly Statement Available</h1>
                    <p>Your banking statement is ready</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <p>Your monthly account statement for <strong>{statement_period}</strong> is now available for download.</p>
                    
                    <div class="statement-info">
                        <h3>📊 Statement Summary</h3>
                        <ul>
                            <li><strong>Account:</strong> {account_number}</li>
                            <li><strong>Statement Period:</strong> {statement_period}</li>
                            <li><strong>Opening Balance:</strong> <span class="highlight">{opening_balance}</span></li>
                            <li><strong>Closing Balance:</strong> <span class="highlight">{closing_balance}</span></li>
                            <li><strong>Total Transactions:</strong> {transaction_count}</li>
                        </ul>
                    </div>
                    
                    <p><strong>📱 How to Access Your Statement:</strong></p>
                    <ol>
                        <li>Log in to your NVC Banking online account</li>
                        <li>Navigate to "Statements & Documents"</li>
                        <li>Download your PDF statement</li>
                        <li>Save a copy for your records</li>
                    </ol>
                    
                    <p><strong>💡 Statement Features:</strong></p>
                    <ul>
                        <li>Detailed transaction history</li>
                        <li>Account balance progression</li>
                        <li>Interest earned summary</li>
                        <li>Fee breakdown (if applicable)</li>
                    </ul>
                    
                    <p>Questions about your statement? Contact our customer service team at <strong>support@nvcfund.com</strong></p>
                    
                    <p>Thank you for banking with NVC Banking Platform!</p>
                    
                    <p>Best regards,<br>NVC Banking Account Services</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>Statements are available online for 7 years for your convenience.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_loan_approval_template(self) -> str:
        """Loan approval email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #28a745; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .approval-box {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .loan-details {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .next-steps {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>Your loan has been approved</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <div class="approval-box">
                        <h2 style="color: #28a745; margin: 0;">LOAN APPROVED!</h2>
                        <p style="margin: 10px 0 0 0;">Your application has been successfully processed</p>
                    </div>
                    
                    <p>We're pleased to inform you that your loan application has been approved! Here are your loan details:</p>
                    
                    <div class="loan-details">
                        <h3>💰 Loan Details</h3>
                        <table width="100%" style="border-collapse: collapse;">
                            <tr><td><strong>Loan Amount:</strong></td><td><strong style="color: #28a745;">{loan_amount}</strong></td></tr>
                            <tr><td><strong>Interest Rate:</strong></td><td>{interest_rate}% APR</td></tr>
                            <tr><td><strong>Loan Term:</strong></td><td>{loan_term} months</td></tr>
                            <tr><td><strong>Monthly Payment:</strong></td><td><strong>{monthly_payment}</strong></td></tr>
                            <tr><td><strong>First Payment Due:</strong></td><td>{first_payment_date}</td></tr>
                        </table>
                    </div>
                    
                    <div class="next-steps">
                        <h3>📋 Next Steps</h3>
                        <ol>
                            <li><strong>Review loan documents</strong> in your online banking portal</li>
                            <li><strong>Sign electronically</strong> or visit a branch to complete paperwork</li>
                            <li><strong>Funds will be disbursed</strong> within 1-2 business days after signing</li>
                            <li><strong>Set up automatic payments</strong> to never miss a payment</li>
                        </ol>
                    </div>
                    
                    <p><strong>🏦 Loan Management Features:</strong></p>
                    <ul>
                        <li>Online payment scheduling and management</li>
                        <li>Mobile app access for payment tracking</li>
                        <li>24/7 customer support for loan questions</li>
                        <li>Early payoff options with potential savings</li>
                    </ul>
                    
                    <p>Questions about your loan? Contact our lending specialists at <strong>loans@nvcfund.com</strong> or call <strong>+1-800-NVC-LOANS</strong></p>
                    
                    <p>Thank you for choosing NVC Banking for your financing needs!</p>
                    
                    <p>Best regards,<br>NVC Banking Loan Department</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>Loan terms and conditions apply. Please review all documents carefully.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_card_application_template(self) -> str:
        """Card application status email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #6f42c1; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .status-box {{ background: #e7f3ff; border: 1px solid #b3d9ff; padding: 20px; border-radius: 5px; margin: 20px 0; text-align: center; }}
                .card-features {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .timeline {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Card Application Update</h1>
                    <p>Your application status</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <div class="status-box">
                        <h2 style="color: #6f42c1; margin: 0;">APPLICATION {application_status}</h2>
                        <p style="margin: 10px 0 0 0;">Your {card_type} application has been processed</p>
                    </div>
                    
                    <p>Thank you for applying for the NVC Banking {card_type}. We're excited to provide you with a premium banking experience.</p>
                    
                    <div class="timeline">
                        <h3>📅 What Happens Next</h3>
                        <ul>
                            <li><strong>Processing Complete:</strong> Your application has been approved</li>
                            <li><strong>Card Production:</strong> 1-2 business days</li>
                            <li><strong>Shipping:</strong> 7-10 business days via secure mail</li>
                            <li><strong>Activation:</strong> Call or use our mobile app when received</li>
                        </ul>
                    </div>
                    
                    <div class="card-features">
                        <h3>🌟 Your Card Benefits</h3>
                        <ul>
                            <li><strong>Contactless Payments:</strong> Tap and go convenience</li>
                            <li><strong>Global Acceptance:</strong> Use worldwide with no foreign transaction fees</li>
                            <li><strong>Fraud Protection:</strong> 24/7 monitoring and zero liability</li>
                            <li><strong>Mobile Banking:</strong> Full control through our mobile app</li>
                            <li><strong>Rewards Program:</strong> Earn points on every purchase</li>
                        </ul>
                    </div>
                    
                    <p><strong>📱 Digital Card Available:</strong> Add your card to your mobile wallet immediately upon approval for instant use!</p>
                    
                    <p><strong>🔒 Security Features:</strong></p>
                    <ul>
                        <li>EMV chip technology for secure transactions</li>
                        <li>Real-time transaction alerts</li>
                        <li>Temporary card freezing through mobile app</li>
                        <li>Advanced fraud detection system</li>
                    </ul>
                    
                    <p>Questions about your new card? Contact our card services team at <strong>cards@nvcfund.com</strong> or call <strong>+1-800-NVC-CARDS</strong></p>
                    
                    <p>Welcome to premium banking with NVC Banking Platform!</p>
                    
                    <p>Best regards,<br>NVC Banking Card Services</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>Terms and conditions apply. Please review your cardholder agreement.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_compliance_template(self) -> str:
        """Compliance notification email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .header {{ background: #6c757d; color: white; padding: 30px 20px; text-align: center; }}
                .content {{ padding: 30px 20px; background: #ffffff; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .notice-box {{ background: #e2e3e5; border: 1px solid #d6d8db; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .action-required {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .compliance-info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Compliance Notification</h1>
                    <p>Important regulatory update</p>
                </div>
                <div class="content">
                    <h2>Dear {user_name},</h2>
                    
                    <div class="notice-box">
                        <h3>📢 Important Compliance Update</h3>
                        <p>{compliance_message}</p>
                    </div>
                    
                    <p>As part of our commitment to regulatory compliance and customer protection, we're notifying you of important updates that may affect your account.</p>
                    
                    <div class="action-required">
                        <h3>⚠️ Action Required</h3>
                        <p>Please review the attached compliance documentation and take any required actions within the specified timeframe.</p>
                    </div>
                    
                    <div class="compliance-info">
                        <h3>🔍 Compliance Standards</h3>
                        <ul>
                            <li><strong>Regulatory Framework:</strong> Banking regulations and standards</li>
                            <li><strong>Customer Protection:</strong> Enhanced security and privacy measures</li>
                            <li><strong>Transparency:</strong> Clear communication of changes and requirements</li>
                            <li><strong>Ongoing Monitoring:</strong> Continuous compliance assessment</li>
                        </ul>
                    </div>
                    
                    <p><strong>📞 Compliance Support:</strong></p>
                    <ul>
                        <li>Email: compliance@nvcfund.com</li>
                        <li>Phone: +1-800-NVC-COMPLY</li>
                        <li>Online chat: Available through your banking portal</li>
                        <li>Office hours: Monday-Friday, 8 AM - 6 PM EST</li>
                    </ul>
                    
                    <p><strong>📚 Additional Resources:</strong></p>
                    <ul>
                        <li>Compliance FAQ section in your online banking</li>
                        <li>Regulatory updates and notifications</li>
                        <li>Educational materials on banking compliance</li>
                    </ul>
                    
                    <p>Your cooperation in maintaining compliance helps us continue providing secure and reliable banking services.</p>
                    
                    <p>Best regards,<br>NVC Banking Compliance Department</p>
                </div>
                <div class="footer">
                    <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                    <p>This compliance notification is required by banking regulations.</p>
                </div>
            </div>
        </body>
        </html>
        """