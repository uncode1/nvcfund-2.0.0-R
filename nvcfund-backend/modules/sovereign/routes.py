"""
Sovereign Banking Routes
Central banking operations, sovereign debt management, and monetary policy
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from .services import SovereignBankingService
from modules.utils.services import ErrorLoggerService

# Initialize services
sovereign_service = SovereignBankingService()
error_logger = ErrorLoggerService()

# Create blueprint
sovereign_bp = Blueprint('sovereign', __name__, url_prefix='/sovereign')

@sovereign_bp.route('/')
@login_required
def dashboard():
    """Sovereign banking dashboard"""
    try:
        # Check authorization for sovereign banking access
        if not _has_sovereign_access(current_user):
            flash('Access denied. Sovereign banking requires appropriate authorization.', 'error')
            return redirect(url_for('auth.login'))
        
        # Get dashboard data
        dashboard_data = sovereign_service.get_dashboard_overview()
        
        return render_template('sovereign_dashboard_main.html', 
                             dashboard_data=dashboard_data,
                             page_title='Sovereign Banking Dashboard')
    
    except Exception as e:
        error_logger.log_error(
            error_type="SOVEREIGN_DASHBOARD_ERROR",
            message=f"Sovereign dashboard error: {str(e)}",
            details={'user_id': current_user.id if current_user.is_authenticated else None}
        )
        flash('Error loading sovereign banking dashboard.', 'error')
        return redirect(url_for('public.index'))

@sovereign_bp.route('/central-bank')
@login_required
def central_bank():
    """Central bank operations dashboard"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        central_bank_data = sovereign_service.get_central_bank_operations()
        
        return render_template('sovereign/central_bank_operations.html',
                             central_bank_data=central_bank_data,
                             user=current_user,
                             page_title='Central Bank Operations')
    
    except Exception as e:
        error_logger.log_error(
            error_type="CENTRAL_BANK_ERROR",
            message=f"Central bank operations error: {str(e)}",
            details={'user_id': current_user.id}
        )
        flash('Error loading central bank operations.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/monetary-policy')
@login_required
def monetary_policy():
    """Monetary policy management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        policy_data = sovereign_service.get_monetary_policy_data()
        
        return render_template('sovereign_monetary_policy.html',
                             policy_data=policy_data,
                             page_title='Monetary Policy Management')
    
    except Exception as e:
        error_logger.log_error(
            error_type="MONETARY_POLICY_ERROR",
            message=f"Monetary policy error: {str(e)}",
            details={'user_id': current_user.id}
        )
        flash('Error loading monetary policy data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/sovereign-debt')
@login_required
def sovereign_debt():
    """Sovereign debt management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        debt_data = sovereign_service.get_sovereign_debt_data()
        
        return render_template('sovereign_debt_management.html',
                             debt_data=debt_data,
                             page_title='Sovereign Debt Management')
    
    except Exception as e:
        error_logger.log_error(
            error_type="SOVEREIGN_DEBT_ERROR",
            message=f"Sovereign debt management error: {str(e)}",
            details={'user_id': current_user.id}
        )
        flash('Error loading sovereign debt data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/foreign-exchange')
@login_required
def foreign_exchange():
    """Foreign exchange operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fx_data = sovereign_service.get_foreign_exchange_data()
        
        return render_template('sovereign_foreign_exchange.html',
                             fx_data=fx_data,
                             page_title='Foreign Exchange Operations')
    
    except Exception as e:
        error_logger.log_error(f"Foreign exchange error: {str(e)}", 
                              user_id=current_user.id)
        flash('Error loading foreign exchange data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/reserves')
@login_required
def reserves():
    """International reserves management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        reserves_data = sovereign_service.get_reserves_data()
        
        return render_template('sovereign_reserves_management.html',
                             reserves_data=reserves_data,
                             page_title='International Reserves Management')
    
    except Exception as e:
        error_logger.log_error(f"Reserves management error: {str(e)}", 
                              user_id=current_user.id)
        flash('Error loading reserves data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/regulatory')
