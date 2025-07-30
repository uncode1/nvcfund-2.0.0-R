"""
Financial Data Integration Routes
NVC Banking Platform - Financial Data Providers Integration Management
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from modules.utils.services import ErrorLoggerService
from datetime import datetime

# Create module blueprint
financial_data_bp = Blueprint('financial_data', __name__, 
                             template_folder='templates',
                             static_folder='static',
                             url_prefix='/integrations/financial-data')

# Initialize services
error_service = ErrorLoggerService()

@financial_data_bp.route('/')
@financial_data_bp.route('/dashboard')
@login_required
def financial_data_dashboard():
    """Financial data integration dashboard"""
    try:
        context = {
            'page_title': 'Financial Data Integration',
            'total_providers': 4,
            'active_connections': 4,
            'daily_api_calls': 12547,
            'data_sources': ['Plaid', 'Federal Reserve', 'SWIFT Network', 'Clearing House']
        }
        
        return render_template('financial_data/dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Financial data dashboard error: {str(e)}", current_user.id)
        flash('Unable to load financial data dashboard. Please try again.', 'error')
        return redirect(url_for('integrations.integrations_dashboard'))

# Redirect routes to individual financial data provider sub-modules
@financial_data_bp.route('/plaid')
@login_required
def plaid_redirect():
    """Redirect to Plaid sub-module"""
    return redirect('/integrations/financial-data/plaid/')

@financial_data_bp.route('/federal-reserve')
@login_required
def federal_reserve_redirect():
    """Redirect to Federal Reserve sub-module"""
    return redirect('/integrations/financial-data/federal-reserve/')

@financial_data_bp.route('/swift-network')
@login_required
def swift_network_redirect():
    """Redirect to SWIFT Network sub-module"""
    return redirect('/integrations/financial-data/swift-network/')

@financial_data_bp.route('/clearing-house')
@login_required
def clearing_house_redirect():
    """Redirect to Clearing House sub-module"""
    return redirect('/integrations/financial-data/clearing-house/')