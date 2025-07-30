"""
Interest Rate Management Service
Comprehensive system for setting and controlling interest rates across all banking products
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import uuid

class InterestRateManagementService:
    """
    Comprehensive Interest Rate Management System
    
    Features:
    - Central bank policy rate management
    - Product-specific rate setting
    - Rate curve management
    - Real-time rate updates
    - Historical rate tracking
    - Risk-based pricing
    - Automated rate adjustment rules
    """
    
    def __init__(self):
        self.module_name = "interest_rate_management"
        self.version = "1.0.0"
        
    def health_check(self) -> Dict[str, Any]:
        """Interest Rate Management module health check"""
        return {
            "module": self.module_name,
            "version": self.version,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "policy_rate_management": "operational",
                "lending_rate_control": "operational",
                "deposit_rate_management": "operational",
                "rate_curve_engine": "operational",
                "pricing_algorithms": "operational",
                "rate_history_tracking": "operational",
                "automated_adjustments": "operational",
                "risk_pricing": "operational"
            }
        }
    
    def get_central_bank_rates(self) -> Dict[str, Any]:
        """Get central bank policy rates and benchmarks"""
        return {
            "policy_rates": {
                "federal_funds_rate": {
                    "current_rate": 5.25,
                    "last_change": "2025-06-15",
                    "change_amount": 0.25,
                    "next_meeting": "2025-07-31",
                    "target_range": "5.00-5.50",
                    "voting_record": "8-3 for increase"
                },
                "discount_window": {
                    "primary_credit": 5.50,
                    "secondary_credit": 6.00,
                    "seasonal_credit": 5.25,
                    "last_updated": "2025-06-15"
                },
                "reserve_requirements": {
                    "net_transaction_accounts": {
                        "up_to_21_million": 0.0,
                        "21_to_182_million": 3.0,
                        "over_182_million": 10.0
                    },
                    "eurodollar_deposits": 0.0,
                    "time_deposits": 0.0
                }
            },
            "benchmark_rates": {
                "sofr": {
                    "overnight": 5.31,
                    "30_day_average": 5.28,
                    "90_day_average": 5.24,
                    "180_day_average": 5.18
                },
                "treasury_yields": {
                    "3_month": 5.35,
                    "6_month": 5.28,
                    "1_year": 5.12,
                    "2_year": 4.85,
                    "5_year": 4.45,
                    "10_year": 4.35,
                    "30_year": 4.55
                },
                "libor_legacy": {
                    "1_month_usd": 5.40,
                    "3_month_usd": 5.42,
                    "6_month_usd": 5.38,
                    "status": "phase_out_complete_2023"
                }
            },
            "international_rates": {
                "ecb_main_refinancing": 4.50,
                "boe_bank_rate": 5.25,
                "boj_policy_rate": -0.10,
                "pboc_loan_prime_rate": 3.45,
                "rbi_repo_rate": 6.50
            }
        }
    
    def get_lending_rates_structure(self) -> Dict[str, Any]:
        """Get comprehensive lending rates structure"""
        return {
            "consumer_lending": {
                "mortgage_rates": {
                    "30_year_fixed": {
                        "prime_rate": 7.25,
                        "good_credit": 7.45,
                        "fair_credit": 8.15,
                        "poor_credit": 9.85,
                        "jumbo_loans": 7.35,
                        "fha_loans": 7.15,
                        "va_loans": 6.95
                    },
                    "15_year_fixed": {
                        "prime_rate": 6.85,
                        "good_credit": 7.05,
                        "fair_credit": 7.75,
                        "poor_credit": 9.25
                    },
                    "adjustable_rate": {
                        "5_1_arm": 6.55,
                        "7_1_arm": 6.75,
                        "10_1_arm": 6.95,
                        "margin_over_index": 2.75
                    }
                },
                "personal_loans": {
                    "unsecured": {
                        "excellent_credit": 8.95,
                        "good_credit": 12.45,
                        "fair_credit": 18.75,
                        "poor_credit": 28.95
                    },
                    "secured": {
                        "auto_secured": 6.25,
                        "home_equity": 8.15,
                        "savings_secured": 3.25
                    }
                },
                "credit_cards": {
                    "prime_cards": 18.24,
                    "rewards_cards": 19.99,
                    "cash_back_cards": 20.74,
                    "balance_transfer": 15.99,
                    "secured_cards": 24.99,
                    "store_cards": 26.99
                },
                "auto_loans": {
                    "new_vehicles": {
                        "excellent_credit": 6.45,
                        "good_credit": 7.85,
                        "fair_credit": 12.25,
                        "poor_credit": 18.95
                    },
                    "used_vehicles": {
                        "excellent_credit": 7.25,
                        "good_credit": 9.15,
                        "fair_credit": 14.85,
                        "poor_credit": 21.95
                    }
                }
            },
            "commercial_lending": {
                "business_loans": {
                    "sba_loans": {
                        "7a_loans": 13.50,
                        "504_loans": 12.75,
                        "microloans": 14.25,
                        "express_loans": 14.75
                    },
                    "conventional": {
                        "term_loans": 8.95,
                        "lines_of_credit": 9.45,
                        "equipment_financing": 7.85,
                        "real_estate": 7.25
                    }
                },
                "commercial_real_estate": {
                    "owner_occupied": 7.45,
                    "investment_property": 8.15,
                    "construction_loans": 9.25,
                    "bridge_loans": 11.50,
                    "mezzanine_financing": 14.75
                },
                "working_capital": {
                    "revolving_credit": 8.75,
                    "invoice_factoring": 12.50,
                    "asset_based_lending": 9.25,
                    "merchant_cash_advance": 24.95
                }
            },
            "institutional_lending": {
                "syndicated_loans": {
                    "investment_grade": 6.85,
                    "sub_investment_grade": 9.45,
                    "leveraged_loans": 8.25
                },
                "corporate_bonds": {
                    "aaa_rated": 5.15,
                    "aa_rated": 5.45,
                    "a_rated": 5.85,
                    "bbb_rated": 6.55,
                    "bb_rated": 8.25,
                    "b_rated": 10.95
                }
            }
        }
    
    def get_deposit_rates_structure(self) -> Dict[str, Any]:
        """Get comprehensive deposit rates structure"""
        return {
            "consumer_deposits": {
                "savings_accounts": {
                    "regular_savings": {
                        "base_rate": 0.45,
                        "relationship_bonus": 0.10,
                        "high_balance_tier": 0.65,
                        "minimum_balance": 100
                    },
                    "high_yield_savings": {
                        "promotional_rate": 4.85,
                        "ongoing_rate": 4.25,
                        "minimum_balance": 10000,
                        "max_promotional_balance": 250000
                    },
                    "money_market": {
                        "base_rate": 3.85,
                        "tiered_rates": {
                            "0_10k": 3.85,
                            "10k_50k": 4.15,
                            "50k_100k": 4.35,
                            "100k_plus": 4.55
                        }
                    }
                },
                "checking_accounts": {
                    "interest_checking": {
                        "base_rate": 0.15,
                        "relationship_bonus": 0.05,
                        "direct_deposit_bonus": 0.10
                    },
                    "premium_checking": {
                        "rate": 2.25,
                        "minimum_balance": 25000,
                        "maintenance_fee_waiver": True
                    }
                },
                "certificates_of_deposit": {
                    "standard_cds": {
                        "3_month": 4.95,
                        "6_month": 5.15,
                        "1_year": 4.85,
                        "2_year": 4.45,
                        "3_year": 4.25,
                        "5_year": 4.15
                    },
                    "jumbo_cds": {
                        "minimum_deposit": 100000,
                        "3_month": 5.05,
                        "6_month": 5.25,
                        "1_year": 4.95,
                        "2_year": 4.55,
                        "3_year": 4.35,
                        "5_year": 4.25
                    },
                    "promotional_cds": {
                        "13_month_special": 5.35,
                        "25_month_special": 4.75,
                        "new_money_only": True
                    }
                }
            },
            "commercial_deposits": {
                "business_checking": {
                    "small_business": 0.25,
                    "commercial_analysis": 0.35,
                    "treasury_management": 0.45
                },
                "business_savings": {
                    "business_money_market": 3.75,
                    "business_savings": 2.85,
                    "sweep_accounts": 4.15
                },
                "time_deposits": {
                    "business_cds": {
                        "30_day": 5.25,
                        "60_day": 5.35,
                        "90_day": 5.45,
                        "180_day": 5.25,
                        "1_year": 4.95
                    }
                }
            },
            "institutional_deposits": {
                "wholesale_deposits": {
                    "institutional_money_market": 4.95,
                    "public_funds": 4.85,
                    "corporate_sweep": 5.05
                },
                "brokered_deposits": {
                    "callable_cds": 5.15,
                    "non_callable_cds": 4.95,
                    "step_up_cds": 4.75
                }
            }
        }
    
    def get_rate_setting_authority(self) -> Dict[str, Any]:
        """Get rate setting authority and approval hierarchy"""
        return {
            "authorization_levels": {
                "level_1_rates": {
                    "description": "Basic consumer rates",
                    "required_roles": ["treasury_officer", "asset_liability_manager"],
                    "products": [
                        "savings_accounts", "checking_accounts", "basic_cds",
                        "personal_loans", "auto_loans"
                    ],
                    "approval_limits": {
                        "max_rate_change": 0.50,
                        "notification_required": ["chief_risk_officer"]
                    }
                },
                "level_2_rates": {
                    "description": "Commercial and mortgage rates",
                    "required_roles": ["chief_financial_officer", "asset_liability_committee"],
                    "products": [
                        "mortgage_rates", "commercial_loans", "business_deposits",
                        "jumbo_cds", "credit_cards"
                    ],
                    "approval_limits": {
                        "max_rate_change": 1.00,
                        "board_notification": True
                    }
                },
                "level_3_rates": {
                    "description": "Institutional and policy rates",
                    "required_roles": ["board_of_directors", "monetary_policy_committee"],
                    "products": [
                        "institutional_lending", "wholesale_deposits", "syndicated_loans",
                        "prime_rate", "base_lending_rate"
                    ],
                    "approval_limits": {
                        "max_rate_change": 2.00,
                        "regulatory_filing": True
                    }
                },
                "emergency_rates": {
                    "description": "Crisis response rates",
                    "required_roles": ["ceo", "board_chairman", "federal_reserve_approval"],
                    "conditions": ["market_crisis", "liquidity_emergency", "regulatory_directive"],
                    "immediate_effect": True,
                    "post_approval_review": 24
                }
            },
            "approval_workflow": {
                "rate_proposal": {
                    "initiator": "product_managers",
                    "analysis_required": [
                        "competitive_analysis", "profitability_impact",
                        "risk_assessment", "customer_impact"
                    ],
                    "review_committee": "asset_liability_committee",
                    "final_approval": "role_dependent"
                },
                "implementation": {
                    "notice_period": {
                        "consumer_products": 30,  # days
                        "commercial_products": 15,
                        "institutional_products": 5
                    },
                    "system_updates": "real_time",
                    "communication": [
                        "customer_notifications", "staff_training",
                        "marketing_updates", "regulatory_filings"
                    ]
                }
            }
        }
    
    def get_rate_adjustment_algorithms(self) -> Dict[str, Any]:
        """Get automated rate adjustment algorithms and triggers"""
        return {
            "fed_funds_correlation": {
                "description": "Automatic adjustment based on Fed funds rate changes",
                "products_affected": [
                    "prime_rate", "variable_mortgages", "credit_cards",
                    "money_market_accounts", "business_lines_of_credit"
                ],
                "adjustment_rules": {
                    "prime_rate": "fed_funds + 3.00",
                    "variable_mortgages": "prime_rate + margin",
                    "credit_cards": "prime_rate + fixed_margin",
                    "money_market": "fed_funds + 0.25 to 1.50"
                },
                "implementation_delay": 1,  # business days
                "manual_override": True
            },
            "competitive_pricing": {
                "description": "Market-based rate adjustments",
                "data_sources": [
                    "bankrate_com", "deposit_accounts", "federal_reserve_data",
                    "peer_bank_rates", "market_surveys"
                ],
                "adjustment_frequency": "weekly",
                "threshold_triggers": {
                    "significant_variance": 0.25,  # percentage points
                    "market_leadership": 0.10,
                    "defensive_pricing": 0.15
                },
                "products_monitored": [
                    "high_yield_savings", "cd_rates", "mortgage_rates",
                    "personal_loans", "auto_loans"
                ]
            },
            "profitability_optimization": {
                "description": "Margin-based rate optimization",
                "target_metrics": {
                    "net_interest_margin": 3.25,
                    "cost_of_funds": "minimize",
                    "loan_to_deposit_ratio": 85.0,
                    "return_on_assets": 1.15
                },
                "adjustment_triggers": {
                    "margin_compression": 0.10,
                    "funding_cost_increase": 0.15,
                    "competitive_pressure": 0.20
                },
                "rebalancing_frequency": "monthly"
            },
            "risk_based_pricing": {
                "description": "Credit risk and term risk adjustments",
                "risk_factors": {
                    "credit_score_impact": {
                        "excellent_750_plus": 0.00,
                        "good_700_749": 0.75,
                        "fair_650_699": 2.25,
                        "poor_below_650": 4.50
                    },
                    "loan_to_value_impact": {
                        "ltv_80_below": 0.00,
                        "ltv_80_90": 0.25,
                        "ltv_90_95": 0.50,
                        "ltv_95_plus": 1.00
                    },
                    "term_risk_premium": {
                        "1_year": 0.00,
                        "5_year": 0.25,
                        "10_year": 0.50,
                        "15_year": 0.75,
                        "30_year": 1.00
                    }
                },
                "dynamic_adjustment": True,
                "stress_test_scenarios": ["recession", "rate_spike", "credit_crisis"]
            }
        }
    
    def get_historical_rate_data(self) -> Dict[str, Any]:
        """Get historical interest rate data and trends"""
        return {
            "rate_history": {
                "fed_funds_rate": {
                    "2024_12": 5.25,
                    "2024_09": 5.00,
                    "2024_06": 5.25,
                    "2024_03": 5.50,
                    "2023_12": 5.50,
                    "2023_09": 5.25,
                    "2023_06": 5.00,
                    "2023_03": 4.75,
                    "2022_12": 4.25,
                    "2022_09": 3.00
                },
                "10_year_treasury": {
                    "2024_12": 4.35,
                    "2024_09": 4.15,
                    "2024_06": 4.45,
                    "2024_03": 4.25,
                    "2023_12": 4.05,
                    "2023_09": 4.85,
                    "2023_06": 3.75,
                    "2023_03": 3.45,
                    "2022_12": 3.85,
                    "2022_09": 3.25
                },
                "prime_rate": {
                    "2024_12": 8.25,
                    "2024_09": 8.00,
                    "2024_06": 8.25,
                    "2024_03": 8.50,
                    "2023_12": 8.50,
                    "2023_09": 8.25,
                    "2023_06": 8.00,
                    "2023_03": 7.75,
                    "2022_12": 7.25,
                    "2022_09": 6.00
                }
            },
            "trend_analysis": {
                "current_cycle": {
                    "cycle_start": "2022-03",
                    "cycle_type": "tightening",
                    "total_moves": 11,
                    "cumulative_change": 5.25,
                    "expected_peak": 5.50,
                    "next_move_probability": {
                        "increase": 25,
                        "hold": 60,
                        "decrease": 15
                    }
                },
                "volatility_metrics": {
                    "30_day_volatility": 0.15,
                    "90_day_volatility": 0.25,
                    "1_year_volatility": 1.85,
                    "max_single_day_move": 0.75
                },
                "correlation_analysis": {
                    "fed_funds_vs_10yr": 0.75,
                    "fed_funds_vs_mortgage": 0.85,
                    "inflation_vs_rates": 0.65,
                    "unemployment_vs_rates": -0.45
                }
            },
            "forecasting": {
                "next_quarter": {
                    "fed_funds_forecast": 5.25,
                    "10yr_treasury_forecast": 4.25,
                    "mortgage_30yr_forecast": 7.15,
                    "confidence_interval": 0.50
                },
                "next_year": {
                    "fed_funds_forecast": 4.75,
                    "10yr_treasury_forecast": 4.05,
                    "mortgage_30yr_forecast": 6.85,
                    "confidence_interval": 1.00
                },
                "economic_scenarios": {
                    "base_case": "gradual_decline",
                    "upside_risk": "persistent_inflation",
                    "downside_risk": "economic_recession"
                }
            }
        }
    
    def apply_rate_change(self, product_category: str, rate_changes: Dict[str, float], 
                         authorized_by: str, effective_date: str = None) -> Dict[str, Any]:
        """Apply interest rate changes with proper authorization"""
        
        # Validate authorization level
        authority = self.get_rate_setting_authority()
        
        # Determine required authorization level
        auth_level = self._determine_auth_level(product_category, rate_changes)
        
        # Mock implementation for demonstration
        change_id = f"RATE-{datetime.now().strftime('%Y%m%d')}-{hash(str(rate_changes))%10000:04d}"
        
        result = {
            "change_id": change_id,
            "status": "approved",
            "product_category": product_category,
            "rate_changes": rate_changes,
            "authorized_by": authorized_by,
            "authorization_level": auth_level,
            "effective_date": effective_date or datetime.now().isoformat(),
            "implementation_status": "pending_system_update",
            "affected_accounts": self._calculate_affected_accounts(product_category),
            "revenue_impact": self._calculate_revenue_impact(rate_changes),
            "customer_notifications": {
                "letters_required": True,
                "email_notifications": True,
                "website_updates": True,
                "notice_period_days": 30
            },
            "regulatory_requirements": {
                "truth_in_savings": True,
                "reg_z_disclosure": True,
                "call_report_update": True
            }
        }
        
        return result
    
    def _determine_auth_level(self, product_category: str, rate_changes: Dict[str, float]) -> str:
        """Determine required authorization level based on product and change magnitude"""
        max_change = max(abs(change) for change in rate_changes.values())
        
        if product_category in ['institutional_lending', 'wholesale_deposits']:
            return "level_3"
        elif product_category in ['commercial_lending', 'mortgage_rates']:
            return "level_2"
        elif max_change > 1.00:
            return "level_3"
        elif max_change > 0.50:
            return "level_2"
        else:
            return "level_1"
    
    def _calculate_affected_accounts(self, product_category: str) -> Dict[str, int]:
        """Calculate number of accounts affected by rate changes"""
        # Mock calculation
        base_accounts = {
            "consumer_deposits": 125000,
            "consumer_lending": 85000,
            "commercial_lending": 12500,
            "institutional_lending": 450
        }
        
        return {
            "total_accounts": base_accounts.get(product_category, 10000),
            "high_balance_accounts": int(base_accounts.get(product_category, 10000) * 0.15),
            "new_accounts_30_days": int(base_accounts.get(product_category, 10000) * 0.05)
        }
    
    def _calculate_revenue_impact(self, rate_changes: Dict[str, float]) -> Dict[str, float]:
        """Calculate revenue impact of rate changes"""
        # Mock calculation
        avg_change = sum(rate_changes.values()) / len(rate_changes)
        
        return {
            "annual_net_interest_income_impact": avg_change * 1500000,  # $1.5M per basis point
            "quarterly_impact": avg_change * 375000,
            "break_even_volume_change": abs(avg_change) * 0.15,  # 15% volume change to offset
            "competitor_response_risk": "medium" if abs(avg_change) > 0.25 else "low"
        }

    # Enhanced Interest Rate Management Methods
    def get_yield_curve_data(self) -> Dict[str, Any]:
        """Get yield curve analysis data"""
        return {
            'treasury_curve': {
                '1M': 4.85,
                '3M': 5.12,
                '6M': 5.28,
                '1Y': 5.45,
                '2Y': 5.62,
                '5Y': 5.78,
                '10Y': 5.95,
                '30Y': 6.12
            },
            'corporate_curve': {
                '1M': 5.25,
                '3M': 5.52,
                '6M': 5.68,
                '1Y': 5.85,
                '2Y': 6.02,
                '5Y': 6.18,
                '10Y': 6.35,
                '30Y': 6.52
            },
            'curve_analysis': {
                'slope': 'normal',
                'steepness': 1.27,
                'inversion_risk': 'low',
                'volatility': 'moderate'
            },
            'historical_comparison': {
                '1_week_ago': 5.89,
                '1_month_ago': 5.72,
                '3_months_ago': 5.45,
                '1_year_ago': 4.23
            }
        }

    def get_rate_products(self) -> Dict[str, Any]:
        """Get rate products for setting"""
        return {
            'deposit_products': [
                {
                    'id': 'savings_basic',
                    'name': 'Basic Savings Account',
                    'current_rate': 2.50,
                    'min_rate': 0.01,
                    'max_rate': 5.00,
                    'tier_structure': True
                },
                {
                    'id': 'checking_premium',
                    'name': 'Premium Checking',
                    'current_rate': 1.75,
                    'min_rate': 0.01,
                    'max_rate': 3.00,
                    'tier_structure': False
                },
                {
                    'id': 'cd_12m',
                    'name': '12-Month Certificate of Deposit',
                    'current_rate': 4.25,
                    'min_rate': 1.00,
                    'max_rate': 7.00,
                    'tier_structure': True
                }
            ],
            'lending_products': [
                {
                    'id': 'mortgage_30y',
                    'name': '30-Year Fixed Mortgage',
                    'current_rate': 7.25,
                    'min_rate': 3.00,
                    'max_rate': 12.00,
                    'risk_based': True
                },
                {
                    'id': 'personal_loan',
                    'name': 'Personal Loan',
                    'current_rate': 12.50,
                    'min_rate': 6.00,
                    'max_rate': 25.00,
                    'risk_based': True
                },
                {
                    'id': 'business_line',
                    'name': 'Business Line of Credit',
                    'current_rate': 8.75,
                    'min_rate': 4.00,
                    'max_rate': 18.00,
                    'risk_based': True
                }
            ],
            'rate_authorities': {
                'treasury_officer': ['deposit_products'],
                'asset_liability_manager': ['deposit_products', 'lending_products'],
                'cfo': ['all'],
                'board_member': ['all']
            }
        }