@login_required
def regulatory():
    """Banking regulation and supervision"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        regulatory_data = sovereign_service.get_regulatory_data()
        
        return render_template('sovereign_regulatory_supervision.html',
                             regulatory_data=regulatory_data,
                             page_title='Banking Regulation & Supervision')
    
    except Exception as e:
        error_logger.log_error(f"Regulatory supervision error: {str(e)}", 
                              user_id=current_user.id)
        flash('Error loading regulatory data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

# ===== MISSING ROUTE ALIASES FOR ORPHANED TEMPLATES =====

@sovereign_bp.route('/dashboard-main')
@login_required
def dashboard_main():
    """Main sovereign banking dashboard - alias route"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        dashboard_data = sovereign_service.get_sovereign_dashboard_data()
        
        return render_template('sovereign_dashboard_main.html',
                             dashboard_data=dashboard_data,
                             page_title='Sovereign Banking Dashboard')
    
    except Exception as e:
        error_logger.log_error(f"Sovereign dashboard main error: {str(e)}", 
                              user_id=current_user.id)
        flash('Error loading sovereign dashboard.', 'error')
        return redirect(url_for('public.index'))

@sovereign_bp.route('/debt-management')
@login_required
def debt_management():
    """Debt management - alias for sovereign-debt route"""
    return sovereign_debt()

@sovereign_bp.route('/reserves-management')
@login_required
def reserves_management():
    """Reserves management - alias for reserves route"""
    return reserves()

@sovereign_bp.route('/regulatory-supervision')
@login_required
def regulatory_supervision():
    """Regulatory supervision - alias for regulatory route"""
    return regulatory()

# ===== ADDITIONAL SOVEREIGN BANKING FEATURES =====

@sovereign_bp.route('/trade-credits')
@login_required
def trade_credits():
    """Trade credits management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        trade_credits_data = sovereign_service.get_trade_credits_data()
        return render_template('sovereign/trade_credits.html',
                             trade_credits_data=trade_credits_data,
                             page_title='Trade Credits Management')
    except Exception as e:
        error_logger.log_error(f"Trade credits error: {str(e)}", user_id=current_user.id)
        flash('Error loading trade credits data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/cross-clearing')
@login_required
def cross_clearing():
    """Cross-clearing operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        cross_clearing_data = sovereign_service.get_cross_clearing_data()
        return render_template('sovereign/cross_clearing.html',
                             cross_clearing_data=cross_clearing_data,
                             page_title='Cross-Clearing Operations')
    except Exception as e:
        error_logger.log_error(f"Cross-clearing error: {str(e)}", user_id=current_user.id)
        flash('Error loading cross-clearing data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/treasury')
@login_required
def treasury():
    """Treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        treasury_data = sovereign_service.get_treasury_data()
        return render_template('sovereign/treasury.html',
                             treasury_data=treasury_data,
                             page_title='Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"Treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/cash-transfer')
@login_required
def cash_transfer():
    """Cash transfer operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        cash_transfer_data = sovereign_service.get_cash_transfer_data()
        return render_template('sovereign/cash_transfer.html',
                             cash_transfer_data=cash_transfer_data,
                             page_title='Cash Transfer Operations')
    except Exception as e:
        error_logger.log_error(f"Cash transfer error: {str(e)}", user_id=current_user.id)
        flash('Error loading cash transfer data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/apis-transfers')
@login_required
def apis_transfers():
    """API transfers management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        apis_data = sovereign_service.get_apis_transfers_data()
        return render_template('sovereign/apis_transfers.html',
                             apis_data=apis_data,
                             page_title='API Transfers Management')
    except Exception as e:
        error_logger.log_error(f"API transfers error: {str(e)}", user_id=current_user.id)
        flash('Error loading API transfers data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/fed-liquidity')
@login_required
def fed_liquidity():
    """Federal liquidity operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fed_liquidity_data = sovereign_service.get_fed_liquidity_data()
        return render_template('sovereign/fed_liquidity.html',
                             fed_liquidity_data=fed_liquidity_data,
                             page_title='Federal Liquidity Operations')
    except Exception as e:
        error_logger.log_error(f"Fed liquidity error: {str(e)}", user_id=current_user.id)
        flash('Error loading Fed liquidity data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/currencies')
