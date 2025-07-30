"""
Loans Module Routes
Loan application, approval, and portfolio management routes
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import logging

from . import loans_bp

logger = logging.getLogger(__name__)

@loans_bp.route('/pending-applications')
@login_required
def pending_applications():
    """Pending loan applications dashboard"""
    try:
        applications_data = {
            'pending_count': 15,
            'applications': [
                {
                    'id': 'APP-2025-001',
                    'applicant': 'John Smith',
                    'amount': 250000.00,
                    'type': 'Business Loan',
                    'submitted': '2025-01-05',
                    'status': 'Under Review'
                },
                {
                    'id': 'APP-2025-002',
                    'applicant': 'Sarah Johnson',
                    'amount': 150000.00,
                    'type': 'Personal Loan',
                    'submitted': '2025-01-04',
                    'status': 'Documentation Required'
                }
            ]
        }
        
        return render_template('loans/pending_applications.html',
                             applications_data=applications_data,
                             page_title='Pending Loan Applications')
    except Exception as e:
        logger.error(f"Pending applications error: {str(e)}")
        flash('Unable to load pending applications. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@loans_bp.route('/approved-loans')
@login_required
def approved_loans():
    """Approved loans dashboard"""
    try:
        approved_data = {
            'approved_count': 23,
            'loans': [
                {
                    'id': 'LOAN-2024-156',
                    'borrower': 'ABC Corporation',
                    'amount': 500000.00,
                    'type': 'Commercial Loan',
                    'approved_date': '2024-12-15',
                    'status': 'Active'
                },
                {
                    'id': 'LOAN-2024-157',
                    'borrower': 'Mike Davis',
                    'amount': 75000.00,
                    'type': 'Auto Loan',
                    'approved_date': '2024-12-20',
                    'status': 'Active'
                }
            ]
        }
        
        return render_template('loans/approved_loans.html',
                             approved_data=approved_data,
                             page_title='Approved Loans')
    except Exception as e:
        logger.error(f"Approved loans error: {str(e)}")
        flash('Unable to load approved loans. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@loans_bp.route('/portfolio-overview')
@login_required
def portfolio_overview():
    """Loan portfolio overview dashboard"""
    try:
        portfolio_data = {
            'total_portfolio_value': 12500000.00,
            'active_loans': 156,
            'delinquency_rate': 2.1,
            'average_loan_size': 80128.21,
            'portfolio_breakdown': [
                {'type': 'Commercial Loans', 'amount': 7500000.00, 'percentage': 60},
                {'type': 'Personal Loans', 'amount': 3000000.00, 'percentage': 24},
                {'type': 'Auto Loans', 'amount': 2000000.00, 'percentage': 16}
            ]
        }
        
        return render_template('loans/portfolio_overview.html',
                             portfolio_data=portfolio_data,
                             page_title='Loan Portfolio Overview')
    except Exception as e:
        logger.error(f"Portfolio overview error: {str(e)}")
        flash('Unable to load portfolio overview. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@loans_bp.route('/new-application')
@login_required
def new_application():
    """New loan application form"""
    try:
        return render_template('loans/new_application.html',
                             page_title='New Loan Application')
    except Exception as e:
        logger.error(f"New application error: {str(e)}")
        flash('Unable to load application form. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@loans_bp.route('/api/health')
def health_check():
    """Loans module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'loans',
        'version': '1.0.0'
    })
