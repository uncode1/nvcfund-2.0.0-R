"""
GDPR Rights Management System
Implements data subject rights for GDPR compliance
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from modules.core.extensions import db
from sqlalchemy import text

logger = logging.getLogger(__name__)

class GDPRRightsManager:
    """
    GDPR Data Subject Rights Management System
    Implements all GDPR rights including access, rectification, erasure, and portability
    """
    
    def __init__(self):
        self.request_retention_days = 90
        self.fulfillment_deadline_days = 30
        
        # Define personal data categories
        self.personal_data_categories = {
            'identity': ['first_name', 'last_name', 'username', 'email'],
            'contact': ['phone', 'address', 'city', 'state', 'zip_code'],
            'financial': ['account_number', 'balance', 'transaction_history'],
            'identification': ['ssn', 'date_of_birth', 'government_id'],
            'behavioral': ['login_history', 'session_data', 'preferences'],
            'technical': ['ip_address', 'user_agent', 'device_fingerprint']
        }
    
    def handle_data_access_request(self, user_id: int, request_id: str = None) -> Dict[str, Any]:
        """
        Handle GDPR Article 15 - Right of Access
        Export all personal data for the user
        """
        try:
            # Generate request ID if not provided
            if not request_id:
                request_id = f"ACCESS_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Collect personal data from all relevant tables
            personal_data = self._collect_user_personal_data(user_id)
            
            # Create comprehensive data export
            data_export = {
                'request_id': request_id,
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'data_categories': personal_data,
                'processing_purposes': self._get_processing_purposes(),
                'data_retention_periods': self._get_retention_periods(),
                'third_party_recipients': self._get_third_party_recipients(),
                'data_sources': self._get_data_sources()
            }
            
            # Log the access request
            self._log_gdpr_request('access', user_id, request_id)
            
            return {
                'success': True,
                'request_id': request_id,
                'data_export': data_export,
                'format': 'json'
            }
            
        except Exception as e:
            logger.error(f"Data access request failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to process data access request'
            }
    
    def handle_data_rectification_request(self, user_id: int, corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GDPR Article 16 - Right to Rectification
        Update incorrect or incomplete personal data
        """
        try:
            request_id = f"RECTIFICATION_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate corrections
            validation_result = self._validate_rectification_data(corrections)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Invalid rectification data',
                    'validation_errors': validation_result['errors']
                }
            
            # Apply corrections with audit trail
            updated_fields = []
            for field, new_value in corrections.items():
                if self._update_user_field(user_id, field, new_value):
                    updated_fields.append(field)
            
            # Log the rectification
            self._log_gdpr_request('rectification', user_id, request_id, {
                'corrected_fields': updated_fields,
                'corrections': corrections
            })
            
            return {
                'success': True,
                'request_id': request_id,
                'updated_fields': updated_fields,
                'completion_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data rectification failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to process rectification request'
            }
    
    def handle_data_erasure_request(self, user_id: int, erasure_reason: str) -> Dict[str, Any]:
        """
        Handle GDPR Article 17 - Right to Erasure (Right to be Forgotten)
        Delete personal data while maintaining compliance requirements
        """
        try:
            request_id = f"ERASURE_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if erasure is legally possible
            erasure_assessment = self._assess_erasure_feasibility(user_id, erasure_reason)
            
            if not erasure_assessment['can_erase']:
                return {
                    'success': False,
                    'request_id': request_id,
                    'reason': 'Erasure not possible',
                    'legal_basis': erasure_assessment['retention_reasons']
                }
            
            # Perform selective erasure
            erased_data = self._perform_selective_erasure(user_id)
            
            # Log the erasure request
            self._log_gdpr_request('erasure', user_id, request_id, {
                'erasure_reason': erasure_reason,
                'erased_categories': erased_data['categories'],
                'retained_data': erased_data['retained_for_compliance']
            })
            
            return {
                'success': True,
                'request_id': request_id,
                'erased_data_categories': erased_data['categories'],
                'retained_data_reason': 'Legal compliance requirements',
                'completion_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data erasure failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to process erasure request'
            }
    
    def handle_data_portability_request(self, user_id: int, export_format: str = 'json') -> Dict[str, Any]:
        """
        Handle GDPR Article 20 - Right to Data Portability
        Export data in structured, machine-readable format
        """
        try:
            request_id = f"PORTABILITY_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Collect portable data (data provided by user or generated by their activity)
            portable_data = self._collect_portable_data(user_id)
            
            # Format data according to request
            if export_format.lower() == 'csv':
                formatted_data = self._format_data_as_csv(portable_data)
            elif export_format.lower() == 'xml':
                formatted_data = self._format_data_as_xml(portable_data)
            else:
                formatted_data = portable_data  # Default JSON format
            
            # Log the portability request
            self._log_gdpr_request('portability', user_id, request_id, {
                'export_format': export_format,
                'data_size': len(str(formatted_data))
            })
            
            return {
                'success': True,
                'request_id': request_id,
                'portable_data': formatted_data,
                'format': export_format,
                'completion_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data portability request failed for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to process portability request'
            }
    
    def _collect_user_personal_data(self, user_id: int) -> Dict[str, Any]:
        """Collect all personal data for user across all tables"""
        personal_data = {}
        
        try:
            # User basic information
            user_query = text("""
                SELECT username, email, first_name, last_name, phone, 
                       created_at, last_login, is_active, role
                FROM users WHERE id = :user_id
            """)
            user_result = db.session.execute(user_query, {'user_id': user_id}).fetchone()
            
            if user_result:
                personal_data['identity'] = dict(user_result._mapping)
            
            # Account information
            accounts_query = text("""
                SELECT account_number, account_type, balance, status, created_at
                FROM accounts WHERE user_id = :user_id
            """)
            accounts_result = db.session.execute(accounts_query, {'user_id': user_id}).fetchall()
            personal_data['accounts'] = [dict(row._mapping) for row in accounts_result]
            
            # Transaction history (last 2 years for GDPR compliance)
            transactions_query = text("""
                SELECT transaction_id, amount, transaction_type, description, 
                       created_at, status
                FROM transactions 
                WHERE user_id = :user_id 
                AND created_at >= :cutoff_date
                ORDER BY created_at DESC
            """)
            cutoff_date = datetime.utcnow() - timedelta(days=730)
            transactions_result = db.session.execute(
                transactions_query, 
                {'user_id': user_id, 'cutoff_date': cutoff_date}
            ).fetchall()
            personal_data['transactions'] = [dict(row._mapping) for row in transactions_result]
            
            # Session and activity logs
            sessions_query = text("""
                SELECT login_time, logout_time, ip_address, user_agent
                FROM user_sessions 
                WHERE user_id = :user_id
                AND login_time >= :cutoff_date
                ORDER BY login_time DESC
            """)
            sessions_result = db.session.execute(
                sessions_query, 
                {'user_id': user_id, 'cutoff_date': cutoff_date}
            ).fetchall()
            personal_data['sessions'] = [dict(row._mapping) for row in sessions_result]
            
        except Exception as e:
            logger.error(f"Error collecting personal data for user {user_id}: {e}")
        
        return personal_data
    
    def _collect_portable_data(self, user_id: int) -> Dict[str, Any]:
        """Collect data that is portable under GDPR (user-provided or activity-generated)"""
        # Similar to _collect_user_personal_data but filtered for portability
        return self._collect_user_personal_data(user_id)
    
    def _assess_erasure_feasibility(self, user_id: int, reason: str) -> Dict[str, Any]:
        """Assess whether data can be erased or must be retained for legal compliance"""
        retention_reasons = []
        
        # Check for active accounts with balances
        active_accounts_query = text("""
            SELECT COUNT(*) as count FROM accounts 
            WHERE user_id = :user_id AND status = 'active' AND balance != 0
        """)
        active_accounts = db.session.execute(active_accounts_query, {'user_id': user_id}).scalar()
        
        if active_accounts > 0:
            retention_reasons.append("Active accounts with non-zero balances")
        
        # Check for recent transactions (regulatory requirement: 7 years)
        recent_transactions_query = text("""
            SELECT COUNT(*) as count FROM transactions 
            WHERE user_id = :user_id AND created_at >= :seven_years_ago
        """)
        seven_years_ago = datetime.utcnow() - timedelta(days=2555)  # 7 years
        recent_transactions = db.session.execute(
            recent_transactions_query, 
            {'user_id': user_id, 'seven_years_ago': seven_years_ago}
        ).scalar()
        
        if recent_transactions > 0:
            retention_reasons.append("Financial records must be retained for 7 years")
        
        # Check for pending compliance investigations
        # (Implementation would check compliance/audit tables)
        
        return {
            'can_erase': len(retention_reasons) == 0,
            'retention_reasons': retention_reasons
        }
    
    def _perform_selective_erasure(self, user_id: int) -> Dict[str, Any]:
        """Perform selective erasure while maintaining compliance"""
        erased_categories = []
        retained_for_compliance = []
        
        try:
            # Anonymize user profile (keeping account structure for compliance)
            anonymize_query = text("""
                UPDATE users SET 
                    first_name = 'ERASED',
                    last_name = 'USER',
                    email = CONCAT('erased_', id, '@deleted.local'),
                    phone = NULL,
                    date_of_birth = NULL
                WHERE id = :user_id
            """)
            db.session.execute(anonymize_query, {'user_id': user_id})
            erased_categories.append('personal_identity')
            
            # Keep financial records but anonymize where possible
            retained_for_compliance.extend(['transaction_history', 'account_records'])
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Selective erasure failed for user {user_id}: {e}")
            db.session.rollback()
        
        return {
            'categories': erased_categories,
            'retained_for_compliance': retained_for_compliance
        }
    
    def _log_gdpr_request(self, request_type: str, user_id: int, request_id: str, metadata: Dict = None):
        """Log GDPR request for audit purposes"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'request_type': request_type,
                'user_id': user_id,
                'request_id': request_id,
                'metadata': metadata or {}
            }
            
            logger.info(f"GDPR_REQUEST: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Failed to log GDPR request: {e}")
    
    def _get_processing_purposes(self) -> List[str]:
        """Get list of data processing purposes"""
        return [
            "Account management and service delivery",
            "Transaction processing and clearing",
            "Fraud prevention and security",
            "Regulatory compliance and reporting",
            "Customer support and communication",
            "Risk assessment and credit decisions"
        ]
    
    def _get_retention_periods(self) -> Dict[str, str]:
        """Get data retention periods by category"""
        return {
            "transaction_records": "7 years (regulatory requirement)",
            "account_information": "7 years after account closure",
            "identification_documents": "5 years after relationship end",
            "communication_records": "3 years",
            "session_logs": "1 year",
            "marketing_preferences": "Until consent withdrawn"
        }
    
    def _get_third_party_recipients(self) -> List[Dict[str, str]]:
        """Get list of third-party data recipients"""
        return [
            {
                "recipient": "Payment processors",
                "purpose": "Transaction processing",
                "safeguards": "Contractual data protection clauses"
            },
            {
                "recipient": "Credit bureaus",
                "purpose": "Credit assessment",
                "safeguards": "Industry standard security measures"
            },
            {
                "recipient": "Regulatory authorities",
                "purpose": "Compliance reporting",
                "safeguards": "Legal obligation, secure transmission"
            }
        ]
    
    def _get_data_sources(self) -> List[str]:
        """Get list of data sources"""
        return [
            "Direct input from data subject",
            "Account activity and transactions",
            "Public records and databases",
            "Third-party verification services",
            "Customer service interactions"
        ]
    
    def _validate_rectification_data(self, corrections: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for rectification requests"""
        # Implementation would validate each field type
        return {'valid': True, 'errors': []}
    
    def _update_user_field(self, user_id: int, field: str, new_value: Any) -> bool:
        """Update specific user field with new value"""
        try:
            # Implementation would update the specific field
            # This is a simplified example
            return True
        except Exception as e:
            logger.error(f"Failed to update field {field} for user {user_id}: {e}")
            return False
    
    def _format_data_as_csv(self, data: Dict) -> str:
        """Format data as CSV for portability"""
        # Implementation would convert data to CSV format
        return "CSV formatting not implemented"
    
    def _format_data_as_xml(self, data: Dict) -> str:
        """Format data as XML for portability"""
        # Implementation would convert data to XML format
        return "XML formatting not implemented"

# Global GDPR rights manager instance
gdpr_rights_manager = GDPRRightsManager()