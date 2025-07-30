"""
Cards & Payments Routes
Enterprise-grade modular routing system
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from modules.utils.services import ErrorLoggerService
from datetime import datetime
from .services import cards_payments_service

# Create module blueprint with hyphenated URL for professional banking appearance
cards_payments_bp = Blueprint('cards_payments', __name__, 
                            template_folder='templates',
                            static_folder='static',
                            url_prefix='/cards-payments')

# Removed legacy redirect blueprints - clean URLs only

# Initialize services
error_service = ErrorLoggerService()

@cards_payments_bp.route('/')
@cards_payments_bp.route('/dashboard')
@cards_payments_bp.route('/card-management')
@login_required
def main_dashboard():
    """Enhanced Cards & Payments main dashboard (also serves as cards_payments_dashboard)"""
    try:
        # Get comprehensive dashboard data
        dashboard_data = cards_payments_service.get_dashboard_data(current_user.id)
        user_cards = cards_payments_service.get_user_cards(current_user.id)
        fraud_alerts = cards_payments_service.get_fraud_alerts(current_user.id)
        
        return render_template('cards_payments/cards_payments_dashboard.html',
                             user=current_user,
                             dashboard_data=dashboard_data,
                             user_cards=user_cards,
                             fraud_alerts=fraud_alerts,
                             csrf_token=generate_csrf())
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.main_dashboard')
        flash('Error loading cards dashboard', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@cards_payments_bp.route('/bill-payment')
@login_required
def bill_payment():
    """Enhanced bill payment interface"""
    try:
        # Get user's saved billers and payment history
        saved_billers = cards_payments_service.get_saved_billers(current_user.id)
        payment_history = cards_payments_service.get_payment_history(current_user.id)
        available_accounts = cards_payments_service.get_payment_accounts(current_user.id)
        
        return render_template('cards_payments/bill_payment.html',
                             user=current_user,
                             saved_billers=saved_billers,
                             payment_history=payment_history,
                             available_accounts=available_accounts,
                             csrf_token=generate_csrf())
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.bill_payment')
        flash('Error loading bill payment', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/process-bill-payment', methods=['POST'])
@login_required
def process_bill_payment():
    """Process bill payment transaction"""
    try:
        payment_data = {
            'biller_id': request.form.get('biller_id'),
            'account_number': request.form.get('account_number'),
            'amount': float(request.form.get('amount', 0)),
            'payment_date': request.form.get('payment_date'),
            'memo': request.form.get('memo', ''),
            'payment_account': request.form.get('payment_account')
        }
        
        # Validate payment data
        if not payment_data['biller_id'] or payment_data['amount'] <= 0:
            flash('Invalid payment information', 'error')
            return redirect(url_for('cards_payments.bill_payment'))
        
        # Process the payment
        result = cards_payments_service.process_bill_payment(current_user.id, payment_data)
        
        if result['success']:
            flash(f'Bill payment of ${payment_data["amount"]:.2f} processed successfully', 'success')
        else:
            flash(f'Payment failed: {result.get("error", "Unknown error")}', 'error')
            
        return redirect(url_for('cards_payments.bill_payment'))
        
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.process_bill_payment')
        flash('Error processing bill payment', 'error')
        return redirect(url_for('cards_payments.bill_payment'))

@cards_payments_bp.route('/card-controls')
@login_required
def card_controls():
    """Advanced card control and security settings"""
    try:
        user_cards = cards_payments_service.get_user_cards(current_user.id)
        security_settings = cards_payments_service.get_card_security_settings(current_user.id)
        
        return render_template('cards_payments/card_controls.html',
                             user=current_user,
                             user_cards=user_cards,
                             security_settings=security_settings,
                             csrf_token=generate_csrf())
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.card_controls')
        flash('Error loading card controls', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/update-card-limits', methods=['POST'])
@login_required
def update_card_limits():
    """Update card spending limits and controls"""
    try:
        card_id = request.form.get('card_id')
        limits_data = {
            'daily_limit': float(request.form.get('daily_limit', 0)),
            'monthly_limit': float(request.form.get('monthly_limit', 0)),
            'atm_limit': float(request.form.get('atm_limit', 0)),
            'international_enabled': request.form.get('international_enabled') == 'on',
            'online_enabled': request.form.get('online_enabled') == 'on',
            'contactless_enabled': request.form.get('contactless_enabled') == 'on'
        }
        
        result = cards_payments_service.update_card_limits(current_user.id, card_id, limits_data)
        
        if result['success']:
            flash('Card limits updated successfully', 'success')
        else:
            flash(f'Failed to update limits: {result.get("error", "Unknown error")}', 'error')
            
        return redirect(url_for('cards_payments.card_controls'))
        
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.update_card_limits')
        flash('Error updating card limits', 'error')
        return redirect(url_for('cards_payments.card_controls'))

@cards_payments_bp.route('/fraud-monitoring')
@login_required
def fraud_monitoring():
    """Fraud detection and monitoring dashboard"""
    try:
        fraud_data = cards_payments_service.get_fraud_monitoring_data(current_user.id)
        recent_alerts = cards_payments_service.get_recent_fraud_alerts(current_user.id)
        
        return render_template('cards_payments/fraud_monitoring.html',
                             user=current_user,
                             fraud_data=fraud_data,
                             recent_alerts=recent_alerts,
                             csrf_token=generate_csrf())
    except Exception as e:
        error_service.log_error(str(e), endpoint='cards_payments.fraud_monitoring')
        flash('Error loading fraud monitoring', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))
        error_service.log_error("DASHBOARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.overview'))

@cards_payments_bp.route('/overview')
@login_required  
def overview():
    """Cards & Payments overview page"""
    try:
        return render_template('cards_payments/cards_payments_overview.html',
                             user=current_user,
                             page_title='Cards & Payments Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')  
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/processing')
@login_required
def payment_processing():
    """Payment processing management"""
    try:
        return render_template('cards_payments/payment_processing.html',
                             user=current_user,
                             page_title='Payment Processing')
    except Exception as e:
        error_service.log_error("PAYMENT_PROCESSING_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """Card application page"""
    if request.method == 'POST':
        try:
            # Process card application
            application_data = {
                'card_type': request.form.get('card_type'),
                'annual_income': request.form.get('annual_income'),
                'employment_status': request.form.get('employment_status'),
                'requested_limit': request.form.get('requested_limit'),
                'user_id': current_user.id
            }
            
            # In production, process application through card service
            flash('Card application submitted successfully. You will receive a decision within 24 hours.', 'success')
            return redirect(url_for('cards_payments.main_dashboard'))
            
        except Exception as e:
            error_service.log_error("CARD_APPLICATION_ERROR", str(e), {"user_id": current_user.id})
            flash('Unable to submit application. Please try again.', 'error')
    
    # GET request - show application form
    try:
        context = {
            'card_types': [
                {'name': 'Visa Classic', 'annual_fee': '$0', 'apr': '18.99%'},
                {'name': 'Visa Gold', 'annual_fee': '$95', 'apr': '16.99%'},
                {'name': 'Visa Platinum', 'annual_fee': '$195', 'apr': '14.99%'},
                {'name': 'Business Visa', 'annual_fee': '$125', 'apr': '15.99%'}
            ],
            'page_title': 'Apply for Card',
            'csrf_token': generate_csrf()
        }
        
        return render_template('cards_payments/card_application.html', **context)
        
    except Exception as e:
        error_service.log_error("CARD_APPLICATION_PAGE_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/card-management')
@login_required
def card_management():
    """Card management page"""
    try:
        return render_template('cards_payments/cards_payments_dashboard.html',
                             user=current_user,
                             current_time=datetime.now(),
                             page_title='Card Management')
    except Exception as e:
        error_service.log_error("CARD_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Card management service temporarily unavailable', 'error')
        return redirect(url_for('dashboard.overview'))


@cards_payments_bp.route('/settings')
@login_required
def settings():
    """Cards & Payments settings page"""
    try:
        return render_template('cards_payments/cards_payments_settings.html',
                             user=current_user,
                             page_title='Cards & Payments Settings')
    except Exception as e:
        error_service.log_error("SETTINGS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/cards')
@login_required
def manage_cards():
    """Card management page"""
    try:
        user_cards = cards_payments_service.get_user_cards(current_user.id)
        return render_template('cards_payments/card_management.html',
                             user=current_user,
                             user_cards=user_cards,
                             page_title='Card Management')
    except Exception as e:
        error_service.log_error("CARD_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load card management', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/cards/<card_id>/transactions')
@login_required
def card_transactions(card_id):
    """View transactions for a specific card"""
    try:
        transactions = cards_payments_service.get_card_transactions(card_id)
        return render_template('cards_payments/card_transactions.html',
                             user=current_user,
                             card_id=card_id,
                             transactions=transactions,
                             page_title='Card Transactions')
    except Exception as e:
        error_service.log_error("CARD_TRANSACTIONS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load card transactions', 'error')
        return redirect(url_for('cards_payments.manage_cards'))

@cards_payments_bp.route('/apply-card', methods=['GET', 'POST'])
@login_required
def apply_card():
    """Apply for a new card"""
    try:
        if request.method == 'POST':
            application_data = {
                'card_type': request.form.get('card_type'),
                'requested_limit': request.form.get('requested_limit', 5000),
                'income': request.form.get('income'),
                'employment_status': request.form.get('employment_status')
            }
            
            result = cards_payments_service.process_card_application(current_user.id, application_data)
            
            if result.get('success'):
                flash(f'Card application submitted successfully. Reference: {result["application"]["application_id"]}', 'success')
            else:
                flash(f'Application failed: {result.get("error")}', 'error')
                
            return redirect(url_for('cards_payments.manage_cards'))
            
        return render_template('cards_payments/apply_card.html',
                             user=current_user,
                             page_title='Apply for Card')
    except Exception as e:
        error_service.log_error("CARD_APPLICATION_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to process application', 'error')
        return redirect(url_for('cards_payments.manage_cards'))

@cards_payments_bp.route('/block-card', methods=['POST'])
@login_required
def block_card():
    """Block a card"""
    try:
        card_id = request.form.get('card_id')
        reason = request.form.get('reason', 'User request')
        
        result = cards_payments_service.block_card(card_id, reason)
        
        if result.get('success'):
            flash('Card blocked successfully', 'success')
        else:
            flash(f'Failed to block card: {result.get("error")}', 'error')
            
    except Exception as e:
        error_service.log_error("BLOCK_CARD_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to block card', 'error')
        
    return redirect(url_for('cards_payments.manage_cards'))

@cards_payments_bp.route('/fraud-alerts')
@login_required
def fraud_alerts():
    """View fraud alerts"""
    try:
        alerts = cards_payments_service.get_fraud_alerts(current_user.id)
        return render_template('cards_payments/fraud_alerts.html',
                             user=current_user,
                             fraud_alerts=alerts,
                             page_title='Fraud Alerts')
    except Exception as e:
        error_service.log_error("FRAUD_ALERTS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load fraud alerts', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

# Missing routes referenced in templates
@cards_payments_bp.route('/analytics')
@login_required
def analytics():
    """Cards and payments analytics"""
    try:
        analytics_data = {
            'total_transactions': 156789,
            'transaction_volume': 2450000.00,
            'success_rate': 99.2,
            'fraud_rate': 0.1
        }
        return render_template('cards_payments/analytics.html',
                             analytics_data=analytics_data,
                             page_title='Cards & Payments Analytics')
    except Exception as e:
        error_service.log_error("ANALYTICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/overview')
@login_required
def cards_payments_overview():
    """Cards and payments overview"""
    try:
        overview_data = {
            'active_cards': 12500,
            'pending_applications': 45,
            'monthly_volume': 1250000.00,
            'processing_fees': 15600.00
        }
        return render_template('cards_payments/overview.html',
                             overview_data=overview_data,
                             page_title='Cards & Payments Overview')
    except Exception as e:
        error_service.log_error("OVERVIEW_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/transaction-analytics')
@login_required
def transaction_analytics():
    """Transaction analytics dashboard"""
    try:
        transaction_data = {
            'daily_transactions': 2547,
            'weekly_growth': 12.5,
            'peak_hours': '2:00 PM - 4:00 PM',
            'avg_transaction_size': 156.78
        }
        return render_template('cards_payments/transaction_analytics.html',
                             transaction_data=transaction_data,
                             page_title='Transaction Analytics')
    except Exception as e:
        error_service.log_error("TRANSACTION_ANALYTICS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/success-rate-analysis')
@login_required
def success_rate_analysis():
    """Success rate analysis dashboard"""
    try:
        success_data = {
            'overall_success_rate': 99.2,
            'card_success_rate': 99.5,
            'online_success_rate': 98.8,
            'mobile_success_rate': 99.1
        }
        return render_template('cards_payments/success_rate_analysis.html',
                             success_data=success_data,
                             page_title='Success Rate Analysis')
    except Exception as e:
        error_service.log_error("SUCCESS_RATE_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

@cards_payments_bp.route('/fraud-analysis')
@login_required
def fraud_analysis():
    """Fraud analysis dashboard"""
    try:
        fraud_data = {
            'fraud_rate': 0.1,
            'blocked_transactions': 25,
            'false_positives': 3,
            'fraud_savings': 45600.00
        }
        return render_template('cards_payments/fraud_analysis.html',
                             fraud_data=fraud_data,
                             page_title='Fraud Analysis')
    except Exception as e:
        error_service.log_error("FRAUD_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('cards_payments.main_dashboard'))

# Module health check
# Route alias handled by existing main_dashboard function

@cards_payments_bp.route('/api/health')
def health_check():
    """Cards & Payments health check"""
    return jsonify({
        "status": "healthy",
        "app_module": "Cards & Payments",
        "version": "1.0.0",
        "routes_active": 22
    })
