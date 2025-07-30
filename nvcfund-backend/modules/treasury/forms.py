"""
Treasury Operations Forms
Enterprise-grade forms for $30T treasury operations and privileged user management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class NVCTSupplyOperationForm(FlaskForm):
    """Form for NVCT stablecoin supply operations (minting/burning)"""
    
    operation_type = SelectField('Operation Type', choices=[
        ('nvct_minting', 'NVCT Minting'),
        ('nvct_burning', 'NVCT Burning')
    ], validators=[DataRequired()])
    
    amount = DecimalField('NVCT Amount', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, max=1000000000000.00, message="Amount must be between $1M and $1T")
    ])
    
    operation_reason = SelectField('Operation Reason', choices=[
        ('market_demand', 'Market Demand'),
        ('collateral_adjustment', 'Collateral Adjustment'),
        ('monetary_policy', 'Monetary Policy'),
        ('emergency_liquidity', 'Emergency Liquidity'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('strategic_rebalancing', 'Strategic Rebalancing')
    ], validators=[DataRequired()])
    
    authorization_level = SelectField('Authorization Level', choices=[
        ('treasury_officer', 'Treasury Officer'),
        ('board_approval', 'Board Approval'),
        ('emergency_authority', 'Emergency Authority')
    ], validators=[DataRequired()])
    
    blockchain_networks = SelectField('Target Networks', choices=[
        ('bsc_only', 'BSC Only'),
        ('polygon_only', 'Polygon Only'),
        ('multi_network', 'Multi-Network Deployment'),
        ('all_networks', 'All Available Networks')
    ], validators=[DataRequired()])
    
    backing_verification = TextAreaField('Asset Backing Verification', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Verification details must be between 100 and 2000 characters")
    ])
    
    compliance_notes = TextAreaField('Compliance Notes', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Compliance notes must be between 50 and 1000 characters")
    ])
    
    effective_date = DateTimeField('Effective Date', validators=[DataRequired()])
    
    risk_assessment = SelectField('Risk Assessment', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], validators=[DataRequired()])
    
    def validate_amount(self, field):
        """Validate NVCT amount based on operation type and current supply"""
        # This would integrate with actual supply data
        max_daily_minting = Decimal('500000000.00')  # $500M daily limit
        max_daily_burning = Decimal('100000000.00')   # $100M daily limit
        
        if self.operation_type.data == 'nvct_minting' and field.data > max_daily_minting:
            raise ValidationError(f"Daily minting limit is ${max_daily_minting:,.2f}")
        elif self.operation_type.data == 'nvct_burning' and field.data > max_daily_burning:
            raise ValidationError(f"Daily burning limit is ${max_daily_burning:,.2f}")

class AssetBackingForm(FlaskForm):
    """Form for asset backing portfolio management"""
    
    asset_name = StringField('Asset Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Asset name must be between 5 and 200 characters")
    ])
    
    asset_class = SelectField('Asset Class', choices=[
        ('us_treasury_bonds', 'US Treasury Bonds'),
        ('corporate_bonds', 'Corporate Bonds'),
        ('real_estate', 'Real Estate'),
        ('gold_reserves', 'Gold Reserves'),
        ('commodity_reserves', 'Commodity Reserves'),
        ('foreign_currency', 'Foreign Currency'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('equity_securities', 'Equity Securities'),
        ('money_market', 'Money Market Instruments'),
        ('derivatives', 'Derivatives')
    ], validators=[DataRequired()])
    
    face_value = DecimalField('Face Value ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum asset value is $1M")
    ])
    
    market_value = DecimalField('Market Value ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000.00, message="Market value must be positive")
    ])
    
    portfolio_weight = DecimalField('Portfolio Weight (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0001, max=50.0000, message="Weight must be between 0.0001% and 50%")
    ])
    
    target_weight = DecimalField('Target Weight (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0001, max=50.0000, message="Target weight must be between 0.0001% and 50%")
    ])
    
    maturity_date = DateTimeField('Maturity Date', validators=[Optional()])
    
    coupon_rate = DecimalField('Coupon Rate (%)', places=6, validators=[
        Optional(),
        NumberRange(min=0.000000, max=50.000000, message="Coupon rate must be between 0% and 50%")
    ])
    
    credit_rating = SelectField('Credit Rating', choices=[
        ('AAA', 'AAA'),
        ('AA+', 'AA+'),
        ('AA', 'AA'),
        ('AA-', 'AA-'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('BBB+', 'BBB+'),
        ('BBB', 'BBB'),
        ('BBB-', 'BBB-'),
        ('BB+', 'BB+'),
        ('BB', 'BB'),
        ('BB-', 'BB-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('CCC', 'CCC')
    ], validators=[Optional()])
    
    geographic_region = StringField('Geographic Region', validators=[
        Optional(),
        Length(max=100, message="Geographic region must be less than 100 characters")
    ])
    
    custodian = StringField('Custodian', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Custodian name must be between 5 and 200 characters")
    ])
    
    valuation_method = SelectField('Valuation Method', choices=[
        ('market', 'Mark-to-Market'),
        ('model', 'Model-Based'),
        ('cost', 'Historical Cost')
    ], validators=[DataRequired()])
    
    def validate_portfolio_weight(self, field):
        """Validate portfolio weight doesn't exceed concentration limits"""
        concentration_limits = {
            'us_treasury_bonds': 60.0,  # Maximum 60% in US Treasuries
            'corporate_bonds': 25.0,    # Maximum 25% in corporate bonds
            'real_estate': 15.0,        # Maximum 15% in real estate
            'gold_reserves': 10.0,      # Maximum 10% in gold
            'single_asset': 5.0         # Maximum 5% in any single asset
        }
        
        asset_class = self.asset_class.data
        if asset_class in concentration_limits and field.data > concentration_limits[asset_class]:
            raise ValidationError(f"Maximum allocation for {asset_class} is {concentration_limits[asset_class]}%")

