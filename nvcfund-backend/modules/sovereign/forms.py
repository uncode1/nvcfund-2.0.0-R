"""
Sovereign Banking Forms
Enterprise-grade forms for central banking operations and privileged sovereign management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class SovereignDebtIssuanceForm(FlaskForm):
    """Form for sovereign debt issuance operations"""
    
    instrument_type = SelectField('Debt Instrument Type', choices=[
        ('treasury_bill', 'Treasury Bill'),
        ('treasury_note', 'Treasury Note'),
        ('treasury_bond', 'Treasury Bond'),
        ('treasury_strip', 'Treasury STRIP'),
        ('inflation_protected', 'Treasury Inflation-Protected Securities (TIPS)'),
        ('foreign_currency_bond', 'Foreign Currency Bond'),
        ('floating_rate_note', 'Floating Rate Note'),
        ('zero_coupon_bond', 'Zero Coupon Bond')
    ], validators=[DataRequired()])
    
    face_value = DecimalField('Face Value ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, max=100000000000.00, message="Face value must be between $1M and $100B")
    ])
    
    coupon_rate = DecimalField('Coupon Rate (%)', places=6, validators=[
        Optional(),
        NumberRange(min=0.000000, max=15.000000, message="Coupon rate must be between 0% and 15%")
    ])
    
    maturity_date = DateTimeField('Maturity Date', validators=[DataRequired()])
    
    issue_date = DateTimeField('Issue Date', validators=[DataRequired()])
    
    auction_type = SelectField('Auction Type', choices=[
        ('competitive_bidding', 'Competitive Bidding'),
        ('non_competitive_bidding', 'Non-Competitive Bidding'),
        ('dutch_auction', 'Dutch Auction'),
        ('uniform_price_auction', 'Uniform Price Auction'),
        ('private_placement', 'Private Placement')
    ], validators=[DataRequired()])
    
    minimum_bid_amount = DecimalField('Minimum Bid Amount ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000.00, message="Minimum bid must be at least $1,000")
    ])
    
    credit_rating_target = SelectField('Target Credit Rating', choices=[
        ('AAA', 'AAA'),
        ('AA+', 'AA+'),
        ('AA', 'AA'),
        ('AA-', 'AA-'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-')
    ], validators=[DataRequired()])
    
    use_of_proceeds = SelectField('Use of Proceeds', choices=[
        ('general_government', 'General Government Operations'),
        ('infrastructure', 'Infrastructure Investment'),
        ('debt_refinancing', 'Debt Refinancing'),
        ('emergency_response', 'Emergency Response'),
        ('economic_stimulus', 'Economic Stimulus'),
        ('reserve_building', 'Reserve Building')
    ], validators=[DataRequired()])
    
    issuance_rationale = TextAreaField('Issuance Rationale', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Issuance rationale must be between 100 and 2000 characters")
    ])
    
    market_conditions_assessment = TextAreaField('Market Conditions Assessment', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Market assessment must be between 100 and 1500 characters")
    ])
    
    investor_demand_analysis = TextAreaField('Investor Demand Analysis', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Demand analysis must be between 100 and 1500 characters")
    ])
    
    def validate_maturity_date(self, field):
        """Validate maturity date based on instrument type"""
        issue_date = self.issue_date.data or datetime.utcnow()
        days_to_maturity = (field.data - issue_date).days
        
        instrument_limits = {
            'treasury_bill': 365,      # Max 1 year
            'treasury_note': 3653,     # Max 10 years  
            'treasury_bond': 10958     # Max 30 years
        }
        
        instrument_type = self.instrument_type.data
        if instrument_type in instrument_limits:
            max_days = instrument_limits[instrument_type]
            if days_to_maturity > max_days:
                max_years = max_days / 365
                raise ValidationError(f"{instrument_type.replace('_', ' ').title()} cannot exceed {max_years} years maturity")

class MonetaryPolicyDecisionForm(FlaskForm):
    """Form for central bank monetary policy decisions"""
    
    meeting_type = SelectField('Meeting Type', choices=[
        ('regular_fomc', 'Regular FOMC Meeting'),
        ('emergency_meeting', 'Emergency Meeting'),
        ('interim_decision', 'Interim Decision'),
        ('coordinated_action', 'Coordinated Central Bank Action')
    ], validators=[DataRequired()])
    
    policy_rate = DecimalField('Policy Rate (%)', places=6, validators=[
        DataRequired(),
        NumberRange(min=0.000000, max=25.000000, message="Policy rate must be between 0% and 25%")
    ])
    
    policy_rate_change = DecimalField('Rate Change (basis points)', places=2, validators=[
        DataRequired(),
        NumberRange(min=-1000.00, max=1000.00, message="Rate change must be between -1000 and +1000 basis points")
    ])
    
    policy_stance = SelectField('Policy Stance', choices=[
        ('hawkish', 'Hawkish (Anti-Inflation)'),
        ('dovish', 'Dovish (Pro-Growth)'),
        ('neutral', 'Neutral'),
        ('data_dependent', 'Data Dependent')
    ], validators=[DataRequired()])
    
    inflation_outlook = DecimalField('Inflation Outlook (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=-5.0000, max=15.0000, message="Inflation outlook must be between -5% and 15%")
    ])
    
    growth_outlook = DecimalField('GDP Growth Outlook (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=-10.0000, max=10.0000, message="Growth outlook must be between -10% and 10%")
    ])
    
    unemployment_outlook = DecimalField('Unemployment Outlook (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=25.0000, message="Unemployment outlook must be between 0% and 25%")
    ])
    
    quantitative_easing_amount = DecimalField('Quantitative Easing Amount ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="QE amount cannot be negative")
    ])
    
    forward_guidance = TextAreaField('Forward Guidance Statement', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Forward guidance must be between 100 and 2000 characters")
    ])
    
    policy_statement = TextAreaField('Official Policy Statement', validators=[
        DataRequired(),
        Length(min=200, max=3000, message="Policy statement must be between 200 and 3000 characters")
    ])
    
    economic_justification = TextAreaField('Economic Justification', validators=[
        DataRequired(),
        Length(min=150, max=2000, message="Economic justification must be between 150 and 2000 characters")
    ])
    
    market_impact_assessment = TextAreaField('Expected Market Impact', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Market impact assessment must be between 100 and 1500 characters")
    ])
    
    international_coordination = SelectField('International Coordination', choices=[
        ('unilateral', 'Unilateral Decision'),
        ('g7_coordinated', 'G7 Coordinated'),
        ('g20_coordinated', 'G20 Coordinated'),
        ('bilateral_coordination', 'Bilateral Coordination'),
        ('emergency_coordination', 'Emergency Coordination')
    ], validators=[DataRequired()])

class BankingSupervisionForm(FlaskForm):
    """Form for banking supervision and regulatory oversight"""
    
    bank_name = StringField('Bank Name', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Bank name must be between 5 and 200 characters")
    ])
    
    bank_id = StringField('Bank Charter Number', validators=[
        DataRequired(),
        Length(min=5, max=50, message="Bank ID must be between 5 and 50 characters")
    ])
    
    bank_type = SelectField('Bank Type', choices=[
        ('commercial_bank', 'Commercial Bank'),
        ('savings_bank', 'Savings Bank'),
        ('credit_union', 'Credit Union'),
        ('investment_bank', 'Investment Bank'),
        ('community_bank', 'Community Bank'),
        ('foreign_branch', 'Foreign Bank Branch')
    ], validators=[DataRequired()])
    
    examination_type = SelectField('Examination Type', choices=[
        ('full_scope', 'Full Scope Examination'),
        ('targeted_examination', 'Targeted Examination'),
        ('follow_up_examination', 'Follow-up Examination'),
        ('special_examination', 'Special Examination'),
        ('enforcement_examination', 'Enforcement Examination')
    ], validators=[DataRequired()])
    
    # CAMELS Ratings (1-5 scale, 1 = strongest)
    capital_adequacy = SelectField('Capital Adequacy Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    asset_quality = SelectField('Asset Quality Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    management = SelectField('Management Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    earnings = SelectField('Earnings Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    liquidity = SelectField('Liquidity Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    sensitivity_to_market_risk = SelectField('Sensitivity to Market Risk Rating', choices=[
        ('1', '1 - Strong'),
        ('2', '2 - Satisfactory'),
        ('3', '3 - Fair'),
        ('4', '4 - Marginal'),
        ('5', '5 - Unsatisfactory')
    ], validators=[DataRequired()])
    
    # Financial Metrics
    tier1_capital_ratio = DecimalField('Tier 1 Capital Ratio (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=50.0000, message="Tier 1 ratio must be between 0% and 50%")
    ])
    
    total_capital_ratio = DecimalField('Total Capital Ratio (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=50.0000, message="Total capital ratio must be between 0% and 50%")
    ])
    
    leverage_ratio = DecimalField('Leverage Ratio (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=50.0000, message="Leverage ratio must be between 0% and 50%")
    ])
    
    npl_ratio = DecimalField('Non-Performing Loans Ratio (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=0.0000, max=100.0000, message="NPL ratio must be between 0% and 100%")
    ])
    
    return_on_assets = DecimalField('Return on Assets (%)', places=6, validators=[
        Optional(),
        NumberRange(min=-50.000000, max=50.000000, message="ROA must be between -50% and 50%")
    ])
    
    return_on_equity = DecimalField('Return on Equity (%)', places=6, validators=[
        Optional(),
        NumberRange(min=-100.000000, max=100.000000, message="ROE must be between -100% and 100%")
    ])
    
    examination_findings = TextAreaField('Examination Findings', validators=[
        DataRequired(),
        Length(min=100, max=5000, message="Examination findings must be between 100 and 5000 characters")
    ])
    
    corrective_measures_required = TextAreaField('Required Corrective Measures', validators=[
        Optional(),
        Length(max=3000, message="Corrective measures must be less than 3000 characters")
    ])
    
    supervisory_concerns = TextAreaField('Supervisory Concerns', validators=[
        Optional(),
        Length(max=2000, message="Supervisory concerns must be less than 2000 characters")
    ])
    
    next_examination_date = DateTimeField('Next Examination Date', validators=[Optional()])

class ForeignExchangeInterventionForm(FlaskForm):
    """Form for foreign exchange operations and interventions"""
    
    operation_type = SelectField('Operation Type', choices=[
        ('market_intervention', 'Market Intervention'),
        ('reserve_management', 'Reserve Management'),
        ('commercial_transaction', 'Commercial Transaction'),
        ('coordinated_intervention', 'Coordinated Intervention')
    ], validators=[DataRequired()])
    
    currency_pair = SelectField('Currency Pair', choices=[
        ('EURUSD', 'EUR/USD'),
        ('GBPUSD', 'GBP/USD'),
        ('USDJPY', 'USD/JPY'),
        ('USDCHF', 'USD/CHF'),
        ('USDCAD', 'USD/CAD'),
        ('AUDUSD', 'AUD/USD'),
        ('NZDUSD', 'NZD/USD'),
        ('USDCNY', 'USD/CNY')
    ], validators=[DataRequired()])
    
    operation_direction = SelectField('Operation Direction', choices=[
        ('buy_domestic', 'Buy Domestic Currency'),
        ('sell_domestic', 'Sell Domestic Currency'),
        ('neutral', 'Neutral Operation')
    ], validators=[DataRequired()])
    
    notional_amount = DecimalField('Notional Amount ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum operation size is $1M")
    ])
    
    target_exchange_rate = DecimalField('Target Exchange Rate', places=8, validators=[
        Optional(),
        NumberRange(min=0.00000001, message="Exchange rate must be positive")
    ])
    
    intervention_objective = SelectField('Intervention Objective', choices=[
        ('reduce_volatility', 'Reduce Exchange Rate Volatility'),
        ('counter_disorderly_markets', 'Counter Disorderly Market Conditions'),
        ('support_monetary_policy', 'Support Monetary Policy'),
        ('maintain_competitiveness', 'Maintain Export Competitiveness'),
        ('build_reserves', 'Build Foreign Exchange Reserves'),
        ('emergency_response', 'Emergency Market Response')
    ], validators=[DataRequired()])
    
    execution_method = SelectField('Execution Method', choices=[
        ('direct_intervention', 'Direct Market Intervention'),
        ('through_dealers', 'Through Primary Dealers'),
        ('auction_mechanism', 'Auction Mechanism'),
        ('gradual_execution', 'Gradual Market Execution')
    ], validators=[DataRequired()])
    
    market_conditions_before = TextAreaField('Market Conditions Before Intervention', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Market conditions description must be between 100 and 1500 characters")
    ])
    
    intervention_rationale = TextAreaField('Intervention Rationale', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Intervention rationale must be between 100 and 2000 characters")
    ])
    
    coordination_level = SelectField('Coordination Level', choices=[
        ('unilateral', 'Unilateral Action'),
        ('bilateral', 'Bilateral Coordination'),
        ('g7_coordinated', 'G7 Coordinated'),
        ('g20_coordinated', 'G20 Coordinated'),
        ('imf_coordinated', 'IMF Coordinated')
    ], validators=[DataRequired()])
    
    expected_market_impact = TextAreaField('Expected Market Impact', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Expected market impact must be between 100 and 1500 characters")
    ])
    
    settlement_date = DateTimeField('Settlement Date', validators=[DataRequired()])

class InternationalReservesForm(FlaskForm):
    """Form for international reserves management"""
    
    position_date = DateTimeField('Position Date', validators=[DataRequired()])
    
    usd_reserves = DecimalField('USD Reserves ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="USD reserves cannot be negative")
    ])
    
    eur_reserves = DecimalField('EUR Reserves ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="EUR reserves cannot be negative")
    ])
    
    jpy_reserves = DecimalField('JPY Reserves ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="JPY reserves cannot be negative")
    ])
    
    gbp_reserves = DecimalField('GBP Reserves ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="GBP reserves cannot be negative")
    ])
    
    gold_ounces = DecimalField('Gold Holdings (Troy Ounces)', places=6, validators=[
        Optional(),
        NumberRange(min=0.000000, message="Gold holdings cannot be negative")
    ])
    
    gold_market_value = DecimalField('Gold Market Value ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Gold market value cannot be negative")
    ])
    
    sdr_holdings = DecimalField('SDR Holdings ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="SDR holdings cannot be negative")
    ])
    
    investment_allocation_strategy = SelectField('Investment Allocation Strategy', choices=[
        ('conservative', 'Conservative (Safety Focus)'),
        ('balanced', 'Balanced (Safety & Return)'),
        ('return_oriented', 'Return Oriented'),
        ('liquidity_focused', 'Liquidity Focused'),
        ('duration_matched', 'Duration Matched')
    ], validators=[DataRequired()])
    
    currency_diversification_target = TextAreaField('Currency Diversification Target', validators=[
        DataRequired(),
        Length(min=100, max=1000, message="Diversification target must be between 100 and 1000 characters")
    ])
    
    risk_management_strategy = TextAreaField('Risk Management Strategy', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Risk management strategy must be between 100 and 1500 characters")
    ])
    
    performance_benchmark = SelectField('Performance Benchmark', choices=[
        ('government_bonds', 'Government Bonds Index'),
        ('money_market', 'Money Market Index'),
        ('custom_benchmark', 'Custom Benchmark'),
        ('peer_central_banks', 'Peer Central Banks')
    ], validators=[DataRequired()])
    
    liquidity_requirements = TextAreaField('Liquidity Requirements', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Liquidity requirements must be between 50 and 1000 characters")
    ])

class SovereignApprovalForm(FlaskForm):
    """Form for sovereign operation approvals"""
    
    operation_id = HiddenField('Operation ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_modification', 'Request Modification'),
        ('escalate_to_parliament', 'Escalate to Parliament'),
        ('escalate_to_cabinet', 'Escalate to Cabinet')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Approval notes must be between 100 and 3000 characters")
    ])
    
    constitutional_compliance = SelectField('Constitutional Compliance', choices=[
        ('fully_compliant', 'Fully Compliant'),
        ('requires_review', 'Requires Legal Review'),
        ('constitutional_concern', 'Constitutional Concern'),
        ('requires_amendment', 'Requires Amendment Process')
    ], validators=[DataRequired()])
    
    fiscal_impact_assessment = TextAreaField('Fiscal Impact Assessment', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Fiscal impact assessment must be between 100 and 2000 characters")
    ])
    
    monetary_policy_consistency = SelectField('Monetary Policy Consistency', choices=[
        ('fully_consistent', 'Fully Consistent'),
        ('generally_consistent', 'Generally Consistent'),
        ('requires_coordination', 'Requires Coordination'),
        ('potential_conflict', 'Potential Conflict')
    ], validators=[DataRequired()])
    
    international_obligations = SelectField('International Obligations Compliance', choices=[
        ('fully_compliant', 'Fully Compliant'),
        ('requires_notification', 'Requires International Notification'),
        ('requires_consultation', 'Requires International Consultation'),
        ('potential_violation', 'Potential Treaty Violation')
    ], validators=[DataRequired()])
    
    parliamentary_notification = SelectField('Parliamentary Notification Required', choices=[
        ('no', 'No'),
        ('yes_routine', 'Yes - Routine Notification'),
        ('yes_immediate', 'Yes - Immediate Notification'),
        ('yes_approval_required', 'Yes - Parliamentary Approval Required')
    ], validators=[DataRequired()])
    
    public_disclosure_requirements = SelectField('Public Disclosure Requirements', choices=[
        ('no_disclosure', 'No Public Disclosure'),
        ('summary_disclosure', 'Summary Disclosure'),
        ('full_disclosure', 'Full Public Disclosure'),
        ('delayed_disclosure', 'Delayed Disclosure')
    ], validators=[DataRequired()])
    
    effective_date = DateTimeField('Effective Date', validators=[Optional()])
    
    review_date = DateTimeField('Next Review Date', validators=[Optional()])