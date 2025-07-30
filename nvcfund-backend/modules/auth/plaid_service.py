"""
Plaid KYC Integration Service
Comprehensive identity verification and compliance using Plaid's Identity Verification API
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

# Configure logging first
logger = logging.getLogger(__name__)

# Check import status only once per module
_import_checked = False
_plaid_import_success = False

def _check_plaid_import():
    """Check Plaid import status only once to prevent duplicate warnings"""
    global _import_checked, _plaid_import_success
    
    if _import_checked:
        return _plaid_import_success
    
    try:
        # Test core Plaid imports first
        from plaid.api import plaid_api
        from plaid.configuration import Configuration
        from plaid.api_client import ApiClient
        
        # Store core imports that are always available
        core_imports = {
            'plaid_api': plaid_api,
            'Configuration': Configuration,
            'ApiClient': ApiClient
        }
        
        # Try model imports - these may vary by version
        model_imports = {}
        model_names = [
            ('IdentityVerificationCreateRequest', 'plaid.model.identity_verification_create_request'),
            ('IdentityVerificationGetRequest', 'plaid.model.identity_verification_get_request'),
            ('LinkTokenCreateRequest', 'plaid.model.link_token_create_request'),
            ('LinkTokenCreateRequestUser', 'plaid.model.link_token_create_request_user'),
            ('CountryCode', 'plaid.model.country_code'),
            ('IdentityVerificationRequestUser', 'plaid.model.identity_verification_request_user'),
            ('IdentityVerificationRequestUserName', 'plaid.model.identity_verification_request_user_name'),
            ('IdentityVerificationRequestUserAddress', 'plaid.model.identity_verification_request_user_address')
        ]
        
        for class_name, module_path in model_names:
            try:
                module = __import__(module_path, fromlist=[class_name])
                model_imports[class_name] = getattr(module, class_name)
            except (ImportError, AttributeError):
                # Skip models that aren't available in this version
                continue
        
        # Store all successful imports globally
        globals().update({**core_imports, **model_imports})
        
        _plaid_import_success = True
        logger.info(f"Plaid SDK successfully imported with {len(model_imports)} model classes")
        
    except ImportError as e:
        _plaid_import_success = False
        # Only log warning once during startup
        if not hasattr(logger, '_plaid_warning_shown'):
            logger.warning("Plaid SDK not available - KYC features will be limited")
            logger._plaid_warning_shown = True
    
    _import_checked = True
    return _plaid_import_success

# Execute import check
PLAID_AVAILABLE = _check_plaid_import()

class PlaidKYCService:
    """
    Plaid Identity Verification Service for KYC compliance
    Provides comprehensive identity verification capabilities
    """
    
    def __init__(self):
        """Initialize Plaid client with configuration"""
        self.client_id = os.environ.get('PLAID_CLIENT_ID')
        self.secret = os.environ.get('PLAID_SECRET')
        self.env = os.environ.get('PLAID_ENV', 'sandbox')  # sandbox, development, or production
        self.template_id = os.environ.get('PLAID_IDV_TEMPLATE_ID')
        self.client = None
        
        if not PLAID_AVAILABLE:
            logger.warning("Plaid SDK not installed - run: pip install plaid-python")
            return
            
        if not all([self.client_id, self.secret]):
            logger.warning("Plaid credentials not found in environment variables")
            return
            
        try:
            # Configure Plaid client
            configuration = Configuration(
                host=self._get_plaid_host(),
                api_key={
                    'clientId': self.client_id,
                    'secret': self.secret
                }
            )
            
            api_client = ApiClient(configuration)
            self.client = plaid_api.PlaidApi(api_client)
            
            logger.info(f"Plaid KYC service initialized for {self.env} environment")
        except Exception as e:
            logger.error(f"Failed to initialize Plaid client: {e}")
    
    def _get_plaid_host(self) -> str:
        """Get appropriate Plaid API host based on environment"""
        hosts = {
            'sandbox': 'https://sandbox.api.plaid.com',
            'development': 'https://development.api.plaid.com', 
            'production': 'https://production.api.plaid.com'
        }
        return hosts.get(self.env, hosts['sandbox'])
    
    def create_link_token(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """
        Create a Link token for Plaid Identity Verification
        
        Args:
            user_id: Unique identifier for the user
            user_email: User's email address
            
        Returns:
            Dictionary containing link token and expiration
        """
        if not self.is_service_available():
            return {
                'success': False,
                'error': 'Plaid service not configured or unavailable'
            }
            
        try:
            request = LinkTokenCreateRequest(
                products=[],  # Empty for IDV
                client_name="NVC Banking Platform",
                country_codes=[CountryCode('US')],
                language='en',
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id,
                    email_address=user_email
                ),
                identity_verification={
                    'template_id': self.template_id
                } if self.template_id else None
            )
            
            response = self.client.link_token_create(request)
            
            return {
                'success': True,
                'link_token': response['link_token'],
                'expiration': response['expiration'],
                'request_id': response['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error creating Plaid link token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_identity_verification(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create identity verification session
        
        Args:
            user_data: Dictionary containing user information:
                - client_user_id: Unique user identifier
                - email_address: User's email
                - phone_number: Phone number (E.164 format)
                - date_of_birth: YYYY-MM-DD format
                - given_name: First name
                - family_name: Last name
                - street: Street address
                - city: City
                - region: State/region code
                - postal_code: ZIP/postal code
                - country: Country code (US, CA, etc.)
                
        Returns:
            Dictionary containing verification session details
        """
        if not self.is_service_available():
            return {
                'success': False,
                'error': 'Plaid service not configured or unavailable'
            }
            
        if not self.template_id:
            return {
                'success': False,
                'error': 'Plaid IDV template not configured'
            }
            
        try:
            # Construct user object
            user = IdentityVerificationRequestUser(
                email_address=user_data.get('email_address'),
                phone_number=user_data.get('phone_number'),
                date_of_birth=user_data.get('date_of_birth'),
                name=IdentityVerificationRequestUserName(
                    given_name=user_data.get('given_name'),
                    family_name=user_data.get('family_name')
                ),
                address=IdentityVerificationRequestUserAddress(
                    street=user_data.get('street'),
                    city=user_data.get('city'),
                    region=user_data.get('region'),
                    postal_code=user_data.get('postal_code'),
                    country=user_data.get('country', 'US')
                )
            )
            
            request = IdentityVerificationCreateRequest(
                client_user_id=user_data.get('client_user_id'),
                template_id=self.template_id,
                gave_consent=True,
                is_shareable=False,
                user=user
            )
            
            response = self.client.identity_verification_create(request)
            
            return {
                'success': True,
                'id': response['id'],
                'client_user_id': response['client_user_id'],
                'status': response['status'],
                'shareable_url': response.get('shareable_url'),
                'request_id': response['request_id']
            }
            
        except Exception as e:
            logger.error(f"Error creating identity verification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_identity_verification(self, verification_id: str) -> Dict[str, Any]:
        """
        Get identity verification status and results
        
        Args:
            verification_id: Identity verification ID from Plaid
            
        Returns:
            Dictionary containing verification status and results
        """
        if not self.is_service_available():
            return {
                'success': False,
                'error': 'Plaid service not configured or unavailable'
            }
            
        try:
            request = IdentityVerificationGetRequest(
                identity_verification_id=verification_id
            )
            
            response = self.client.identity_verification_get(request)
            
            # Extract verification results
            results = {
                'success': True,
                'id': response['id'],
                'client_user_id': response['client_user_id'],
                'status': response['status'],
                'created_at': response['created_at'].isoformat() if response.get('created_at') else None,
                'completed_at': response['completed_at'].isoformat() if response.get('completed_at') else None,
                'previous_attempt_id': response.get('previous_attempt_id'),
                'shareable_url': response.get('shareable_url'),
                'request_id': response['request_id']
            }
            
            # Add steps information if available
            if 'steps' in response:
                results['steps'] = []
                for step in response['steps']:
                    step_data = {
                        'step_name': step.get('step_name'),
                        'status': step.get('status'),
                        'acceptable_documents': step.get('acceptable_documents', []),
                        'requirements': step.get('requirements', {}),
                        'results': step.get('results', {})
                    }
                    results['steps'].append(step_data)
            
            # Add documentary verification details if available
            if 'documentary_verification' in response:
                doc_verification = response['documentary_verification']
                results['documentary_verification'] = {
                    'status': doc_verification.get('status'),
                    'documents': []
                }
                
                if 'documents' in doc_verification:
                    for doc in doc_verification['documents']:
                        doc_data = {
                            'status': doc.get('status'),
                            'attempt': doc.get('attempt'),
                            'images': doc.get('images', []),
                            'extracted_data': doc.get('extracted_data', {}),
                            'analysis': doc.get('analysis', {})
                        }
                        results['documentary_verification']['documents'].append(doc_data)
            
            # Add KYC check results if available
            if 'kyc_check' in response:
                kyc = response['kyc_check']
                results['kyc_check'] = {
                    'status': kyc.get('status'),
                    'score': kyc.get('score'),
                    'risk_level': kyc.get('risk_level'),
                    'insights': kyc.get('insights', {}),
                    'results': kyc.get('results', {})
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting identity verification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_verification_summary(self, verification_id: str) -> Dict[str, Any]:
        """
        Get a simplified verification summary for database storage
        
        Args:
            verification_id: Identity verification ID from Plaid
            
        Returns:
            Simplified verification summary
        """
        verification_data = self.get_identity_verification(verification_id)
        
        if not verification_data.get('success'):
            return verification_data
        
        # Extract key information for database
        summary = {
            'verification_id': verification_data.get('id'),
            'client_user_id': verification_data.get('client_user_id'),
            'status': verification_data.get('status'),
            'created_at': verification_data.get('created_at'),
            'completed_at': verification_data.get('completed_at'),
            'overall_score': None,
            'risk_level': None,
            'document_verified': False,
            'kyc_passed': False,
            'selfie_verified': False,
            'data_sources_verified': False
        }
        
        # Extract KYC results
        if 'kyc_check' in verification_data:
            kyc = verification_data['kyc_check']
            summary['overall_score'] = kyc.get('score')
            summary['risk_level'] = kyc.get('risk_level')
            summary['kyc_passed'] = kyc.get('status') == 'success'
        
        # Extract document verification results
        if 'documentary_verification' in verification_data:
            doc_status = verification_data['documentary_verification'].get('status')
            summary['document_verified'] = doc_status == 'success'
        
        # Extract step results
        if 'steps' in verification_data:
            for step in verification_data['steps']:
                step_name = step.get('step_name', '').lower()
                step_status = step.get('status') == 'success'
                
                if 'selfie' in step_name or 'liveness' in step_name:
                    summary['selfie_verified'] = step_status
                elif 'data_source' in step_name or 'identity' in step_name:
                    summary['data_sources_verified'] = step_status
        
        return {
            'success': True,
            'summary': summary
        }
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Plaid Identity Verification webhook
        
        Args:
            webhook_data: Webhook payload from Plaid
            
        Returns:
            Processing result
        """
        try:
            webhook_type = webhook_data.get('webhook_type')
            webhook_code = webhook_data.get('webhook_code')
            
            if webhook_type != 'IDENTITY_VERIFICATION':
                return {
                    'success': False,
                    'error': f'Unexpected webhook type: {webhook_type}'
                }
            
            if webhook_code == 'STATUS_UPDATED':
                verification_id = webhook_data.get('identity_verification_id')
                
                if not verification_id:
                    return {
                        'success': False,
                        'error': 'Missing verification ID in webhook'
                    }
                
                # Get updated verification data
                verification_data = self.get_verification_summary(verification_id)
                
                if verification_data.get('success'):
                    return {
                        'success': True,
                        'event': 'status_updated',
                        'verification_id': verification_id,
                        'data': verification_data.get('summary')
                    }
                else:
                    return verification_data
            
            return {
                'success': True,
                'event': 'unhandled',
                'webhook_code': webhook_code
            }
            
        except Exception as e:
            logger.error(f"Error processing Plaid webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_supported_countries(self) -> List[str]:
        """
        Get list of countries supported by Plaid Identity Verification
        
        Returns:
            List of country codes
        """
        # Plaid supports nearly 190 countries for Identity Verification
        # This is a subset of major supported countries
        return [
            'US', 'CA', 'GB', 'AU', 'DE', 'FR', 'ES', 'IT', 'NL', 'BE',
            'AT', 'CH', 'SE', 'NO', 'DK', 'FI', 'IE', 'PT', 'GR', 'LU',
            'JP', 'KR', 'SG', 'HK', 'MY', 'TH', 'PH', 'ID', 'VN', 'IN',
            'BR', 'MX', 'AR', 'CL', 'CO', 'PE', 'UY', 'CR', 'PA', 'GT',
            'ZA', 'NG', 'KE', 'GH', 'EG', 'MA', 'TN', 'UG', 'TZ', 'RW'
        ]
    
    def is_service_available(self) -> bool:
        """
        Check if Plaid KYC service is properly configured and available
        
        Returns:
            True if service is available
        """
        return bool(PLAID_AVAILABLE and self.client and self.template_id)
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get detailed service status for health checks
        
        Returns:
            Service status information
        """
        return {
            'service': 'Plaid KYC Integration',
            'available': self.is_service_available(),
            'plaid_sdk_installed': PLAID_AVAILABLE,
            'environment': self.env,
            'template_configured': bool(self.template_id),
            'credentials_configured': bool(self.client_id and self.secret),
            'supported_countries': len(self.get_supported_countries()),
            'features': {
                'document_verification': True,
                'selfie_verification': True,
                'data_source_verification': True,
                'behavioral_analytics': True,
                'device_intelligence': True,
                'anti_fraud_engine': True
            }
        }

# Singleton service instance
_service_instance = None

def get_plaid_kyc_service():
    """Get singleton instance of PlaidKYCService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = PlaidKYCService()
    return _service_instance

# Global service instance for compatibility
plaid_kyc_service = get_plaid_kyc_service()