# Liquidity Risk Management Policy
## NVC Banking Platform

### Document Control
- **Document ID**: LRM-POL-001
- **Version**: 1.0
- **Effective Date**: July 2025
- **Review Cycle**: Annual
- **Owner**: Chief Risk Officer
- **Approved By**: Board of Directors

---

## Table of Contents

1. [Liquidity Risk Framework](#liquidity-risk-framework)
2. [Basel III Liquidity Requirements](#basel-iii-liquidity-requirements)
3. [Liquidity Risk Appetite](#liquidity-risk-appetite)
4. [Liquidity Monitoring and Measurement](#liquidity-monitoring-and-measurement)
5. [Stress Testing and Scenario Analysis](#stress-testing-and-scenario-analysis)
6. [Contingency Funding Plan](#contingency-funding-plan)
7. [Liquidity Risk Governance](#liquidity-risk-governance)

---

## Liquidity Risk Framework

### 1. Definition and Scope

#### 1.1 Liquidity Risk Definition
Liquidity risk is the risk that the bank cannot meet its financial obligations when they come due, without incurring unacceptable losses. This includes both funding liquidity risk and market liquidity risk.

**Funding Liquidity Risk:**
- Inability to fund increases in assets
- Inability to meet obligations as they come due
- Forced borrowing at disadvantageous rates

**Market Liquidity Risk:**
- Inability to easily liquidate positions
- Significant price deterioration upon liquidation
- Limited market depth for asset sales

#### 1.2 Liquidity Sources
**Primary Liquidity:**
- Cash and cash equivalents
- Central bank reserves
- High-quality liquid assets (HQLA)
- Unencumbered government securities

**Secondary Liquidity:**
- Marketable securities
- Committed credit facilities
- Federal Home Loan Bank advances
- Discount window access

```python
# Liquidity Classification System
class LiquidityClassifier:
    def classify_assets(self, asset):
        liquidity_categories = {
            'level_1_hqla': ['cash', 'central_bank_reserves', 'government_bonds'],
            'level_2a_hqla': ['agency_mbs', 'corporate_bonds_aa_minus'],
            'level_2b_hqla': ['corporate_bonds_bbb_minus', 'equity_securities'],
            'non_hqla': ['loans', 'real_estate', 'private_equity']
        }
        
        return self.determine_asset_category(asset, liquidity_categories)
```

---

## Basel III Liquidity Requirements

### 1. Liquidity Coverage Ratio (LCR)

#### 1.1 LCR Calculation
**Formula:** LCR = High-Quality Liquid Assets / Net Cash Outflows over 30 days

**Minimum Requirement:** 100%

**Components:**
- Numerator: Stock of HQLA
- Denominator: Total net cash outflows over 30-day stress period

```python
# LCR Calculator
class LCRCalculator:
    def calculate_lcr(self):
        hqla = self.calculate_hqla()
        net_outflows = self.calculate_net_outflows_30_days()
        
        lcr = hqla / net_outflows if net_outflows > 0 else float('inf')
        
        return {
            'lcr_ratio': lcr,
            'hqla_amount': hqla,
            'net_outflows': net_outflows,
            'excess_liquidity': max(0, hqla - net_outflows),
            'compliance_status': 'Compliant' if lcr >= 1.0 else 'Non-Compliant'
        }
```

#### 1.2 HQLA Categories
**Level 1 Assets (0% haircut):**
- Cash and central bank reserves
- Government bonds (0% risk weight)
- Central bank securities

**Level 2A Assets (15% haircut):**
- Government bonds (20% risk weight)
- Agency mortgage-backed securities
- Corporate bonds (AA- or higher)

**Level 2B Assets (25-50% haircut):**
- Corporate bonds (BBB- to A+)
- Residential mortgage-backed securities
- Common equity shares in major stock indices

### 2. Net Stable Funding Ratio (NSFR)

#### 2.1 NSFR Calculation
**Formula:** NSFR = Available Stable Funding / Required Stable Funding

**Minimum Requirement:** 100%

```python
# NSFR Calculator
class NSFRCalculator:
    def calculate_nsfr(self):
        asf = self.calculate_available_stable_funding()
        rsf = self.calculate_required_stable_funding()
        
        nsfr = asf / rsf if rsf > 0 else float('inf')
        
        return {
            'nsfr_ratio': nsfr,
            'available_stable_funding': asf,
            'required_stable_funding': rsf,
            'funding_gap': max(0, rsf - asf),
            'compliance_status': 'Compliant' if nsfr >= 1.0 else 'Non-Compliant'
        }
```

#### 2.2 ASF and RSF Factors
**Available Stable Funding Factors:**
- Tier 1 and Tier 2 capital: 100%
- Deposits < $250K: 95%
- Deposits > $250K: 90%
- Wholesale funding > 1 year: 100%

**Required Stable Funding Factors:**
- Cash and short-term assets: 0-5%
- Government bonds: 5%
- Corporate bonds: 15-65%
- Mortgages: 65-85%
- Other loans: 85%

---

## Liquidity Risk Appetite

### 1. Risk Appetite Framework

#### 1.1 Quantitative Limits
**Regulatory Ratios:**
- LCR minimum: 120% (above regulatory 100%)
- NSFR minimum: 110% (above regulatory 100%)
- Deposit concentration: No single depositor > 5% of total deposits

**Internal Limits:**
- Cash-to-deposits ratio: Minimum 10%
- Wholesale funding dependency: Maximum 25%
- Overnight borrowing: Maximum 5% of total assets

#### 1.2 Qualitative Standards
- Maintain access to diverse funding sources
- Avoid concentration in any single funding type
- Preserve strong relationships with funding providers
- Maintain operational capability during stress periods

```python
# Risk Appetite Monitoring
class LiquidityRiskAppetite:
    def monitor_appetite_limits(self):
        current_metrics = {
            'lcr_ratio': self.get_current_lcr(),
            'nsfr_ratio': self.get_current_nsfr(),
            'deposit_concentration': self.calculate_deposit_concentration(),
            'wholesale_dependency': self.calculate_wholesale_dependency(),
            'overnight_borrowing': self.calculate_overnight_borrowing()
        }
        
        return self.assess_appetite_compliance(current_metrics)
```

---

## Liquidity Monitoring and Measurement

### 1. Daily Monitoring

#### 1.1 Daily Liquidity Reports
**Cash Flow Monitoring:**
- Expected cash inflows and outflows
- Net liquidity position by maturity
- Available borrowing capacity
- Collateral availability

**Key Metrics:**
- LCR calculation and components
- Available liquid assets by category
- Funding concentration ratios
- Early warning indicators

#### 1.2 Intraday Liquidity Management
```python
# Intraday Liquidity Monitor
class IntradayLiquidityMonitor:
    def monitor_intraday_position(self):
        position_updates = {
            'opening_balance': self.get_opening_cash_position(),
            'expected_inflows': self.forecast_intraday_inflows(),
            'expected_outflows': self.forecast_intraday_outflows(),
            'current_position': self.get_current_cash_position(),
            'minimum_balance': self.calculate_minimum_required_balance(),
            'action_required': self.determine_required_actions()
        }
        
        return self.generate_intraday_report(position_updates)
```

### 2. Funding Analysis

#### 2.1 Funding Composition
**Deposit Analysis:**
- Demand deposits by customer type
- Time deposits by maturity and rate
- Deposit stability assessment
- Deposit concentration monitoring

**Wholesale Funding:**
- Federal funds purchased
- Repurchase agreements
- Brokered deposits
- Long-term debt

#### 2.2 Maturity Analysis
- Assets and liabilities by maturity bucket
- Gap analysis by time period
- Cumulative gap calculations
- Maturity transformation assessment

---

## Stress Testing and Scenario Analysis

### 1. Stress Testing Framework

#### 1.1 Stress Scenarios
**Idiosyncratic Stress:**
- Credit rating downgrade
- Operational loss event
- Regulatory action
- Reputational damage

**Market-wide Stress:**
- Economic recession
- Financial market disruption
- Interest rate shock
- Credit crisis

**Combined Stress:**
- Simultaneous idiosyncratic and market stress
- Prolonged stress conditions
- Multiple shock events
- Extreme tail risk scenarios

```python
# Liquidity Stress Testing
class LiquidityStressTester:
    def run_stress_scenarios(self):
        scenarios = {
            'base_case': self.run_base_case_scenario(),
            'mild_stress': self.run_mild_stress_scenario(),
            'severe_stress': self.run_severe_stress_scenario(),
            'extreme_stress': self.run_extreme_stress_scenario()
        }
        
        return self.analyze_stress_results(scenarios)
    
    def run_severe_stress_scenario(self):
        stress_assumptions = {
            'deposit_runoff_rate': 0.15,  # 15% deposit outflow
            'wholesale_funding_loss': 0.50,  # 50% wholesale funding unavailable
            'asset_haircuts': {'bonds': 0.10, 'loans': 0.20},
            'credit_line_drawdowns': 0.75  # 75% of committed facilities drawn
        }
        
        return self.calculate_stress_impact(stress_assumptions)
```

#### 1.2 Stress Testing Results
- Liquidity survival period
- Additional funding requirements
- Asset liquidation needs
- Contingency plan activation triggers

### 2. Scenario Planning

#### 2.1 Scenario Development
**Economic Scenarios:**
- Baseline economic forecast
- Adverse economic conditions
- Severely adverse conditions
- Recovery scenarios

**Institution-Specific Scenarios:**
- Business growth scenarios
- Credit loss scenarios
- Market share changes
- Product mix evolution

---

## Contingency Funding Plan

### 1. CFP Framework

#### 1.1 Plan Components
**Funding Sources:**
- Primary funding sources availability
- Secondary funding source access
- Emergency funding mechanisms
- Asset liquidation options

**Action Triggers:**
- Early warning indicators
- Escalation thresholds
- Decision points
- Communication protocols

```python
# Contingency Funding Plan
class ContingencyFundingPlan:
    def assess_funding_stress_level(self):
        stress_indicators = {
            'lcr_below_threshold': self.check_lcr_threshold(),
            'deposit_outflows': self.monitor_deposit_trends(),
            'funding_cost_increase': self.track_funding_costs(),
            'market_access_deterioration': self.assess_market_access(),
            'credit_rating_pressure': self.monitor_rating_outlook()
        }
        
        return self.determine_stress_level(stress_indicators)
    
    def activate_contingency_measures(self, stress_level):
        if stress_level == 'high':
            return self.execute_high_stress_actions()
        elif stress_level == 'severe':
            return self.execute_severe_stress_actions()
        else:
            return self.execute_normal_monitoring()
```

#### 1.2 Stress Levels and Actions
**Normal Conditions:**
- Regular monitoring and reporting
- Maintain standard operating procedures
- Monitor early warning indicators

**Elevated Stress:**
- Increase monitoring frequency
- Activate additional funding sources
- Reduce asset growth
- Enhance communication

**High Stress:**
- Daily senior management meetings
- Execute asset sales program
- Access emergency funding
- Implement cost reduction measures

**Crisis:**
- Continuous monitoring
- Asset fire sales if necessary
- Access lender of last resort
- Engage regulators and stakeholders

### 2. Funding Sources and Tools

#### 2.1 Emergency Funding
**Central Bank Facilities:**
- Discount window access
- Emergency lending facilities
- Federal Reserve programs
- International swap lines

**Market Sources:**
- Overnight funding markets
- Term funding markets
- Asset-backed financing
- Interbank markets

#### 2.2 Asset Liquidation
**Primary Liquidation Assets:**
- Government securities
- Agency bonds
- High-grade corporate bonds
- Marketable equity securities

**Secondary Liquidation Assets:**
- Loan sales and participations
- Real estate dispositions
- Non-core business units
- Investment portfolios

---

## Liquidity Risk Governance

### 1. Governance Structure

#### 1.1 Board Oversight
**Board Responsibilities:**
- Approve liquidity risk appetite
- Review and approve liquidity policy
- Oversee liquidity risk management
- Ensure adequate resources and capabilities

**Risk Committee:**
- Monitor liquidity risk exposures
- Review stress testing results
- Oversee contingency planning
- Evaluate risk management effectiveness

#### 1.2 Management Structure
```
CEO
├── Chief Risk Officer
│   ├── Liquidity Risk Manager
│   ├── Stress Testing Manager
│   └── Risk Analytics Team
├── Treasurer
│   ├── Funding Manager
│   ├── Cash Management
│   └── Investment Portfolio Manager
└── ALCO (Asset Liability Committee)
```

### 2. Risk Management Functions

#### 2.1 Asset Liability Committee (ALCO)
**Composition:**
- CEO (Chair)
- CFO
- CRO
- Treasurer
- Chief Investment Officer
- Business Line Heads

**Responsibilities:**
- Liquidity risk strategy
- Funding plan approval
- Investment guidelines
- Transfer pricing methodology

#### 2.2 Independent Risk Management
**Second Line Functions:**
- Independent liquidity risk assessment
- Model validation and oversight
- Policy compliance monitoring
- Regulatory reporting coordination

### 3. Reporting and Communication

#### 3.1 Internal Reporting
**Daily Reports:**
- Cash position and forecasts
- LCR calculation and trends
- Funding market conditions
- Early warning indicators

**Monthly Reports:**
- Comprehensive liquidity analysis
- NSFR calculation and components
- Stress testing results
- Funding strategy performance

#### 3.2 Regulatory Reporting
**LCR Reporting:**
- Daily LCR calculation (large banks)
- Monthly LCR reporting to regulators
- Quarterly detailed analysis
- Annual comprehensive assessment

**Additional Requirements:**
- Contingency funding plan updates
- Stress testing documentation
- Liquidity risk appetite statements
- Model documentation and validation

---

## Training and Competency

### 1. Training Program

#### 1.1 Role-Based Training
**Senior Management:**
- Liquidity risk strategy
- Regulatory requirements
- Crisis management
- Stakeholder communication

**Risk Management Staff:**
- Technical risk measurement
- Model development and validation
- Stress testing methodologies
- Regulatory reporting requirements

**Treasury Staff:**
- Funding market operations
- Cash management techniques
- Investment guidelines
- Relationship management

#### 1.2 Continuous Education
- Regulatory update training
- Industry best practice seminars
- Professional certification programs
- Crisis simulation exercises

### 2. Competency Assessment

#### 2.1 Knowledge Validation
- Annual competency testing
- Technical skills assessment
- Regulatory knowledge verification
- Practical scenario evaluation

#### 2.2 Performance Monitoring
- Decision quality assessment
- Risk identification effectiveness
- Communication and escalation
- Continuous improvement initiatives

---

## Conclusion

This Liquidity Risk Management Policy establishes comprehensive framework for managing liquidity risk in accordance with regulatory requirements and banking best practices. Effective implementation ensures adequate liquidity under normal and stressed conditions while supporting business objectives.

**Document Approval:**

- **Chief Risk Officer**: [Signature Required]
- **Treasurer**: [Signature Required]
- **Chief Financial Officer**: [Signature Required]
- **Chief Executive Officer**: [Signature Required]

**Next Review Date**: July 2026

---

*This document contains confidential and proprietary information. Distribution is restricted to authorized personnel only.*