@login_required
def currencies():
    """Currency management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        currencies_data = sovereign_service.get_currencies_data()
        return render_template('sovereign/currencies.html',
                             currencies_data=currencies_data,
                             page_title='Currency Management')
    except Exception as e:
        error_logger.log_error(f"Currencies error: {str(e)}", user_id=current_user.id)
        flash('Error loading currencies data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/settlement-networks')
@login_required
def settlement_networks():
    """Settlement networks management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        settlement_data = sovereign_service.get_settlement_networks_data()
        return render_template('sovereign/settlement_networks.html',
                             settlement_data=settlement_data,
                             page_title='Settlement Networks')
    except Exception as e:
        error_logger.log_error(f"Settlement networks error: {str(e)}", user_id=current_user.id)
        flash('Error loading settlement networks data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/stc-integration')
@login_required
def stc_integration():
    """STC integration management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        stc_data = sovereign_service.get_stc_integration_data()
        return render_template('sovereign/stc_integration.html',
                             stc_data=stc_data,
                             page_title='STC Integration')
    except Exception as e:
        error_logger.log_error(f"STC integration error: {str(e)}", user_id=current_user.id)
        flash('Error loading STC integration data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/trust-links')
@login_required
def trust_links():
    """Trust links management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        trust_links_data = sovereign_service.get_trust_links_data()
        return render_template('sovereign/trust_links.html',
                             trust_links_data=trust_links_data,
                             page_title='Trust Links Management')
    except Exception as e:
        error_logger.log_error(f"Trust links error: {str(e)}", user_id=current_user.id)
        flash('Error loading trust links data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/transfer-agent')
@login_required
def transfer_agent():
    """Transfer agent operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        transfer_agent_data = sovereign_service.get_transfer_agent_data()
        return render_template('sovereign/transfer_agent.html',
                             transfer_agent_data=transfer_agent_data,
                             page_title='Transfer Agent Operations')
    except Exception as e:
        error_logger.log_error(f"Transfer agent error: {str(e)}", user_id=current_user.id)
        flash('Error loading transfer agent data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/fdic-compliance')
@login_required
def fdic_compliance():
    """FDIC compliance management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fdic_data = sovereign_service.get_fdic_compliance_data()
        return render_template('sovereign/fdic_compliance.html',
                             fdic_data=fdic_data,
                             page_title='FDIC Compliance')
    except Exception as e:
        error_logger.log_error(f"FDIC compliance error: {str(e)}", user_id=current_user.id)
        flash('Error loading FDIC compliance data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/retail-network')
@login_required
def retail_network():
    """Retail network operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        retail_network_data = sovereign_service.get_retail_network_data()
        return render_template('sovereign/retail_network.html',
                             retail_network_data=retail_network_data,
                             page_title='Retail Network Operations')
    except Exception as e:
        error_logger.log_error(f"Retail network error: {str(e)}", user_id=current_user.id)
        flash('Error loading retail network data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/liquidity-access')
@login_required
def liquidity_access():
    """Liquidity access management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        liquidity_data = sovereign_service.get_liquidity_access_data()
        return render_template('sovereign/liquidity_access.html',
                             liquidity_data=liquidity_data,
                             page_title='Liquidity Access Management')
    except Exception as e:
        error_logger.log_error(f"Liquidity access error: {str(e)}", user_id=current_user.id)
        flash('Error loading liquidity access data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/bank-capital')
