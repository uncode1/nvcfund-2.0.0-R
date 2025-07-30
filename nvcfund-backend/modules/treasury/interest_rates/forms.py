"""
Enterprise-Grade Forms and Validation for Interest Rate Management
Role-based forms for Treasury Officers, Asset Liability Managers, and Executive Level
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class BaseRateForm(FlaskForm):
    """Base form for all rate management operations"""
    
    def __init__(self, user_role: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_role = user_role
        self._set_role_based_limits()
    
    def _set_role_based_limits(self):
        """Set rate change limits based on user role"""
        self.rate_limits = {
            'treasury_officer': {'max_change': 0.50, 'products': ['savings', 'checking', 'personal_loans']},
            'asset_liability_manager': {'max_change': 1.00, 'products': ['mortgages', 'commercial_loans', 'deposits']},
            'cfo': {'max_change': 2.00, 'products': ['institutional', 'policy_rates', 'emergency_rates']},
            'board_member': {'max_change': 5.00, 'products': ['all']},
            'monetary_policy_committee': {'max_change': 10.00, 'products': ['all']}
        }

class FederalRateForm(BaseRateForm):
    """Form for Federal Funds Rate and Prime Rate management"""
    
    rate_type = SelectField('Rate Type', choices=[
        ('federal_funds', 'Federal Funds Rate'),
        ('prime_rate', 'Prime Rate'),
        ('discount_rate', 'Discount Rate')
    ], validators=[DataRequired()])
    
    current_rate = DecimalField('Current Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=25.0000, message="Rate must be between 0% and 25%")
    ])
    
    new_rate = DecimalField('New Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=25.0000, message="Rate must be between 0% and 25%")
    ])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    justification = TextAreaField('Rate Change Justification', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Justification must be between 50 and 1000 characters")
    ])
    
    emergency_change = SelectField('Emergency Change', choices=[
        ('no', 'Regular Rate Change'),
        ('yes', 'Emergency Rate Change')
    ], default='no')
    
    def validate_new_rate(self, field):
        """Validate rate change authority"""
        if not self.current_rate.data:
            return
        
        rate_change = abs(field.data - self.current_rate.data)
        user_limits = self.rate_limits.get(self.user_role, {'max_change': 0.25})
        
        if rate_change > user_limits['max_change']:
            raise ValidationError(f"Rate change of {rate_change:.4f}% exceeds your authority limit of {user_limits['max_change']:.4f}%")
    
    def validate_effective_date(self, field):
        """Validate effective date is not in the past"""
        if field.data < datetime.now():
            raise ValidationError("Effective date cannot be in the past")

class ConsumerRateForm(BaseRateForm):
    """Form for consumer banking rates (mortgages, personal loans, auto loans)"""
    
    product_type = SelectField('Product Type', choices=[
        ('mortgage_30_year', '30-Year Fixed Mortgage'),
        ('mortgage_15_year', '15-Year Fixed Mortgage'),
        ('mortgage_arm', 'Adjustable Rate Mortgage'),
        ('personal_loan', 'Personal Loan'),
        ('auto_loan_new', 'Auto Loan (New)'),
        ('auto_loan_used', 'Auto Loan (Used)'),
        ('home_equity', 'Home Equity Line of Credit'),
        ('student_loan', 'Student Loan')
    ], validators=[DataRequired()])
    
    credit_tier = SelectField('Credit Tier', choices=[
        ('excellent', 'Excellent (740+)'),
        ('good', 'Good (670-739)'),
        ('fair', 'Fair (580-669)'),
        ('poor', 'Poor (300-579)')
    ], validators=[DataRequired()])
    
    current_rate = DecimalField('Current Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=35.0000, message="Rate must be between 0% and 35%")
    ])
    
    new_rate = DecimalField('New Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=35.0000, message="Rate must be between 0% and 35%")
    ])
    
    ltv_ratio = DecimalField('Loan-to-Value Ratio (%)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, max=100.00, message="LTV must be between 0% and 100%")
    ])
    
    term_months = SelectField('Term (Months)', choices=[
        ('12', '12 Months'),
        ('24', '24 Months'),
        ('36', '36 Months'),
        ('60', '60 Months'),
        ('84', '84 Months'),
        ('180', '180 Months (15 Years)'),
        ('360', '360 Months (30 Years)')
    ], validators=[Optional()])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    rate_justification = TextAreaField('Rate Change Justification', validators=[
        DataRequired(),
        Length(min=30, max=500, message="Justification must be between 30 and 500 characters")
    ])
    
    competitive_analysis = TextAreaField('Competitive Analysis', validators=[
        Optional(),
        Length(max=500, message="Analysis must be less than 500 characters")
    ])

class CommercialRateForm(BaseRateForm):
    """Form for commercial banking rates"""
    
    product_type = SelectField('Commercial Product', choices=[
        ('business_loan', 'Business Term Loan'),
        ('sba_loan', 'SBA Loan'),
        ('commercial_real_estate', 'Commercial Real Estate'),
        ('equipment_financing', 'Equipment Financing'),
        ('business_line_of_credit', 'Business Line of Credit'),
        ('commercial_mortgage', 'Commercial Mortgage'),
        ('working_capital', 'Working Capital Loan')
    ], validators=[DataRequired()])
    
    business_size = SelectField('Business Size', choices=[
        ('small', 'Small Business (<$10M Revenue)'),
        ('medium', 'Medium Business ($10M-$100M)'),
        ('large', 'Large Business (>$100M)'),
        ('enterprise', 'Enterprise (>$1B)')
    ], validators=[DataRequired()])
    
    risk_rating = SelectField('Risk Rating', choices=[
        ('aaa', 'AAA (Minimal Risk)'),
        ('aa', 'AA (Low Risk)'),
        ('a', 'A (Moderate Risk)'),
        ('bbb', 'BBB (Acceptable Risk)'),
        ('bb', 'BB (High Risk)'),
        ('b', 'B (Very High Risk)')
    ], validators=[DataRequired()])
    
    current_rate = DecimalField('Current Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=50.0000, message="Rate must be between 0% and 50%")
    ])
    
    new_rate = DecimalField('New Rate (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=50.0000, message="Rate must be between 0% and 50%")
    ])
    
    loan_amount_range = SelectField('Loan Amount Range', choices=[
        ('under_100k', 'Under $100,000'),
        ('100k_500k', '$100,000 - $500,000'),
        ('500k_1m', '$500,000 - $1,000,000'),
        ('1m_5m', '$1,000,000 - $5,000,000'),
        ('5m_25m', '$5,000,000 - $25,000,000'),
        ('over_25m', 'Over $25,000,000')
    ], validators=[DataRequired()])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    credit_analysis = TextAreaField('Credit Analysis Summary', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Analysis must be between 50 and 1000 characters")
    ])
    
    profitability_impact = TextAreaField('Profitability Impact Assessment', validators=[
        DataRequired(),
        Length(min=30, max=500, message="Impact assessment must be between 30 and 500 characters")
    ])

class DepositRateForm(BaseRateForm):
    """Form for deposit rates (savings, CDs, money market)"""
    
    product_type = SelectField('Deposit Product', choices=[
        ('savings', 'Regular Savings'),
        ('high_yield_savings', 'High-Yield Savings'),
        ('money_market', 'Money Market Account'),
        ('cd_3_month', 'CD - 3 Month'),
        ('cd_6_month', 'CD - 6 Month'),
        ('cd_1_year', 'CD - 1 Year'),
        ('cd_2_year', 'CD - 2 Year'),
        ('cd_5_year', 'CD - 5 Year'),
        ('business_savings', 'Business Savings'),
        ('business_money_market', 'Business Money Market')
    ], validators=[DataRequired()])
    
    balance_tier = SelectField('Balance Tier', choices=[
        ('under_1k', 'Under $1,000'),
        ('1k_10k', '$1,000 - $10,000'),
        ('10k_50k', '$10,000 - $50,000'),
        ('50k_100k', '$50,000 - $100,000'),
        ('100k_500k', '$100,000 - $500,000'),
        ('over_500k', 'Over $500,000')
    ], validators=[DataRequired()])
    
    current_rate = DecimalField('Current APY (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=10.0000, message="APY must be between 0% and 10%")
    ])
    
    new_rate = DecimalField('New APY (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=10.0000, message="APY must be between 0% and 10%")
    ])
    
    promotional_rate = SelectField('Promotional Rate', choices=[
        ('no', 'Standard Rate'),
        ('yes', 'Promotional Rate')
    ], default='no')
    
    promotional_period = SelectField('Promotional Period', choices=[
        ('', 'Not Applicable'),
        ('30_days', '30 Days'),
        ('60_days', '60 Days'),
        ('90_days', '90 Days'),
        ('180_days', '180 Days'),
        ('365_days', '365 Days')
    ], validators=[Optional()])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    market_analysis = TextAreaField('Market Rate Analysis', validators=[
        DataRequired(),
        Length(min=40, max=800, message="Market analysis must be between 40 and 800 characters")
    ])
    
    customer_impact = TextAreaField('Customer Impact Assessment', validators=[
        DataRequired(),
        Length(min=30, max=500, message="Impact assessment must be between 30 and 500 characters")
    ])

class RateApprovalForm(FlaskForm):
    """Form for rate change approvals"""
    
    rate_change_id = HiddenField('Rate Change ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_revision', 'Request Revision')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=20, max=1000, message="Notes must be between 20 and 1000 characters")
    ])
    
    conditions = TextAreaField('Conditions/Requirements', validators=[
        Optional(),
        Length(max=500, message="Conditions must be less than 500 characters")
    ])
    
    risk_assessment = SelectField('Risk Assessment', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk')
    ], validators=[DataRequired()])

class BulkRateUpdateForm(BaseRateForm):
    """Form for bulk rate updates across product categories"""
    
    product_category = SelectField('Product Category', choices=[
        ('all_consumer', 'All Consumer Products'),
        ('all_commercial', 'All Commercial Products'),
        ('all_deposits', 'All Deposit Products'),
        ('mortgages', 'All Mortgage Products'),
        ('auto_loans', 'All Auto Loans'),
        ('personal_loans', 'All Personal Loans'),
        ('business_loans', 'All Business Loans')
    ], validators=[DataRequired()])
    
    adjustment_type = SelectField('Adjustment Type', choices=[
        ('percentage_increase', 'Percentage Increase'),
        ('percentage_decrease', 'Percentage Decrease'),
        ('basis_point_increase', 'Basis Point Increase'),
        ('basis_point_decrease', 'Basis Point Decrease'),
        ('set_absolute', 'Set Absolute Rate')
    ], validators=[DataRequired()])
    
    adjustment_value = DecimalField('Adjustment Value', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0001, max=10.0000, message="Adjustment must be between 0.0001 and 10.0000")
    ])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    justification = TextAreaField('Bulk Update Justification', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Justification must be between 100 and 2000 characters")
    ])
    
    fed_policy_correlation = SelectField('Fed Policy Correlation', choices=[
        ('fed_rate_increase', 'Fed Rate Increase'),
        ('fed_rate_decrease', 'Fed Rate Decrease'),
        ('market_conditions', 'Market Conditions'),
        ('competitive_pressure', 'Competitive Pressure'),
        ('profitability_adjustment', 'Profitability Adjustment'),
        ('risk_adjustment', 'Risk Adjustment')
    ], validators=[DataRequired()])
    
    def validate_adjustment_value(self, field):
        """Validate adjustment value based on user role"""
        user_limits = self.rate_limits.get(self.user_role, {'max_change': 0.25})
        
        if field.data > user_limits['max_change']:
            raise ValidationError(f"Adjustment of {field.data:.4f} exceeds your authority limit of {user_limits['max_change']:.4f}")

class RateHistorySearchForm(FlaskForm):
    """Form for searching rate history and analytics"""
    
    product_type = SelectField('Product Type', choices=[
        ('', 'All Products'),
        ('federal_funds', 'Federal Funds'),
        ('prime_rate', 'Prime Rate'),
        ('mortgages', 'Mortgages'),
        ('auto_loans', 'Auto Loans'),
        ('personal_loans', 'Personal Loans'),
        ('business_loans', 'Business Loans'),
        ('deposits', 'Deposits')
    ], validators=[Optional()])
    
    date_from = DateTimeField('From Date', validators=[Optional()])
    date_to = DateTimeField('To Date', validators=[Optional()])
    
    rate_range_min = DecimalField('Min Rate (%)', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, max=100.0000)
    ])
    
    rate_range_max = DecimalField('Max Rate (%)', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, max=100.0000)
    ])
    
    approved_by = SelectField('Approved By', choices=[
        ('', 'All Approvers'),
        ('treasury_officer', 'Treasury Officer'),
        ('asset_liability_manager', 'Asset Liability Manager'),
        ('cfo', 'CFO'),
        ('board_member', 'Board Member')
    ], validators=[Optional()])
    
    def validate_date_to(self, field):
        """Validate date range"""
        if self.date_from.data and field.data:
            if field.data < self.date_from.data:
                raise ValidationError("End date must be after start date")
    
    def validate_rate_range_max(self, field):
        """Validate rate range"""
        if self.rate_range_min.data and field.data:
            if field.data < self.rate_range_min.data:
                raise ValidationError("Max rate must be greater than min rate")