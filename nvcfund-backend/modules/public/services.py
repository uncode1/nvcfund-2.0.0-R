"""
Public Module Services
NVC Banking Platform - Services for public-facing functionality
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

class PublicService:
    """Service class for public module functionality"""
    
    def __init__(self):
        """Initialize the public service"""
        self.service_name = "PublicService"
        self.version = "1.0.0"
        logger.info(f"Initialized {self.service_name} v{self.version}")
    
    def validate_contact_form(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate contact form data
        
        Args:
            form_data: Dictionary containing form fields
            
        Returns:
            Dictionary with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Required fields validation
            required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
            for field in required_fields:
                if not form_data.get(field, '').strip():
                    errors.append(f"{field} is required")
            
            # Email validation
            email = form_data.get('email', '').strip()
            if email:
                email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                if not re.match(email_pattern, email):
                    errors.append("Invalid email format")
            
            # Phone validation (optional)
            phone = form_data.get('phone', '').strip()
            if phone:
                # Basic phone number validation
                phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
                cleaned_phone = re.sub(r'[^\d\+]', '', phone)
                if not re.match(phone_pattern, cleaned_phone):
                    warnings.append("Phone number format may be invalid")
            
            # Name validation
            first_name = form_data.get('firstName', '').strip()
            last_name = form_data.get('lastName', '').strip()
            
            if first_name and len(first_name) < 2:
                errors.append("First name must be at least 2 characters")
            if last_name and len(last_name) < 2:
                errors.append("Last name must be at least 2 characters")
            
            # Message length validation
            message = form_data.get('message', '').strip()
            if message and len(message) < 10:
                errors.append("Message must be at least 10 characters")
            elif message and len(message) > 5000:
                errors.append("Message must not exceed 5000 characters")
            
            # Subject validation
            subject = form_data.get('subject', '').strip()
            valid_subjects = ['general', 'account', 'technical', 'treasury', 'compliance', 'partnership', 'other']
            if subject and subject not in valid_subjects:
                errors.append("Invalid subject selection")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'validated_data': {
                    'firstName': first_name,
                    'lastName': last_name,
                    'email': email.lower() if email else '',
                    'phone': cleaned_phone if phone else '',
                    'subject': subject,
                    'message': message
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating contact form: {e}")
            return {
                'valid': False,
                'errors': ['Validation error occurred'],
                'warnings': [],
                'validated_data': {}
            }
    
    def process_contact_submission(self, validated_data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a validated contact form submission
        
        Args:
            validated_data: Validated form data
            metadata: Request metadata (IP, user agent, etc.)
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Create contact record
            contact_record = {
                **validated_data,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'priority': self._determine_priority(validated_data['subject']),
                'metadata': metadata,
                'id': self._generate_ticket_id()
            }
            
            # Log the contact submission
            logger.info(f"Contact form submitted: {contact_record['id']} - {validated_data['email']}")
            
            # In a real implementation, this would:
            # 1. Save to database
            # 2. Send notification emails
            # 3. Create support ticket
            # 4. Route to appropriate department
            
            return {
                'success': True,
                'ticket_id': contact_record['id'],
                'estimated_response_time': self._get_response_time(contact_record['priority']),
                'message': 'Your message has been received and will be processed shortly.'
            }
            
        except Exception as e:
            logger.error(f"Error processing contact submission: {e}")
            return {
                'success': False,
                'error': 'Processing error occurred',
                'message': 'An error occurred while processing your request. Please try again.'
            }
    
    def _determine_priority(self, subject: str) -> str:
        """Determine ticket priority based on subject"""
        priority_map = {
            'technical': 'high',
            'account': 'high',
            'compliance': 'medium',
            'treasury': 'medium',
            'partnership': 'low',
            'general': 'low',
            'other': 'low'
        }
        return priority_map.get(subject, 'low')
    
    def _get_response_time(self, priority: str) -> str:
        """Get estimated response time based on priority"""
        response_times = {
            'high': '2 hours',
            'medium': '4 hours',
            'low': '24 hours'
        }
        return response_times.get(priority, '24 hours')
    
    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID"""
        import uuid
        return f"NVC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information
        
        Returns:
            Dictionary with service details
        """
        return {
            'name': self.service_name,
            'version': self.version,
            'status': 'active',
            'capabilities': [
                'Contact form validation',
                'Contact form processing',
                'Ticket generation',
                'Priority management',
                'Response time estimation'
            ],
            'health_status': 'healthy',
            'last_check': datetime.now().isoformat()
        }
    
    def get_contact_categories(self) -> List[Dict[str, Any]]:
        """
        Get available contact categories
        
        Returns:
            List of contact categories with descriptions
        """
        return [
            {
                'id': 'general',
                'name': 'General Inquiry',
                'description': 'General questions about NVC Banking services',
                'icon': 'fas fa-info-circle',
                'priority': 'low'
            },
            {
                'id': 'account',
                'name': 'Account Support',
                'description': 'Account management, profile updates, security settings',
                'icon': 'fas fa-user-circle',
                'priority': 'high'
            },
            {
                'id': 'technical',
                'name': 'Technical Support',
                'description': 'Technical issues, platform problems, API support',
                'icon': 'fas fa-cog',
                'priority': 'high'
            },
            {
                'id': 'treasury',
                'name': 'Treasury Services',
                'description': 'Investment management, NVCT stablecoin, institutional banking',
                'icon': 'fas fa-chart-line',
                'priority': 'medium'
            },
            {
                'id': 'compliance',
                'name': 'Compliance Question',
                'description': 'Regulatory compliance, KYC, AML, legal questions',
                'icon': 'fas fa-shield-alt',
                'priority': 'medium'
            },
            {
                'id': 'partnership',
                'name': 'Partnership Inquiry',
                'description': 'Business partnerships, integration opportunities',
                'icon': 'fas fa-handshake',
                'priority': 'low'
            },
            {
                'id': 'other',
                'name': 'Other',
                'description': 'Other inquiries not covered above',
                'icon': 'fas fa-question-circle',
                'priority': 'low'
            }
        ]
    
    def get_office_information(self) -> Dict[str, Any]:
        """
        Get office and contact information
        
        Returns:
            Dictionary with office details
        """
        return {
            'headquarters': {
                'name': 'NVC Banking Plaza',
                'address': {
                    'street': '1200 Financial District',
                    'city': 'New York',
                    'state': 'NY',
                    'zip': '10005',
                    'country': 'United States'
                },
                'phone': '+1 (800) 682-2265',
                'fax': '+1 (800) 682-2266',
                'hours': {
                    'monday_friday': '9:00 AM - 5:00 PM EST',
                    'saturday': '10:00 AM - 2:00 PM EST',
                    'sunday': 'Closed'
                }
            },
            'support_lines': {
                'customer_service': '+1 (800) 682-2265',
                'treasury_services': '+1 (800) 682-8732',
                'technical_support': '+1 (800) 682-8324',
                'emergency_support': '+1 (800) 682-4357'
            },
            'email_addresses': {
                'general_support': 'support@nvcfund.com',
                'technical_support': 'technical@nvcfund.com',
                'treasury_services': 'treasury@nvcfund.com',
                'compliance': 'compliance@nvcfund.com',
                'partnerships': 'partnerships@nvcfund.com'
            },
            'emergency_contact': {
                'available_24_7': True,
                'phone': '+1 (800) 682-4357',
                'description': 'For urgent security issues, suspected fraud, or critical system problems'
            }
        }

# Module service instance
public_service = PublicService()