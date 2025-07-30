"""
Dashboard API Routes - Separate API endpoints from web routes
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)

# Create separate API blueprint
dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/v1/dashboard')

@dashboard_api_bp.route('/data')
@login_required
def get_dashboard_data():
    """API endpoint for dashboard data - returns JSON"""
    try:
        # Safe attribute access
        try:
            user_role = getattr(current_user, 'role', None)
            if user_role and hasattr(user_role, 'value'):
                user_role = user_role.value
            else:
                user_role = 'standard'
            username = getattr(current_user, 'username', 'Demo User')
        except:
            user_role = 'standard'
            username = 'Demo User'

        dashboard_data = {
            'account_balance': '$10,000.00',
            'recent_transactions': [],
            'quick_actions': ['Transfer Money', 'View Statements', 'Pay Bills', 'Apply for Card'],
            'total_balance': 10000.00,
            'pending_transactions': 0,
            'active_cards': 1,
            'notifications': []
        }
        
        return jsonify({
            'message': 'Dashboard Module Operational',
            'status': 'success',
            'user': username,
            'role': user_role,
            'dashboard_data': dashboard_data
        })
    
    except Exception as e:
        logger.error(f"Dashboard API error: {e}")
        return jsonify({'error': 'Dashboard temporarily unavailable', 'status': 'error'}), 500

@dashboard_api_bp.route('/overview')
@login_required
def get_overview_data():
    """API endpoint for overview data"""
    return jsonify({
        'message': 'Dashboard Overview Operational',
        'status': 'success',
        'overview_data': {
            'accounts_summary': {'total_accounts': 3, 'total_balance': 25000.0},
            'performance_metrics': {'growth_rate': 5.2, 'uptime': '99.9%'},
            'financial_overview': {'revenue': 120000.0, 'expenses': 45000.0}
        }
    })