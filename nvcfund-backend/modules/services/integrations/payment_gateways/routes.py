"""
Payment Gateways Routes - Gateway Processing and Management
Self-contained payment gateway routes with multi-provider support
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from modules.utils.services import ErrorLoggerService
from .services import PaymentGatewayService
from datetime import datetime

# Create module blueprint
payment_gateways_bp = Blueprint('payment_gateways', __name__, 
                               template_folder='templates',
                               static_folder='static',
                               url_prefix='/integrations/payment-gateways')

# Initialize services
error_service = ErrorLoggerService()
gateway_service = PaymentGatewayService()

@payment_gateways_bp.route('/')
@payment_gateways_bp.route('/dashboard')
@login_required
def gateway_dashboard():
    """Payment gateways dashboard"""
    try:
        gateways = gateway_service.get_available_gateways(current_user.id)
        statistics = gateway_service.get_gateway_statistics()
        
        context = {
            'gateways': gateways,
            'statistics': statistics,
            'page_title': 'Payment Gateways Dashboard',
            'total_gateways': len(gateways),
            'active_gateways': len([g for g in gateways if g['available']])
        }
        
        return render_template('payment_gateways/gateway_dashboard.html', **context)
        
    except Exception as e:
        error_service.log_error(f"Gateway dashboard error: {str(e)}", current_user.id)
        flash('Unable to load gateway dashboard. Please try again.', 'error')
        return redirect(url_for('dashboard.main_dashboard'))

@payment_gateways_bp.route('/paypal', methods=['GET', 'POST'])
@login_required
def paypal_transfer():
    """PayPal transfer processing"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'gateway': 'paypal',
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }
            
            # Process PayPal transfer
            result = gateway_service.process_gateway_transfer(transfer_data)
            
            if result.get('success'):
                flash(f'PayPal transfer of ${transfer_data["amount"]} initiated successfully. Transfer ID: {result["transfer_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'PayPal transfer failed: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            error_service.log_error(f"PayPal transfer error: {str(e)}", current_user.id)
            flash('PayPal transfer failed. Please try again.', 'error')
    
    gateway_details = gateway_service.get_gateway_details('paypal')
    return render_template('payment_gateways/gateway_transfer.html', 
                         gateway='PayPal', 
                         gateway_id='paypal',
                         gateway_details=gateway_details,
                         page_title='PayPal Transfer')

# Redirect routes to individual gateway sub-modules
@payment_gateways_bp.route('/paypal-redirect')
@login_required
def paypal_redirect():
    """Redirect to PayPal sub-module"""
    return redirect('/integrations/payment-gateways/paypal/')

@payment_gateways_bp.route('/stripe-redirect')
@login_required  
def stripe_redirect():
    """Redirect to Stripe sub-module"""
    return redirect('/integrations/payment-gateways/stripe/')

@payment_gateways_bp.route('/flutterwave-redirect')
@login_required
def flutterwave_redirect():
    """Redirect to Flutterwave sub-module"""
    return redirect('/integrations/payment-gateways/flutterwave/')

@payment_gateways_bp.route('/ach-network-redirect')
@login_required
def ach_network_redirect():
    """Redirect to ACH Network sub-module"""
    return redirect('/integrations/payment-gateways/ach-network/')

@payment_gateways_bp.route('/stripe', methods=['GET', 'POST'])
@login_required
def stripe_transfer():
    """Stripe transfer processing"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'gateway': 'stripe',
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }
            
            # Process Stripe transfer
            result = gateway_service.process_gateway_transfer(transfer_data)
            
            if result.get('success'):
                flash(f'Stripe transfer of ${transfer_data["amount"]} initiated successfully. Transfer ID: {result["transfer_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Stripe transfer failed: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            error_service.log_error(f"Stripe transfer error: {str(e)}", current_user.id)
            flash('Stripe transfer failed. Please try again.', 'error')
    
    gateway_details = gateway_service.get_gateway_details('stripe')
    return render_template('payment_gateways/gateway_transfer.html', 
                         gateway='Stripe', 
                         gateway_id='stripe',
                         gateway_details=gateway_details,
                         page_title='Stripe Transfer')

@payment_gateways_bp.route('/flutterwave', methods=['GET', 'POST'])
@login_required
def flutterwave_transfer():
    """Flutterwave transfer processing"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'gateway': 'flutterwave',
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }
            
            # Process Flutterwave transfer
            result = gateway_service.process_gateway_transfer(transfer_data)
            
            if result.get('success'):
                flash(f'Flutterwave transfer of ${transfer_data["amount"]} initiated successfully. Transfer ID: {result["transfer_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Flutterwave transfer failed: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            error_service.log_error(f"Flutterwave transfer error: {str(e)}", current_user.id)
            flash('Flutterwave transfer failed. Please try again.', 'error')
    
    gateway_details = gateway_service.get_gateway_details('flutterwave')
    return render_template('payment_gateways/gateway_transfer.html', 
                         gateway='Flutterwave', 
                         gateway_id='flutterwave',
                         gateway_details=gateway_details,
                         page_title='Flutterwave Transfer')

@payment_gateways_bp.route('/mojaloop', methods=['GET', 'POST'])
@login_required
def mojaloop_transfer():
    """Mojaloop transfer processing"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'gateway': 'mojaloop',
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }
            
            # Process Mojaloop transfer
            result = gateway_service.process_gateway_transfer(transfer_data)
            
            if result.get('success'):
                flash(f'Mojaloop transfer of ${transfer_data["amount"]} initiated successfully. Transfer ID: {result["transfer_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Mojaloop transfer failed: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            error_service.log_error(f"Mojaloop transfer error: {str(e)}", current_user.id)
            flash('Mojaloop transfer failed. Please try again.', 'error')
    
    gateway_details = gateway_service.get_gateway_details('mojaloop')
    return render_template('payment_gateways/gateway_transfer.html', 
                         gateway='Mojaloop', 
                         gateway_id='mojaloop',
                         gateway_details=gateway_details,
                         page_title='Mojaloop Transfer')

@payment_gateways_bp.route('/mobile', methods=['GET', 'POST'])
@login_required
def mobile_transfer():
    """Mobile transfer processing"""
    if request.method == 'POST':
        try:
            transfer_data = {
                'gateway': 'mobile',
                'amount': request.form.get('amount'),
                'recipient': request.form.get('recipient'),
                'currency': request.form.get('currency', 'USD'),
                'description': request.form.get('description', ''),
                'user_id': current_user.id
            }
            
            # Process Mobile transfer
            result = gateway_service.process_gateway_transfer(transfer_data)
            
            if result.get('success'):
                flash(f'Mobile transfer of ${transfer_data["amount"]} initiated successfully. Transfer ID: {result["transfer_id"]}', 'success')
                return redirect(url_for('banking.transfers'))
            else:
                flash(f'Mobile transfer failed: {result.get("error", "Unknown error")}', 'error')
                
        except Exception as e:
            error_service.log_error(f"Mobile transfer error: {str(e)}", current_user.id)
            flash('Mobile transfer failed. Please try again.', 'error')
    
    gateway_details = gateway_service.get_gateway_details('mobile')
    return render_template('payment_gateways/gateway_transfer.html', 
                         gateway='Mobile Transfer', 
                         gateway_id='mobile',
                         gateway_details=gateway_details,
                         page_title='Mobile Transfer')

@payment_gateways_bp.route('/api/status')
@login_required
def gateway_status():
    """Get gateway status API endpoint"""
    try:
        health = gateway_service.health_check()
        statistics = gateway_service.get_gateway_statistics()
        
        return jsonify({
            'health': health,
            'statistics': statistics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@payment_gateways_bp.route('/api/gateways')
@login_required
def api_gateways():
    """Get available gateways API endpoint"""
    try:
        gateways = gateway_service.get_available_gateways(current_user.id)
        return jsonify({
            'gateways': gateways,
            'total': len(gateways),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Missing route referenced in templates
@payment_gateways_bp.route('/gateway-transfer')
@login_required
def gateway_transfer():
    """Generic gateway transfer - redirect based on gateway_id parameter"""
    try:
        gateway_id = request.args.get('gateway_id', 'paypal')

        # Map gateway IDs to specific transfer routes
        gateway_routes = {
            'paypal': 'payment_gateways.paypal_transfer',
            'stripe': 'payment_gateways.stripe_transfer',
            'flutterwave': 'payment_gateways.flutterwave_transfer',
            'mojaloop': 'payment_gateways.mojaloop_transfer',
            'mobile': 'payment_gateways.mobile_transfer'
        }

        route = gateway_routes.get(gateway_id, 'payment_gateways.paypal_transfer')
        return redirect(url_for(route))

    except Exception as e:
        logger.error(f"Gateway transfer error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('payment_gateways.gateway_dashboard'))