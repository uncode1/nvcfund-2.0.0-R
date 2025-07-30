"""
User Management Forms
Customer-facing forms for account management, profile updates, and banking services
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField, BooleanField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError, Email, EqualTo
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class UserProfileForm(FlaskForm):
    """Form for user profile management"""
    
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message="First name must be 2-100 characters")
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Last name must be 2-100 characters")
    ])
    
    middle_name = StringField('Middle Name', validators=[
        Optional(),
        Length(max=100, message="Middle name must be max 100 characters")
    ])
    
    date_of_birth = DateTimeField('Date of Birth', validators=[DataRequired()])
    
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Length(min=10, max=20, message="Phone number must be 10-20 characters")
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
    
    state_province = StringField('State/Province', validators=[
        DataRequired(),
        Length(min=2, max=100, message="State/Province must be 2-100 characters")
    ])
    
    postal_code = StringField('Postal Code', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Postal code must be 3-20 characters")
    ])
    
    country = StringField('Country', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Country must be 2-100 characters")
    ])
    
    employment_status = SelectField('Employment Status', choices=[
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
        ('homemaker', 'Homemaker')
    ], validators=[DataRequired()])
    
    employer_name = StringField('Employer Name', validators=[
        Optional(),
        Length(max=200, message="Employer name must be max 200 characters")
    ])
    
    annual_income = DecimalField('Annual Income ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Income cannot be negative")
    ])
    
    source_of_funds = TextAreaField('Source of Funds', validators=[
        Optional(),
        Length(max=200, message="Source of funds must be max 200 characters")
    ])
    
    preferred_language = SelectField('Preferred Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ar', 'Arabic')
    ], validators=[DataRequired()])
    
    preferred_currency = SelectField('Preferred Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar')
    ], validators=[DataRequired()])
    
    marketing_consent = BooleanField('Receive Marketing Communications')
    data_sharing_consent = BooleanField('Consent to Data Sharing for Enhanced Services')

class AccountCreationForm(FlaskForm):
    """Form for creating new bank accounts"""
    
    account_type = SelectField('Account Type', choices=[
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('business', 'Business Account'),
        ('investment', 'Investment Account'),
        ('certificate_deposit', 'Certificate of Deposit'),
        ('money_market', 'Money Market Account')
    ], validators=[DataRequired()])
    
    account_name = StringField('Account Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Account name must be 5-200 characters")
    ])
    
    currency = SelectField('Account Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    initial_deposit = DecimalField('Initial Deposit', places=2, validators=[
        DataRequired(),
        NumberRange(min=25.00, message="Minimum initial deposit is $25")
    ])
    
    account_purpose = TextAreaField('Account Purpose', validators=[
        DataRequired(),
        Length(min=10, max=200, message="Purpose must be 10-200 characters")
    ])
    
    online_banking_enabled = BooleanField('Enable Online Banking', default=True)
    mobile_banking_enabled = BooleanField('Enable Mobile Banking', default=True)
    card_access_enabled = BooleanField('Enable Debit Card Access', default=True)
    
    daily_withdrawal_limit = DecimalField('Daily Withdrawal Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=100.00, max=5000.00, message="Daily limit must be $100-$5,000")
    ])
    
    daily_transfer_limit = DecimalField('Daily Transfer Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=500.00, max=25000.00, message="Transfer limit must be $500-$25,000")
    ])
    
    terms_accepted = BooleanField('I accept the account terms and conditions', validators=[DataRequired()])
    
    def validate_initial_deposit(self, field):
        """Validate initial deposit based on account type"""
        minimum_deposits = {
            'checking': 25.00,
            'savings': 100.00,
            'business': 500.00,
            'investment': 1000.00,
            'certificate_deposit': 1000.00,
            'money_market': 2500.00
        }
        
        min_deposit = minimum_deposits.get(self.account_type.data, 25.00)
        if field.data < min_deposit:
            raise ValidationError(f"Minimum deposit for {self.account_type.data} account is ${min_deposit}")

class TransferForm(FlaskForm):
    """Form for bank transfers"""
    
    from_account = SelectField('From Account', validators=[DataRequired()])
    
    transfer_type = SelectField('Transfer Type', choices=[
        ('internal', 'Internal Transfer (Between My Accounts)'),
        ('domestic', 'Domestic Transfer'),
        ('international', 'International Wire Transfer'),
        ('ach', 'ACH Transfer')
    ], validators=[DataRequired()])
    
    to_account = StringField('To Account', validators=[
        DataRequired(),
        Length(min=10, max=34, message="Account number must be 10-34 characters")
    ])
    
    beneficiary_name = StringField('Beneficiary Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Beneficiary name must be 5-200 characters")
    ])
    
    amount = DecimalField('Transfer Amount', places=2, validators=[
        DataRequired(),
        NumberRange(min=1.00, message="Minimum transfer amount is $1.00")
    ])
    
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    description = StringField('Transfer Description', validators=[
        DataRequired(),
        Length(min=5, max=500, message="Description must be 5-500 characters")
    ])
    
    transfer_date = DateTimeField('Transfer Date', validators=[DataRequired()])
    
    # International transfer fields
    recipient_bank_name = StringField('Recipient Bank Name', validators=[
        Optional(),
        Length(max=200, message="Bank name must be max 200 characters")
    ])
    
    recipient_bank_address = TextAreaField('Recipient Bank Address', validators=[
        Optional(),
        Length(max=500, message="Bank address must be max 500 characters")
    ])
    
    swift_code = StringField('SWIFT/BIC Code', validators=[
        Optional(),
        Length(min=8, max=11, message="SWIFT code must be 8-11 characters")
    ])
    
    purpose_of_payment = TextAreaField('Purpose of Payment', validators=[
        Optional(),
        Length(max=200, message="Purpose must be max 200 characters")
    ])
    
    urgency = SelectField('Transfer Urgency', choices=[
        ('standard', 'Standard (2-3 business days)'),
        ('express', 'Express (1 business day)'),
        ('urgent', 'Urgent (Same day)')
    ], validators=[DataRequired()])
    
    def validate_transfer_date(self, field):
        """Validate transfer date is not in the past"""
        if field.data and field.data.date() < datetime.utcnow().date():
            raise ValidationError("Transfer date cannot be in the past")

class PasswordChangeForm(FlaskForm):
    """Form for changing user password"""
    
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128, message="Password must be 8-128 characters"),
    ])
    
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    
    def validate_new_password(self, field):
        """Validate password complexity"""
        password = field.data
        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one number")
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise ValidationError("Password must contain at least one special character")

class SupportTicketForm(FlaskForm):
    """Form for creating support tickets"""
    
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=10, max=200, message="Subject must be 10-200 characters")
    ])
    
    category = SelectField('Category', choices=[
        ('account', 'Account Issues'),
        ('cards', 'Debit/Credit Cards'),
        ('transfers', 'Transfers & Payments'),
        ('loans', 'Loans & Credit'),
        ('online_banking', 'Online Banking'),
        ('mobile_app', 'Mobile App'),
        ('statements', 'Statements & Documents'),
        ('fees', 'Fees & Charges'),
        ('security', 'Security Concerns'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low - General Inquiry'),
        ('medium', 'Medium - Account Issue'),
        ('high', 'High - Urgent Matter'),
        ('urgent', 'Urgent - Security/Fraud')
    ], validators=[DataRequired()])
    
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=50, max=2000, message="Description must be 50-2000 characters")
    ])
    
    preferred_contact_method = SelectField('Preferred Contact Method', choices=[
        ('email', 'Email'),
        ('phone', 'Phone Call'),
        ('sms', 'Text Message'),
        ('online', 'Online Chat')
    ], validators=[DataRequired()])
    
    contact_time_preference = SelectField('Best Time to Contact', choices=[
        ('business_hours', 'Business Hours (9 AM - 5 PM)'),
        ('evening', 'Evening (5 PM - 9 PM)'),
        ('anytime', 'Anytime'),
        ('weekend', 'Weekends Only')
    ], validators=[DataRequired()])

class UserPreferencesForm(FlaskForm):
    """Form for user preferences and settings"""
    
    # Display preferences
    theme = SelectField('Theme', choices=[
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System Setting)')
    ], validators=[DataRequired()])
    
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ar', 'Arabic')
    ], validators=[DataRequired()])
    
    currency_display = SelectField('Currency Display', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    date_format = SelectField('Date Format', choices=[
        ('MM/DD/YYYY', 'MM/DD/YYYY (US)'),
        ('DD/MM/YYYY', 'DD/MM/YYYY (UK)'),
        ('YYYY-MM-DD', 'YYYY-MM-DD (ISO)'),
        ('DD-MM-YYYY', 'DD-MM-YYYY'),
        ('MM-DD-YYYY', 'MM-DD-YYYY')
    ], validators=[DataRequired()])
    
    time_format = SelectField('Time Format', choices=[
        ('12h', '12 Hour (AM/PM)'),
        ('24h', '24 Hour')
    ], validators=[DataRequired()])
    
    # Notification preferences
    email_notifications = BooleanField('Email Notifications', default=True)
    sms_notifications = BooleanField('SMS Notifications', default=True)
    push_notifications = BooleanField('Push Notifications', default=True)
    marketing_emails = BooleanField('Marketing Emails', default=False)
    
    # Security preferences
    two_factor_required = BooleanField('Require Two-Factor Authentication')
    login_alerts = BooleanField('Login Alerts', default=True)
    transaction_alerts = BooleanField('Transaction Alerts', default=True)
    suspicious_activity_alerts = BooleanField('Suspicious Activity Alerts', default=True)
    
    # Communication preferences
    preferred_contact_method = SelectField('Preferred Contact Method', choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('mail', 'Physical Mail')
    ], validators=[DataRequired()])
    
    statement_delivery = SelectField('Statement Delivery', choices=[
        ('email', 'Email Only'),
        ('mail', 'Physical Mail Only'),
        ('both', 'Both Email and Mail')
    ], validators=[DataRequired()])
    
    # Privacy settings
    profile_visibility = SelectField('Profile Visibility', choices=[
        ('private', 'Private'),
        ('limited', 'Limited Visibility'),
        ('public', 'Public (Basic Info Only)')
    ], validators=[DataRequired()])
    
    data_sharing_consent = BooleanField('Consent to Data Sharing for Enhanced Services')
    analytics_tracking = BooleanField('Allow Analytics Tracking', default=True)

class AccountLimitsForm(FlaskForm):
    """Form for managing account limits"""
    
    account_id = SelectField('Account', validators=[DataRequired()])
    
    daily_withdrawal_limit = DecimalField('Daily Withdrawal Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=100.00, max=10000.00, message="Daily withdrawal limit must be $100-$10,000")
    ])
    
    daily_transfer_limit = DecimalField('Daily Transfer Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=500.00, max=50000.00, message="Daily transfer limit must be $500-$50,000")
    ])
    
    monthly_transfer_limit = DecimalField('Monthly Transfer Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=5000.00, max=500000.00, message="Monthly transfer limit must be $5,000-$500,000")
    ])
    
    payment_limit = DecimalField('Single Payment Limit ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=100.00, max=25000.00, message="Payment limit must be $100-$25,000")
    ])
    
    international_transfer_enabled = BooleanField('Enable International Transfers')
    
    wire_transfer_enabled = BooleanField('Enable Wire Transfers')
    
    large_transaction_alerts = BooleanField('Large Transaction Alerts', default=True)
    
    foreign_transaction_alerts = BooleanField('Foreign Transaction Alerts', default=True)
    
    justification = TextAreaField('Justification for Changes', validators=[
        DataRequired(),
        Length(min=20, max=500, message="Justification must be 20-500 characters")
    ])

class DocumentUploadForm(FlaskForm):
    """Form for uploading KYC documents"""
    
    document_type = SelectField('Document Type', choices=[
        ('passport', 'Passport'),
        ('driver_license', 'Driver\'s License'),
        ('national_id', 'National ID Card'),
        ('utility_bill', 'Utility Bill'),
        ('bank_statement', 'Bank Statement'),
        ('tax_return', 'Tax Return'),
        ('employment_letter', 'Employment Letter'),
        ('proof_of_address', 'Proof of Address'),
        ('business_registration', 'Business Registration'),
        ('other', 'Other Document')
    ], validators=[DataRequired()])
    
    document_number = StringField('Document Number', validators=[
        Optional(),
        Length(max=100, message="Document number must be max 100 characters")
    ])
    
    issue_date = DateTimeField('Issue Date', validators=[Optional()])
    
    expiry_date = DateTimeField('Expiry Date', validators=[Optional()])
    
    issuing_authority = StringField('Issuing Authority', validators=[
        Optional(),
        Length(max=200, message="Issuing authority must be max 200 characters")
    ])
    
    issuing_country = StringField('Issuing Country', validators=[
        Optional(),
        Length(max=100, message="Country must be max 100 characters")
    ])
    
    document_description = TextAreaField('Document Description', validators=[
        Optional(),
        Length(max=500, message="Description must be max 500 characters")
    ])
    
    def validate_expiry_date(self, field):
        """Validate expiry date is in the future"""
        if field.data and field.data.date() <= datetime.utcnow().date():
            raise ValidationError("Document expiry date must be in the future")

class FeedbackForm(FlaskForm):
    """Form for customer feedback"""
    
    feedback_type = SelectField('Feedback Type', choices=[
        ('compliment', 'Compliment'),
        ('suggestion', 'Suggestion'),
        ('complaint', 'Complaint'),
        ('bug_report', 'Bug Report'),
        ('feature_request', 'Feature Request')
    ], validators=[DataRequired()])
    
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Subject must be 5-200 characters")
    ])
    
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=20, max=2000, message="Message must be 20-2000 characters")
    ])
    
    rating = SelectField('Overall Rating', choices=[
        ('1', '1 Star - Very Poor'),
        ('2', '2 Stars - Poor'),
        ('3', '3 Stars - Average'),
        ('4', '4 Stars - Good'),
        ('5', '5 Stars - Excellent')
    ], validators=[Optional()])
    
    service_area = SelectField('Service Area', choices=[
        ('online_banking', 'Online Banking'),
        ('mobile_app', 'Mobile App'),
        ('customer_service', 'Customer Service'),
        ('branch_service', 'Branch Service'),
        ('atm_services', 'ATM Services'),
        ('cards', 'Debit/Credit Cards'),
        ('loans', 'Loans & Credit'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    anonymous_feedback = BooleanField('Submit Anonymous Feedback')
    
    follow_up_requested = BooleanField('Request Follow-up Contact')