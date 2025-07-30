"""
SendGrid Email Service for NVC Banking Platform
Comprehensive email communication system with templates and tracking
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
import json

# Configure logging
logger = logging.getLogger(__name__)

class SendGridEmailService:
    """Professional SendGrid email service for banking communications"""
    
    def __init__(self):
        """Initialize SendGrid service with API key validation"""
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        if not self.api_key:
            logger.error("❌ SENDGRID_API_KEY environment variable not set")
            sys.exit('SENDGRID_API_KEY environment variable must be set')
        
        self.sg = SendGridAPIClient(self.api_key)
        self.from_email = "noreply@nvcfund.com"
        self.from_name = "NVC Banking Platform"
        
        # Email templates for banking operations
        self.templates = {
            'welcome': self._get_welcome_template(),
            'kyc_verification': self._get_kyc_template(),
            'password_reset': self._get_password_reset_template(),
            'transaction_alert': self._get_transaction_alert_template(),
            'account_statement': self._get_statement_template(),
            'security_alert': self._get_security_alert_template(),
            'two_factor_auth': self._get_2fa_template(),
            'loan_approval': self._get_loan_approval_template(),
            'card_application': self._get_card_application_template(),
            'compliance_notification': self._get_compliance_template()
        }
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        template_type: str = 'generic',
        template_data: Optional[Dict[str, Any]] = None,
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Send email with template support and comprehensive error handling"""
        
        try:
            # Validate email address
            if not self._validate_email(to_email):
                return {
                    'success': False,
                    'error': 'Invalid email address format',
                    'status_code': 400
                }
            
            # Create mail object
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject
            )
            
            # Use template or custom content
            if template_type in self.templates:
                content = self._process_template(template_type, template_data or {})
                message.content = Content("text/html", content)
            elif html_content:
                message.content = Content("text/html", html_content)
            elif text_content:
                message.content = Content("text/plain", text_content)
            else:
                return {
                    'success': False,
                    'error': 'No content provided for email',
                    'status_code': 400
                }
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email
            response = self.sg.send(message)
            
            # Log successful send
            logger.info(f"✅ Email sent successfully to {to_email} - Subject: {subject}")
            
            return {
                'success': True,
                'message': 'Email sent successfully',
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ SendGrid email error: {str(e)}")
            return {
                'success': False,
                'error': f'Email sending failed: {str(e)}',
                'status_code': 500
            }
    
    def send_welcome_email(self, to_email: str, user_name: str, account_type: str) -> Dict[str, Any]:
        """Send welcome email for new banking customers"""
        
        template_data = {
            'user_name': user_name,
            'account_type': account_type,
            'platform_name': 'NVC Banking Platform',
            'support_email': 'support@nvcfund.com',
            'login_url': 'https://nvcfund.com/auth/login'
        }
        
        subject = f"Welcome to NVC Banking Platform, {user_name}!"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            template_type='welcome',
            template_data=template_data
        )
    
    def send_kyc_verification_email(self, to_email: str, user_name: str, verification_link: str) -> Dict[str, Any]:
        """Send KYC verification email"""
        
        template_data = {
            'user_name': user_name,
            'verification_link': verification_link,
            'support_email': 'kyc@nvcfund.com',
            'expires_in': '24 hours'
        }
        
        subject = "Complete Your KYC Verification - NVC Banking"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            template_type='kyc_verification',
            template_data=template_data
        )
    
    def send_password_reset_email(self, to_email: str, user_name: str, reset_link: str) -> Dict[str, Any]:
        """Send password reset email"""
        
        template_data = {
            'user_name': user_name,
            'reset_link': reset_link,
            'expires_in': '1 hour',
            'support_email': 'security@nvcfund.com'
        }
        
        subject = "Password Reset Request - NVC Banking"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            template_type='password_reset',
            template_data=template_data
        )
    
    def send_transaction_alert(self, to_email: str, user_name: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send transaction alert email"""
        
        template_data = {
            'user_name': user_name,
            'transaction_amount': transaction_data.get('amount', 'N/A'),
            'transaction_type': transaction_data.get('type', 'N/A'),
            'transaction_date': transaction_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'account_number': transaction_data.get('account_number', 'N/A'),
            'balance': transaction_data.get('balance', 'N/A')
        }
        
        subject = f"Transaction Alert - {transaction_data.get('type', 'Banking Transaction')}"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            template_type='transaction_alert',
            template_data=template_data
        )
    
    def send_security_alert(self, to_email: str, user_name: str, alert_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Send security alert email"""
        
        template_data = {
            'user_name': user_name,
            'alert_type': alert_type,
            'ip_address': details.get('ip_address', 'Unknown'),
            'location': details.get('location', 'Unknown'),
            'timestamp': details.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'action_required': details.get('action_required', False)
        }
        
        subject = f"Security Alert - {alert_type}"
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            template_type='security_alert',
            template_data=template_data
        )
    
    def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send bulk emails for marketing or notifications"""
        
        results = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for email_data in email_list:
            try:
                result = self.send_email(**email_data)
                results['total_sent'] += 1
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'email': email_data.get('to_email', 'Unknown'),
                        'error': result['error']
                    })
                    
            except Exception as e:
                results['total_sent'] += 1
                results['failed'] += 1
                results['errors'].append({
                    'email': email_data.get('to_email', 'Unknown'),
                    'error': str(e)
                })
        
        logger.info(f"📧 Bulk email results: {results['successful']}/{results['total_sent']} successful")
        return results
    
    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _process_template(self, template_type: str, data: Dict[str, Any]) -> str:
        """Process email template with data substitution"""
        template = self.templates.get(template_type, '')
        
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            template = template.replace(placeholder, str(value))
        
        return template
    
    def _add_attachment(self, message: Mail, attachment_data: Dict[str, str]):
        """Add file attachment to email"""
        try:
            attachment = Attachment()
            attachment.file_content = FileContent(attachment_data['content'])
            attachment.file_type = FileType(attachment_data.get('type', 'application/pdf'))
            attachment.file_name = FileName(attachment_data['filename'])
            attachment.disposition = Disposition('attachment')
            message.attachment = attachment
        except Exception as e:
            logger.error(f"❌ Failed to add attachment: {str(e)}")
    
    def _get_welcome_template(self) -> str:
        """Banking welcome email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
                .button { background: #66ccff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to {{platform_name}}</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                <p>Welcome to NVC Banking Platform! Your {{account_type}} account has been successfully created.</p>
                
                <p><strong>What's Next?</strong></p>
                <ul>
                    <li>Complete your KYC verification</li>
                    <li>Set up your banking preferences</li>
                    <li>Explore our comprehensive banking services</li>
                    <li>Download our mobile banking app</li>
                </ul>
                
                <a href="{{login_url}}" class="button">Access Your Account</a>
                
                <p>If you have any questions, please contact our support team at {{support_email}}</p>
                
                <p>Best regards,<br>The NVC Banking Team</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_kyc_template(self) -> str:
        """KYC verification email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .button { background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>KYC Verification Required</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <div class="alert">
                    <strong>Action Required:</strong> Please complete your KYC verification to activate your banking account.
                </div>
                
                <p>To comply with banking regulations, we need to verify your identity. This process typically takes 2-3 business days.</p>
                
                <p><strong>Required Documents:</strong></p>
                <ul>
                    <li>Government-issued photo ID</li>
                    <li>Proof of address (utility bill or bank statement)</li>
                    <li>Income verification documents</li>
                </ul>
                
                <a href="{{verification_link}}" class="button">Complete KYC Verification</a>
                
                <p><strong>Important:</strong> This verification link expires in {{expires_in}}.</p>
                
                <p>For assistance, contact our KYC team at {{support_email}}</p>
                
                <p>Best regards,<br>NVC Banking Compliance Team</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
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
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .security-notice { background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .button { background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <p>We received a request to reset your NVC Banking Platform password.</p>
                
                <div class="security-notice">
                    <strong>Security Notice:</strong> If you did not request this password reset, please contact our security team immediately.
                </div>
                
                <a href="{{reset_link}}" class="button">Reset Your Password</a>
                
                <p><strong>Important Security Information:</strong></p>
                <ul>
                    <li>This reset link expires in {{expires_in}}</li>
                    <li>Use a strong, unique password</li>
                    <li>Never share your login credentials</li>
                    <li>Enable two-factor authentication</li>
                </ul>
                
                <p>For security assistance, contact {{support_email}}</p>
                
                <p>Best regards,<br>NVC Banking Security Team</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
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
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .transaction-details { background: #e7f3ff; border: 1px solid #b3d9ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .amount { font-size: 24px; font-weight: bold; color: #28a745; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Transaction Alert</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <p>A transaction has been processed on your account:</p>
                
                <div class="transaction-details">
                    <p><strong>Transaction Type:</strong> {{transaction_type}}</p>
                    <p><strong>Amount:</strong> <span class="amount">${{transaction_amount}}</span></p>
                    <p><strong>Date & Time:</strong> {{transaction_date}}</p>
                    <p><strong>Account:</strong> ****{{account_number}}</p>
                    <p><strong>Available Balance:</strong> ${{balance}}</p>
                </div>
                
                <p>If you did not authorize this transaction, please contact our security team immediately.</p>
                
                <p>Best regards,<br>NVC Banking Operations</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_statement_template(self) -> str:
        """Account statement email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Monthly Account Statement</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                <p>Your monthly account statement is now available.</p>
                <p>Please find your statement attached to this email.</p>
                <p>Best regards,<br>NVC Banking Platform</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
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
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .alert { background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Security Alert</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <div class="alert">
                    <strong>Security Event Detected:</strong> {{alert_type}}
                </div>
                
                <p><strong>Event Details:</strong></p>
                <ul>
                    <li><strong>IP Address:</strong> {{ip_address}}</li>
                    <li><strong>Location:</strong> {{location}}</li>
                    <li><strong>Time:</strong> {{timestamp}}</li>
                </ul>
                
                <p>If this was not you, please contact our security team immediately and change your password.</p>
                
                <p>Best regards,<br>NVC Banking Security Team</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_2fa_template(self) -> str:
        """Two-factor authentication email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; text-align: center; }
                .code { background: #f8f9fa; border: 2px solid #66ccff; padding: 20px; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0; border-radius: 10px; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Two-Factor Authentication</h1>
            </div>
            <div class="content">
                <h2>Your Verification Code</h2>
                <div class="code">{{verification_code}}</div>
                <p>This code expires in 10 minutes.</p>
                <p>If you did not request this code, please contact security immediately.</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
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
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .approval { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Loan Approved!</h1>
            </div>
            <div class="content">
                <h2>Congratulations {{user_name}}!</h2>
                
                <div class="approval">
                    <strong>Your loan application has been approved!</strong>
                </div>
                
                <p><strong>Loan Details:</strong></p>
                <ul>
                    <li><strong>Loan Amount:</strong> ${{loan_amount}}</li>
                    <li><strong>Interest Rate:</strong> {{interest_rate}}%</li>
                    <li><strong>Term:</strong> {{loan_term}} months</li>
                    <li><strong>Monthly Payment:</strong> ${{monthly_payment}}</li>
                </ul>
                
                <p>Next steps: Review and sign your loan documents through your online banking portal.</p>
                
                <p>Best regards,<br>NVC Banking Loan Department</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_card_application_template(self) -> str:
        """Card application email template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #0a2447; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .status { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Card Application Update</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <div class="status">
                    <strong>Application Status:</strong> {{application_status}}
                </div>
                
                <p>Your {{card_type}} application has been {{application_status}}.</p>
                
                <p>If approved, your new card will arrive within 7-10 business days.</p>
                
                <p>Best regards,<br>NVC Banking Card Services</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
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
                body { font-family: Arial, sans-serif; color: #333; }
                .header { background: #6c757d; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .notice { background: #e2e3e5; border: 1px solid #d6d8db; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Compliance Notification</h1>
            </div>
            <div class="content">
                <h2>Dear {{user_name}},</h2>
                
                <div class="notice">
                    <strong>Important Compliance Update</strong>
                </div>
                
                <p>{{compliance_message}}</p>
                
                <p>Please review the attached compliance documentation and take any required actions.</p>
                
                <p>For compliance questions, contact our team at compliance@nvcfund.com</p>
                
                <p>Best regards,<br>NVC Banking Compliance Department</p>
            </div>
            <div class="footer">
                <p>© 2025 NVC Banking Platform. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

# Initialize service instance
email_service = SendGridEmailService()