"""
Compliance Forms
Enterprise-grade forms for regulatory compliance, AML operations, and privileged compliance management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class ComplianceFrameworkForm(FlaskForm):
    """Form for creating and managing compliance frameworks"""
    
    framework_code = StringField('Framework Code', validators=[
        DataRequired(),
        Length(min=3, max=50, message="Framework code must be between 3 and 50 characters")
    ])
    
    framework_name = StringField('Framework Name', validators=[
        DataRequired(),
        Length(min=10, max=200, message="Framework name must be between 10 and 200 characters")
    ])
    
    regulation_type = SelectField('Regulation Type', choices=[
        ('bsa_aml', 'BSA/AML Compliance'),
        ('kyc_cdd', 'KYC/Customer Due Diligence'),
        ('patriot_act', 'USA PATRIOT Act'),
        ('ofac_sanctions', 'OFAC Sanctions'),
        ('pci_dss', 'PCI DSS'),
        ('sox_compliance', 'Sarbanes-Oxley'),
        ('basel_iii', 'Basel III'),
        ('dodd_frank', 'Dodd-Frank'),
        ('mifid_ii', 'MiFID II'),
        ('gdpr', 'GDPR'),
        ('ccar_stress_test', 'CCAR Stress Testing'),
        ('volcker_rule', 'Volcker Rule')
    ], validators=[DataRequired()])
    
    regulatory_body = StringField('Regulatory Body', validators=[
        DataRequired(),
        Length(min=3, max=200, message="Regulatory body must be between 3 and 200 characters")
    ])
    
    jurisdiction = StringField('Jurisdiction', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Jurisdiction must be between 2 and 100 characters")
    ])
    
    risk_level = SelectField('Risk Level', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], validators=[DataRequired()])
    
    testing_frequency = SelectField('Testing Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi_annual', 'Semi-Annual'),
        ('annual', 'Annual')
    ], validators=[DataRequired()])
    
    compliance_requirements = TextAreaField('Compliance Requirements', validators=[
        DataRequired(),
        Length(min=100, max=5000, message="Requirements must be between 100 and 5000 characters")
    ])
    
    control_objectives = TextAreaField('Control Objectives', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Control objectives must be between 100 and 3000 characters")
    ])
    
    key_controls = TextAreaField('Key Controls', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Key controls must be between 100 and 3000 characters")
    ])
    
    regulatory_penalties = TextAreaField('Regulatory Penalties', validators=[
        Optional(),
        Length(max=2000, message="Penalties description must be less than 2000 characters")
    ])
    
    business_impact = TextAreaField('Business Impact Assessment', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Business impact must be between 100 and 2000 characters")
    ])
    
    implementation_deadline = DateTimeField('Implementation Deadline', validators=[Optional()])
    
    next_assessment_date = DateTimeField('Next Assessment Date', validators=[DataRequired()])

class ComplianceAssessmentForm(FlaskForm):
    """Form for compliance assessments and audits"""
    
    framework_id = SelectField('Compliance Framework', validators=[DataRequired()])
    
    assessment_type = SelectField('Assessment Type', choices=[
        ('internal_audit', 'Internal Audit'),
        ('external_audit', 'External Audit'),
        ('regulatory_examination', 'Regulatory Examination'),
        ('self_assessment', 'Self Assessment'),
        ('third_party_review', 'Third Party Review')
    ], validators=[DataRequired()])
    
    assessment_period_start = DateTimeField('Assessment Period Start', validators=[DataRequired()])
    
    assessment_period_end = DateTimeField('Assessment Period End', validators=[DataRequired()])
    
    external_auditor = StringField('External Auditor', validators=[
        Optional(),
        Length(max=200, message="External auditor name must be less than 200 characters")
    ])
    
    assessment_methodology = SelectField('Assessment Methodology', choices=[
        ('risk_based', 'Risk-Based Approach'),
        ('controls_based', 'Controls-Based Approach'),
        ('substantive_testing', 'Substantive Testing'),
        ('hybrid_approach', 'Hybrid Approach')
    ], validators=[DataRequired()])
    
    sampling_approach = SelectField('Sampling Approach', choices=[
        ('statistical_sampling', 'Statistical Sampling'),
        ('judgmental_sampling', 'Judgmental Sampling'),
        ('random_sampling', 'Random Sampling'),
        ('stratified_sampling', 'Stratified Sampling'),
        ('full_population', 'Full Population Testing')
    ], validators=[DataRequired()])
    
    overall_rating = SelectField('Overall Rating', choices=[
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('under_review', 'Under Review'),
        ('remediation_required', 'Remediation Required'),
        ('escalated', 'Escalated')
    ], validators=[DataRequired()])
    
    control_effectiveness = SelectField('Control Effectiveness', choices=[
        ('effective', 'Effective'),
        ('partially_effective', 'Partially Effective'),
        ('ineffective', 'Ineffective'),
        ('not_tested', 'Not Tested')
    ], validators=[DataRequired()])
    
    inherent_risk = SelectField('Inherent Risk', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    
    residual_risk = SelectField('Residual Risk (After Controls)', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], validators=[DataRequired()])
    
    key_findings = TextAreaField('Key Findings', validators=[
        DataRequired(),
        Length(min=100, max=5000, message="Key findings must be between 100 and 5000 characters")
    ])
    
    control_deficiencies = TextAreaField('Control Deficiencies', validators=[
        Optional(),
        Length(max=3000, message="Control deficiencies must be less than 3000 characters")
    ])
    
    process_improvements = TextAreaField('Recommended Process Improvements', validators=[
        Optional(),
        Length(max=3000, message="Process improvements must be less than 3000 characters")
    ])
    
    management_response = TextAreaField('Management Response', validators=[
        Optional(),
        Length(max=2000, message="Management response must be less than 2000 characters")
    ])
    
    remediation_deadline = DateTimeField('Remediation Deadline', validators=[Optional()])
    
    follow_up_required = BooleanField('Follow-up Required')
    
    follow_up_date = DateTimeField('Follow-up Date', validators=[Optional()])

class ComplianceViolationForm(FlaskForm):
    """Form for reporting compliance violations and incidents"""
    
    framework_id = SelectField('Related Compliance Framework', validators=[DataRequired()])
    
    violation_type = StringField('Violation Type', validators=[
        DataRequired(),
        Length(min=10, max=100, message="Violation type must be between 10 and 100 characters")
    ])
    
    violation_severity = SelectField('Violation Severity', choices=[
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact'),
        ('critical', 'Critical Impact')
    ], validators=[DataRequired()])
    
    incident_date = DateTimeField('Incident Date', validators=[DataRequired()])
    
    discovery_date = DateTimeField('Discovery Date', validators=[DataRequired()])
    
    discovery_method = SelectField('Discovery Method', choices=[
        ('internal_audit', 'Internal Audit'),
        ('external_audit', 'External Audit'),
        ('self_reported', 'Self Reported'),
        ('customer_complaint', 'Customer Complaint'),
        ('regulatory_examination', 'Regulatory Examination'),
        ('automated_monitoring', 'Automated Monitoring'),
        ('whistleblower', 'Whistleblower Report')
    ], validators=[DataRequired()])
    
    violation_description = TextAreaField('Violation Description', validators=[
        DataRequired(),
        Length(min=100, max=5000, message="Description must be between 100 and 5000 characters")
    ])
    
    affected_customers = IntegerField('Number of Affected Customers', validators=[
        DataRequired(),
        NumberRange(min=0, message="Number of customers cannot be negative")
    ])
    
    financial_impact = DecimalField('Financial Impact ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Financial impact cannot be negative")
    ])
    
    root_cause = TextAreaField('Root Cause Analysis', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Root cause analysis must be between 100 and 3000 characters")
    ])
    
    immediate_actions = TextAreaField('Immediate Actions Taken', validators=[
        DataRequired(),
        Length(min=50, max=2000, message="Immediate actions must be between 50 and 2000 characters")
    ])
    
    corrective_actions = TextAreaField('Corrective Actions Plan', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Corrective actions must be between 100 and 3000 characters")
    ])
    
    preventive_measures = TextAreaField('Preventive Measures', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Preventive measures must be between 100 and 2000 characters")
    ])
    
    remediation_deadline = DateTimeField('Remediation Deadline', validators=[DataRequired()])
    
    regulatory_notification_required = BooleanField('Regulatory Notification Required')
    
    regulatory_notification_date = DateTimeField('Regulatory Notification Date', validators=[Optional()])

class AMLTransactionReviewForm(FlaskForm):
    """Form for AML transaction review and investigation"""
    
    transaction_id = StringField('Transaction ID', validators=[
        DataRequired(),
        Length(min=5, max=100, message="Transaction ID must be between 5 and 100 characters")
    ])
    
    customer_id = SelectField('Customer', validators=[DataRequired()])
    
    transaction_amount = DecimalField('Transaction Amount ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Transaction amount must be positive")
    ])
    
    transaction_currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('AUD', 'Australian Dollar')
    ], validators=[DataRequired()])
    
    transaction_type = SelectField('Transaction Type', choices=[
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('wire_transfer', 'Wire Transfer'),
        ('ach_transfer', 'ACH Transfer'),
        ('check_deposit', 'Check Deposit'),
        ('international_transfer', 'International Transfer'),
        ('currency_exchange', 'Currency Exchange')
    ], validators=[DataRequired()])
    
    counterparty_name = StringField('Counterparty Name', validators=[
        Optional(),
        Length(max=200, message="Counterparty name must be less than 200 characters")
    ])
    
    counterparty_country = StringField('Counterparty Country', validators=[
        Optional(),
        Length(max=100, message="Counterparty country must be less than 100 characters")
    ])
    
    aml_risk_score = IntegerField('AML Risk Score (1-100)', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message="Risk score must be between 1 and 100")
    ])
    
    suspicious_indicators = TextAreaField('Suspicious Activity Indicators', validators=[
        Optional(),
        Length(max=2000, message="Suspicious indicators must be less than 2000 characters")
    ])
    
    high_risk_country = BooleanField('High Risk Country Involved')
    
    pep_involvement = BooleanField('Politically Exposed Person (PEP) Involved')
    
    sanctions_screening_result = SelectField('Sanctions Screening Result', choices=[
        ('clear', 'Clear - No Matches'),
        ('potential_match', 'Potential Match - Review Required'),
        ('confirmed_match', 'Confirmed Match - Blocked'),
        ('false_positive', 'False Positive - Cleared')
    ], validators=[DataRequired()])
    
    alert_type = SelectField('Alert Type', choices=[
        ('threshold_breach', 'Threshold Breach'),
        ('unusual_pattern', 'Unusual Transaction Pattern'),
        ('structuring', 'Potential Structuring'),
        ('velocity_check', 'High Velocity Activity'),
        ('geographic_risk', 'Geographic Risk'),
        ('customer_behavior', 'Unusual Customer Behavior'),
        ('manual_review', 'Manual Review Required')
    ], validators=[DataRequired()])
    
    alert_priority = SelectField('Alert Priority', choices=[
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical Priority')
    ], validators=[DataRequired()])
    
    investigation_notes = TextAreaField('Investigation Notes', validators=[
        DataRequired(),
        Length(min=100, max=5000, message="Investigation notes must be between 100 and 5000 characters")
    ])
    
    sar_required = BooleanField('Suspicious Activity Report (SAR) Required')
    
    sar_reason = TextAreaField('SAR Filing Reason', validators=[
        Optional(),
        Length(max=2000, message="SAR reason must be less than 2000 characters")
    ])
    
    ctr_required = BooleanField('Currency Transaction Report (CTR) Required')
    
    resolution_status = SelectField('Resolution Status', choices=[
        ('cleared', 'Cleared - No Suspicious Activity'),
        ('escalated', 'Escalated for Further Review'),
        ('reported_sar', 'Reported via SAR'),
        ('reported_ctr', 'Reported via CTR'),
        ('blocked', 'Transaction Blocked'),
        ('account_closed', 'Account Closure Recommended')
    ], validators=[DataRequired()])
    
    resolution_notes = TextAreaField('Resolution Notes', validators=[
        DataRequired(),
        Length(min=50, max=2000, message="Resolution notes must be between 50 and 2000 characters")
    ])

class RegulatoryReportForm(FlaskForm):
    """Form for regulatory report preparation and submission"""
    
    report_type = SelectField('Report Type', choices=[
        ('call_report', 'Call Report (FFIEC 031/041)'),
        ('sar', 'Suspicious Activity Report'),
        ('ctr', 'Currency Transaction Report'),
        ('fbar', 'Foreign Bank Account Report'),
        ('form_8300', 'Form 8300 (Cash Payments)'),
        ('ccar_submission', 'CCAR Submission'),
        ('dfast_submission', 'DFAST Submission'),
        ('basel_pillar3', 'Basel Pillar 3 Report'),
        ('liquidity_report', 'Liquidity Coverage Ratio Report')
    ], validators=[DataRequired()])
    
    report_period = StringField('Report Period', validators=[
        DataRequired(),
        Length(min=5, max=50, message="Report period must be between 5 and 50 characters")
    ])
    
    regulatory_body = SelectField('Regulatory Body', choices=[
        ('fdic', 'FDIC'),
        ('occ', 'OCC'),
        ('fed', 'Federal Reserve'),
        ('fincen', 'FinCEN'),
        ('sec', 'SEC'),
        ('cftc', 'CFTC'),
        ('treasury', 'US Treasury'),
        ('irs', 'IRS')
    ], validators=[DataRequired()])
    
    filing_deadline = DateTimeField('Filing Deadline', validators=[DataRequired()])
    
    submission_method = SelectField('Submission Method', choices=[
        ('electronic_portal', 'Electronic Portal'),
        ('secure_api', 'Secure API'),
        ('email_encrypted', 'Encrypted Email'),
        ('physical_delivery', 'Physical Delivery'),
        ('certified_mail', 'Certified Mail')
    ], validators=[DataRequired()])
    
    data_validation_status = SelectField('Data Validation Status', choices=[
        ('pending', 'Pending Validation'),
        ('passed', 'Validation Passed'),
        ('failed', 'Validation Failed'),
        ('partially_passed', 'Partially Passed')
    ], validators=[DataRequired()])
    
    qa_reviewed = BooleanField('QA Review Completed')
    
    report_summary = TextAreaField('Report Summary', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Report summary must be between 100 and 3000 characters")
    ])
    
    data_sources = TextAreaField('Data Sources and Methodology', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Data sources must be between 100 and 2000 characters")
    ])
    
    validation_procedures = TextAreaField('Validation Procedures', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Validation procedures must be between 100 and 2000 characters")
    ])
    
    supporting_documentation = TextAreaField('Supporting Documentation', validators=[
        Optional(),
        Length(max=1000, message="Supporting documentation must be less than 1000 characters")
    ])
    
    management_certification = BooleanField('Management Certification Obtained', validators=[DataRequired()])
    
    board_approval_required = BooleanField('Board Approval Required')
    
    confidentiality_classification = SelectField('Confidentiality Classification', choices=[
        ('public', 'Public'),
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
        ('highly_confidential', 'Highly Confidential')
    ], validators=[DataRequired()])

class ComplianceTrainingForm(FlaskForm):
    """Form for compliance training management"""
    
    training_name = StringField('Training Name', validators=[
        DataRequired(),
        Length(min=10, max=200, message="Training name must be between 10 and 200 characters")
    ])
    
    training_category = SelectField('Training Category', choices=[
        ('aml_bsa', 'AML/BSA Training'),
        ('kyc_training', 'KYC Training'),
        ('ethics_training', 'Ethics Training'),
        ('privacy_training', 'Privacy/GDPR Training'),
        ('cybersecurity', 'Cybersecurity Training'),
        ('insider_trading', 'Insider Trading Prevention'),
        ('fraud_prevention', 'Fraud Prevention'),
        ('regulatory_updates', 'Regulatory Updates'),
        ('risk_management', 'Risk Management'),
        ('data_governance', 'Data Governance')
    ], validators=[DataRequired()])
    
    training_provider = StringField('Training Provider', validators=[
        Optional(),
        Length(max=200, message="Training provider must be less than 200 characters")
    ])
    
    training_description = TextAreaField('Training Description', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Description must be between 100 and 2000 characters")
    ])
    
    delivery_method = SelectField('Delivery Method', choices=[
        ('online_self_paced', 'Online Self-Paced'),
        ('virtual_instructor_led', 'Virtual Instructor-Led'),
        ('classroom_training', 'Classroom Training'),
        ('blended_learning', 'Blended Learning'),
        ('webinar', 'Webinar'),
        ('workshop', 'Workshop')
    ], validators=[DataRequired()])
    
    duration_hours = DecimalField('Duration (Hours)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.25, max=40.00, message="Duration must be between 0.25 and 40 hours")
    ])
    
    mandatory = BooleanField('Mandatory Training', default=True)
    
    frequency = SelectField('Training Frequency', choices=[
        ('one_time', 'One Time'),
        ('annual', 'Annual'),
        ('biannual', 'Biannual'),
        ('quarterly', 'Quarterly'),
        ('monthly', 'Monthly'),
        ('as_needed', 'As Needed')
    ], validators=[DataRequired()])
    
    target_audience = TextAreaField('Target Audience', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Target audience must be between 50 and 1000 characters")
    ])
    
    learning_objectives = TextAreaField('Learning Objectives', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Learning objectives must be between 100 and 2000 characters")
    ])
    
    assessment_required = BooleanField('Assessment Required', default=True)
    
    passing_score = IntegerField('Passing Score (%)', validators=[
        Optional(),
        NumberRange(min=50, max=100, message="Passing score must be between 50% and 100%")
    ])
    
    certification_validity_months = IntegerField('Certification Validity (Months)', validators=[
        DataRequired(),
        NumberRange(min=1, max=60, message="Validity must be between 1 and 60 months")
    ])
    
    completion_deadline = DateTimeField('Completion Deadline', validators=[DataRequired()])

class ComplianceApprovalForm(FlaskForm):
    """Form for compliance operation approvals"""
    
    operation_id = HiddenField('Operation ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('approve_with_conditions', 'Approve with Conditions'),
        ('reject', 'Reject'),
        ('request_modification', 'Request Modification'),
        ('escalate_to_board', 'Escalate to Board'),
        ('escalate_to_regulator', 'Escalate to Regulator')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Approval notes must be between 100 and 3000 characters")
    ])
    
    regulatory_compliance_check = SelectField('Regulatory Compliance Assessment', choices=[
        ('fully_compliant', 'Fully Compliant'),
        ('compliant_with_conditions', 'Compliant with Conditions'),
        ('minor_compliance_issues', 'Minor Compliance Issues'),
        ('material_compliance_concerns', 'Material Compliance Concerns'),
        ('non_compliant', 'Non-Compliant')
    ], validators=[DataRequired()])
    
    risk_assessment = SelectField('Risk Assessment', choices=[
        ('low_risk', 'Low Risk'),
        ('medium_risk', 'Medium Risk'),
        ('high_risk', 'High Risk'),
        ('critical_risk', 'Critical Risk')
    ], validators=[DataRequired()])
    
    conditions_and_requirements = TextAreaField('Conditions and Requirements', validators=[
        Optional(),
        Length(max=2000, message="Conditions must be less than 2000 characters")
    ])
    
    monitoring_requirements = TextAreaField('Ongoing Monitoring Requirements', validators=[
        Optional(),
        Length(max=1500, message="Monitoring requirements must be less than 1500 characters")
    ])
    
    board_notification_required = SelectField('Board Notification Required', choices=[
        ('no', 'No'),
        ('yes_summary', 'Yes - Summary Notification'),
        ('yes_detailed', 'Yes - Detailed Report'),
        ('yes_immediate', 'Yes - Immediate Notification')
    ], validators=[DataRequired()])
    
    regulatory_notification_required = SelectField('Regulatory Notification Required', choices=[
        ('no', 'No'),
        ('yes_routine', 'Yes - Routine Notification'),
        ('yes_immediate', 'Yes - Immediate Notification'),
        ('yes_prior_approval', 'Yes - Prior Approval Required')
    ], validators=[DataRequired()])
    
    effective_date = DateTimeField('Effective Date', validators=[Optional()])
    
    review_date = DateTimeField('Next Review Date', validators=[Optional()])
    
    def validate_approval_action(self, field):
        """Validate approval action based on compliance assessment"""
        if (self.regulatory_compliance_check.data == 'non_compliant' and 
            field.data not in ['reject', 'escalate_to_regulator']):
            raise ValidationError("Non-compliant operations can only be rejected or escalated to regulator")
    
    def validate_conditions_and_requirements(self, field):
        """Validate that conditions are provided when approval is conditional"""
        if (self.approval_action.data == 'approve_with_conditions' and 
            (not field.data or len(field.data.strip()) < 50)):
            raise ValidationError("Conditions must be specified when approving with conditions")