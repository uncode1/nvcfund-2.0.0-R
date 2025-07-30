"""
Trading Platform Forms
WTForms for trading operations with validation and security
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, FloatField, IntegerField, SelectField, DateTimeField,
    TextAreaField, BooleanField, FieldList, FormField
)
from wtforms.validators import (
    DataRequired, NumberRange, Length, Email, Optional, ValidationError
)
from decimal import Decimal, InvalidOperation
from datetime import datetime

class BaseOrderForm(FlaskForm):
    """Base class for trading order forms with common validations"""
    
    # Basic Order Information
    symbol = StringField('Symbol',
        validators=[
            DataRequired(message='Symbol is required'),
            Length(min=1, max=20, message='Symbol must be 1-20 characters')
        ]
    )
    
    order_side = SelectField('Order Side',
        choices=[
            ('BUY', 'Buy'),
            ('SELL', 'Sell')
        ],
        validators=[DataRequired(message='Order side is required')]
    )
    
    quantity = FloatField('Quantity',
        validators=[
            DataRequired(message='Quantity is required'),
            NumberRange(min=1, max=10000000, message='Invalid quantity range')
        ]
    )
    
    # Order Types
    order_type = SelectField('Order Type',
        choices=[
            ('MARKET', 'Market Order'),
            ('LIMIT', 'Limit Order'),
            ('STOP', 'Stop Order'),
            ('STOP_LIMIT', 'Stop Limit Order')
        ],
        validators=[DataRequired(message='Order type is required')]
    )

class EquityOrderForm(BaseOrderForm):
    """Form for equity (stock) orders"""
    
    # Price Fields
    limit_price = FloatField('Limit Price',
        validators=[
            Optional(),
            NumberRange(min=0.01, max=1000000, message='Invalid price range')
        ]
    )
    
    stop_price = FloatField('Stop Price',
        validators=[
            Optional(),
            NumberRange(min=0.01, max=1000000, message='Invalid price range')
        ]
    )
    
    # Order Duration
    time_in_force = SelectField('Time in Force',
        choices=[
            ('DAY', 'Day'),
            ('GTC', 'Good Till Cancelled'),
            ('IOC', 'Immediate or Cancel'),
            ('FOK', 'Fill or Kill')
        ],
        default='DAY'
    )

class ForexOrderForm(BaseOrderForm):
    """Form for foreign exchange orders"""
    
    # Currency pair specific fields
    base_currency = StringField('Base Currency',
        validators=[
            DataRequired(message='Base currency is required'),
            Length(min=3, max=3, message='Currency code must be 3 characters')
        ]
    )
    
    quote_currency = StringField('Quote Currency',
        validators=[
            DataRequired(message='Quote currency is required'),
            Length(min=3, max=3, message='Currency code must be 3 characters')
        ]
    )
    
    exchange_rate = FloatField('Exchange Rate',
        validators=[
            Optional(),
            NumberRange(min=0.0001, max=1000, message='Invalid exchange rate')
        ]
    )

class CommodityOrderForm(BaseOrderForm):
    """Form for commodity orders"""
    
    # Commodity specific fields
    commodity_type = SelectField('Commodity Type',
        choices=[
            ('GOLD', 'Gold'),
            ('SILVER', 'Silver'),
            ('OIL', 'Oil'),
            ('WHEAT', 'Wheat'),
            ('CORN', 'Corn'),
            ('NATURAL_GAS', 'Natural Gas')
        ],
        validators=[DataRequired(message='Commodity type is required')]
    )
    
    delivery_month = StringField('Delivery Month',
        validators=[
            Optional(),
            Length(min=6, max=6, message='Delivery month format: YYYYMM')
        ]
    )

class DerivativeOrderForm(BaseOrderForm):
    """Form for derivative instruments"""
    
    # Derivative specific fields
    derivative_type = SelectField('Derivative Type',
        choices=[
            ('OPTION', 'Option'),
            ('FUTURE', 'Future'),
            ('SWAP', 'Swap'),
            ('FORWARD', 'Forward')
        ],
        validators=[DataRequired(message='Derivative type is required')]
    )
    
    strike_price = FloatField('Strike Price',
        validators=[
            Optional(),
            NumberRange(min=0.01, max=100000)
        ]
    )
    
    expiration_date = DateTimeField('Expiration Date',
        validators=[Optional()]
    )

class PortfolioRebalanceForm(FlaskForm):
    """Form for portfolio rebalancing operations"""
    
    account_id = StringField('Account ID',
        validators=[
            DataRequired(message='Account ID is required'),
            Length(min=5, max=50, message='Invalid account ID length')
        ]
    )
    
    target_allocation = TextAreaField('Target Allocation (JSON)',
        validators=[
            DataRequired(message='Target allocation is required'),
            Length(max=5000, message='Allocation data too large')
        ]
    )
    
    rebalance_threshold = FloatField('Rebalance Threshold (%)',
        validators=[
            DataRequired(message='Rebalance threshold is required'),
            NumberRange(min=1, max=50, message='Threshold must be 1-50%')
        ]
    )
    
    dry_run = BooleanField('Dry Run (Preview Only)', default=True)

class RiskLimitForm(FlaskForm):
    """Form for setting trading risk limits"""
    
    max_position_size = FloatField('Max Position Size',
        validators=[
            DataRequired(message='Max position size is required'),
            NumberRange(min=1000, max=100000000, message='Invalid position size range')
        ]
    )
    
    max_daily_loss = FloatField('Max Daily Loss',
        validators=[
            DataRequired(message='Max daily loss is required'),
            NumberRange(min=100, max=10000000, message='Invalid loss limit range')
        ]
    )
    
    max_leverage = FloatField('Max Leverage Ratio',
        validators=[
            DataRequired(message='Max leverage is required'),
            NumberRange(min=1, max=100, message='Leverage must be 1-100x')
        ]
    )

class TradingAlgorithmForm(FlaskForm):
    """Form for algorithmic trading strategy setup"""
    
    strategy_name = StringField('Strategy Name',
        validators=[
            DataRequired(message='Strategy name is required'),
            Length(min=3, max=100, message='Strategy name must be 3-100 characters')
        ]
    )
    
    algorithm_type = SelectField('Algorithm Type',
        choices=[
            ('MOMENTUM', 'Momentum'),
            ('MEAN_REVERSION', 'Mean Reversion'),
            ('ARBITRAGE', 'Arbitrage'),
            ('MARKET_MAKING', 'Market Making'),
            ('TREND_FOLLOWING', 'Trend Following')
        ],
        validators=[DataRequired(message='Algorithm type is required')]
    )
    
    parameters = TextAreaField('Algorithm Parameters (JSON)',
        validators=[
            DataRequired(message='Algorithm parameters are required'),
            Length(max=10000, message='Parameters data too large')
        ]
    )
    
    risk_parameters = TextAreaField('Risk Parameters (JSON)',
        validators=[
            DataRequired(message='Risk parameters are required'),
            Length(max=5000, message='Risk parameters data too large')
        ]
    )
    
    active = BooleanField('Active', default=False)