@login_required
def bank_capital():
    """Bank capital management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        bank_capital_data = sovereign_service.get_bank_capital_data()
        return render_template('sovereign/bank_capital.html',
                             bank_capital_data=bank_capital_data,
                             page_title='Bank Capital Management')
    except Exception as e:
        error_logger.log_error(f"Bank capital error: {str(e)}", user_id=current_user.id)
        flash('Error loading bank capital data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/trade-links')
@login_required
def trade_links():
    """Trade links management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        trade_links_data = sovereign_service.get_trade_links_data()
        return render_template('sovereign/trade_links.html',
                             trade_links_data=trade_links_data,
                             page_title='Trade Links Management')
    except Exception as e:
        error_logger.log_error(f"Trade links error: {str(e)}", user_id=current_user.id)
        flash('Error loading trade links data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/sovereign-rights')
@login_required
def sovereign_rights():
    """Sovereign rights management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        sovereign_rights_data = sovereign_service.get_sovereign_rights_data()
        return render_template('sovereign/sovereign_rights.html',
                             sovereign_rights_data=sovereign_rights_data,
                             page_title='Sovereign Rights Management')
    except Exception as e:
        error_logger.log_error(f"Sovereign rights error: {str(e)}", user_id=current_user.id)
        flash('Error loading sovereign rights data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/ibis-icr')
@login_required
def ibis_icr():
    """IBIS & ICR operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        ibis_icr_data = sovereign_service.get_ibis_icr_data()
        return render_template('sovereign/ibis_icr.html',
                             ibis_icr_data=ibis_icr_data,
                             page_title='IBIS & ICR Operations')
    except Exception as e:
        error_logger.log_error(f"IBIS & ICR error: {str(e)}", user_id=current_user.id)
        flash('Error loading IBIS & ICR data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/un-framework')
@login_required
def un_framework():
    """UN Framework operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        un_framework_data = sovereign_service.get_un_framework_data()
        return render_template('sovereign/un_framework.html',
                             un_framework_data=un_framework_data,
                             page_title='UN Framework Operations')
    except Exception as e:
        error_logger.log_error(f"UN Framework error: {str(e)}", user_id=current_user.id)
        flash('Error loading UN Framework data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/nvct-stablecoin')
@login_required
def nvct_stablecoin():
    """NVCT Stablecoin operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        nvct_data = sovereign_service.get_nvct_stablecoin_data()
        return render_template('sovereign/nvct_stablecoin.html',
                             nvct_data=nvct_data,
                             page_title='NVCT Stablecoin Operations')
    except Exception as e:
        error_logger.log_error(f"NVCT Stablecoin error: {str(e)}", user_id=current_user.id)
        flash('Error loading NVCT Stablecoin data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/loan-registry')
@login_required
def loan_registry():
    """Loan registry management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        loan_registry_data = sovereign_service.get_loan_registry_data()
        return render_template('sovereign/loan_registry.html',
                             loan_registry_data=loan_registry_data,
                             page_title='Loan Registry Management')
    except Exception as e:
        error_logger.log_error(f"Loan registry error: {str(e)}", user_id=current_user.id)
        flash('Error loading loan registry data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/fedwire-treasury')
@login_required
def fedwire_treasury():
    """Fedwire treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fedwire_data = sovereign_service.get_fedwire_treasury_data()
        return render_template('sovereign/fedwire_treasury.html',
                             fedwire_data=fedwire_data,
                             page_title='Fedwire Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"Fedwire treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading Fedwire treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/spdr-treasury')
@login_required
def spdr_treasury():
    """SPDR treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        spdr_data = sovereign_service.get_spdr_treasury_data()
        return render_template('sovereign/spdr_treasury.html',
                             spdr_data=spdr_data,
                             page_title='SPDR Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"SPDR treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading SPDR treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/fed-treasury')
@login_required
def fed_treasury():
    """Fed treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fed_treasury_data = sovereign_service.get_fed_treasury_data()
        return render_template('sovereign/fed_treasury.html',
                             fed_treasury_data=fed_treasury_data,
                             page_title='Fed Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"Fed treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading Fed treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/credit-misc')
