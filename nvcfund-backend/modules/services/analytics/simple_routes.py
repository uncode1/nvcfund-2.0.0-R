"""
Analytics Simple Routes
Simplified analytics routes to avoid decorator conflicts
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)

# Create simple analytics blueprint
analytics_simple = Blueprint(
    'analytics',
    __name__,
    url_prefix='/analytics',
    template_folder='templates'
)

@analytics_simple.route('/')
@analytics_simple.route('/dashboard')
@login_required
def analytics_dashboard():
    """Analytics Dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing analytics dashboard")
        return render_template('analytics/analytics_dashboard.html')
    except Exception as e:
        logger.error(f"Error loading analytics dashboard: {e}")
        return redirect(url_for('dashboard.main_dashboard'))

@analytics_simple.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'module': 'analytics'})