class LiquidityManagementForm(FlaskForm):
    """Form for daily liquidity management operations"""
    
    position_date = DateTimeField('Position Date', validators=[DataRequired()])
    
    currency = SelectField('Currency', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar')
    ], validators=[DataRequired()])
    
    opening_balance = DecimalField('Opening Balance', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Opening balance cannot be negative")
    ])
    
    projected_inflows = DecimalField('Projected Inflows', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Inflows cannot be negative")
    ])
    
    projected_outflows = DecimalField('Projected Outflows', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Outflows cannot be negative")
    ])
    
    fed_funds_requirement = DecimalField('Fed Funds Requirement', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Fed funds requirement cannot be negative")
    ])
    
    discount_window_usage = DecimalField('Discount Window Usage', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Discount window usage cannot be negative")
    ])
    
    liquidity_strategy = SelectField('Liquidity Strategy', choices=[
        ('maintain_excess', 'Maintain Excess Liquidity'),
        ('optimize_cost', 'Optimize Cost of Funds'),
        ('stress_preparation', 'Stress Test Preparation'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('emergency_response', 'Emergency Response')
    ], validators=[DataRequired()])
    
    stress_scenario = SelectField('Stress Scenario', choices=[
        ('baseline', 'Baseline Scenario'),
        ('moderate_stress', 'Moderate Stress'),
        ('severe_stress', 'Severe Stress'),
        ('tail_risk', 'Tail Risk Event')
    ], validators=[DataRequired()])
    
    contingency_plans = TextAreaField('Contingency Plans', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Contingency plans must be between 50 and 1000 characters")
    ])

class MonetaryPolicyForm(FlaskForm):
    """Form for monetary policy operations"""
    
    operation_type = SelectField('Operation Type', choices=[
        ('open_market', 'Open Market Operations'),
        ('discount_window', 'Discount Window'),
        ('reserve_requirement', 'Reserve Requirement'),
        ('quantitative_easing', 'Quantitative Easing'),
        ('forward_guidance', 'Forward Guidance')
    ], validators=[DataRequired()])
    
    operation_direction = SelectField('Policy Direction', choices=[
        ('tightening', 'Monetary Tightening'),
        ('easing', 'Monetary Easing'),
        ('neutral', 'Policy Neutral')
    ], validators=[DataRequired()])
    
    notional_amount = DecimalField('Notional Amount ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum operation size is $1M")
    ])
    
    execution_rate = DecimalField('Execution Rate (%)', places=6, validators=[
        DataRequired(),
        NumberRange(min=0.000000, max=25.000000, message="Rate must be between 0% and 25%")
    ])
    
    maturity_date = DateTimeField('Maturity Date', validators=[Optional()])
    
    fed_facility = SelectField('Federal Reserve Facility', choices=[
        ('primary_credit', 'Primary Credit Facility'),
        ('secondary_credit', 'Secondary Credit Facility'),
        ('seasonal_credit', 'Seasonal Credit Facility'),
        ('term_auction', 'Term Auction Facility'),
        ('repo_facility', 'Repo Facility'),
        ('swap_line', 'Central Bank Swap Line')
    ], validators=[Optional()])
    
    collateral_provided = DecimalField('Collateral Provided ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Collateral cannot be negative")
    ])
    
    economic_justification = TextAreaField('Economic Justification', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Economic justification must be between 100 and 2000 characters")
    ])
    
    market_impact_assessment = TextAreaField('Market Impact Assessment', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Market impact assessment must be between 100 and 1500 characters")
    ])
    
    fomc_coordination = SelectField('FOMC Coordination', choices=[
        ('coordinated', 'Coordinated with FOMC'),
        ('emergency', 'Emergency Action'),
        ('routine', 'Routine Operation'),
        ('inter_meeting', 'Inter-Meeting Action')
    ], validators=[DataRequired()])