@login_required
def credit_misc():
    """Credit miscellaneous operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        credit_misc_data = sovereign_service.get_credit_misc_data()
        return render_template('sovereign/credit_misc.html',
                             credit_misc_data=credit_misc_data,
                             page_title='Credit Miscellaneous Operations')
    except Exception as e:
        error_logger.log_error(f"Credit misc error: {str(e)}", user_id=current_user.id)
        flash('Error loading credit misc data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/uedc-bridge')
@login_required
def uedc_bridge():
    """UEDC bridge operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        uedc_data = sovereign_service.get_uedc_bridge_data()
        return render_template('sovereign/uedc_bridge.html',
                             uedc_data=uedc_data,
                             page_title='UEDC Bridge Operations')
    except Exception as e:
        error_logger.log_error(f"UEDC bridge error: {str(e)}", user_id=current_user.id)
        flash('Error loading UEDC bridge data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/bank-of-america')
@login_required
def bank_of_america():
    """Bank of America operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        boa_data = sovereign_service.get_bank_of_america_data()
        return render_template('sovereign/bank_of_america.html',
                             boa_data=boa_data,
                             page_title='Bank of America Operations')
    except Exception as e:
        error_logger.log_error(f"Bank of America error: {str(e)}", user_id=current_user.id)
        flash('Error loading Bank of America data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/routing-info')
@login_required
def routing_info():
    """Routing information management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        routing_data = sovereign_service.get_routing_info_data()
        return render_template('sovereign/routing_info.html',
                             routing_data=routing_data,
                             page_title='Routing Information Management')
    except Exception as e:
        error_logger.log_error(f"Routing info error: {str(e)}", user_id=current_user.id)
        flash('Error loading routing info data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/uba-treasury')
@login_required
def uba_treasury():
    """UBA Treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        uba_treasury_data = sovereign_service.get_uba_treasury_data()
        return render_template('sovereign/uba_treasury.html',
                             uba_treasury_data=uba_treasury_data,
                             page_title='UBA Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"UBA Treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading UBA Treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/fidelity-treasury')
@login_required
def fidelity_treasury():
    """Fidelity Treasury operations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        fidelity_treasury_data = sovereign_service.get_fidelity_treasury_data()
        return render_template('sovereign/fidelity_treasury.html',
                             fidelity_treasury_data=fidelity_treasury_data,
                             page_title='Fidelity Treasury Operations')
    except Exception as e:
        error_logger.log_error(f"Fidelity Treasury error: {str(e)}", user_id=current_user.id)
        flash('Error loading Fidelity Treasury data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/operations-overview')
@login_required
def operations_overview():
    """Complete sovereign operations overview"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))
        
        return render_template('sovereign/sovereign_operations_overview.html',
                             page_title='Sovereign Banking Operations - Priority Access')
    except Exception as e:
        error_logger.log_error(f"Operations overview error: {str(e)}", user_id=current_user.id)
        flash('Error loading operations overview.', 'error')
        return redirect(url_for('sovereign.dashboard'))

# Missing routes referenced from dashboard templates
@sovereign_bp.route('/asset-management')
@login_required
def asset_management():
    """Sovereign asset management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        asset_data = sovereign_service.get_asset_management_data()
        return render_template('sovereign/asset_management.html',
                             asset_data=asset_data,
                             page_title='Sovereign Asset Management')
    except Exception as e:
        error_logger.log_error(f"Asset management error: {str(e)}", user_id=current_user.id)
        flash('Error loading asset management data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/currency-issuance')
