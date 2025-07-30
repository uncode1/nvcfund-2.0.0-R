"""
Core Form Processing System for NVC Banking Platform
Handles CSRF-protected form submissions with database storage and audit trails
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from flask import request, session, g
from flask_wtf.csrf import validate_csrf
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db
from .models import FormSubmission, FormSubmissionStatus, AuditLog, TreasuryOperation
from modules.banking.models import Transaction
from .enterprise_logging import get_enterprise_logger

# Initialize logger
logger = get_enterprise_logger('form_processor')

class FormProcessor:
    """Core form processing system with CSRF protection and database storage"""
    
    def __init__(self):
        self.logger = logger
    
    def process_form(self, form_type: str, module_name: str, form_data: Dict[str, Any], 
                    user_id: Optional[int] = None, require_csrf: bool = True) -> Dict[str, Any]:
        """
        Process a form submission with CSRF protection and database storage
        
        Args:
            form_type: Type of form (e.g., 'transfer', 'loan_application')
            module_name: Module name (e.g., 'banking', 'treasury')
            form_data: Form data dictionary
            user_id: User ID (optional, will use current_user if available)
            require_csrf: Whether to require CSRF token validation
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Get user information
            if user_id is None and current_user and current_user.is_authenticated:
                user_id = current_user.id
            
            # Validate CSRF token if required
            if require_csrf:
                csrf_valid = self._validate_csrf_token()
                if not csrf_valid:
                    return {
                        'success': False,
                        'error': 'CSRF token validation failed',
                        'error_code': 'CSRF_INVALID'
                    }
            
            # Create form submission record
            submission = self._create_form_submission(
                form_type=form_type,
                module_name=module_name,
                form_data=form_data,
                user_id=user_id
            )
            
            # Process specific form types
            processing_result = self._process_form_type(
                submission=submission,
                form_type=form_type,
                module_name=module_name,
                form_data=form_data
            )
            
            # Update submission status
            self._update_submission_status(submission.id, processing_result)
            
            # Create audit log
            self._create_audit_log(
                event_type='form_submission',
                event_description=f'{module_name}.{form_type} form submitted',
                user_id=user_id,
                form_submission_id=submission.id,
                additional_data=json.dumps({
                    'form_type': form_type,
                    'module_name': module_name,
                    'processing_result': processing_result
                })
            )
            
            return {
                'success': True,
                'submission_id': submission.submission_id,
                'processing_result': processing_result
            }
            
        except Exception as e:
            self.logger.error(f"Form processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'PROCESSING_ERROR'
            }
    
    def _validate_csrf_token(self) -> bool:
        """Validate CSRF token"""
        try:
            csrf_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not csrf_token:
                return False
            
            validate_csrf(csrf_token)
            return True
        except Exception as e:
            self.logger.warning(f"CSRF validation failed: {str(e)}")
            return False
    
    def _create_form_submission(self, form_type: str, module_name: str, 
                              form_data: Dict[str, Any], user_id: Optional[int]) -> FormSubmission:
        """Create form submission record"""
        try:
            # Get request metadata
            user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_agent = request.headers.get('User-Agent', '')
            csrf_token = request.form.get('csrf_token', '')
            session_id = session.get('session_id', str(uuid.uuid4()))
            
            # Create submission record
            submission = FormSubmission(
                form_type=form_type,
                module_name=module_name,
                user_id=user_id,
                user_ip=user_ip,
                user_agent=user_agent,
                csrf_token=csrf_token,
                session_id=session_id,
                form_data=json.dumps(form_data),
                status=FormSubmissionStatus.PENDING.value
            )
            
            db.session.add(submission)
            db.session.commit()
            
            return submission
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Database error creating form submission: {str(e)}")
            raise
    
    def _process_form_type(self, submission: FormSubmission, form_type: str, 
                          module_name: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process specific form types"""
        try:
            # Update submission status to processing
            submission.status = FormSubmissionStatus.PROCESSING.value
            db.session.commit()
            
            # Route to specific processors based on module and form type
            if module_name == 'banking':
                return self._process_banking_form(submission, form_type, form_data)
            elif module_name == 'treasury':
                return self._process_treasury_form(submission, form_type, form_data)
            elif module_name == 'trading':
                return self._process_trading_form(submission, form_type, form_data)
            elif module_name == 'cards_payments':
                return self._process_payment_form(submission, form_type, form_data)
            else:
                return self._process_generic_form(submission, form_type, form_data)
                
        except Exception as e:
            submission.status = FormSubmissionStatus.FAILED.value
            submission.error_message = str(e)
            db.session.commit()
            raise
    
    def _process_banking_form(self, submission: FormSubmission, form_type: str, 
                             form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process banking-specific forms"""
        if form_type in ['transfer', 'wire_transfer', 'ach_transfer']:
            return self._process_transfer_form(submission, form_data)
        elif form_type in ['deposit', 'withdrawal']:
            return self._process_account_transaction(submission, form_type, form_data)
        else:
            return {'status': 'processed', 'message': f'Banking form {form_type} processed'}
    
    def _process_treasury_form(self, submission: FormSubmission, form_type: str, 
                              form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process treasury-specific forms"""
        try:
            # Create treasury operation record
            treasury_op = TreasuryOperation(
                operation_type=form_type,
                operation_data=json.dumps(form_data),
                form_submission_id=submission.id,
                authorized_by=submission.user_id or 1,  # Default to system user
                authorization_level='treasury_officer'
            )
            
            db.session.add(treasury_op)
            db.session.commit()
            
            return {
                'status': 'processed',
                'treasury_operation_id': treasury_op.operation_id,
                'message': f'Treasury operation {form_type} created'
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise
    
    def _process_transfer_form(self, submission: FormSubmission, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transfer forms"""
        try:
            # Create banking transaction record
            transaction = Transaction(
                transaction_type='transfer',
                amount=float(form_data.get('amount', 0)),
                currency=form_data.get('currency', 'USD'),
                from_account_id=form_data.get('from_account_id'),
                to_account_id=form_data.get('to_account_id'),
                external_account_number=form_data.get('external_account_number'),
                routing_number=form_data.get('routing_number'),
                description=form_data.get('description', ''),
                form_submission_id=submission.id,
                initiated_by=submission.user_id or 1
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'status': 'processed',
                'transaction_id': transaction.transaction_id,
                'message': 'Transfer transaction created'
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise
    
    def _process_account_transaction(self, submission: FormSubmission, transaction_type: str, 
                                   form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process account transactions (deposits/withdrawals)"""
        try:
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=float(form_data.get('amount', 0)),
                currency=form_data.get('currency', 'USD'),
                from_account_id=form_data.get('account_id') if transaction_type == 'withdrawal' else None,
                to_account_id=form_data.get('account_id') if transaction_type == 'deposit' else None,
                description=form_data.get('description', ''),
                form_submission_id=submission.id,
                initiated_by=submission.user_id or 1
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'status': 'processed',
                'transaction_id': transaction.transaction_id,
                'message': f'{transaction_type.title()} transaction created'
            }
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise
    
    def _process_trading_form(self, submission: FormSubmission, form_type: str, 
                             form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process trading-specific forms"""
        return {'status': 'processed', 'message': f'Trading form {form_type} processed'}
    
    def _process_payment_form(self, submission: FormSubmission, form_type: str, 
                             form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment-specific forms"""
        return {'status': 'processed', 'message': f'Payment form {form_type} processed'}
    
    def _process_generic_form(self, submission: FormSubmission, form_type: str, 
                             form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic forms"""
        return {'status': 'processed', 'message': f'Generic form {form_type} processed'}
    
    def _update_submission_status(self, submission_id: int, processing_result: Dict[str, Any]):
        """Update submission status based on processing result"""
        try:
            submission = FormSubmission.query.get(submission_id)
            if submission:
                if processing_result.get('status') == 'processed':
                    submission.status = FormSubmissionStatus.COMPLETED.value
                else:
                    submission.status = FormSubmissionStatus.FAILED.value
                    submission.error_message = processing_result.get('error', 'Unknown error')
                
                submission.processed_at = datetime.utcnow()
                submission.processing_notes = json.dumps(processing_result)
                db.session.commit()
                
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error updating submission status: {str(e)}")
    
    def _create_audit_log(self, event_type: str, event_description: str, 
                         user_id: Optional[int] = None, form_submission_id: Optional[int] = None,
                         transaction_id: Optional[int] = None, additional_data: Optional[str] = None):
        """Create audit log entry"""
        try:
            user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            session_id = session.get('session_id', str(uuid.uuid4()))
            
            audit_log = AuditLog(
                event_type=event_type,
                event_description=event_description,
                user_id=user_id,
                session_id=session_id,
                user_ip=user_ip,
                form_submission_id=form_submission_id,
                transaction_id=transaction_id,
                additional_data=additional_data
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating audit log: {str(e)}")
    
    def get_form_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get form submission status"""
        try:
            submission = FormSubmission.query.filter_by(submission_id=submission_id).first()
            if not submission:
                return None
            
            return {
                'submission_id': submission.submission_id,
                'form_type': submission.form_type,
                'module_name': submission.module_name,
                'status': submission.status,
                'submitted_at': submission.submitted_at.isoformat(),
                'processed_at': submission.processed_at.isoformat() if submission.processed_at else None,
                'error_message': submission.error_message,
                'processing_notes': json.loads(submission.processing_notes) if submission.processing_notes else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting form status: {str(e)}")
            return None
    
    def get_user_submissions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's form submissions"""
        try:
            submissions = FormSubmission.query.filter_by(user_id=user_id)\
                                            .order_by(FormSubmission.submitted_at.desc())\
                                            .limit(limit).all()
            
            return [
                {
                    'submission_id': sub.submission_id,
                    'form_type': sub.form_type,
                    'module_name': sub.module_name,
                    'status': sub.status,
                    'submitted_at': sub.submitted_at.isoformat(),
                    'processed_at': sub.processed_at.isoformat() if sub.processed_at else None
                }
                for sub in submissions
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting user submissions: {str(e)}")
            return []

# Global form processor instance
form_processor = FormProcessor()