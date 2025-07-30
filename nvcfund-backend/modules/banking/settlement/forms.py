"""
Settlement Forms
Enterprise-grade forms for settlement operations, SWIFT messaging, and privileged settlement management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class SettlementTransactionForm(FlaskForm):
    """Form for creating settlement transactions"""
    
    settlement_type = SelectField('Settlement Type', choices=[
        ('rtgs', 'RTGS - Real-Time Gross Settlement'),
        ('ach', 'ACH - Automated Clearing House'),
        ('swift', 'SWIFT Network'),
        ('fedwire', 'Federal Reserve Wire Network'),
        ('chips', 'CHIPS - Clearing House Interbank Payments'),
        ('sepa', 'SEPA - Single Euro Payments Area'),
        ('target2', 'TARGET2 - Trans-European RTGS')
    ], validators=[DataRequired()])
    
    amount = DecimalField('Settlement Amount', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Amount must be positive")
    ])
    
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar')
    ], validators=[DataRequired()])
    
    sender_institution = StringField('Sender Institution (BIC)', validators=[
        DataRequired(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    sender_account = StringField('Sender Account', validators=[
        DataRequired(),
        Length(min=10, max=34, message="Account must be 10-34 characters")
    ])
    
    sender_name = StringField('Sender Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Sender name must be 5-200 characters")
    ])
    
    receiver_institution = StringField('Receiver Institution (BIC)', validators=[
        DataRequired(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    receiver_account = StringField('Receiver Account', validators=[
        DataRequired(),
        Length(min=10, max=34, message="Account must be 10-34 characters")
    ])
    
    receiver_name = StringField('Receiver Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Receiver name must be 5-200 characters")
    ])
    
    value_date = DateTimeField('Value Date', validators=[DataRequired()])
    
    priority = SelectField('Settlement Priority', choices=[
        ('high', 'High Priority'),
        ('normal', 'Normal Priority'),
        ('low', 'Low Priority')
    ], validators=[DataRequired()])
    
    payment_purpose = TextAreaField('Payment Purpose', validators=[
        DataRequired(),
        Length(min=10, max=500, message="Purpose must be 10-500 characters")
    ])
    
    regulatory_reporting = BooleanField('Regulatory Reporting Required')
    
    aml_clearance = BooleanField('AML Clearance Obtained', validators=[DataRequired()])
    
    sanctions_screening = BooleanField('OFAC Sanctions Screening Completed', validators=[DataRequired()])
    
    correspondent_charges = SelectField('Correspondent Charges', choices=[
        ('our', 'OUR - All charges borne by sender'),
        ('ben', 'BEN - All charges borne by beneficiary'),
        ('sha', 'SHA - Charges shared')
    ], validators=[DataRequired()])
    
    settlement_fee = DecimalField('Settlement Fee', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, message="Fee cannot be negative")
    ])
    
    authorization_override = BooleanField('Authorization Override Required')
    
    def validate_value_date(self, field):
        """Validate value date is not in the past"""
        if field.data and field.data.date() < datetime.utcnow().date():
            raise ValidationError("Value date cannot be in the past")
    
    def validate_amount(self, field):
        """Validate amount based on settlement type"""
        if self.settlement_type.data == 'rtgs' and field.data < 1000000:
            raise ValidationError("RTGS transactions require minimum $1M amount")

class SwiftMessageForm(FlaskForm):
    """Form for SWIFT message creation and management"""
    
    message_type = SelectField('Message Type', choices=[
        ('MT103', 'MT103 - Single Customer Credit Transfer'),
        ('MT202', 'MT202 - General Financial Institution Transfer'),
        ('MT900', 'MT900 - Confirmation of Debit'),
        ('MT910', 'MT910 - Confirmation of Credit'),
        ('MT950', 'MT950 - Statement Message'),
        ('MT940', 'MT940 - Customer Statement Message'),
        ('MT199', 'MT199 - Free Format Message'),
        ('MT299', 'MT299 - Free Format Message')
    ], validators=[DataRequired()])
    
    sender_bic = StringField('Sender BIC', validators=[
        DataRequired(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    receiver_bic = StringField('Receiver BIC', validators=[
        DataRequired(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    message_priority = SelectField('Message Priority', choices=[
        ('U', 'U - Urgent'),
        ('N', 'N - Normal'),
        ('S', 'S - System')
    ], validators=[DataRequired()])
    
    transaction_reference = StringField('Transaction Reference', validators=[
        DataRequired(),
        Length(min=16, max=16, message="Reference must be exactly 16 characters")
    ])
    
    related_reference = StringField('Related Reference', validators=[
        Optional(),
        Length(max=16, message="Related reference must be max 16 characters")
    ])
    
    value_date = DateTimeField('Value Date', validators=[DataRequired()])
    
    currency_amount = StringField('Currency and Amount', validators=[
        DataRequired(),
        Length(min=6, max=15, message="Format: CCCNNNNNNN.NN")
    ])
    
    ordering_customer = TextAreaField('Ordering Customer', validators=[
        DataRequired(),
        Length(min=10, max=350, message="Ordering customer must be 10-350 characters")
    ])
    
    beneficiary_customer = TextAreaField('Beneficiary Customer', validators=[
        DataRequired(),
        Length(min=10, max=350, message="Beneficiary customer must be 10-350 characters")
    ])
    
    remittance_information = TextAreaField('Remittance Information', validators=[
        Optional(),
        Length(max=350, message="Remittance info must be max 350 characters")
    ])
    
    intermediary_institution = StringField('Intermediary Institution', validators=[
        Optional(),
        Length(max=35, message="Intermediary institution must be max 35 characters")
    ])
    
    account_with_institution = StringField('Account With Institution', validators=[
        Optional(),
        Length(max=35, message="Account with institution must be max 35 characters")
    ])
    
    charges_code = SelectField('Charges Code', choices=[
        ('OUR', 'OUR - All charges borne by ordering customer'),
        ('BEN', 'BEN - All charges borne by beneficiary customer'),
        ('SHA', 'SHA - Transaction charges shared')
    ], validators=[DataRequired()])
    
    regulatory_information = TextAreaField('Regulatory Information', validators=[
        Optional(),
        Length(max=350, message="Regulatory info must be max 350 characters")
    ])
    
    test_message = BooleanField('Test Message')
    
    duplicate_detection = BooleanField('Duplicate Detection Enabled', default=True)

class CorrespondentBankForm(FlaskForm):
    """Form for correspondent bank management"""
    
    bank_name = StringField('Bank Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Bank name must be 5-200 characters")
    ])
    
    bic_code = StringField('BIC Code', validators=[
        DataRequired(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    country_code = StringField('Country Code', validators=[
        DataRequired(),
        Length(min=2, max=2, message="Country code must be exactly 2 characters")
    ])
    
    address_line1 = StringField('Address Line 1', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Address must be 5-200 characters")
    ])
    
    address_line2 = StringField('Address Line 2', validators=[
        Optional(),
        Length(max=200, message="Address must be max 200 characters")
    ])
    
    city = StringField('City', validators=[
        DataRequired(),
        Length(min=2, max=100, message="City must be 2-100 characters")
    ])
    
    postal_code = StringField('Postal Code', validators=[
        Optional(),
        Length(max=20, message="Postal code must be max 20 characters")
    ])
    
    country = StringField('Country', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Country must be 2-100 characters")
    ])
    
    nostro_account = StringField('Nostro Account (Our account with them)', validators=[
        Optional(),
        Length(max=34, message="Account number must be max 34 characters")
    ])
    
    vostro_account = StringField('Vostro Account (Their account with us)', validators=[
        Optional(),
        Length(max=34, message="Account number must be max 34 characters")
    ])
    
    relationship_type = SelectField('Relationship Type', choices=[
        ('correspondent', 'Correspondent Banking'),
        ('agent', 'Agent Banking'),
        ('clearing', 'Clearing Services'),
        ('custody', 'Custody Services'),
        ('trade_finance', 'Trade Finance')
    ], validators=[DataRequired()])
    
    currencies_supported = TextAreaField('Supported Currencies (comma-separated)', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Currencies must be 3-100 characters")
    ])
    
    daily_settlement_limit = DecimalField('Daily Settlement Limit', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum limit is $1M")
    ])
    
    relationship_start_date = DateTimeField('Relationship Start Date', validators=[DataRequired()])
    
    risk_rating = SelectField('Risk Rating', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ], validators=[DataRequired()])
    
    compliance_status = SelectField('Compliance Status', choices=[
        ('compliant', 'Compliant'),
        ('under_review', 'Under Review'),
        ('non_compliant', 'Non-Compliant'),
        ('suspended', 'Suspended')
    ], validators=[DataRequired()])
    
    last_due_diligence = DateTimeField('Last Due Diligence Date', validators=[Optional()])
    
    next_review_date = DateTimeField('Next Review Date', validators=[DataRequired()])
    
    standard_fee = DecimalField('Standard Transaction Fee', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, message="Fee cannot be negative")
    ])
    
    priority_fee = DecimalField('Priority Transaction Fee', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, message="Fee cannot be negative")
    ])
    
    investigation_fee = DecimalField('Investigation Fee', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, message="Fee cannot be negative")
    ])
    
    additional_notes = TextAreaField('Additional Notes', validators=[
        Optional(),
        Length(max=1000, message="Notes must be max 1000 characters")
    ])

class LiquidityPositionForm(FlaskForm):
    """Form for liquidity position management"""
    
    position_date = DateTimeField('Position Date', validators=[DataRequired()])
    
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    account_type = SelectField('Account Type', choices=[
        ('settlement', 'Settlement Account'),
        ('nostro', 'Nostro Account'),
        ('operational', 'Operational Account'),
        ('reserve', 'Reserve Account')
    ], validators=[DataRequired()])
    
    opening_balance = DecimalField('Opening Balance', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Opening balance cannot be negative")
    ])
    
    incoming_settlements = DecimalField('Incoming Settlements', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Incoming settlements cannot be negative")
    ])
    
    outgoing_settlements = DecimalField('Outgoing Settlements', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Outgoing settlements cannot be negative")
    ])
    
    funding_received = DecimalField('Funding Received', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Funding received cannot be negative")
    ])
    
    funding_provided = DecimalField('Funding Provided', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Funding provided cannot be negative")
    ])
    
    overnight_funding = DecimalField('Overnight Funding', places=2, validators=[
        Optional()
    ])
    
    minimum_balance_requirement = DecimalField('Minimum Balance Requirement', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Minimum balance cannot be negative")
    ])
    
    maximum_exposure_limit = DecimalField('Maximum Exposure Limit', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Exposure limit cannot be negative")
    ])
    
    early_warning_threshold = DecimalField('Early Warning Threshold', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Warning threshold cannot be negative")
    ])
    
    liquidity_coverage_ratio = DecimalField('Liquidity Coverage Ratio (%)', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, max=500.0000, message="LCR must be between 0% and 500%")
    ])
    
    stressed_liquidity_requirement = DecimalField('Stressed Liquidity Requirement', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Stressed liquidity cannot be negative")
    ])
    
    funding_risk = SelectField('Funding Risk Assessment', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ], validators=[DataRequired()])
    
    position_notes = TextAreaField('Position Notes', validators=[
        Optional(),
        Length(max=1000, message="Notes must be max 1000 characters")
    ])

class SettlementLimitForm(FlaskForm):
    """Form for settlement limit management"""
    
    limit_type = SelectField('Limit Type', choices=[
        ('daily', 'Daily Limit'),
        ('transaction', 'Single Transaction Limit'),
        ('counterparty', 'Counterparty Limit'),
        ('currency', 'Currency Limit'),
        ('total_exposure', 'Total Exposure Limit')
    ], validators=[DataRequired()])
    
    limit_name = StringField('Limit Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Limit name must be 5-200 characters")
    ])
    
    currency = SelectField('Currency', choices=[
        ('', 'All Currencies'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[Optional()])
    
    counterparty_bic = StringField('Counterparty BIC (if applicable)', validators=[
        Optional(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    settlement_type = SelectField('Settlement Type', choices=[
        ('', 'All Settlement Types'),
        ('rtgs', 'RTGS'),
        ('ach', 'ACH'),
        ('swift', 'SWIFT'),
        ('fedwire', 'Fedwire'),
        ('chips', 'CHIPS')
    ], validators=[Optional()])
    
    limit_amount = DecimalField('Limit Amount', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000.00, message="Minimum limit is $1,000")
    ])
    
    warning_threshold = DecimalField('Warning Threshold (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=50.0000, max=95.0000, message="Warning threshold must be 50%-95%")
    ])
    
    breach_threshold = DecimalField('Breach Threshold (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=90.0000, max=100.0000, message="Breach threshold must be 90%-100%")
    ])
    
    effective_from = DateTimeField('Effective From', validators=[DataRequired()])
    
    effective_to = DateTimeField('Effective To', validators=[Optional()])
    
    reset_frequency = SelectField('Reset Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual')
    ], validators=[DataRequired()])
    
    override_authorization_required = BooleanField('Override Authorization Required')
    
    business_justification = TextAreaField('Business Justification', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Justification must be 50-1000 characters")
    ])
    
    monitoring_frequency = SelectField('Monitoring Frequency', choices=[
        ('real_time', 'Real-Time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ], validators=[DataRequired()])

class SettlementReconciliationForm(FlaskForm):
    """Form for settlement reconciliation"""
    
    reconciliation_date = DateTimeField('Reconciliation Date', validators=[DataRequired()])
    
    reconciliation_type = SelectField('Reconciliation Type', choices=[
        ('daily', 'Daily Reconciliation'),
        ('intraday', 'Intraday Reconciliation'),
        ('week_end', 'Week-End Reconciliation'),
        ('month_end', 'Month-End Reconciliation'),
        ('year_end', 'Year-End Reconciliation')
    ], validators=[DataRequired()])
    
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    account_identifier = StringField('Account Identifier', validators=[
        DataRequired(),
        Length(min=5, max=50, message="Account identifier must be 5-50 characters")
    ])
    
    counterparty_bic = StringField('Counterparty BIC', validators=[
        Optional(),
        Length(min=8, max=11, message="BIC must be 8-11 characters")
    ])
    
    expected_balance = DecimalField('Expected Balance', places=2, validators=[
        DataRequired()
    ])
    
    actual_balance = DecimalField('Actual Balance', places=2, validators=[
        DataRequired()
    ])
    
    expected_transaction_count = IntegerField('Expected Transaction Count', validators=[
        Optional(),
        NumberRange(min=0, message="Transaction count cannot be negative")
    ])
    
    actual_transaction_count = IntegerField('Actual Transaction Count', validators=[
        Optional(),
        NumberRange(min=0, message="Transaction count cannot be negative")
    ])
    
    reconciliation_status = SelectField('Reconciliation Status', choices=[
        ('pending', 'Pending'),
        ('matched', 'Matched'),
        ('unmatched', 'Unmatched'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved')
    ], validators=[DataRequired()])
    
    investigation_notes = TextAreaField('Investigation Notes', validators=[
        Optional(),
        Length(max=2000, message="Investigation notes must be max 2000 characters")
    ])
    
    resolution_notes = TextAreaField('Resolution Notes', validators=[
        Optional(),
        Length(max=2000, message="Resolution notes must be max 2000 characters")
    ])
    
    management_review_required = BooleanField('Management Review Required')
    
    regulatory_reporting_impact = BooleanField('Regulatory Reporting Impact')
    
    estimated_resolution_date = DateTimeField('Estimated Resolution Date', validators=[Optional()])

class SettlementApprovalForm(FlaskForm):
    """Form for settlement operation approvals"""
    
    operation_id = HiddenField('Operation ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('approve_with_conditions', 'Approve with Conditions'),
        ('reject', 'Reject'),
        ('request_modification', 'Request Modification'),
        ('escalate_to_management', 'Escalate to Management'),
        ('hold_for_investigation', 'Hold for Investigation')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=50, max=2000, message="Approval notes must be 50-2000 characters")
    ])
    
    aml_compliance_check = SelectField('AML Compliance Assessment', choices=[
        ('cleared', 'AML Cleared'),
        ('pending_review', 'Pending AML Review'),
        ('additional_screening', 'Additional Screening Required'),
        ('suspicious_activity', 'Suspicious Activity Detected')
    ], validators=[DataRequired()])
    
    sanctions_compliance_check = SelectField('Sanctions Compliance Assessment', choices=[
        ('cleared', 'Sanctions Cleared'),
        ('pending_screening', 'Pending Sanctions Screening'),
        ('potential_match', 'Potential Sanctions Match'),
        ('confirmed_violation', 'Confirmed Sanctions Violation')
    ], validators=[DataRequired()])
    
    operational_risk_assessment = SelectField('Operational Risk Assessment', choices=[
        ('low_risk', 'Low Risk'),
        ('medium_risk', 'Medium Risk'),
        ('high_risk', 'High Risk'),
        ('unacceptable_risk', 'Unacceptable Risk')
    ], validators=[DataRequired()])
    
    liquidity_impact_assessment = TextAreaField('Liquidity Impact Assessment', validators=[
        DataRequired(),
        Length(min=50, max=1500, message="Impact assessment must be 50-1500 characters")
    ])
    
    conditions_and_requirements = TextAreaField('Conditions and Requirements', validators=[
        Optional(),
        Length(max=1500, message="Conditions must be max 1500 characters")
    ])
    
    monitoring_requirements = TextAreaField('Monitoring Requirements', validators=[
        Optional(),
        Length(max=1000, message="Monitoring requirements must be max 1000 characters")
    ])
    
    regulatory_notification_required = SelectField('Regulatory Notification Required', choices=[
        ('no', 'No'),
        ('routine', 'Routine Notification'),
        ('immediate', 'Immediate Notification'),
        ('suspicious_activity', 'Suspicious Activity Report')
    ], validators=[DataRequired()])
    
    correspondent_notification = BooleanField('Correspondent Bank Notification Required')
    
    customer_notification = BooleanField('Customer Notification Required')
    
    effective_date = DateTimeField('Effective Date', validators=[Optional()])
    
    review_date = DateTimeField('Next Review Date', validators=[Optional()])
    
    def validate_approval_action(self, field):
        """Validate approval based on compliance assessments"""
        if (self.sanctions_compliance_check.data == 'confirmed_violation' and 
            field.data not in ['reject', 'hold_for_investigation']):
            raise ValidationError("Confirmed sanctions violations cannot be approved")
        
        if (self.operational_risk_assessment.data == 'unacceptable_risk' and 
            field.data == 'approve'):
            raise ValidationError("Unacceptable risk operations cannot be approved without modification")