@login_required
def currency_issuance():
    """Sovereign currency issuance"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        issuance_data = sovereign_service.get_currency_issuance_data()
        return render_template('sovereign/currency_issuance.html',
                             issuance_data=issuance_data,
                             page_title='Currency Issuance')
    except Exception as e:
        error_logger.log_error(f"Currency issuance error: {str(e)}", user_id=current_user.id)
        flash('Error loading currency issuance data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/diplomatic-channels')
@login_required
def diplomatic_channels():
    """Sovereign diplomatic channels"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        diplomatic_data = sovereign_service.get_diplomatic_channels_data()
        return render_template('sovereign/diplomatic_channels.html',
                             diplomatic_data=diplomatic_data,
                             page_title='Diplomatic Channels')
    except Exception as e:
        error_logger.log_error(f"Diplomatic channels error: {str(e)}", user_id=current_user.id)
        flash('Error loading diplomatic channels data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/diplomatic-relations')
@login_required
def diplomatic_relations():
    """Sovereign diplomatic relations"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        relations_data = sovereign_service.get_diplomatic_relations_data()
        return render_template('sovereign/diplomatic_relations.html',
                             relations_data=relations_data,
                             page_title='Diplomatic Relations')
    except Exception as e:
        error_logger.log_error(f"Diplomatic relations error: {str(e)}", user_id=current_user.id)
        flash('Error loading diplomatic relations data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/economic-dashboard')
@login_required
def economic_dashboard():
    """Sovereign economic dashboard"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        economic_data = sovereign_service.get_economic_dashboard_data()
        return render_template('sovereign/economic_dashboard.html',
                             economic_data=economic_data,
                             page_title='Economic Dashboard')
    except Exception as e:
        error_logger.log_error(f"Economic dashboard error: {str(e)}", user_id=current_user.id)
        flash('Error loading economic dashboard data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/financial-audit')
@login_required
def financial_audit():
    """Sovereign financial audit"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        audit_data = sovereign_service.get_financial_audit_data()
        return render_template('sovereign/financial_audit.html',
                             audit_data=audit_data,
                             page_title='Financial Audit')
    except Exception as e:
        error_logger.log_error(f"Financial audit error: {str(e)}", user_id=current_user.id)
        flash('Error loading financial audit data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/reserve-management')
@login_required
def reserve_management():
    """Sovereign reserve management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        reserve_data = sovereign_service.get_reserve_management_data()
        return render_template('sovereign/reserve_management.html',
                             reserve_data=reserve_data,
                             page_title='Reserve Management')
    except Exception as e:
        error_logger.log_error(f"Reserve management error: {str(e)}", user_id=current_user.id)
        flash('Error loading reserve management data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/treasury-management')
@login_required
def treasury_management():
    """Sovereign treasury management"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        treasury_data = sovereign_service.get_treasury_management_data()
        return render_template('sovereign/treasury_management.html',
                             treasury_data=treasury_data,
                             page_title='Treasury Management')
    except Exception as e:
        error_logger.log_error(f"Treasury management error: {str(e)}", user_id=current_user.id)
        flash('Error loading treasury management data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

# Additional missing routes referenced in templates
@sovereign_bp.route('/economic-indicators')
@login_required
def economic_indicators():
    """Economic indicators dashboard"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        indicators_data = {
            'gdp_growth': 3.2,
            'inflation_rate': 2.1,
            'unemployment_rate': 4.5,
            'interest_rate': 5.25,
            'exchange_rate': 1.08,
            'trade_balance': 125000000.00,
            'economic_indicators': [
                {'indicator': 'GDP Growth (YoY)', 'value': '3.2%', 'change': '+0.5%', 'status': 'Positive'},
                {'indicator': 'Inflation Rate', 'value': '2.1%', 'change': '-0.3%', 'status': 'Stable'},
                {'indicator': 'Unemployment', 'value': '4.5%', 'change': '-0.2%', 'status': 'Improving'},
                {'indicator': 'Trade Balance', 'value': '$125M', 'change': '+$15M', 'status': 'Surplus'}
            ],
            'forecasts': [
                {'period': 'Q2 2025', 'gdp_forecast': 3.5, 'inflation_forecast': 2.0},
                {'period': 'Q3 2025', 'gdp_forecast': 3.3, 'inflation_forecast': 2.2},
                {'period': 'Q4 2025', 'gdp_forecast': 3.1, 'inflation_forecast': 2.1}
            ]
        }
        return render_template('sovereign/economic_indicators.html',
                             indicators_data=indicators_data,
                             page_title='Economic Indicators')
    except Exception as e:
        error_logger.log_error(f"Economic indicators error: {str(e)}", user_id=current_user.id)
        flash('Error loading economic indicators.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/sovereign-monetary-policy')