class AssetTransactionForm(FlaskForm):
    """Form for asset portfolio transactions"""
    
    transaction_type = SelectField('Transaction Type', choices=[
        ('buy', 'Purchase Asset'),
        ('sell', 'Sell Asset'),
        ('rebalance', 'Portfolio Rebalancing'),
        ('valuation_adjustment', 'Valuation Adjustment'),
        ('maturity_rollover', 'Maturity Rollover')
    ], validators=[DataRequired()])
    
    quantity = DecimalField('Quantity', places=8, validators=[
        DataRequired(),
        NumberRange(min=0.00000001, message="Quantity must be positive")
    ])
    
    price_per_unit = DecimalField('Price per Unit ($)', places=8, validators=[
        DataRequired(),
        NumberRange(min=0.00000001, message="Price must be positive")
    ])
    
    total_amount = DecimalField('Total Amount ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000.00, message="Minimum transaction size is $1,000")
    ])
    
    counterparty = StringField('Counterparty', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Counterparty name must be between 5 and 200 characters")
    ])
    
    execution_venue = StringField('Execution Venue', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Execution venue must be between 5 and 200 characters")
    ])
    
    settlement_date = DateTimeField('Settlement Date', validators=[DataRequired()])
    
    trade_rationale = TextAreaField('Trade Rationale', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Trade rationale must be between 50 and 1000 characters")
    ])
    
    risk_impact_analysis = TextAreaField('Risk Impact Analysis', validators=[
        DataRequired(),
        Length(min=50, max=800, message="Risk impact analysis must be between 50 and 800 characters")
    ])
    
    regulatory_approval = SelectField('Regulatory Approval Status', choices=[
        ('not_required', 'Not Required'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('conditional', 'Conditional Approval')
    ], validators=[DataRequired()])

class RiskMetricsForm(FlaskForm):
    """Form for treasury risk metrics reporting"""
    
    measurement_date = DateTimeField('Measurement Date', validators=[DataRequired()])
    
    var_confidence_level = SelectField('VaR Confidence Level', choices=[
        ('95', '95%'),
        ('99', '99%'),
        ('99.9', '99.9%')
    ], validators=[DataRequired()])
    
    var_time_horizon = SelectField('VaR Time Horizon', choices=[
        ('1_day', '1 Day'),
        ('10_day', '10 Days'),
        ('1_month', '1 Month')
    ], validators=[DataRequired()])
    
    portfolio_var = DecimalField('Portfolio VaR ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="VaR cannot be negative")
    ])
    
    credit_var = DecimalField('Credit VaR ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Credit VaR cannot be negative")
    ])
    
    liquidity_var = DecimalField('Liquidity-Adjusted VaR ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Liquidity VaR cannot be negative")
    ])
    
    stress_test_scenario = SelectField('Stress Test Scenario', choices=[
        ('2008_financial_crisis', '2008 Financial Crisis'),
        ('2020_covid_pandemic', '2020 COVID Pandemic'),
        ('1987_black_monday', '1987 Black Monday'),
        ('custom_scenario', 'Custom Scenario'),
        ('regulatory_ccar', 'Regulatory CCAR Scenario')
    ], validators=[DataRequired()])
    
    stress_test_loss = DecimalField('Stress Test Loss ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Stress test loss cannot be negative")
    ])
    
    concentration_risk_score = IntegerField('Concentration Risk Score', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message="Risk score must be between 1 and 100")
    ])
    
    liquidity_risk_score = IntegerField('Liquidity Risk Score', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message="Risk score must be between 1 and 100")
    ])
    
    operational_risk_score = IntegerField('Operational Risk Score', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message="Risk score must be between 1 and 100")
    ])
    
    risk_mitigation_actions = TextAreaField('Risk Mitigation Actions', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Risk mitigation actions must be between 100 and 2000 characters")
    ])
    
    executive_summary = TextAreaField('Executive Risk Summary', validators=[
        DataRequired(),
        Length(min=100, max=1000, message="Executive summary must be between 100 and 1000 characters")
    ])

class TreasuryApprovalForm(FlaskForm):
    """Form for treasury operation approvals"""
    
    operation_id = HiddenField('Operation ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_modification', 'Request Modification'),
        ('escalate', 'Escalate to Higher Authority')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=50, max=2000, message="Approval notes must be between 50 and 2000 characters")
    ])
    
    conditions_and_requirements = TextAreaField('Conditions and Requirements', validators=[
        Optional(),
        Length(max=1000, message="Conditions must be less than 1000 characters")
    ])
    
    risk_tolerance_assessment = SelectField('Risk Tolerance Assessment', choices=[
        ('within_tolerance', 'Within Risk Tolerance'),
        ('acceptable_risk', 'Acceptable Risk'),
        ('elevated_risk', 'Elevated Risk'),
        ('unacceptable_risk', 'Unacceptable Risk')
    ], validators=[DataRequired()])
    
    regulatory_compliance_check = SelectField('Regulatory Compliance', choices=[
        ('fully_compliant', 'Fully Compliant'),
        ('minor_issues', 'Minor Issues'),
        ('material_concerns', 'Material Concerns'),
        ('non_compliant', 'Non-Compliant')
    ], validators=[DataRequired()])
    
    board_notification_required = SelectField('Board Notification Required', choices=[
        ('no', 'No'),
        ('yes', 'Yes'),
        ('immediate', 'Immediate Notification Required')
    ], validators=[DataRequired()])
    
    effective_date = DateTimeField('Effective Date', validators=[Optional()])
    
    review_date = DateTimeField('Next Review Date', validators=[Optional()])