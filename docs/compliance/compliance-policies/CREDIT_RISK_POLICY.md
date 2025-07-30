# Credit Risk Management Policy
## NVC Banking Platform

### Document Control
- **Document ID**: CRM-POL-001
- **Version**: 1.0
- **Effective Date**: July 2025
- **Review Cycle**: Annual
- **Owner**: Chief Risk Officer
- **Approved By**: Board of Directors

---

## Table of Contents

1. [Credit Risk Framework](#credit-risk-framework)
2. [Credit Risk Appetite](#credit-risk-appetite)
3. [Credit Underwriting Standards](#credit-underwriting-standards)
4. [Portfolio Management](#portfolio-management)
5. [Credit Risk Measurement](#credit-risk-measurement)
6. [Loan Loss Provisioning](#loan-loss-provisioning)
7. [Problem Asset Management](#problem-asset-management)
8. [Regulatory Compliance](#regulatory-compliance)

---

## Credit Risk Framework

### 1. Definition and Scope

#### 1.1 Credit Risk Definition
Credit risk is the potential for loss due to the failure of a borrower or counterparty to meet their contractual obligations. This includes direct lending, investment securities, derivatives, and off-balance sheet commitments.

**Components of Credit Risk:**
- **Default Risk**: Probability of borrower default
- **Exposure Risk**: Amount at risk upon default
- **Recovery Risk**: Potential loss given default
- **Concentration Risk**: Portfolio concentration effects

#### 1.2 Credit Risk Categories
**Consumer Credit:**
- Residential mortgages
- Home equity lines of credit
- Credit cards and personal loans
- Auto loans and consumer installment

**Commercial Credit:**
- Commercial real estate loans
- Commercial and industrial loans
- Equipment financing
- Small business lending

**Financial Institution Credit:**
- Interbank lending
- Correspondent banking
- Trading counterparty exposure
- Investment securities

```python
# Credit Risk Classification System
class CreditRiskClassifier:
    def classify_exposure(self, loan):
        risk_categories = {
            'consumer': {
                'mortgage': self.assess_mortgage_risk(loan),
                'credit_card': self.assess_card_risk(loan),
                'auto_loan': self.assess_auto_risk(loan),
                'personal_loan': self.assess_personal_risk(loan)
            },
            'commercial': {
                'cre': self.assess_cre_risk(loan),
                'ci': self.assess_ci_risk(loan),
                'equipment': self.assess_equipment_risk(loan),
                'sba': self.assess_sba_risk(loan)
            }
        }
        
        return self.determine_risk_rating(loan, risk_categories)
```

---

## Credit Risk Appetite

### 1. Risk Appetite Framework

#### 1.1 Quantitative Limits
**Portfolio Concentration Limits:**
- Single borrower limit: 15% of capital
- Industry concentration: 25% of total loans
- Geographic concentration: 40% in primary market
- Commercial real estate: 300% of capital

**Credit Quality Targets:**
- Pass-rated loans: Minimum 95% of portfolio
- Special mention: Maximum 3% of portfolio
- Substandard: Maximum 1.5% of portfolio
- Net charge-off ratio: Maximum 0.75% annually

#### 1.2 Qualitative Standards
- Maintain conservative underwriting standards
- Diversify portfolio across products and geographies
- Focus on relationship-based lending
- Avoid speculative or high-risk lending

```python
# Credit Risk Appetite Monitoring
class CreditRiskAppetite:
    def monitor_appetite_compliance(self):
        current_metrics = {
            'single_borrower_concentration': self.calculate_single_borrower_limits(),
            'industry_concentration': self.assess_industry_concentration(),
            'geographic_concentration': self.measure_geographic_risk(),
            'credit_quality_distribution': self.analyze_credit_ratings(),
            'charge_off_trends': self.track_charge_offs()
        }
        
        return self.assess_appetite_compliance(current_metrics)
```

### 2. Credit Limits and Authorities

#### 2.1 Lending Authorities
**Individual Limits:**
- Loan Officers: Up to $500K
- Senior Loan Officers: Up to $1M
- Regional Managers: Up to $2.5M
- Chief Credit Officer: Up to $5M
- Loan Committee: Up to $10M
- Board of Directors: Above $10M

#### 2.2 Delegated Authority Framework
- Experience and training requirements
- Performance and risk management criteria
- Regular authority reviews and adjustments
- Exception reporting and approval processes

---

## Credit Underwriting Standards

### 1. Consumer Lending Standards

#### 1.1 Mortgage Underwriting
**Borrower Qualification:**
- Debt-to-income ratio: Maximum 43%
- Credit score: Minimum 620 (conventional)
- Employment history: 2 years stable employment
- Down payment: Minimum 5% for owner-occupied

**Property Requirements:**
- Professional appraisal required
- Property inspection completion
- Title insurance and flood insurance
- Loan-to-value limits by property type

```python
# Mortgage Underwriting Engine
class MortgageUnderwriter:
    def evaluate_mortgage_application(self, application):
        underwriting_factors = {
            'credit_score': self.evaluate_credit_score(application.credit_score),
            'debt_to_income': self.calculate_dti_ratio(application),
            'employment_history': self.verify_employment(application),
            'down_payment': self.validate_down_payment(application),
            'property_value': self.assess_property_value(application),
            'cash_reserves': self.verify_reserves(application)
        }
        
        return self.make_underwriting_decision(underwriting_factors)
```

#### 1.2 Consumer Loan Standards
**Credit Card Underwriting:**
- Minimum credit score: 650
- Verified income requirements
- Debt-to-income considerations
- Credit line assignment methodology

**Auto Loan Standards:**
- Loan-to-value limits by vehicle age
- Credit score and income verification
- Payment-to-income ratio limits
- Gap insurance requirements

### 2. Commercial Lending Standards

#### 2.1 Commercial Real Estate
**Property Analysis:**
- Professional appraisal requirements
- Market analysis and absorption studies
- Environmental assessments
- Property condition evaluations

**Borrower Analysis:**
- Debt service coverage ratio: Minimum 1.25x
- Loan-to-value ratio: Maximum 80%
- Borrower liquidity and net worth
- Property management experience

#### 2.2 Commercial and Industrial Lending
**Financial Analysis:**
- Global cash flow analysis
- Financial statement quality assessment
- Industry and competitive position
- Management evaluation

**Collateral and Structure:**
- Collateral valuation and monitoring
- Personal guarantee requirements
- Loan covenant structure
- Repayment source analysis

```python
# Commercial Loan Underwriting
class CommercialUnderwriter:
    def evaluate_commercial_loan(self, application):
        analysis_components = {
            'financial_analysis': self.analyze_financial_statements(application),
            'cash_flow_analysis': self.project_cash_flows(application),
            'collateral_analysis': self.evaluate_collateral(application),
            'industry_analysis': self.assess_industry_risk(application),
            'management_assessment': self.evaluate_management(application)
        }
        
        return self.make_credit_decision(analysis_components)
```

---

## Portfolio Management

### 1. Portfolio Monitoring

#### 1.1 Portfolio Composition Analysis
**Asset Quality Metrics:**
- Risk rating distribution
- Delinquency and default rates
- Net charge-off ratios
- Provision coverage ratios

**Concentration Analysis:**
- Geographic concentration
- Industry sector concentration
- Product type concentration
- Large borrower concentration

#### 1.2 Performance Monitoring
```python
# Portfolio Performance Monitor
class PortfolioMonitor:
    def analyze_portfolio_performance(self):
        performance_metrics = {
            'credit_quality_trends': self.track_rating_migrations(),
            'delinquency_analysis': self.monitor_delinquency_rates(),
            'charge_off_analysis': self.analyze_charge_off_trends(),
            'yield_analysis': self.calculate_risk_adjusted_returns(),
            'concentration_analysis': self.assess_portfolio_concentrations()
        }
        
        return self.generate_portfolio_dashboard(performance_metrics)
```

### 2. Portfolio Stress Testing

#### 2.1 Stress Test Scenarios
**Economic Scenarios:**
- Baseline economic forecast
- Adverse economic conditions
- Severely adverse scenario
- Historical stress replication

**Portfolio-Specific Stress:**
- Interest rate shock scenarios
- Real estate price decline
- Unemployment rate increases
- Industry-specific stress events

#### 2.2 Loss Estimation Models
- Probability of default models
- Loss given default estimation
- Exposure at default calculation
- Economic capital requirements

---

## Credit Risk Measurement

### 1. Risk Rating Systems

#### 1.1 Internal Risk Rating Structure
**Pass Grades (1-6):**
1. Exceptional: Minimal credit risk
2. Strong: Low credit risk
3. Satisfactory: Acceptable credit risk
4. Acceptable: Average credit risk
5. Watch: Elevated credit risk
6. Special Mention: Potential weakness

**Criticized Grades (7-9):**
7. Substandard: Well-defined weakness
8. Doubtful: Collection in full questionable
9. Loss: Uncollectible or of little value

```python
# Credit Risk Rating System
class CreditRatingSystem:
    def assign_risk_rating(self, borrower):
        rating_factors = {
            'financial_strength': self.assess_financial_metrics(borrower),
            'cash_flow_adequacy': self.analyze_cash_flow(borrower),
            'management_quality': self.evaluate_management(borrower),
            'market_position': self.assess_competitive_position(borrower),
            'industry_outlook': self.analyze_industry_trends(borrower)
        }
        
        return self.calculate_composite_rating(rating_factors)
```

#### 1.2 Rating Validation and Calibration
- Annual rating system validation
- Default rate backtesting
- Rating migration analysis
- Model performance assessment

### 2. Credit Risk Models

#### 2.1 Probability of Default Models
**Consumer Models:**
- Credit score-based models
- Behavioral scoring models
- Application scoring models
- Collection scoring models

**Commercial Models:**
- Financial ratio models
- Cash flow models
- Industry-specific models
- Hybrid qualitative/quantitative models

#### 2.2 Loss Given Default Models
- Collateral-based recovery models
- Workout process modeling
- Recovery time estimation
- Economic cycle adjustments

---

## Loan Loss Provisioning

### 1. CECL Implementation

#### 1.1 Current Expected Credit Loss Model
**Key Components:**
- Lifetime expected losses
- Forward-looking information
- Reasonable and supportable forecasts
- Reversion to historical loss rates

```python
# CECL Calculation Engine
class CECLCalculator:
    def calculate_cecl_provision(self, loan_portfolio):
        cecl_components = {
            'pd_models': self.calculate_probability_of_default(),
            'lgd_models': self.estimate_loss_given_default(),
            'ead_models': self.project_exposure_at_default(),
            'economic_forecasts': self.incorporate_forward_looking_info(),
            'qualitative_adjustments': self.apply_qualitative_factors()
        }
        
        return self.compute_expected_credit_losses(cecl_components)
```

#### 1.2 Model Development and Validation
- Segmentation and pooling analysis
- Historical loss analysis
- Economic scenario development
- Model validation and backtesting

### 2. Allowance for Credit Losses

#### 2.1 ACL Methodology
**Quantitative Analysis:**
- Statistical loss models
- Migration analysis
- Vintage analysis
- Roll-rate analysis

**Qualitative Factors:**
- Economic environment changes
- Portfolio composition changes
- Underwriting standard changes
- External factors assessment

#### 2.2 ACL Governance
- Monthly ACL calculation
- Quarterly validation and review
- Annual model validation
- Independent model validation

---

## Problem Asset Management

### 1. Early Warning Systems

#### 1.1 Risk Identification
**Financial Indicators:**
- Declining financial performance
- Covenant violations
- Rating downgrades
- Collateral deterioration

**Behavioral Indicators:**
- Payment irregularities
- Communication problems
- Management changes
- Legal issues

```python
# Early Warning System
class EarlyWarningSystem:
    def monitor_portfolio_risks(self):
        risk_indicators = {
            'financial_deterioration': self.monitor_financial_metrics(),
            'payment_behavior': self.track_payment_patterns(),
            'external_factors': self.monitor_external_risks(),
            'covenant_compliance': self.check_covenant_status(),
            'collateral_monitoring': self.assess_collateral_values()
        }
        
        return self.generate_watch_list(risk_indicators)
```

#### 1.2 Watch List Management
- Quarterly watch list review
- Risk mitigation planning
- Enhanced monitoring procedures
- Workout planning preparation

### 2. Workout and Recovery

#### 2.1 Workout Strategies
**Restructuring Options:**
- Payment modification
- Rate reduction
- Term extension
- Principal forgiveness

**Liquidation Options:**
- Voluntary liquidation
- Foreclosure proceedings
- Deed in lieu
- Short sale approval

#### 2.2 Recovery Maximization
- Asset valuation and marketing
- Legal action coordination
- Collection agency management
- Recovery tracking and reporting

---

## Regulatory Compliance

### 1. Regulatory Requirements

#### 1.1 Capital Adequacy
**Basel III Requirements:**
- Common Equity Tier 1 ratio
- Tier 1 capital ratio
- Total capital ratio
- Leverage ratio

**Stress Testing:**
- Dodd-Frank stress testing
- CCAR participation
- Internal stress testing
- Scenario design and modeling

#### 1.2 Credit Risk Reporting
**Call Report Requirements:**
- Past due and nonaccrual loans
- Charge-offs and recoveries
- Allowance for credit losses
- Credit concentrations

```python
# Regulatory Reporting System
class RegulatoryReporter:
    def generate_credit_risk_reports(self):
        regulatory_reports = {
            'call_report_schedule_ri': self.prepare_income_statement(),
            'call_report_schedule_rc': self.prepare_balance_sheet(),
            'call_report_schedule_rcn': self.prepare_past_due_report(),
            'stress_test_submission': self.prepare_stress_test_results()
        }
        
        return self.validate_and_submit_reports(regulatory_reports)
```

### 2. Compliance Monitoring

#### 2.1 Regulatory Limits
- Legal lending limits
- Insider lending restrictions
- Related party transactions
- Country exposure limits

#### 2.2 Examination Preparedness
- Regulatory examination preparation
- Documentation and evidence
- Management response coordination
- Corrective action implementation

---

## Training and Competency

### 1. Credit Training Program

#### 1.1 Role-Based Training
**Credit Officers:**
- Credit analysis fundamentals
- Industry-specific training
- Regulatory requirements
- Documentation standards

**Credit Administration:**
- Loan processing procedures
- Compliance requirements
- System operations
- Customer service

**Senior Management:**
- Portfolio management
- Risk appetite setting
- Strategic planning
- Regulatory relations

#### 1.2 Continuous Education
- Annual training requirements
- Regulatory update sessions
- Industry best practices
- Professional certification

### 2. Performance Management

#### 2.1 Credit Performance Metrics
- Loan quality indicators
- Decision accuracy tracking
- Customer satisfaction scores
- Regulatory compliance ratings

#### 2.2 Incentive Alignment
- Risk-adjusted performance metrics
- Long-term incentive structures
- Quality over quantity emphasis
- Compliance requirements integration

---

## Conclusion

This Credit Risk Management Policy establishes comprehensive framework for prudent credit risk management while supporting business growth objectives. Effective implementation ensures sound credit decisions and portfolio performance in accordance with regulatory requirements and banking best practices.

**Document Approval:**

- **Chief Risk Officer**: [Signature Required]
- **Chief Credit Officer**: [Signature Required]
- **Chief Financial Officer**: [Signature Required]
- **Chief Executive Officer**: [Signature Required]

**Next Review Date**: July 2026

---

*This document contains confidential and proprietary information. Distribution is restricted to authorized personnel only.*