@login_required
def sovereign_monetary_policy():
    """Sovereign monetary policy dashboard"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        policy_data = {
            'current_policy_rate': 5.25,
            'reserve_requirement': 10.0,
            'money_supply_growth': 8.5,
            'policy_stance': 'Neutral',
            'recent_decisions': [
                {'date': '2025-01-15', 'decision': 'Rate Hold', 'rate': 5.25, 'rationale': 'Economic stability'},
                {'date': '2024-12-15', 'decision': 'Rate Increase', 'rate': 5.25, 'rationale': 'Inflation control'},
                {'date': '2024-11-15', 'decision': 'Rate Hold', 'rate': 5.00, 'rationale': 'Data assessment'}
            ],
            'policy_tools': [
                {'tool': 'Interest Rates', 'current_setting': '5.25%', 'last_change': '2024-12-15'},
                {'tool': 'Reserve Requirements', 'current_setting': '10.0%', 'last_change': '2024-10-01'},
                {'tool': 'Open Market Operations', 'current_setting': 'Active', 'last_change': '2025-01-10'}
            ]
        }
        return render_template('sovereign/sovereign_monetary_policy.html',
                             policy_data=policy_data,
                             page_title='Sovereign Monetary Policy')
    except Exception as e:
        error_logger.log_error(f"Monetary policy error: {str(e)}", user_id=current_user.id)
        flash('Error loading monetary policy data.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/sovereign-operations-overview')
@login_required
def sovereign_operations_overview():
    """Sovereign operations overview dashboard"""
    try:
        if not _has_sovereign_access(current_user):
            flash('Access denied.', 'error')
            return redirect(url_for('auth.login'))

        operations_data = {
            'operational_status': 'Normal',
            'active_operations': 15,
            'pending_approvals': 3,
            'daily_transaction_volume': 2500000000.00,
            'operations_summary': [
                {'category': 'Currency Operations', 'count': 5, 'volume': 1250000000.00, 'status': 'Active'},
                {'category': 'Reserve Management', 'count': 3, 'volume': 750000000.00, 'status': 'Active'},
                {'category': 'International Transfers', 'count': 4, 'volume': 350000000.00, 'status': 'Active'},
                {'category': 'Policy Implementation', 'count': 3, 'volume': 150000000.00, 'status': 'Pending'}
            ],
            'performance_metrics': {
                'processing_time': '2.5 minutes',
                'success_rate': '99.8%',
                'compliance_score': '98.5%',
                'operational_efficiency': '96.2%'
            }
        }
        return render_template('sovereign/sovereign_operations_overview.html',
                             operations_data=operations_data,
                             page_title='Sovereign Operations Overview')
    except Exception as e:
        error_logger.log_error(f"Operations overview error: {str(e)}", user_id=current_user.id)
        flash('Error loading operations overview.', 'error')
        return redirect(url_for('sovereign.dashboard'))

@sovereign_bp.route('/api/health')
def health_check():
    """Health check endpoint for sovereign banking module"""
    try:
        health_status = sovereign_service.get_health_status()
        return jsonify({
            'status': 'healthy',
            'app_module': 'sovereign_banking',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': health_status
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy', 
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def _has_sovereign_access(user) -> bool:
    """Check if user has sovereign banking access"""
    if not user or not user.is_authenticated:
        return False
    
    # Define sovereign banking roles
    sovereign_roles = [
        'central_bank_governor',
        'sovereign_banker', 
        'monetary_policy_committee',
        'admin',
        'super_admin'
    ]
    
    user_role = getattr(user, 'role', None)
    return user_role in sovereign_roles