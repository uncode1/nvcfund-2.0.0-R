"""
Banking Module Routes - Comprehensive Banking Operations
Self-contained banking routes with account management, transfers, cards, and payments
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session, make_response
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf, validate_csrf
from datetime import datetime
import logging
import os
from decimal import Decimal

from .services import BankingService
from modules.services.integrations.payment_gateways.services import PaymentGatewayService
from modules.utils.services import ErrorLoggerService
from modules.core.form_decorators import banking_form, process_form, require_post_data
from modules.core.form_processor import form_processor
from modules.core.security_enforcement import require_session_security
from modules.banking.transfer_service import TransferService

# Initialize logging and services
logger = logging.getLogger(__name__)
banking_service = BankingService()
gateway_service = PaymentGatewayService()
error_service = ErrorLoggerService()
transfer_service = TransferService()

# Create Banking Blueprint
banking_bp = Blueprint('banking', __name__, 
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/banking/static',
                      url_prefix='/banking')

# Endpoint to log user onclick actions for debugging
@banking_bp.route('/log-action', methods=['POST'])
@login_required
def log_user_action():
    """Log user onclick actions for debugging"""
    try:
        # Validate CSRF token for security
        csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except Exception as csrf_error:
                logger.warning(f"CSRF validation failed for log action: {csrf_error}")
                return jsonify({'status': 'error', 'message': 'CSRF validation failed'}), 403
        else:
            logger.warning("No CSRF token provided for log action")
            return jsonify({'status': 'error', 'message': 'CSRF token required'}), 403

        data = request.get_json() or {}
        action = data.get('action', 'unknown')
        element = data.get('element', 'unknown')
        target_url = data.get('targetUrl', 'unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())

        # Enhanced logging with clear action details
        logger.info(f"🎯 USER ONCLICK ACTION: {action} | Element: {element} | Target: {target_url} | User: {current_user.username}")

        return jsonify({'status': 'logged', 'action': action})
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Also add API route for consistency
@banking_bp.route('/api/log-user-action', methods=['POST'])
@login_required
def api_log_user_action():
    """API endpoint for logging user actions from JavaScript"""
    return log_user_action()

# Main Banking Dashboard
@banking_bp.route('/')
@banking_bp.route('/home')
@login_required
def banking_dashboard():
    """Banking dashboard with account overview"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)
        user_cards = banking_service.get_user_cards(current_user.id)
        recent_transfers = banking_service.get_transfer_history(current_user.id, limit=5)

        context = {
            'accounts': user_accounts,
            'cards': user_cards,
            'recent_transfers': recent_transfers,
            'total_balance': sum(acc['balance'] for acc in user_accounts),
            'active_cards': len([card for card in user_cards if card['status'] == 'Active'])
        }

        logger.info(f"Banking dashboard accessed by user {current_user.id}")
        return render_template('banking/modular_banking_dashboard.html', **context)

    except Exception as e:
        error_service.log_error(f"Banking dashboard error: {str(e)}", current_user.id)
        flash('Unable to load banking dashboard. Please try again.', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

# Account Management Routes
@banking_bp.route('/accounts')
@login_required
def accounts():
    """Account management page"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'accounts': user_accounts,
            'page_title': 'Account Management'
        }

        return render_template('banking/modular_banking_accounts.html', **context)

    except Exception as e:
        error_service.log_error(f"Accounts page error: {str(e)}", current_user.id)
        flash('Unable to load accounts. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create new account"""
    if request.method == 'POST':
        try:
            account_data = {
                'type': request.form.get('account_type'),
                'currency': request.form.get('currency', 'USD'),
                'branch': request.form.get('branch', 'Main Branch'),
                'initial_deposit': request.form.get('initial_deposit', '0.00')
            }

            result = banking_service.create_account(current_user.id, account_data)

            if result['success']:
                flash(f'Account application submitted successfully. Account Number: {result["account"]["account_number"]}', 'success')
                return redirect(url_for('banking.accounts'))
            else:
                flash(f'Account creation failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Account creation error: {str(e)}", current_user.id)
            flash('Unable to create account. Please try again.', 'error')

    # GET request - show account creation form
    context = {
        'account_types': ['Checking', 'Savings', 'Business', 'Investment'],
        'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
        'page_title': 'Create New Account'
    }

    return render_template('banking/modular_banking_create_account.html', **context)

# Transfer Routes
@banking_bp.route('/transfer')
@login_required
def transfer():
    """Transfer page - redirect to transfers dashboard"""
    return redirect(url_for('banking.transfers'))

@banking_bp.route('/send-transfer')
@login_required
def send_transfer():
    """Send money transfer page - redirect to new transfer form"""
    return redirect(url_for('banking.new_transfer'))

@banking_bp.route('/transfers')
@login_required
def transfers():
    """Modern comprehensive transfer channels dashboard"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        # Redirect to account creation if no accounts
        if not user_accounts:
            flash('You need to create an account before making transfers.', 'info')
            return redirect(url_for('banking.create_account'))

        transfer_history = banking_service.get_transfer_history(current_user.id, limit=10)

        # Transfer channel metrics and options
        transfer_channels = [
            {
                'name': 'Internal Transfer',
                'description': 'Transfer between your NVC accounts',
                'icon': 'fas fa-arrows-alt-h',
                'color': 'primary',
                'speed': 'Instant',
                'cost': 'Free',
                'limit': '$50,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Instant processing', 'No fees', 'Real-time confirmation']
            },
            {
                'name': 'ACH Transfer',
                'description': 'US bank-to-bank transfers via ACH network',
                'icon': 'fas fa-university',
                'color': 'success',
                'speed': '1-3 business days',
                'cost': '$0.50',
                'limit': '$25,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Low cost', 'Secure', 'Batch processing']
            },
            {
                'name': 'Wire Transfer',
                'description': 'Fast domestic and international wire transfers',
                'icon': 'fas fa-bolt',
                'color': 'warning',
                'speed': '30 mins - 2 hours',
                'cost': '$15-35',
                'limit': '$1,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Same-day processing', 'High limits', 'Global reach']
            },
            {
                'name': 'SWIFT Transfer',
                'description': 'International transfers via SWIFT network',
                'icon': 'fas fa-globe',
                'color': 'info',
                'speed': '1-5 business days',
                'cost': '$25-50',
                'limit': '$500,000',
                'route': 'banking.swift_transfer',
                'available': True,
                'features': ['Worldwide coverage', 'Multi-currency', 'Tracking available']
            },
            {
                'name': 'Fedwire Transfer',
                'description': 'Federal Reserve real-time gross settlement',
                'icon': 'fas fa-university',
                'color': 'danger',
                'speed': 'Same day',
                'cost': '$30',
                'limit': '$10,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Same-day settlement', 'Large amounts', 'Federal Reserve network']
            },
            {
                'name': 'Blockchain Transfer',
                'description': 'Cryptocurrency and digital asset transfers',
                'icon': 'fab fa-bitcoin',
                'color': 'secondary',
                'speed': '10-60 minutes',
                'cost': '$2-10',
                'limit': '$100,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Decentralized', 'Programmable', 'Cross-border']
            },
            {
                'name': 'NVCT Transfer',
                'description': 'Transfer using NVCT stablecoin',
                'icon': 'fas fa-coins',
                'color': 'primary',
                'speed': 'Instant',
                'cost': '$0.25',
                'limit': '$250,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Stable value', 'Instant settlement', 'Low fees']
            },
            {
                'name': 'Mobile Transfer',
                'description': 'Send money to mobile wallets',
                'icon': 'fas fa-mobile-alt',
                'color': 'success',
                'speed': 'Instant',
                'cost': '$1-3',
                'limit': '$10,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Mobile-friendly', 'QR codes', 'Push notifications']
            },
            {
                'name': 'PayPal Transfer',
                'description': 'Global digital payments via PayPal network',
                'icon': 'fab fa-paypal',
                'color': 'primary',
                'speed': 'Instant',
                'cost': '2.9% + $0.30',
                'limit': '$60,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Global reach', 'Buyer protection', 'Mobile app']
            },
            {
                'name': 'Stripe Transfer',
                'description': 'Online payment processing and transfers',
                'icon': 'fab fa-stripe',
                'color': 'secondary',
                'speed': '2-7 business days',
                'cost': '2.9% + $0.30',
                'limit': '$2,000,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Developer-friendly', 'Global coverage', 'Real-time API']
            },
            {
                'name': 'Flutterwave',
                'description': 'African payment infrastructure and transfers',
                'icon': 'fas fa-credit-card',
                'color': 'warning',
                'speed': '1-3 business days',
                'cost': '1.4% + $0.25',
                'limit': '$500,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Pan-African', 'Multiple currencies', 'Mobile money']
            },
            {
                'name': 'Mojaloop',
                'description': 'Open-source financial inclusion platform',
                'icon': 'fas fa-handshake',
                'color': 'info',
                'speed': 'Real-time',
                'cost': '$0.05',
                'limit': '$25,000',
                'route': 'banking.new_transfer',
                'available': True,
                'features': ['Financial inclusion', 'Interoperability', 'Low cost']
            }
        ]

        # Transfer statistics (updated for 12 channels)
        transfer_stats = {
            'total_volume': 3247692.50,
            'total_transfers': 22847,
            'success_rate': 99.8,
            'average_amount': 1547.25,
            'channels_active': len([c for c in transfer_channels if c['available']]),
            'daily_volume': 147832.50,
            'daily_transfers': 1124,
            'pending_transfers': 31
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''
        
        context = {
            'accounts': user_accounts,
            'transfer_history': transfer_history,
            'transfer_channels': transfer_channels,
            'transfer_stats': transfer_stats,
            'page_title': 'Transfer Channels',
            'csrf_token': csrf_token
        }

        return render_template('banking/modern_transfer_dashboard.html', **context)

    except Exception as e:
        logger.error(f"Transfers page error: {str(e)} - User: {current_user.id}")
        print(f"DEBUG: Transfers page error - {str(e)} - Type: {type(e)}")
        import traceback
        traceback.print_exc()
        flash('Unable to load transfers. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers/new', methods=['GET', 'POST'])
@login_required
@banking_form('transfer')
def new_transfer():
    """Create new money transfer"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'from_account': request.form.get('from_account'),
                'to_account': request.form.get('to_account'),
                'amount': request.form.get('amount'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }

            result = banking_service.process_transfer(current_user.id, transfer_data)

            if result['success']:
                flash(f'Transfer completed successfully. Transaction ID: {result["transaction_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Transfer failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Transfer processing error: {str(e)}", current_user.id)
            flash('Unable to process transfer. Please try again.', 'error')

    # GET request - show transfer form
    try:
        # Get the selected channel from URL parameter
        channel_param = request.args.get('channel', 'internal_transfer')
        
        # Channel parameter normalization (handle both hyphen and underscore formats)
        channel_mapping = {
            'swift-transfer': 'swift_transfer',
            'wire-transfer': 'wire_transfer', 
            'ach-transfer': 'ach_transfer',
            'paypal-transfer': 'paypal_transfer',
            'stripe-transfer': 'stripe_transfer',
            'blockchain-transfer': 'blockchain_transfer',
            'mobile-transfer': 'mobile_transfer',
            'nvct-stablecoin': 'nvct_stablecoin',
            'nvct-transfer': 'nvct_stablecoin',
            'internal-transfer': 'internal_transfer',
            'fedwire-transfer': 'fedwire'
        }
        
        channel = channel_mapping.get(channel_param, channel_param)
        
        # Log the channel resolution for troubleshooting (development only)
        is_development = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG_TRANSFERS') == 'true'
        if is_development:
            logger.info(f"🎯 CHANNEL RESOLUTION: {channel_param} -> {channel}")
            print(f"🎯 CHANNEL RESOLUTION: {channel_param} -> {channel}")
        
        user_accounts = banking_service.get_user_accounts(current_user.id)

        # Redirect to account creation if no accounts
        if not user_accounts:
            flash('You need to create an account before making transfers.', 'info')
            return redirect(url_for('banking.create_account'))

        # Channel-specific configurations
        channel_configs = {
            'internal_transfer': {
                'template': 'banking/transfers/internal_transfer.html',
                'title': 'Internal Transfer',
                'description': 'Transfer between your NVC accounts',
                'features': ['Instant processing', 'No fees', 'Real-time confirmation'],
                'limits': {'min': 1, 'max': 50000},
                'fee': 0,
                'processing_time': 'Instant'
            },
            'paypal_transfer': {
                'template': 'banking/transfers/paypal_transfer.html',
                'title': 'PayPal Transfer',
                'description': 'Send money via PayPal worldwide',
                'features': ['Global reach', 'Buyer protection', 'Instant to PayPal accounts'],
                'limits': {'min': 1, 'max': 10000},
                'fee': 2.9,
                'processing_time': 'Instant'
            },
            'stripe_transfer': {
                'template': 'banking/transfers/stripe_transfer.html',
                'title': 'Stripe Transfer',
                'description': 'Professional payment processing',
                'features': ['Secure processing', 'International support', 'Business-grade'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 2.4,
                'processing_time': '2-7 business days'
            },
            'flutterwave': {
                'template': 'banking/transfers/flutterwave_transfer.html',
                'title': 'Flutterwave Transfer',
                'description': 'African payment gateway',
                'features': ['Pan-African coverage', 'Mobile money', 'Local currency support'],
                'limits': {'min': 1, 'max': 15000},
                'fee': 1.4,
                'processing_time': 'Instant to 24 hours'
            },
            'wire_transfer': {
                'template': 'banking/transfers/wire_transfer.html',
                'title': 'Wire Transfer',
                'description': 'Secure international wire transfers',
                'features': ['Global coverage', 'High security', 'Large amounts'],
                'limits': {'min': 100, 'max': 1000000},
                'fee': 25,
                'processing_time': '1-3 business days'
            },
            'swift_transfer': {
                'template': 'banking/transfers/wire_transfer.html',
                'title': 'SWIFT Transfer',
                'description': 'International transfers via SWIFT network',
                'features': ['Worldwide coverage', 'Multi-currency', 'Tracking available'],
                'limits': {'min': 100, 'max': 500000},
                'fee': 35,
                'processing_time': '1-5 business days'
            },
            'ach_transfer': {
                'template': 'banking/transfers/ach_transfer.html',
                'title': 'ACH Transfer',
                'description': 'US bank-to-bank transfers',
                'features': ['Low cost', 'Secure', 'US domestic only'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 0.50,
                'processing_time': '1-3 business days'
            },
            'fedwire': {
                'template': 'banking/transfers/fedwire_transfer.html',
                'title': 'Fedwire Transfer',
                'description': 'Federal Reserve real-time gross settlement',
                'features': ['Same-day settlement', 'Large amounts', 'Federal Reserve network'],
                'limits': {'min': 1000, 'max': 10000000},
                'fee': 30,
                'processing_time': 'Same day'
            },
            'blockchain_transfer': {
                'template': 'banking/transfers/blockchain_transfer.html',
                'title': 'Blockchain Transfer',
                'description': 'Cryptocurrency and digital asset transfers',
                'features': ['Decentralized', 'Global reach', 'Smart contracts'],
                'limits': {'min': 1, 'max': 100000},
                'fee': 2.0,
                'processing_time': '5-30 minutes'
            },
            'mojaloop': {
                'template': 'banking/transfers/mojaloop_transfer.html',
                'title': 'Mojaloop Transfer',
                'description': 'Open-source financial inclusion platform',
                'features': ['Financial inclusion', 'Interoperability', 'Low cost'],
                'limits': {'min': 1, 'max': 25000},
                'fee': 0.05,
                'processing_time': 'Real-time'
            },
            'mobile_transfer': {
                'template': 'banking/transfers/mobile_transfer.html',
                'title': 'Mobile Transfer',
                'description': 'Mobile money and SMS-based transfers',
                'features': ['No internet required', 'SMS-based', 'Mobile wallet'],
                'limits': {'min': 1, 'max': 5000},
                'fee': 1.0,
                'processing_time': 'Instant'
            },
            'nvct_stablecoin': {
                'template': 'banking/transfers/nvct_stablecoin_transfer.html',
                'title': 'NVCT Stablecoin Transfer',
                'description': 'NVC token stablecoin transfers',
                'features': ['Stable value', 'Blockchain-based', 'Low volatility'],
                'limits': {'min': 1, 'max': 1000000},
                'fee': 0.25,
                'processing_time': '2-5 minutes'
            }
        }

        # Get configuration for selected channel
        config = channel_configs.get(channel, channel_configs['internal_transfer'])

        context = {
            'accounts': user_accounts,
            'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'NVCT', 'BTC', 'ETH'],
            'channel': channel,
            'channel_config': config,
            'page_title': config['title']
        }

        # Add troubleshooting headers for better debugging
        response = make_response(render_template(config['template'], **context))
        response.headers['X-Served-Channel'] = channel
        response.headers['X-Template-Used'] = config['template']
        response.headers['X-Final-URL'] = f"/banking/transfers/new?channel={channel}"
        
        # Enhanced response logging with served details (development/verbose only)
        served_details = f"Template={config['template']}, Channel={channel}, Title={config['title']}"
        if is_development:
            logger.info(f"🎯 SERVING: {served_details}")
            logger.info(f"🎯 RESPONSE DETAILS: 200 OK | Served: {served_details} | URL: /banking/transfers/new?channel={channel}")
            print(f"🎯 SERVING: {served_details}")
            print(f"🎯 RESPONSE DETAILS: 200 OK | Served: {served_details} | URL: /banking/transfers/new?channel={channel}")
        else:
            # Production: minimal logging for troubleshooting
            logger.debug(f"Transfer channel served: {channel} -> {config['template']}")
        
        return response

    except Exception as e:
        error_service.log_error(f"New transfer page error: {str(e)}", current_user.id)
        flash('Unable to load transfer form. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers/send', methods=['POST'])
@login_required
def process_send_transfer():
    """Process money transfer"""
    try:
        transfer_data = {
            'from_account': request.form.get('from_account'),
            'to_account': request.form.get('to_account'),
            'amount': request.form.get('amount'),
            'currency': request.form.get('currency', 'USD'),
            'description': request.form.get('description', ''),
            'user_id': current_user.id
        }

        # Validate transfer amount
        try:
            amount = Decimal(transfer_data['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            flash('Invalid transfer amount.', 'error')
            return redirect(url_for('banking.transfers'))

        result = banking_service.process_transfer(transfer_data)

        if result['success']:
            flash(f'Transfer initiated successfully. Reference: {result["transfer"]["transfer_id"]}', 'success')
        else:
            flash(f'Transfer failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Transfer processing error: {str(e)}", current_user.id)
        flash('Unable to process transfer. Please try again.', 'error')

    return redirect(url_for('banking.transfers'))

# Card Management Routes
@banking_bp.route('/cards')
@login_required
def cards():
    """Card management page"""
    try:
        user_cards = banking_service.get_user_cards(current_user.id)
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'cards': user_cards,
            'accounts': user_accounts,
            'page_title': 'Card Management'
        }

        return render_template('banking/modular_banking_cards.html', **context)

    except Exception as e:
        error_service.log_error(f"Cards page error: {str(e)}", current_user.id)
        flash('Unable to load cards. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/cards/apply', methods=['GET', 'POST'])
@login_required
def apply_card():
    """Card application"""
    if request.method == 'POST':
        try:
            card_data = {
                'card_type': request.form.get('card_type'),
                'network': request.form.get('network'),
                'linked_account': request.form.get('linked_account'),
                'express_delivery': request.form.get('express_delivery') == 'on'
            }

            result = banking_service.apply_for_card(current_user.id, card_data)

            if result['success']:
                flash(f'Card application submitted. Application ID: {result["application"]["application_id"]}', 'success')
                return redirect(url_for('banking.cards'))
            else:
                flash(f'Card application failed: {result["error"]}', 'error')

        except Exception as e:
            error_service.log_error(f"Card application error: {str(e)}", current_user.id)
            flash('Unable to submit card application. Please try again.', 'error')

    # GET request - show card application form
    user_accounts = banking_service.get_user_accounts(current_user.id)

    context = {
        'card_types': ['Debit', 'Credit', 'Prepaid'],
        'networks': ['Visa', 'Mastercard', 'American Express', 'Discover'],
        'accounts': user_accounts,
        'page_title': 'Apply for Card'
    }

    # Generate CSRF token properly
    from flask_wtf.csrf import generate_csrf
    context['csrf_token'] = generate_csrf()

    return render_template('banking/modular_banking_card_application.html', **context)

# Payment Routes
@banking_bp.route('/payments')
@login_required
def payments():
    """Payment management page"""
    try:
        payment_methods = banking_service.get_payment_methods(current_user.id)

        context = {
            'payment_methods': payment_methods,
            'page_title': 'Payment Management'
        }

        return render_template('banking/modular_banking_payments.html', **context)

    except Exception as e:
        error_service.log_error(f"Payments page error: {str(e)}", current_user.id)
        flash('Unable to load payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/payments/send', methods=['POST'])
@login_required
def send_payment():
    """Process payment"""
    try:
        payment_data = {
            'recipient': request.form.get('recipient'),
            'amount': request.form.get('amount'),
            'currency': request.form.get('currency', 'USD'),
            'payment_method': request.form.get('payment_method'),
            'description': request.form.get('description', ''),
            'user_id': current_user.id
        }

        result = banking_service.process_payment(payment_data)

        if result['success']:
            flash(f'Payment processed successfully. Reference: {result["payment"]["payment_id"]}', 'success')
        else:
            flash(f'Payment failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Payment processing error: {str(e)}", current_user.id)
        flash('Unable to process payment. Please try again.', 'error')

    return redirect(url_for('banking.payments'))

# Transfer History
@banking_bp.route('/transfer-history')
@banking_bp.route('/transaction_history')  # Add alias for legacy navigation links
@login_required
def transfer_history():
    """Transfer history page"""
    try:
        transfers = banking_service.get_transfer_history(current_user.id, limit=100)

        context = {
            'transfers': transfers,
            'page_title': 'Transfer History'
        }

        return render_template('banking/transfer_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transfer history error: {str(e)}", current_user.id)
        flash('Unable to load transfer history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Transaction History
@banking_bp.route('/history')
@banking_bp.route('/transaction-history')  # Alias for convenience
@login_required
def transaction_history():
    """Complete transaction history"""
    try:
        transfers = banking_service.get_transfer_history(current_user.id, limit=100)

        context = {
            'transactions': transfers,
            'page_title': 'Transaction History'
        }

        return render_template('banking/modular_banking_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transaction history error: {str(e)}", current_user.id)
        flash('Unable to load transaction history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Account Statements
@banking_bp.route('/statements')
@login_required
def statements():
    """Account statements page"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)

        context = {
            'accounts': user_accounts,
            'page_title': 'Account Statements'
        }

        return render_template('banking/modular_banking_statements.html', **context)

    except Exception as e:
        error_service.log_error(f"Statements page error: {str(e)}", current_user.id)
        flash('Unable to load statements. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/statements/generate', methods=['GET', 'POST'])
@login_required
def generate_statement():
    """Generate account statement"""
    try:
        if request.method == 'GET':
            # Show statement generation form
            accounts = banking_service.get_user_accounts(current_user.id)
            return render_template('banking/generate_statement.html', accounts=accounts)

        # POST request - process statement generation
        account_id = request.form.get('account_id')
        period = request.form.get('period', 'monthly')

        if not account_id:
            flash('Please select an account.', 'error')
            return redirect(url_for('banking.generate_statement'))

        result = banking_service.generate_statement(current_user.id, int(account_id), period)

        if result['success']:
            flash(f'Statement generated successfully. ID: {result["statement"]["statement_id"]}', 'success')
        else:
            flash(f'Statement generation failed: {result["error"]}', 'error')

    except Exception as e:
        error_service.log_error(f"Statement generation error: {str(e)}", current_user.id)
        flash('Unable to generate statement. Please try again.', 'error')

    return redirect(url_for('banking.statements'))

@banking_bp.route('/accounts/history')
@login_required
def history():
    """Transaction history page"""
    try:
        # Sample transaction data for display
        sample_transactions = [
            {
                'id': 1,
                'date': 'December 17, 2024',
                'time': '2:30 PM',
                'description': 'Transfer to Savings',
                'type': 'transfer',
                'amount': -500.00,
                'balance': 45280.25,
                'status': 'completed',
                'reference': 'TXN-001',
                'account_number': 'SAV-007-000001',
                'account_type': 'Checking'
            },
            {
                'id': 2,
                'date': 'December 15, 2024',
                'time': '10:15 AM',
                'description': 'Salary Deposit',
                'type': 'deposit',
                'amount': 3500.00,
                'balance': 45780.25,
                'status': 'completed',
                'reference': 'TXN-002',
                'account_number': 'SAV-007-000001',
                'account_type': 'Checking'
            }
        ]

        context = {
            'transactions': sample_transactions,
            'page_title': 'Transaction History'
        }

        logger.info(f"Transaction history accessed by user {current_user.id}")
        return render_template('banking/modular_banking_history.html', **context)

    except Exception as e:
        error_service.log_error(f"Transaction history error: {str(e)}", current_user.id)
        flash('Unable to load transaction history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate create_account function removed - using main one at line 75

@banking_bp.route('/security')
@login_required
def security():
    """Banking security settings"""
    return render_template('banking/modular_banking_security.html', 
                         user=current_user, 
                         page_title='Security Settings')

# Duplicate send_transfer function removed - using main one at line 137

# Duplicate apply_card function removed - using main one at line 195

# Legacy Banking Operations Integration (Phase 3 Consolidation)

@banking_bp.route('/payment-history')
@login_required
def payment_history():
    """Payment history from legacy payment routes"""
    try:
        payments = banking_service.get_payment_history(current_user.id)

        logger.info(f"Payment history accessed by user {current_user.id}")
        return render_template('banking/legacy_payment_history.html', 
                             payments=payments, 
                             title="Payment History")
    except Exception as e:
        error_service.log_error(f"Payment history error: {str(e)}", current_user.id)
        flash('Unable to load payment history. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/make-payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    """Make payment from legacy payment routes"""
    try:
        if request.method == 'POST':
            payment_data = {
                'user_id': current_user.id,
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'payment_method': request.form.get('payment_method'),
                'description': request.form.get('description', '')
            }

            result = banking_service.process_payment(payment_data)

            if result.get('success'):
                flash('Payment processed successfully.', 'success')
                logger.info(f"Payment processed by user {current_user.id}: {result['payment']['payment_id']}")
                return redirect(url_for('banking.payment_history'))
            else:
                flash(f'Payment failed: {result.get("error")}', 'error')

        # GET request - show payment form
        gateways = banking_service.get_payment_gateways(current_user.id)

        return render_template('banking/legacy_make_payment.html', 
                             gateways=gateways, 
                             title="Make Payment")
    except Exception as e:
        error_service.log_error(f"Make payment error: {str(e)}", current_user.id)
        flash('Unable to process payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate transaction_history function removed - using main one at line 280

@banking_bp.route('/transaction-details/<transaction_id>')
@login_required
def transaction_details(transaction_id):
    """Transaction details from legacy banking routes"""
    try:
        transaction = banking_service.get_transaction_details(current_user.id, transaction_id)

        if not transaction:
            flash('Transaction not found.', 'error')
            return redirect(url_for('banking.transaction_history'))

        logger.info(f"Transaction details accessed by user {current_user.id}: {transaction_id}")
        return render_template('banking/legacy_transaction_details.html', 
                             transaction=transaction, 
                             title="Transaction Details")
    except Exception as e:
        error_service.log_error(f"Transaction details error: {str(e)}", current_user.id)
        flash('Unable to load transaction details. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

@banking_bp.route('/account-statements')
@login_required
def account_statements():
    """Account statements from legacy banking routes"""
    try:
        accounts = banking_service.get_user_accounts(current_user.id)

        # Default to first account if available
        account_id = request.args.get('account_id')
        if not account_id and accounts:
            account_id = accounts[0]['id']

        statement = None
        if account_id:
            statement = banking_service.get_account_statements(current_user.id, int(account_id))

        logger.info(f"Account statements accessed by user {current_user.id}")
        return render_template('banking/legacy_account_statements.html', 
                             accounts=accounts, 
                             statement=statement, 
                             selected_account=account_id,
                             title="Account Statements")
    except Exception as e:
        error_service.log_error(f"Account statements error: {str(e)}", current_user.id)
        flash('Unable to load account statements. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/business-services')
@login_required
def business_services():
    """Business banking services from legacy business routes"""
    try:
        services = banking_service.get_business_banking_services(current_user.id)

        logger.info(f"Business services accessed by user {current_user.id}")
        return render_template('banking/legacy_business_services.html', 
                             services=services, 
                             title="Business Banking Services")
    except Exception as e:
        error_service.log_error(f"Business services error: {str(e)}", current_user.id)
        flash('Unable to load business services. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/international-transfers')
@login_required
def international_transfers():
    """International transfer options from legacy transfer routes"""
    try:
        options = banking_service.get_international_transfer_options(current_user.id)

        logger.info(f"International transfers accessed by user {current_user.id}")
        return render_template('banking/legacy_international_transfers.html', 
                             transfer_options=options, 
                             title="International Transfers")
    except Exception as e:
        error_service.log_error(f"International transfers error: {str(e)}", current_user.id)
        flash('Unable to load international transfer options. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Additional Missing Banking Routes for Navigation Dropdown

@banking_bp.route('/wire-transfers')
@login_required
def wire_transfers():
    """Wire transfer services"""
    try:
        wire_data = {
            'available_currencies': ['USD', 'EUR', 'GBP', 'JPY'],
            'processing_times': {'standard': '1-3 days', 'express': 'same day'},
            'fees': {'domestic': 15, 'international': 45}
        }

        return render_template('banking/wire_transfers.html', 
                             wire_data=wire_data,
                             page_title='Wire Transfers')
    except Exception as e:
        error_service.log_error(f"Wire transfers error: {str(e)}", current_user.id)
        flash('Unable to load wire transfers. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/bill-payment')
@banking_bp.route('/bill_payment')  # Add alias for legacy navigation links
@login_required
def bill_payment():
    """Enhanced bill payment services with comprehensive features"""
    try:
        # Get comprehensive bill payment data
        payment_history = banking_service.get_bill_payment_history(current_user.id)
        saved_payees = banking_service.get_saved_payees(current_user.id)

        bill_data = {
            'bill_categories': ['Utilities', 'Telecom', 'Insurance', 'Loans', 'Credit Cards'],
            'saved_payees': saved_payees,
            'payment_history': payment_history,
            'quick_pay_options': [
                {'name': 'Electric Company', 'category': 'Utilities', 'last_amount': '125.45'},
                {'name': 'Internet Provider', 'category': 'Telecom', 'last_amount': '89.99'},
                {'name': 'Auto Insurance', 'category': 'Insurance', 'last_amount': '234.67'}
            ],
            'monthly_stats': {
                'total_paid': sum([float(p.get('amount', 0)) for p in payment_history[:30]]),  
                'payments_count': len(payment_history),
                'avg_amount': sum([float(p.get('amount', 0)) for p in payment_history[:10]]) / max(len(payment_history[:10]), 1)
            }
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''

        return render_template('banking/bill_payment.html', 
                             bill_data=bill_data,
                             page_title='Bill Payment',
                             csrf_token=csrf_token)
    except Exception as e:
        error_service.log_error(f"Bill payment error: {str(e)}", current_user.id)
        flash('Unable to load bill payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/process-bill-payment', methods=['POST'])
@login_required
def process_bill_payment():
    """Process bill payment"""
    try:
        payment_data = {
            'payee_name': request.form.get('payee_name'),
            'account_number': request.form.get('account_number'),
            'amount': float(request.form.get('amount', 0)),
            'category': request.form.get('category'),
            'due_date': request.form.get('due_date'),
            'memo': request.form.get('memo', '')
        }

        # Process the payment (this would integrate with actual payment processing)
        result = banking_service.process_bill_payment(current_user.id, payment_data)

        if result.get('success'):
            flash(f'Bill payment processed successfully. Reference: {result.get("reference_id")}', 'success')
        else:
            flash(f'Bill payment failed: {result.get("error", "Unknown error")}', 'error')

    except Exception as e:
        error_service.log_error(f"Bill payment processing error: {str(e)}", current_user.id)
        flash('Unable to process bill payment. Please try again.', 'error')

    return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/schedule-bill-payment', methods=['POST'])
@login_required
def schedule_bill_payment():
    """Schedule a future bill payment"""
    try:
        payment_data = {
            'payee_name': request.form.get('payee_name'),
            'amount': float(request.form.get('amount', 0)),
            'category': request.form.get('category'),
            'scheduled_date': request.form.get('scheduled_date'),
            'frequency': request.form.get('frequency', 'once')
        }

        result = banking_service.schedule_bill_payment(current_user.id, payment_data)

        if result.get('success'):
            flash(f'Bill payment scheduled successfully. Schedule ID: {result.get("schedule_id")}', 'success')
        else:
            flash(f'Scheduling failed: {result.get("error", "Unknown error")}', 'error')

    except Exception as e:
        error_service.log_error(f"Bill payment scheduling error: {str(e)}", current_user.id)
        flash('Unable to schedule bill payment. Please try again.', 'error')

    return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/saved-payees')
@login_required
def saved_payees():
    """View and manage saved payees"""
    try:
        payees = banking_service.get_saved_payees(current_user.id)
        
        return render_template('banking/saved_payees.html',
                             payees=payees,
                             page_title='Saved Payees')
    except Exception as e:
        error_service.log_error(f"Saved payees error: {str(e)}", current_user.id)
        flash('Unable to load saved payees. Please try again.', 'error')
        return redirect(url_for('banking.bill_payment'))

@banking_bp.route('/scheduled-payments')
@login_required
def scheduled_payments():
    """Scheduled payment management"""
    try:
        scheduled_data = {
            'upcoming_payments': [],
            'payment_templates': []
        }

        return render_template('banking/scheduled_payments.html', 
                             scheduled_data=scheduled_data,
                             page_title='Scheduled Payments')
    except Exception as e:
        error_service.log_error(f"Scheduled payments error: {str(e)}", current_user.id)
        flash('Unable to load scheduled payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/recurring-payments')
@login_required
def recurring_payments():
    """Recurring payment management"""
    try:
        recurring_data = {
            'active_subscriptions': [],
            'payment_schedules': []
        }

        return render_template('banking/recurring_payments.html', 
                             recurring_data=recurring_data,
                             page_title='Recurring Payments')
    except Exception as e:
        error_service.log_error(f"Recurring payments error: {str(e)}", current_user.id)
        flash('Unable to load recurring payments. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/notifications')
@login_required
def notifications():
    """Banking notifications"""
    try:
        notifications_data = {
            'unread_notifications': [],
            'notification_settings': {}
        }

        return render_template('banking/notifications.html', 
                             notifications_data=notifications_data,
                             page_title='Notifications')
    except Exception as e:
        error_service.log_error(f"Notifications error: {str(e)}", current_user.id)
        flash('Unable to load notifications. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/preferences')
@login_required
def preferences():
    """Banking preferences"""
    try:
        preferences_data = {
            'language': 'en',
            'currency': 'USD',
            'timezone': 'UTC'
        }

        return render_template('banking/preferences.html', 
                             preferences_data=preferences_data,
                             page_title='Preferences')
    except Exception as e:
        error_service.log_error(f"Preferences error: {str(e)}", current_user.id)
        flash('Unable to load preferences. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Transaction Statement Download
@banking_bp.route('/statements/transaction/<int:transaction_id>')
@login_required
def download_transaction_statement(transaction_id):
    """Download transaction statement/receipt as PDF"""
    try:
        from flask import make_response
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import black, blue
        from reportlab.lib.units import inch
        from io import BytesIO

        # Get transaction details
        transaction = banking_service.get_transaction_details(current_user.id, transaction_id)

        if not transaction:
            flash('Transaction not found.', 'error')
            return redirect(url_for('banking.transaction_history'))

        # Create PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        p.setFont("Helvetica-Bold", 18)
        p.setFillColor(blue)
        p.drawString(50, height - 50, "NVC BANKING PLATFORM")

        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(black)
        p.drawString(50, height - 80, "Transaction Receipt")

        # Draw line
        p.line(50, height - 90, width - 50, height - 90)

        # Transaction details
        y_position = height - 130
        line_height = 25

        p.setFont("Helvetica", 12)

        details = [
            f"Transaction ID: {transaction_id}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Account: ****{str(transaction_id)[-4:]}",
            f"Type: Transfer",
            f"Amount: $500.00",
            f"Status: Completed",
            "",
            f"Reference: REF-{transaction_id}",
            f"Description: Monthly rent payment"
        ]
        y_position -= 15
        p.drawString(50, y_position, "Phone: (555) 123-4567")

        # Disclaimer
        y_position -= 30
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, y_position, "This is a computer-generated receipt. No signature required.")

        # Save PDF
        p.showPage()
        p.save()

        # Get PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()

        # Create response for download
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=transaction_{transaction_id}_receipt.pdf'

        logger.info(f"Transaction PDF statement downloaded by user {current_user.id}: {transaction_id}")
        return response

    except Exception as e:
        error_service.log_error(f"Transaction PDF statement download error: {str(e)}", current_user.id)
        flash('Unable to download transaction statement. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

# Drill-down routes for detailed views
@banking_bp.route('/accounts/detailed')
@login_required
def accounts_detailed():
    """Detailed accounts drill-down view"""
    try:
        user_accounts = banking_service.get_user_accounts(current_user.id)
        
        context = {
            'accounts': user_accounts,
            'page_title': 'Detailed Accounts'
        }
        
        return render_template('banking/modular_banking_accounts.html', **context)
    except Exception as e:
        error_service.log_error(f"Accounts detailed view error: {str(e)}", current_user.id)
        flash('Unable to load detailed accounts. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers/management')
@login_required
def transfers_management():
    """Transfer management drill-down view"""
    try:
        return render_template('banking/transfers_management.html',
                             user=current_user,
                             page_title='Transfer Management')
    except Exception as e:
        error_service.log_error("TRANSFERS_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/cards/management')
@login_required
def cards_management():
    """Cards management drill-down view"""
    try:
        return render_template('banking/cards_management.html',
                             user=current_user,
                             page_title='Cards Management')
    except Exception as e:
        error_service.log_error("CARDS_MANAGEMENT_ERROR", str(e), {"user_id": current_user.id})
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transactions-analysis')
@login_required
def transactions_analysis():
    """Transaction analysis page"""
    try:
        # Get user transaction analytics
        transactions = banking_service.get_transfer_history(current_user.id, limit=100)
        
        # Basic analytics for now
        analytics = {
            'total_transactions': len(transactions),
            'total_amount': sum(t.get('amount', 0) for t in transactions),
            'average_amount': sum(t.get('amount', 0) for t in transactions) / len(transactions) if transactions else 0,
            'monthly_trend': []  # Can be enhanced later
        }
        
        return render_template('banking/transaction_history.html',
                             transactions=transactions,
                             analytics=analytics,
                             user=current_user,
                             page_title='Transaction Analysis')
    except Exception as e:
        error_service.log_error("TRANSACTIONS_ANALYSIS_ERROR", str(e), {"user_id": current_user.id})
        flash('Unable to load transaction analysis', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Account Detail Routes
# Payment Gateway Integration Routes (now handled by payment_gateways module)

@banking_bp.route('/accounts/<account_id>')
@login_required
def account_details(account_id):
    """Individual account details view"""
    try:
        # Get account details for the specific account
        account_data = {
            'account_id': account_id,
            'account_type': 'Savings Account' if 'SAV' in account_id else 'Checking Account',
            'balance': 45750.00,
            'available_balance': 45750.00,
            'account_number': account_id,
            'routing_number': '123456789',
            'interest_rate': 2.5 if 'SAV' in account_id else 0.1,
            'opened_date': '2023-01-15',
            'status': 'Active'
        }

        # Get recent transactions for this account
        recent_transactions = [
            {
                'date': '2025-01-05',
                'description': 'Direct Deposit - Salary',
                'amount': 5500.00,
                'type': 'credit',
                'balance': 45750.00
            },
            {
                'date': '2025-01-04',
                'description': 'Online Transfer',
                'amount': -150.00,
                'type': 'debit',
                'balance': 40250.00
            },
            {
                'date': '2025-01-03',
                'description': 'ATM Withdrawal',
                'amount': -200.00,
                'type': 'debit',
                'balance': 40400.00
            }
        ]

        return render_template('banking/account_details.html',
                             account=account_data,
                             transactions=recent_transactions,
                             page_title=f'Account Details - {account_id}')

    except Exception as e:
        error_service.log_error(f"Account details error: {str(e)}", current_user.id)
        flash('Unable to load account details. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate create_account function removed - using main one at line 75

# Duplicate apply_card function removed - using main one at line 195

# Legacy Banking Operations Integration (Phase 3 Consolidation)

        flash('Unable to load transaction details. Please try again.', 'error')
        return redirect(url_for('banking.transaction_history'))

# Additional Missing Banking Routes for Navigation Dropdown

    try:
        # Get bill payment history for the current user
        payment_history = banking_service.get_bill_payment_history(current_user.id)

        bill_data = {
            'bill_categories': ['Utilities', 'Telecom', 'Insurance', 'Loans', 'Credit Cards'],
            'saved_payees': [],
            'payment_history': payment_history
        }

        # Generate CSRF token safely
        try:
            csrf_token = generate_csrf()
        except Exception as csrf_error:
            logger.error(f"CSRF token generation error: {csrf_error}")
            csrf_token = ''

        return render_template('banking/bill_payment.html', 
                             bill_data=bill_data,
                             page_title='Bill Payment',
                             csrf_token=csrf_token)
    except Exception as e:
        logger.error(f"Bill payment error: {str(e)} - User: {current_user.id}")
        flash('Unable to load bill payment. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/crypto-portfolio')
@login_required
def crypto_portfolio():
    """Crypto portfolio dashboard"""
    try:
        crypto_data = {
            'total_portfolio_value': 125000.00,
            'total_holdings': 8,
            'portfolio_change_24h': 3.2,
            'holdings': [
                {
                    'symbol': 'BTC',
                    'name': 'Bitcoin',
                    'amount': 2.5,
                    'value': 87500.00,
                    'change_24h': 2.1
                },
                {
                    'symbol': 'ETH',
                    'name': 'Ethereum',
                    'amount': 15.0,
                    'value': 30000.00,
                    'change_24h': 4.5
                },
                {
                    'symbol': 'NVCT',
                    'name': 'NVCT Stablecoin',
                    'amount': 7500.0,
                    'value': 7500.00,
                    'change_24h': 0.0
                }
            ]
        }

        return render_template('banking/crypto_portfolio.html',
                             crypto_data=crypto_data,
                             page_title='Crypto Portfolio')
    except Exception as e:
        error_service.log_error(f"Crypto portfolio error: {str(e)}", current_user.id)
        flash('Unable to load crypto portfolio. Please try again.', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Loan management routes (referenced in loan officer dashboard)
@banking_bp.route('/loans/pending-applications')
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

        return render_template('banking/pending_applications.html',
                             applications_data=applications_data,
                             page_title='Pending Loan Applications')
    except Exception as e:
        error_service.log_error(f"Pending applications error: {str(e)}", current_user.id)
        flash('Unable to load pending applications. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@banking_bp.route('/loans/approved-loans')
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

        return render_template('banking/approved_loans.html',
                             approved_data=approved_data,
                             page_title='Approved Loans')
    except Exception as e:
        error_service.log_error(f"Approved loans error: {str(e)}", current_user.id)
        flash('Unable to load approved loans. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

@banking_bp.route('/loans/portfolio-overview')
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

        return render_template('banking/portfolio_overview.html',
                             portfolio_data=portfolio_data,
                             page_title='Loan Portfolio Overview')
    except Exception as e:
        error_service.log_error(f"Portfolio overview error: {str(e)}", current_user.id)
        flash('Unable to load portfolio overview. Please try again.', 'error')
        return redirect(url_for('dashboard.loan_officer_dashboard'))

# Additional missing routes referenced in templates
@banking_bp.route('/account-management')
@login_required
def account_management():
    """Account management dashboard"""
    try:
        account_data = {
            'total_accounts': 15247,
            'active_accounts': 14892,
            'pending_accounts': 355,
            'account_types': [
                {'type': 'Checking', 'count': 8500, 'percentage': 56},
                {'type': 'Savings', 'count': 4200, 'percentage': 28},
                {'type': 'Business', 'count': 2547, 'percentage': 16}
            ]
        }
        return render_template('banking/account_management.html',
                             account_data=account_data,
                             page_title='Account Management')
    except Exception as e:
        logger.error(f"Account management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/customer-details')
@login_required
def customer_details():
    """Customer details view"""
    try:
        customer_id = request.args.get('id', '12345')
        customer_data = {
            'id': customer_id,
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1-555-0123',
            'account_balance': 25000.00,
            'account_type': 'Premium Checking',
            'member_since': '2020-03-15',
            'last_login': '2025-01-15 10:30'
        }
        return render_template('banking/customer_details.html',
                             customer_data=customer_data,
                             page_title='Customer Details')
    except Exception as e:
        logger.error(f"Customer details error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/customer-management')
@login_required
def customer_management():
    """Customer management dashboard"""
    try:
        customer_data = {
            'total_customers': 15247,
            'new_customers': 342,
            'active_customers': 14892,
            'customer_segments': [
                {'segment': 'Individual', 'count': 12500, 'percentage': 82},
                {'segment': 'Business', 'count': 2000, 'percentage': 13},
                {'segment': 'Institutional', 'count': 747, 'percentage': 5}
            ]
        }
        return render_template('banking/customer_management.html',
                             customer_data=customer_data,
                             page_title='Customer Management')
    except Exception as e:
        logger.error(f"Customer management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transaction-management')
@login_required
def transaction_management():
    """Transaction management dashboard"""
    try:
        transaction_data = {
            'daily_transactions': 2547,
            'pending_transactions': 45,
            'failed_transactions': 12,
            'transaction_volume': 12500000.00,
            'success_rate': 98.7
        }
        return render_template('banking/transaction_management.html',
                             transaction_data=transaction_data,
                             page_title='Transaction Management')
    except Exception as e:
        logger.error(f"Transaction management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/pending-approvals')
@login_required
def pending_approvals():
    """Pending approvals dashboard"""
    try:
        approval_data = {
            'pending_loans': 15,
            'pending_accounts': 8,
            'pending_transfers': 23,
            'pending_cards': 12,
            'total_pending': 58
        }
        return render_template('banking/pending_approvals.html',
                             approval_data=approval_data,
                             page_title='Pending Approvals')
    except Exception as e:
        logger.error(f"Pending approvals error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Additional missing routes referenced from dashboard templates
@banking_bp.route('/institutional-account-creation')
@login_required
def institutional_account_creation():
    """Institutional account creation"""
    try:
        institutional_data = {
            'account_types': ['Corporate Checking', 'Business Savings', 'Treasury Management'],
            'minimum_deposits': {'Corporate Checking': 25000, 'Business Savings': 50000, 'Treasury Management': 100000},
            'required_documents': ['Articles of Incorporation', 'Tax ID', 'Board Resolution']
        }
        return render_template('banking/institutional_account_creation.html',
                             institutional_data=institutional_data,
                             page_title='Institutional Account Creation')
    except Exception as e:
        logger.error(f"Institutional account creation error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/modular-banking-create-account')
@login_required
def modular_banking_create_account():
    """Modular banking account creation"""
    try:
        account_options = {
            'personal_accounts': ['Checking', 'Savings', 'Money Market'],
            'business_accounts': ['Business Checking', 'Business Savings', 'Merchant Services'],
            'investment_accounts': ['Brokerage', 'IRA', 'Trust Account']
        }
        return render_template('banking/modular_banking_create_account.html',
                             account_options=account_options,
                             page_title='Create Account')
    except Exception as e:
        logger.error(f"Modular banking create account error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/modular-banking-dashboard')
@login_required
def modular_banking_dashboard():
    """Modular banking dashboard"""
    try:
        modular_data = {
            'active_modules': ['Accounts', 'Transfers', 'Cards', 'Loans'],
            'account_summary': {'total_accounts': 5, 'total_balance': 125000.00},
            'recent_activity': [
                {'type': 'Transfer', 'amount': 2500.00, 'date': '2025-01-15'},
                {'type': 'Payment', 'amount': 450.00, 'date': '2025-01-14'}
            ]
        }
        return render_template('banking/modular_banking_dashboard.html',
                             modular_data=modular_data,
                             page_title='Modular Banking Dashboard')
    except Exception as e:
        logger.error(f"Modular banking dashboard error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/modular-banking-history')
@login_required
def modular_banking_history():
    """Modular banking transaction history"""
    try:
        # Get transaction history for the current user
        transfers = banking_service.get_transfer_history(current_user.id, limit=50)

        # Sample data if no transfers found
        if not transfers:
            transfers = [
                {
                    'id': 'TXN001',
                    'date': '2025-01-15',
                    'description': 'Transfer to Savings',
                    'amount': -2500.00,
                    'balance': 47500.00,
                    'type': 'transfer',
                    'status': 'completed'
                },
                {
                    'id': 'TXN002',
                    'date': '2025-01-14',
                    'description': 'Direct Deposit',
                    'amount': 5500.00,
                    'balance': 50000.00,
                    'type': 'deposit',
                    'status': 'completed'
                },
                {
                    'id': 'TXN003',
                    'date': '2025-01-13',
                    'description': 'Bill Payment',
                    'amount': -450.00,
                    'balance': 44500.00,
                    'type': 'payment',
                    'status': 'completed'
                }
            ]

        context = {
            'transactions': transfers,
            'page_title': 'Transaction History',
            'total_transactions': len(transfers)
        }

        logger.info(f"Modular banking history accessed by user {current_user.id}")
        return render_template('banking/modular_banking_history.html', **context)

    except Exception as e:
        logger.error(f"Modular banking history error: {e}")
        flash('Error loading transaction history', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfers', methods=['GET'])
@login_required
def transfer_dashboard():
    """Transfer dashboard page"""
    try:
        # Get user's accounts for transfer options
        user_accounts = BankingAccount.query.filter_by(
            user_id=current_user.id,
            status='ACTIVE'
        ).all()
        
        # Get recent transfers
        recent_transfers = Transaction.query.filter(
            Transaction.account_id.in_([acc.id for acc in user_accounts]),
            Transaction.transaction_type.like('%TRANSFER%')
        ).order_by(Transaction.created_at.desc()).limit(10).all()
        
        return render_template('banking/transfer_dashboard.html',
                             page_title='Transfer Hub',
                             accounts=user_accounts,
                             recent_transfers=recent_transfers)
    except Exception as e:
        logger.error(f"Transfer dashboard error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.dashboard'))

@banking_bp.route('/api/transfers/internal', methods=['POST'])
@login_required
@require_session_security(max_age_minutes=30)
def internal_transfer():
    """Process internal transfer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_account', 'to_account', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Process transfer
        result = transfer_service.initiate_internal_transfer(
            from_account_id=data['from_account'],
            to_account_id=data['to_account'],
            amount=Decimal(str(data['amount'])),
            memo=data.get('memo')
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Internal transfer API error: {e}")
        return jsonify({'error': 'Transfer processing failed'}), 500

@banking_bp.route('/api/transfers/wire', methods=['POST'])
@login_required
@require_session_security(max_age_minutes=30)
def wire_transfer():
    """Process wire transfer"""
    try:
        data = request.get_json()
        
        # Validate wire transfer data
        required_fields = ['from_account', 'amount', 'beneficiary_name', 
                          'beneficiary_bank', 'swift_code']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required wire details'}), 400
        
        # Extract wire details
        wire_details = {
            'beneficiary_name': data['beneficiary_name'],
            'beneficiary_bank': data['beneficiary_bank'],
            'swift_code': data['swift_code'],
            'beneficiary_account': data.get('beneficiary_account'),
            'purpose': data.get('purpose', 'Personal transfer')
        }
        
        # Process wire transfer
        result = transfer_service.initiate_wire_transfer(
            from_account_id=data['from_account'],
            wire_details=wire_details,
            amount=Decimal(str(data['amount']))
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Wire transfer API error: {e}")
        return jsonify({'error': 'Wire transfer processing failed'}), 500

@banking_bp.route('/api/transfers/ach', methods=['POST'])
@login_required
@require_session_security(max_age_minutes=30)
def ach_transfer():
    """Process ACH transfer"""
    try:
        data = request.get_json()
        
        # Validate ACH data
        required_fields = ['from_account', 'to_routing', 'to_account', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required ACH details'}), 400
        
        # Process ACH transfer
        result = transfer_service.initiate_ach_transfer(
            from_account_id=data['from_account'],
            to_routing=data['to_routing'],
            to_account=data['to_account'],
            amount=Decimal(str(data['amount']))
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"ACH transfer API error: {e}")
        return jsonify({'error': 'ACH transfer processing failed'}), 500

@banking_bp.route('/modular-banking-history-alt')
@login_required
def modular_banking_history_alt():
    """Modular banking history page (alternative)"""
    try:
        history_data = {
            'total_transactions': 156,
            'date_range': '2024-01-01 to 2025-01-15'
        }
        return render_template('banking/modular_banking_history.html',
                             history_data=history_data,
                             page_title='Transaction History')
    except Exception as e:
        logger.error(f"Modular banking history error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transactions')
@login_required
def transactions():
    """Banking transactions - alias for transaction_history"""
    return transaction_history()

# Sub-module routes referenced from dashboard templates
@banking_bp.route('/banking-accounts/accounts')
@login_required
def banking_accounts_accounts():
    """Banking accounts sub-module"""
    try:
        accounts_data = {
            'total_accounts': 15247,
            'account_types': ['Checking', 'Savings', 'Business', 'Investment'],
            'new_accounts_today': 23,
            'account_summary': [
                {'type': 'Checking', 'count': 8500, 'total_balance': 125000000.00},
                {'type': 'Savings', 'count': 4200, 'total_balance': 89000000.00},
                {'type': 'Business', 'count': 2547, 'total_balance': 156000000.00}
            ]
        }
        return render_template('banking/banking_accounts.html',
                             accounts_data=accounts_data,
                             page_title='Banking Accounts')
    except Exception as e:
        logger.error(f"Banking accounts error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/banking-cards/new-card')
@login_required
def banking_cards_new_card():
    """Banking cards new card application"""
    try:
        card_options = {
            'card_types': ['Debit Card', 'Credit Card', 'Business Card', 'Premium Card'],
            'features': ['Contactless Payment', 'International Usage', 'Rewards Program'],
            'processing_time': '5-7 business days'
        }
        return render_template('banking/banking_cards_new.html',
                             card_options=card_options,
                             page_title='New Card Application')
    except Exception as e:
        logger.error(f"Banking cards new card error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/banking-loans/dashboard')
@login_required
def banking_loans_dashboard():
    """Banking loans dashboard"""
    try:
        loans_data = {
            'active_loans': 156,
            'total_loan_amount': 125000000.00,
            'pending_applications': 23,
            'loan_types': ['Personal', 'Business', 'Mortgage', 'Auto'],
            'default_rate': 2.1
        }
        return render_template('banking/banking_loans_dashboard.html',
                             loans_data=loans_data,
                             page_title='Banking Loans Dashboard')
    except Exception as e:
        logger.error(f"Banking loans dashboard error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/banking-operations/dashboard')
@login_required
def banking_operations_dashboard():
    """Banking operations dashboard"""
    try:
        operations_data = {
            'daily_transactions': 2547,
            'system_uptime': 99.9,
            'active_sessions': 1247,
            'processing_queue': 45,
            'operational_metrics': [
                {'metric': 'Transaction Success Rate', 'value': 99.7, 'status': 'Good'},
                {'metric': 'Average Processing Time', 'value': 2.3, 'status': 'Good'},
                {'metric': 'System Load', 'value': 67.5, 'status': 'Normal'}
            ]
        }
        return render_template('banking/banking_operations_dashboard.html',
                             operations_data=operations_data,
                             page_title='Banking Operations Dashboard')
    except Exception as e:
        logger.error(f"Banking operations dashboard error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/banking-transfers/transfers')
@login_required
def banking_transfers_transfers():
    """Banking transfers sub-module"""
    try:
        transfers_data = {
            'daily_transfers': 1247,
            'transfer_volume': 25000000.00,
            'pending_transfers': 23,
            'transfer_types': ['Internal', 'External', 'Wire', 'ACH'],
            'success_rate': 99.8
        }
        return render_template('banking/banking_transfers.html',
                             transfers_data=transfers_data,
                             page_title='Banking Transfers')
    except Exception as e:
        logger.error(f"Banking transfers error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Additional missing routes referenced in templates
@banking_bp.route('/active-sessions')
@login_required
def active_sessions():
    """Active banking sessions"""
    try:
        sessions_data = {
            'current_session': {
                'ip': '192.168.1.100',
                'location': 'New York, NY',
                'device': 'Chrome on Windows',
                'started': '2025-01-15 10:30'
            },
            'other_sessions': [
                {'ip': '192.168.1.101', 'location': 'Boston, MA', 'device': 'Safari on iPhone', 'started': '2025-01-14 15:20'},
                {'ip': '192.168.1.102', 'location': 'Chicago, IL', 'device': 'Firefox on Mac', 'started': '2025-01-13 09:15'}
            ],
            'session_settings': {
                'auto_logout': 30,
                'concurrent_sessions': 3,
                'notifications_enabled': True
            }
        }
        return render_template('banking/active_sessions.html',
                             sessions_data=sessions_data,
                             page_title='Active Sessions')
    except Exception as e:
        logger.error(f"Active sessions error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/add-payee')
@login_required
def add_payee():
    """Add new payee for payments"""
    try:
        payee_data = {
            'payee_types': ['Individual', 'Business', 'Utility Company', 'Government'],
            'required_fields': ['Name', 'Account Number', 'Routing Number'],
            'verification_methods': ['Micro Deposits', 'Instant Verification', 'Manual Review']
        }
        return render_template('banking/add_payee.html',
                             payee_data=payee_data,
                             page_title='Add Payee')
    except Exception as e:
        logger.error(f"Add payee error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/create-digital-account')
@login_required
def create_digital_account():
    """Create digital banking account"""
    try:
        account_options = {
            'digital_account_types': ['Digital Checking', 'Digital Savings', 'Digital Business'],
            'features': ['Mobile Banking', 'Online Banking', 'Digital Wallet Integration'],
            'requirements': ['Valid ID', 'Email Verification', 'Phone Verification'],
            'benefits': ['No Monthly Fees', 'Higher Interest Rates', 'Instant Transfers']
        }
        return render_template('banking/create_digital_account.html',
                             account_options=account_options,
                             page_title='Create Digital Account')
    except Exception as e:
        logger.error(f"Create digital account error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/deposit')
@login_required
def deposit():
    """Banking deposit interface"""
    try:
        deposit_data = {
            'deposit_methods': ['Mobile Check Deposit', 'ATM Deposit', 'Wire Transfer', 'Direct Deposit'],
            'account_options': [
                {'id': 'CHK001', 'name': 'Primary Checking', 'balance': 5000.00},
                {'id': 'SAV001', 'name': 'Savings Account', 'balance': 15000.00}
            ],
            'limits': {
                'mobile_check': 5000.00,
                'atm_deposit': 10000.00,
                'wire_transfer': 50000.00
            }
        }
        return render_template('banking/deposit.html',
                             deposit_data=deposit_data,
                             page_title='Make Deposit')
    except Exception as e:
        logger.error(f"Deposit error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/edit-payee')
@login_required
def edit_payee():
    """Edit existing payee information"""
    try:
        payee_id = request.args.get('id', '1')
        payee_data = {
            'payee_id': payee_id,
            'name': 'Electric Company',
            'account_number': '****1234',
            'routing_number': '****5678',
            'payee_type': 'Utility Company',
            'status': 'Active',
            'last_payment': '2025-01-10'
        }
        return render_template('banking/edit_payee.html',
                             payee_data=payee_data,
                             page_title='Edit Payee')
    except Exception as e:
        logger.error(f"Edit payee error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Additional missing routes (continued)
@banking_bp.route('/login-history')
@login_required
def login_history():
    """Banking login history"""
    try:
        login_data = {
            'recent_logins': [
                {'date': '2025-01-15 10:30', 'ip': '192.168.1.100', 'location': 'New York, NY', 'device': 'Chrome', 'status': 'Success'},
                {'date': '2025-01-14 15:20', 'ip': '192.168.1.101', 'location': 'Boston, MA', 'device': 'Safari', 'status': 'Success'},
                {'date': '2025-01-13 09:15', 'ip': '192.168.1.102', 'location': 'Chicago, IL', 'device': 'Firefox', 'status': 'Failed'}
            ],
            'security_settings': {
                'login_notifications': True,
                'failed_attempt_alerts': True,
                'new_device_alerts': True
            }
        }
        return render_template('banking/login_history.html',
                             login_data=login_data,
                             page_title='Login History')
    except Exception as e:
        logger.error(f"Login history error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/modular-banking-cards')
@login_required
def modular_banking_cards():
    """Modular banking cards management"""
    try:
        cards_data = {
            'active_cards': [
                {'id': 'CARD001', 'type': 'Debit', 'last_four': '1234', 'status': 'Active', 'expires': '12/27'},
                {'id': 'CARD002', 'type': 'Credit', 'last_four': '5678', 'status': 'Active', 'expires': '08/26'}
            ],
            'card_features': ['Contactless Payment', 'International Usage', 'Fraud Protection'],
            'available_designs': ['Classic', 'Premium', 'Custom']
        }
        return render_template('banking/modular_banking_cards.html',
                             cards_data=cards_data,
                             page_title='Banking Cards')
    except Exception as e:
        logger.error(f"Modular banking cards error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/schedule-payment')
@login_required
def schedule_payment():
    """Schedule future payment"""
    try:
        payment_data = {
            'payees': [
                {'id': 'PAY001', 'name': 'Electric Company', 'account': '****1234'},
                {'id': 'PAY002', 'name': 'Water Utility', 'account': '****5678'},
                {'id': 'PAY003', 'name': 'Internet Provider', 'account': '****9012'}
            ],
            'frequency_options': ['One-time', 'Weekly', 'Bi-weekly', 'Monthly', 'Quarterly'],
            'payment_methods': ['Checking Account', 'Savings Account', 'Credit Card']
        }
        return render_template('banking/schedule_payment.html',
                             payment_data=payment_data,
                             page_title='Schedule Payment')
    except Exception as e:
        logger.error(f"Schedule payment error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/security-alerts')
@login_required
def security_alerts():
    """Banking security alerts"""
    try:
        alerts_data = {
            'active_alerts': [
                {'type': 'Login Alert', 'message': 'New device login detected', 'date': '2025-01-15', 'severity': 'Medium'},
                {'type': 'Transaction Alert', 'message': 'Large transaction processed', 'date': '2025-01-14', 'severity': 'Low'}
            ],
            'alert_settings': {
                'login_alerts': True,
                'transaction_alerts': True,
                'card_usage_alerts': True,
                'account_changes_alerts': True
            },
            'notification_methods': ['Email', 'SMS', 'Push Notification']
        }
        return render_template('banking/security_alerts.html',
                             alerts_data=alerts_data,
                             page_title='Security Alerts')
    except Exception as e:
        logger.error(f"Security alerts error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/setup-bank-transfer')
@login_required
def setup_bank_transfer():
    """Setup bank transfer"""
    try:
        transfer_data = {
            'transfer_types': ['Internal Transfer', 'External Transfer', 'Wire Transfer', 'ACH Transfer'],
            'account_options': [
                {'id': 'CHK001', 'name': 'Primary Checking', 'balance': 5000.00},
                {'id': 'SAV001', 'name': 'Savings Account', 'balance': 15000.00}
            ],
            'external_accounts': [
                {'id': 'EXT001', 'bank': 'Chase Bank', 'account': '****1234', 'status': 'Verified'},
                {'id': 'EXT002', 'bank': 'Wells Fargo', 'account': '****5678', 'status': 'Pending'}
            ]
        }
        return render_template('banking/setup_bank_transfer.html',
                             transfer_data=transfer_data,
                             page_title='Setup Bank Transfer')
    except Exception as e:
        logger.error(f"Setup bank transfer error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/setup-mfa')
@login_required
def setup_mfa():
    """Setup MFA for banking"""
    try:
        mfa_data = {
            'mfa_methods': ['SMS', 'Email', 'Authenticator App', 'Hardware Token'],
            'current_status': 'Not Enabled',
            'security_level': 'Standard',
            'recommended_method': 'Authenticator App'
        }
        return render_template('banking/setup_mfa.html',
                             mfa_data=mfa_data,
                             page_title='Setup MFA')
    except Exception as e:
        logger.error(f"Setup MFA error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Final batch of missing routes
@banking_bp.route('/transfer-details')
@login_required
def transfer_details():
    """Transfer details view"""
    try:
        transfer_id = request.args.get('id', 'TXN001')
        transfer_data = {
            'transfer_id': transfer_id,
            'amount': 2500.00,
            'from_account': 'Primary Checking (****1234)',
            'to_account': 'Savings Account (****5678)',
            'date': '2025-01-15',
            'status': 'Completed',
            'reference_number': 'REF123456789',
            'fee': 0.00
        }
        return render_template('banking/transfer_details.html',
                             transfer_data=transfer_data,
                             page_title='Transfer Details')
    except Exception as e:
        logger.error(f"Transfer details error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/transfer-receipt')
@login_required
def transfer_receipt():
    """Transfer receipt view"""
    try:
        transfer_id = request.args.get('id', 'TXN001')
        receipt_data = {
            'transfer_id': transfer_id,
            'amount': 2500.00,
            'from_account': 'Primary Checking (****1234)',
            'to_account': 'Savings Account (****5678)',
            'date': '2025-01-15 10:30 AM',
            'confirmation_number': 'CONF123456789',
            'transaction_fee': 0.00,
            'total_amount': 2500.00
        }
        return render_template('banking/transfer_receipt.html',
                             receipt_data=receipt_data,
                             page_title='Transfer Receipt')
    except Exception as e:
        logger.error(f"Transfer receipt error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/withdrawal')
@login_required
def withdrawal():
    """Banking withdrawal interface"""
    try:
        withdrawal_data = {
            'withdrawal_methods': ['ATM', 'Bank Teller', 'Online Transfer', 'Check Request'],
            'account_options': [
                {'id': 'CHK001', 'name': 'Primary Checking', 'balance': 5000.00, 'available': 4500.00},
                {'id': 'SAV001', 'name': 'Savings Account', 'balance': 15000.00, 'available': 15000.00}
            ],
            'daily_limits': {
                'atm': 500.00,
                'online': 2500.00,
                'teller': 10000.00
            }
        }
        return render_template('banking/withdrawal.html',
                             withdrawal_data=withdrawal_data,
                             page_title='Make Withdrawal')
    except Exception as e:
        logger.error(f"Withdrawal error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

@banking_bp.route('/withdrawal-history')
@login_required
def withdrawal_history():
    """Banking withdrawal history"""
    try:
        history_data = {
            'withdrawals': [
                {'date': '2025-01-15', 'amount': 200.00, 'method': 'ATM', 'location': 'Main St Branch', 'status': 'Completed'},
                {'date': '2025-01-14', 'amount': 500.00, 'method': 'Online', 'location': 'Online Banking', 'status': 'Completed'},
                {'date': '2025-01-13', 'amount': 100.00, 'method': 'ATM', 'location': 'Downtown Branch', 'status': 'Completed'}
            ],
            'total_withdrawals': 3,
            'total_amount': 800.00,
            'date_range': '2025-01-01 to 2025-01-15'
        }
        return render_template('banking/withdrawal_history.html',
                             history_data=history_data,
                             page_title='Withdrawal History')
    except Exception as e:
        logger.error(f"Withdrawal history error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('banking.banking_dashboard'))

# Duplicate functions removed - using originals from earlier in the file

