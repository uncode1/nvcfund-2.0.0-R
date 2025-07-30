"""
NVCT Stablecoin Forms
Enterprise-grade forms for $30T NVCT stablecoin operations and privileged treasury management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateTimeField, SelectField, TextAreaField, HiddenField, IntegerField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List

class NVCTSupplyOperationForm(FlaskForm):
    """Form for NVCT supply operations (minting/burning)"""
    
    operation_type = SelectField('Operation Type', choices=[
        ('minting', 'NVCT Minting'),
        ('burning', 'NVCT Burning'),
        ('emergency_pause', 'Emergency Pause'),
        ('reserve_rebalancing', 'Reserve Rebalancing')
    ], validators=[DataRequired()])
    
    amount = DecimalField('NVCT Amount', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, max=1000000000000.00, message="Amount must be between $1M and $1T")
    ])
    
    target_network = SelectField('Target Blockchain Network', choices=[
        ('bsc', 'Binance Smart Chain (BSC)'),
        ('polygon', 'Polygon'),
        ('ethereum', 'Ethereum'),
        ('fantom', 'Fantom'),
        ('arbitrum', 'Arbitrum'),
        ('optimism', 'Optimism'),
        ('avalanche', 'Avalanche')
    ], validators=[DataRequired()])
    
    authorization_level = SelectField('Authorization Level', choices=[
        ('treasury_officer', 'Treasury Officer'),
        ('board_approval', 'Board Approval Required'),
        ('emergency_authority', 'Emergency Authority'),
        ('governance_vote', 'Governance Vote Required')
    ], validators=[DataRequired()])
    
    operation_reason = SelectField('Operation Reason', choices=[
        ('market_demand', 'Market Demand Response'),
        ('collateral_adjustment', 'Collateral Adjustment'),
        ('peg_stabilization', 'Price Peg Stabilization'),
        ('liquidity_management', 'Liquidity Management'),
        ('regulatory_compliance', 'Regulatory Compliance'),
        ('emergency_response', 'Emergency Response'),
        ('reserve_optimization', 'Reserve Optimization')
    ], validators=[DataRequired()])
    
    collateral_required = DecimalField('Required Collateral ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Collateral cannot be negative")
    ])
    
    collateral_sources = TextAreaField('Collateral Sources', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Collateral sources must be between 100 and 2000 characters")
    ])
    
    risk_assessment = SelectField('Risk Assessment', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], validators=[DataRequired()])
    
    market_conditions = TextAreaField('Market Conditions Analysis', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Market conditions analysis must be between 100 and 2000 characters")
    ])
    
    backing_verification = TextAreaField('Asset Backing Verification', validators=[
        DataRequired(),
        Length(min=100, max=1500, message="Backing verification must be between 100 and 1500 characters")
    ])
    
    compliance_verification = BooleanField('Regulatory Compliance Verified', validators=[DataRequired()])
    
    aml_clearance = BooleanField('AML/KYC Clearance Obtained', validators=[DataRequired()])
    
    emergency_justification = TextAreaField('Emergency Justification (if applicable)', validators=[
        Optional(),
        Length(max=1000, message="Emergency justification must be less than 1000 characters")
    ])
    
    execution_timeframe = SelectField('Execution Timeframe', choices=[
        ('immediate', 'Immediate Execution'),
        ('next_block', 'Next Block'),
        ('scheduled', 'Scheduled Execution'),
        ('market_open', 'Market Open'),
        ('governance_approval', 'After Governance Approval')
    ], validators=[DataRequired()])
    
    def validate_amount(self, field):
        """Validate amount based on operation type and limits"""
        daily_mint_limit = Decimal('500000000.00')  # $500M
        daily_burn_limit = Decimal('100000000.00')   # $100M
        
        if self.operation_type.data == 'minting' and field.data > daily_mint_limit:
            if self.authorization_level.data != 'emergency_authority':
                raise ValidationError(f"Daily minting limit is ${daily_mint_limit:,.2f} without emergency authorization")
        
        elif self.operation_type.data == 'burning' and field.data > daily_burn_limit:
            if self.authorization_level.data != 'emergency_authority':
                raise ValidationError(f"Daily burning limit is ${daily_burn_limit:,.2f} without emergency authorization")

class NVCTBridgeTransactionForm(FlaskForm):
    """Form for cross-chain bridge transactions"""
    
    source_network = SelectField('Source Network', choices=[
        ('bsc', 'Binance Smart Chain'),
        ('polygon', 'Polygon'),
        ('ethereum', 'Ethereum'),
        ('fantom', 'Fantom'),
        ('arbitrum', 'Arbitrum'),
        ('optimism', 'Optimism')
    ], validators=[DataRequired()])
    
    destination_network = SelectField('Destination Network', choices=[
        ('bsc', 'Binance Smart Chain'),
        ('polygon', 'Polygon'),
        ('ethereum', 'Ethereum'),
        ('fantom', 'Fantom'),
        ('arbitrum', 'Arbitrum'),
        ('optimism', 'Optimism')
    ], validators=[DataRequired()])
    
    amount = DecimalField('Bridge Amount (NVCT)', places=2, validators=[
        DataRequired(),
        NumberRange(min=100.00, max=100000000.00, message="Bridge amount must be between 100 and 100M NVCT")
    ])
    
    user_address_source = StringField('Source Address', validators=[
        DataRequired(),
        Length(min=42, max=42, message="Must be a valid Ethereum address (42 characters)")
    ])
    
    user_address_destination = StringField('Destination Address', validators=[
        DataRequired(),
        Length(min=42, max=42, message="Must be a valid Ethereum address (42 characters)")
    ])
    
    bridge_fee = DecimalField('Bridge Fee (NVCT)', places=8, validators=[
        Optional(),
        NumberRange(min=0.00000000, message="Bridge fee cannot be negative")
    ])
    
    priority_level = SelectField('Transaction Priority', choices=[
        ('standard', 'Standard Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent Priority'),
        ('emergency', 'Emergency Priority')
    ], validators=[DataRequired()])
    
    required_confirmations = IntegerField('Required Confirmations', validators=[
        DataRequired(),
        NumberRange(min=1, max=50, message="Confirmations must be between 1 and 50")
    ])
    
    slippage_tolerance = DecimalField('Slippage Tolerance (%)', places=4, validators=[
        Optional(),
        NumberRange(min=0.0000, max=5.0000, message="Slippage tolerance must be between 0% and 5%")
    ])
    
    bridge_justification = TextAreaField('Bridge Justification', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Bridge justification must be between 50 and 1000 characters")
    ])
    
    regulatory_clearance = BooleanField('Cross-Border Regulatory Clearance', validators=[DataRequired()])
    
    def validate_networks(self, field):
        """Validate that source and destination networks are different"""
        if self.source_network.data == self.destination_network.data:
            raise ValidationError("Source and destination networks must be different")

class NVCTGovernanceProposalForm(FlaskForm):
    """Form for NVCT governance proposals"""
    
    proposal_title = StringField('Proposal Title', validators=[
        DataRequired(),
        Length(min=10, max=200, message="Title must be between 10 and 200 characters")
    ])
    
    proposal_type = SelectField('Proposal Type', choices=[
        ('parameter_change', 'Parameter Change'),
        ('protocol_upgrade', 'Protocol Upgrade'),
        ('emergency_action', 'Emergency Action'),
        ('treasury_action', 'Treasury Action'),
        ('collateral_change', 'Collateral Requirements Change'),
        ('fee_adjustment', 'Fee Structure Adjustment'),
        ('network_addition', 'New Network Addition')
    ], validators=[DataRequired()])
    
    proposal_description = TextAreaField('Proposal Description', validators=[
        DataRequired(),
        Length(min=200, max=5000, message="Description must be between 200 and 5000 characters")
    ])
    
    target_parameter = StringField('Target Parameter (if applicable)', validators=[
        Optional(),
        Length(max=100, message="Parameter name must be less than 100 characters")
    ])
    
    current_value = StringField('Current Value', validators=[
        Optional(),
        Length(max=200, message="Current value must be less than 200 characters")
    ])
    
    proposed_value = StringField('Proposed Value', validators=[
        Optional(),
        Length(max=200, message="Proposed value must be less than 200 characters")
    ])
    
    implementation_timeline = SelectField('Implementation Timeline', choices=[
        ('immediate', 'Immediate (Emergency)'),
        ('24_hours', '24 Hours'),
        ('7_days', '7 Days'),
        ('30_days', '30 Days'),
        ('90_days', '90 Days'),
        ('custom', 'Custom Timeline')
    ], validators=[DataRequired()])
    
    voting_duration = SelectField('Voting Duration', choices=[
        ('3_days', '3 Days'),
        ('7_days', '7 Days'),
        ('14_days', '14 Days'),
        ('30_days', '30 Days')
    ], validators=[DataRequired()])
    
    minimum_quorum = DecimalField('Minimum Quorum (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=10.0000, max=80.0000, message="Quorum must be between 10% and 80%")
    ])
    
    approval_threshold = DecimalField('Approval Threshold (%)', places=4, validators=[
        DataRequired(),
        NumberRange(min=50.0000, max=90.0000, message="Approval threshold must be between 50% and 90%")
    ])
    
    proposer_stake = DecimalField('Proposer Stake (NVCT)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum proposer stake is 1M NVCT")
    ])
    
    impact_assessment = TextAreaField('Impact Assessment', validators=[
        DataRequired(),
        Length(min=200, max=3000, message="Impact assessment must be between 200 and 3000 characters")
    ])
    
    security_review_required = BooleanField('Security Review Required', default=True)
    
    technical_review_required = BooleanField('Technical Review Required', default=True)
    
    legal_review_required = BooleanField('Legal Review Required', default=False)
    
    emergency_proposal = BooleanField('Emergency Proposal')
    
    emergency_justification = TextAreaField('Emergency Justification', validators=[
        Optional(),
        Length(max=1500, message="Emergency justification must be less than 1500 characters")
    ])

class NVCTCollateralManagementForm(FlaskForm):
    """Form for NVCT collateral management operations"""
    
    operation_type = SelectField('Collateral Operation', choices=[
        ('deposit', 'Collateral Deposit'),
        ('withdrawal', 'Collateral Withdrawal'),
        ('rebalancing', 'Portfolio Rebalancing'),
        ('liquidation', 'Asset Liquidation'),
        ('acquisition', 'Asset Acquisition')
    ], validators=[DataRequired()])
    
    asset_type = SelectField('Asset Type', choices=[
        ('us_treasury_bonds', 'US Treasury Bonds'),
        ('corporate_bonds', 'Corporate Bonds'),
        ('real_estate', 'Real Estate'),
        ('gold', 'Gold Reserves'),
        ('commodities', 'Commodity Reserves'),
        ('cash_equivalents', 'Cash Equivalents'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('foreign_currency', 'Foreign Currency')
    ], validators=[DataRequired()])
    
    asset_value = DecimalField('Asset Value ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=1000000.00, message="Minimum asset value is $1M")
    ])
    
    quantity = DecimalField('Quantity/Amount', places=8, validators=[
        DataRequired(),
        NumberRange(min=0.00000001, message="Quantity must be positive")
    ])
    
    market_price = DecimalField('Current Market Price', places=8, validators=[
        DataRequired(),
        NumberRange(min=0.00000001, message="Market price must be positive")
    ])
    
    custodian = StringField('Custodian/Counterparty', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Custodian name must be between 5 and 200 characters")
    ])
    
    settlement_date = DateTimeField('Settlement Date', validators=[DataRequired()])
    
    portfolio_impact = TextAreaField('Portfolio Impact Analysis', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Portfolio impact analysis must be between 100 and 2000 characters")
    ])
    
    backing_ratio_impact = DecimalField('Backing Ratio Impact (%)', places=4, validators=[
        Optional(),
        NumberRange(min=-10.0000, max=10.0000, message="Backing ratio impact must be between -10% and +10%")
    ])
    
    regulatory_approval = SelectField('Regulatory Approval Status', choices=[
        ('not_required', 'Not Required'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('conditional', 'Conditional Approval')
    ], validators=[DataRequired()])
    
    due_diligence_status = SelectField('Due Diligence Status', choices=[
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('required', 'Required'),
        ('waived', 'Waived (Emergency)')
    ], validators=[DataRequired()])
    
    risk_assessment = SelectField('Risk Assessment', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk')
    ], validators=[DataRequired()])
    
    valuation_method = SelectField('Valuation Method', choices=[
        ('market_price', 'Current Market Price'),
        ('independent_appraisal', 'Independent Appraisal'),
        ('model_based', 'Model-Based Valuation'),
        ('cost_basis', 'Historical Cost Basis')
    ], validators=[DataRequired()])
    
    operational_justification = TextAreaField('Operational Justification', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Operational justification must be between 100 and 2000 characters")
    ])

class NVCTMarketDataForm(FlaskForm):
    """Form for NVCT market data updates and monitoring"""
    
    price_usd = DecimalField('NVCT Price (USD)', places=8, validators=[
        DataRequired(),
        NumberRange(min=0.80000000, max=1.20000000, message="Price must be between $0.80 and $1.20")
    ])
    
    volume_24h = DecimalField('24h Volume ($)', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.00, message="Volume cannot be negative")
    ])
    
    market_cap = DecimalField('Market Cap ($)', places=2, validators=[
        Optional(),
        NumberRange(min=0.00, message="Market cap cannot be negative")
    ])
    
    liquidity_pools = TextAreaField('Liquidity Pool Information', validators=[
        Optional(),
        Length(max=2000, message="Liquidity pool info must be less than 2000 characters")
    ])
    
    exchange_listings = TextAreaField('Exchange Listings', validators=[
        Optional(),
        Length(max=1500, message="Exchange listings must be less than 1500 characters")
    ])
    
    trading_pairs = TextAreaField('Active Trading Pairs', validators=[
        Optional(),
        Length(max=1000, message="Trading pairs must be less than 1000 characters")
    ])
    
    volatility_24h = DecimalField('24h Volatility (%)', places=6, validators=[
        Optional(),
        NumberRange(min=0.000000, max=50.000000, message="Volatility must be between 0% and 50%")
    ])
    
    peg_deviation = DecimalField('Peg Deviation (%)', places=6, validators=[
        Optional(),
        NumberRange(min=-5.000000, max=5.000000, message="Peg deviation must be between -5% and +5%")
    ])
    
    arbitrage_opportunities = TextAreaField('Arbitrage Opportunities', validators=[
        Optional(),
        Length(max=1500, message="Arbitrage opportunities must be less than 1500 characters")
    ])
    
    market_sentiment = SelectField('Market Sentiment', choices=[
        ('very_bullish', 'Very Bullish'),
        ('bullish', 'Bullish'),
        ('neutral', 'Neutral'),
        ('bearish', 'Bearish'),
        ('very_bearish', 'Very Bearish')
    ], validators=[Optional()])
    
    data_sources = TextAreaField('Data Sources', validators=[
        DataRequired(),
        Length(min=50, max=1000, message="Data sources must be between 50 and 1000 characters")
    ])
    
    data_quality_score = IntegerField('Data Quality Score (1-100)', validators=[
        DataRequired(),
        NumberRange(min=1, max=100, message="Quality score must be between 1 and 100")
    ])
    
    alert_thresholds = TextAreaField('Price Alert Thresholds', validators=[
        Optional(),
        Length(max=500, message="Alert thresholds must be less than 500 characters")
    ])

class NVCTEmergencyActionForm(FlaskForm):
    """Form for NVCT emergency actions and interventions"""
    
    emergency_type = SelectField('Emergency Type', choices=[
        ('peg_deviation', 'Severe Peg Deviation'),
        ('smart_contract_vulnerability', 'Smart Contract Vulnerability'),
        ('bridge_failure', 'Cross-Chain Bridge Failure'),
        ('market_manipulation', 'Market Manipulation'),
        ('liquidity_crisis', 'Liquidity Crisis'),
        ('regulatory_action', 'Regulatory Action'),
        ('technical_failure', 'Technical System Failure'),
        ('security_breach', 'Security Breach')
    ], validators=[DataRequired()])
    
    severity_level = SelectField('Severity Level', choices=[
        ('low', 'Low - Minor Impact'),
        ('medium', 'Medium - Moderate Impact'),
        ('high', 'High - Significant Impact'),
        ('critical', 'Critical - System-Wide Impact')
    ], validators=[DataRequired()])
    
    emergency_description = TextAreaField('Emergency Description', validators=[
        DataRequired(),
        Length(min=200, max=5000, message="Emergency description must be between 200 and 5000 characters")
    ])
    
    immediate_actions = TextAreaField('Immediate Actions Taken', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Immediate actions must be between 100 and 3000 characters")
    ])
    
    proposed_solution = TextAreaField('Proposed Solution', validators=[
        DataRequired(),
        Length(min=200, max=4000, message="Proposed solution must be between 200 and 4000 characters")
    ])
    
    pause_protocol = BooleanField('Pause Protocol Operations')
    
    pause_duration = SelectField('Pause Duration', choices=[
        ('1_hour', '1 Hour'),
        ('6_hours', '6 Hours'),
        ('24_hours', '24 Hours'),
        ('72_hours', '72 Hours'),
        ('indefinite', 'Indefinite (Manual Resume)')
    ], validators=[Optional()])
    
    affected_networks = TextAreaField('Affected Networks', validators=[
        DataRequired(),
        Length(min=10, max=500, message="Affected networks must be between 10 and 500 characters")
    ])
    
    user_communication = TextAreaField('User Communication Plan', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Communication plan must be between 100 and 2000 characters")
    ])
    
    regulatory_notification = BooleanField('Regulatory Notification Required')
    
    external_support = TextAreaField('External Support Required', validators=[
        Optional(),
        Length(max=1000, message="External support details must be less than 1000 characters")
    ])
    
    estimated_resolution_time = SelectField('Estimated Resolution Time', choices=[
        ('1_hour', '1 Hour'),
        ('6_hours', '6 Hours'),
        ('24_hours', '24 Hours'),
        ('72_hours', '72 Hours'),
        ('1_week', '1 Week'),
        ('unknown', 'Unknown')
    ], validators=[DataRequired()])
    
    authorization_override = BooleanField('Emergency Authorization Override')
    
    post_incident_review = BooleanField('Post-Incident Review Required', default=True)

class NVCTApprovalForm(FlaskForm):
    """Form for NVCT operation approvals"""
    
    operation_id = HiddenField('Operation ID', validators=[DataRequired()])
    
    approval_action = SelectField('Approval Action', choices=[
        ('approve', 'Approve'),
        ('approve_with_conditions', 'Approve with Conditions'),
        ('reject', 'Reject'),
        ('request_modification', 'Request Modification'),
        ('escalate_to_board', 'Escalate to Board'),
        ('escalate_to_governance', 'Escalate to Governance Vote')
    ], validators=[DataRequired()])
    
    approval_notes = TextAreaField('Approval Notes', validators=[
        DataRequired(),
        Length(min=100, max=3000, message="Approval notes must be between 100 and 3000 characters")
    ])
    
    collateral_verification = SelectField('Collateral Verification', choices=[
        ('verified', 'Fully Verified'),
        ('partial', 'Partially Verified'),
        ('pending', 'Verification Pending'),
        ('insufficient', 'Insufficient Collateral')
    ], validators=[DataRequired()])
    
    risk_tolerance = SelectField('Risk Tolerance Assessment', choices=[
        ('acceptable', 'Acceptable Risk'),
        ('elevated', 'Elevated Risk - Monitoring Required'),
        ('high', 'High Risk - Additional Controls Required'),
        ('unacceptable', 'Unacceptable Risk')
    ], validators=[DataRequired()])
    
    regulatory_compliance = SelectField('Regulatory Compliance Assessment', choices=[
        ('compliant', 'Fully Compliant'),
        ('minor_issues', 'Minor Compliance Issues'),
        ('material_concerns', 'Material Compliance Concerns'),
        ('non_compliant', 'Non-Compliant')
    ], validators=[DataRequired()])
    
    market_impact_assessment = TextAreaField('Market Impact Assessment', validators=[
        DataRequired(),
        Length(min=100, max=2000, message="Market impact assessment must be between 100 and 2000 characters")
    ])
    
    conditions_and_requirements = TextAreaField('Conditions and Requirements', validators=[
        Optional(),
        Length(max=2000, message="Conditions must be less than 2000 characters")
    ])
    
    monitoring_requirements = TextAreaField('Monitoring Requirements', validators=[
        Optional(),
        Length(max=1500, message="Monitoring requirements must be less than 1500 characters")
    ])
    
    board_notification = SelectField('Board Notification', choices=[
        ('no', 'No'),
        ('summary', 'Summary Notification'),
        ('detailed', 'Detailed Report'),
        ('immediate', 'Immediate Notification')
    ], validators=[DataRequired()])
    
    governance_notification = SelectField('Governance Community Notification', choices=[
        ('no', 'No'),
        ('routine', 'Routine Update'),
        ('detailed', 'Detailed Disclosure'),
        ('vote_required', 'Governance Vote Required')
    ], validators=[DataRequired()])
    
    effective_date = DateTimeField('Effective Date', validators=[Optional()])
    
    review_date = DateTimeField('Next Review Date', validators=[Optional()])
    
    def validate_approval_action(self, field):
        """Validate approval based on compliance and risk assessments"""
        if (self.regulatory_compliance.data == 'non_compliant' and 
            field.data not in ['reject', 'escalate_to_board']):
            raise ValidationError("Non-compliant operations cannot be approved without board escalation")
        
        if (self.risk_tolerance.data == 'unacceptable' and 
            field.data == 'approve'):
            raise ValidationError("Operations with unacceptable risk cannot be approved without modification")