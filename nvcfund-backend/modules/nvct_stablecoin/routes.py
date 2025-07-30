"""
NVCT Stablecoin Module Routes
Comprehensive $30 trillion stablecoin management and blockchain operations
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import logging
from datetime import datetime
from .services import NVCTStablecoinService, AssetBackingService, CrossChainService

# Create blueprint with hyphenated URL for professional banking appearance
nvct_stablecoin_bp = Blueprint(
    'nvct_stablecoin',
    __name__,
    url_prefix='/nvct-stablecoin',
    template_folder='templates',
    static_folder='static'
)

# Removed legacy redirect blueprint - clean URLs only

# Removed redundant hyphen blueprint - main blueprint already uses /nvct-stablecoin prefix

logger = logging.getLogger(__name__)

# Initialize services
nvct_service = NVCTStablecoinService()
asset_service = AssetBackingService()
crosschain_service = CrossChainService()

@nvct_stablecoin_bp.route('/')
@login_required
def nvct_dashboard():
    """NVCT Stablecoin main dashboard"""
    try:
        logger.info(f"User {current_user.username} accessing NVCT dashboard")
        
        # Get comprehensive NVCT data
        nvct_overview = nvct_service.get_nvct_overview()
        asset_backing = asset_service.get_asset_backing_status()
        network_status = crosschain_service.get_network_deployment_status()
        supply_metrics = nvct_service.get_supply_metrics()
        
        dashboard_data = {
            'nvct_overview': nvct_overview,
            'asset_backing': asset_backing,
            'network_status': network_status,
            'supply_metrics': supply_metrics,
            'total_supply': '30,000,000,000,000',  # 30T NVCT
            'backing_value': '56,700,000,000,000',  # $56.7T backing
            'backing_ratio': '189',  # 189% over-collateralization
            'current_price': '1.00'  # $1.00 USD parity target
        }
        
        return render_template(
            'nvct_stablecoin/nvct_stablecoin_dashboard.html',
            dashboard_data=dashboard_data,
            page_title="NVCT Stablecoin Operations"
        )
    except Exception as e:
        logger.error(f"Error loading NVCT dashboard: {e}")
        flash('Error loading NVCT dashboard', 'error')
        return redirect(url_for('dashboard.dashboard_home'))

@nvct_stablecoin_bp.route('/supply')
@login_required
def supply_management():
    """NVCT supply management and minting controls"""
    try:
        supply_data = nvct_service.get_detailed_supply_data()
        minting_history = nvct_service.get_minting_history()
        burn_history = nvct_service.get_burn_history()
        
        return render_template(
            'nvct_stablecoin/nvct_supply_management.html',
            supply_data=supply_data,
            minting_history=minting_history,
            burn_history=burn_history,
            page_title="NVCT Supply Management"
        )
    except Exception as e:
        logger.error(f"Error loading supply management: {e}")
        flash('Error loading supply management page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/assets')
@login_required
def asset_backing():
    """Asset backing dashboard with $56.7T backing portfolio"""
    try:
        backing_portfolio = asset_service.get_backing_portfolio()
        asset_allocation = asset_service.get_asset_allocation()
        valuation_reports = asset_service.get_valuation_reports()
        compliance_status = asset_service.get_compliance_status()
        
        return render_template(
            'nvct_asset_backing.html',
            backing_portfolio=backing_portfolio,
            asset_allocation=asset_allocation,
            valuation_reports=valuation_reports,
            compliance_status=compliance_status,
            page_title="NVCT Asset Backing Portfolio"
        )
    except Exception as e:
        logger.error(f"Error loading asset backing: {e}")
        flash('Error loading asset backing page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/networks')
@login_required
def network_management():
    """Multi-chain network deployment and management"""
    try:
        deployment_status = crosschain_service.get_deployment_status()
        bridge_operations = crosschain_service.get_bridge_operations()
        network_metrics = crosschain_service.get_network_metrics()
        pending_deployments = crosschain_service.get_pending_deployments()
        
        return render_template(
            'nvct_network_management.html',
            deployment_status=deployment_status,
            bridge_operations=bridge_operations,
            network_metrics=network_metrics,
            pending_deployments=pending_deployments,
            page_title="NVCT Network Management"
        )
    except Exception as e:
        logger.error(f"Error loading network management: {e}")
        flash('Error loading network management page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/bridge')
@login_required
def cross_chain_bridge():
    """Cross-chain bridge interface for NVCT transfers"""
    try:
        supported_chains = crosschain_service.get_supported_chains()
        bridge_fees = crosschain_service.get_bridge_fees()
        recent_transfers = crosschain_service.get_recent_bridge_transfers()
        
        return render_template(
            'nvct_cross_chain_bridge.html',
            supported_chains=supported_chains,
            bridge_fees=bridge_fees,
            recent_transfers=recent_transfers,
            page_title="NVCT Cross-Chain Bridge"
        )
    except Exception as e:
        logger.error(f"Error loading cross-chain bridge: {e}")
        flash('Error loading bridge interface', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/governance')
@login_required
def governance_dashboard():
    """NVCT governance and voting interface"""
    try:
        governance_data = nvct_service.get_governance_data()
        active_proposals = nvct_service.get_active_proposals()
        voting_history = nvct_service.get_voting_history()
        
        return render_template(
            'nvct_stablecoin/nvct_governance.html',
            governance_data=governance_data,
            active_proposals=active_proposals,
            voting_history=voting_history,
            page_title="NVCT Governance"
        )
    except Exception as e:
        logger.error(f"Error loading governance dashboard: {e}")
        flash('Error loading governance page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics')
@login_required
def nvct_analytics_dashboard():
    """NVCT analytics and performance metrics"""
    try:
        market_data = nvct_service.get_market_analytics()
        price_stability = nvct_service.get_price_stability_metrics()
        volume_data = nvct_service.get_volume_analytics()
        holder_metrics = nvct_service.get_holder_analytics()
        
        return render_template(
            'nvct_stablecoin/analytics_dashboard.html',
            market_data=market_data,
            price_stability=price_stability,
            volume_data=volume_data,
            holder_metrics=holder_metrics,
            page_title="NVCT Analytics"
        )
    except Exception as e:
        logger.error(f"Error loading analytics dashboard: {e}")
        flash('Error loading analytics page', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/mint', methods=['POST'])
@login_required
def mint_nvct():
    """Mint new NVCT tokens (restricted access)"""
    try:
        # Check user permissions for minting
        if not nvct_service.user_can_mint(current_user):
            flash('Insufficient permissions for NVCT minting', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        amount = request.form.get('amount')
        recipient = request.form.get('recipient')
        justification = request.form.get('justification')
        
        if not amount or not recipient or not justification:
            flash('All fields required for minting operation', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        # Execute minting operation
        result = nvct_service.mint_tokens(
            amount=float(amount),
            recipient=recipient,
            justification=justification,
            authorized_by=current_user.username
        )
        
        if result['success']:
            flash(f'Successfully minted {amount} NVCT tokens', 'success')
            logger.info(f"NVCT minting: {amount} tokens minted by {current_user.username}")
        else:
            flash(f'Minting failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.supply_management'))
        
    except Exception as e:
        logger.error(f"Error in NVCT minting: {e}")
        flash('Minting operation failed', 'error')
        return redirect(url_for('nvct_stablecoin.supply_management'))

@nvct_stablecoin_bp.route('/burn', methods=['POST'])
@login_required
def burn_nvct():
    """Burn NVCT tokens to reduce supply"""
    try:
        # Check user permissions for burning
        if not nvct_service.user_can_burn(current_user):
            flash('Insufficient permissions for NVCT burning', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        amount = request.form.get('amount')
        justification = request.form.get('justification')
        
        if not amount or not justification:
            flash('Amount and justification required for burning operation', 'error')
            return redirect(url_for('nvct_stablecoin.supply_management'))
        
        # Execute burning operation
        result = nvct_service.burn_tokens(
            amount=float(amount),
            justification=justification,
            authorized_by=current_user.username
        )
        
        if result['success']:
            flash(f'Successfully burned {amount} NVCT tokens', 'success')
            logger.info(f"NVCT burning: {amount} tokens burned by {current_user.username}")
        else:
            flash(f'Burning failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.supply_management'))
        
    except Exception as e:
        logger.error(f"Error in NVCT burning: {e}")
        flash('Burning operation failed', 'error')
        return redirect(url_for('nvct_stablecoin.supply_management'))

@nvct_stablecoin_bp.route('/deploy', methods=['POST'])
@login_required
def deploy_to_network():
    """Deploy NVCT to new blockchain network"""
    try:
        # Check deployment permissions
        if not crosschain_service.user_can_deploy(current_user):
            flash('Insufficient permissions for network deployment', 'error')
            return redirect(url_for('nvct_stablecoin.network_management'))
        
        network = request.form.get('network')
        if not network:
            flash('Network selection required', 'error')
            return redirect(url_for('nvct_stablecoin.network_management'))
        
        # Execute deployment
        result = crosschain_service.deploy_to_network(
            network=network,
            deployed_by=current_user.username
        )
        
        if result['success']:
            flash(f'NVCT deployment to {network} initiated successfully', 'success')
            logger.info(f"NVCT deployment: {network} deployment by {current_user.username}")
        else:
            flash(f'Deployment failed: {result["error"]}', 'error')
        
        return redirect(url_for('nvct_stablecoin.network_management'))
        
    except Exception as e:
        logger.error(f"Error in network deployment: {e}")
        flash('Network deployment failed', 'error')
        return redirect(url_for('nvct_stablecoin.network_management'))

@nvct_stablecoin_bp.route('/stablecoin-dashboard')
@login_required
def nvct_stablecoin_dashboard_page():
    """NVCT Stablecoin dashboard using orphaned template"""
    try:
        nvct_overview = nvct_service.get_nvct_overview()
        
        return render_template('nvct_stablecoin/nvct_stablecoin_dashboard.html',
                             nvct_overview=nvct_overview,
                             page_title='NVCT Stablecoin Dashboard')
        
    except Exception as e:
        logger.error(f"NVCT dashboard error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/supply-operations')
@login_required
def nvct_supply_operations():
    """NVCT supply management using orphaned template"""
    try:
        supply_data = nvct_service.get_supply_metrics()
        
        return render_template('nvct_stablecoin/nvct_supply_management.html',
                             supply_data=supply_data,
                             page_title='NVCT Supply Management')
        
    except Exception as e:
        logger.error(f"NVCT supply operations error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics-center')
@login_required
def nvct_analytics_center():
    """NVCT analytics dashboard using orphaned template"""
    try:
        analytics_data = nvct_service.get_analytics_data()
        
        return render_template('nvct_stablecoin/nvct_analytics_dashboard.html',
                             analytics_data=analytics_data,
                             page_title='NVCT Analytics Dashboard')
        
    except Exception as e:
        logger.error(f"NVCT analytics error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/governance-portal')
@login_required
def nvct_governance_portal():
    """NVCT governance using orphaned template"""
    try:
        governance_data = nvct_service.get_governance_data()
        
        return render_template('nvct_stablecoin/nvct_governance.html',
                             governance_data=governance_data,
                             page_title='NVCT Governance Portal')
        
    except Exception as e:
        logger.error(f"NVCT governance error: {e}")
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

# Bridge Analytics Routes
@nvct_stablecoin_bp.route('/bridge-analytics')
@login_required
def bridge_analytics():
    """Bridge analytics dashboard"""
    try:
        analytics_data = crosschain_service.get_bridge_analytics()
        return render_template('nvct_stablecoin/bridge_analytics.html',
                             analytics_data=analytics_data,
                             page_title='Bridge Analytics')
    except Exception as e:
        logger.error(f"Error loading bridge analytics: {e}")
        flash('Error loading bridge analytics', 'error')
        return redirect(url_for('nvct_stablecoin.cross_chain_bridge'))

@nvct_stablecoin_bp.route('/active-bridges')
@login_required
def active_bridges():
    """Active bridges monitoring"""
    try:
        active_bridges_data = crosschain_service.get_active_bridges()
        return render_template('nvct_stablecoin/active_bridges.html',
                             bridges_data=active_bridges_data,
                             page_title='Active Bridges')
    except Exception as e:
        logger.error(f"Error loading active bridges: {e}")
        flash('Error loading active bridges', 'error')
        return redirect(url_for('nvct_stablecoin.cross_chain_bridge'))

@nvct_stablecoin_bp.route('/bridge-volume')
@login_required
def bridge_volume():
    """Bridge volume analytics"""
    try:
        volume_data = crosschain_service.get_bridge_volume()
        return render_template('nvct_stablecoin/bridge_volume.html',
                             volume_data=volume_data,
                             page_title='Bridge Volume')
    except Exception as e:
        logger.error(f"Error loading bridge volume: {e}")
        flash('Error loading bridge volume', 'error')
        return redirect(url_for('nvct_stablecoin.cross_chain_bridge'))

@nvct_stablecoin_bp.route('/bridge-fees')
@login_required
def bridge_fees():
    """Bridge fees analytics"""
    try:
        fees_data = crosschain_service.get_bridge_fees()
        return render_template('nvct_stablecoin/bridge_fees.html',
                             fees_data=fees_data,
                             page_title='Bridge Fees')
    except Exception as e:
        logger.error(f"Error loading bridge fees: {e}")
        flash('Error loading bridge fees', 'error')
        return redirect(url_for('nvct_stablecoin.cross_chain_bridge'))

@nvct_stablecoin_bp.route('/bridge-history')
@login_required
def bridge_history():
    """Bridge transaction history"""
    try:
        history_data = crosschain_service.get_bridge_history()
        return render_template('nvct_stablecoin/bridge_history.html',
                             history_data=history_data,
                             page_title='Bridge History')
    except Exception as e:
        logger.error(f"Error loading bridge history: {e}")
        flash('Error loading bridge history', 'error')
        return redirect(url_for('nvct_stablecoin.cross_chain_bridge'))

# Additional network management routes
@nvct_stablecoin_bp.route('/active-networks')
@login_required
def active_networks():
    """Active networks monitoring"""
    try:
        networks_data = crosschain_service.get_active_networks()
        return render_template('nvct_stablecoin/active_networks.html',
                             networks_data=networks_data,
                             page_title='Active Networks')
    except Exception as e:
        logger.error(f"Error loading active networks: {e}")
        flash('Error loading active networks', 'error')
        return redirect(url_for('nvct_stablecoin.network_management'))

@nvct_stablecoin_bp.route('/deployment-history')
@login_required
def deployment_history():
    """Deployment history dashboard"""
    try:
        history_data = crosschain_service.get_deployment_history()
        return render_template('nvct_stablecoin/deployment_history.html',
                             history_data=history_data,
                             page_title='Deployment History')
    except Exception as e:
        logger.error(f"Error loading deployment history: {e}")
        flash('Error loading deployment history', 'error')
        return redirect(url_for('nvct_stablecoin.network_management'))

@nvct_stablecoin_bp.route('/network-health')
@login_required
def network_health():
    """Network health monitoring"""
    try:
        health_data = crosschain_service.get_network_health()
        return render_template('nvct_stablecoin/network_health.html',
                             health_data=health_data,
                             page_title='Network Health')
    except Exception as e:
        logger.error(f"Error loading network health: {e}")
        flash('Error loading network health', 'error')
        return redirect(url_for('nvct_stablecoin.network_management'))

# Additional missing routes referenced in templates
@nvct_stablecoin_bp.route('/nvct-supply-management')
@login_required
def nvct_supply_management():
    """NVCT supply management - alias for supply_management"""
    return supply_management()

@nvct_stablecoin_bp.route('/market-data')
@login_required
def market_data():
    """NVCT market data dashboard"""
    try:
        market_data = {
            'current_price': 1.00,
            'market_cap': 125000000.00,
            'trading_volume_24h': 2450000.00,
            'price_stability': 99.98
        }
        return render_template('nvct_stablecoin/market_data.html',
                             market_data=market_data,
                             page_title='Market Data')
    except Exception as e:
        logger.error(f"Error loading market data: {e}")
        flash('Error loading market data', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/nvct-governance')
@login_required
def nvct_governance():
    """NVCT governance dashboard"""
    try:
        governance_data = {
            'active_proposals': 3,
            'total_voters': 1247,
            'voting_power': 85.6,
            'governance_token_supply': 10000000
        }
        return render_template('nvct_stablecoin/nvct_governance.html',
                             governance_data=governance_data,
                             page_title='NVCT Governance')
    except Exception as e:
        logger.error(f"Error loading governance: {e}")
        flash('Error loading governance', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics')
@login_required
def analytics():
    """NVCT analytics dashboard"""
    try:
        analytics_data = {
            'total_supply': 125000000.00,
            'circulating_supply': 124500000.00,
            'burn_rate': 0.1,
            'mint_rate': 2.5
        }
        return render_template('nvct_stablecoin/analytics.html',
                             analytics_data=analytics_data,
                             page_title='NVCT Analytics')
    except Exception as e:
        logger.error(f"Error loading analytics: {e}")
        flash('Error loading analytics', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/analytics-dashboard')
@login_required
def analytics_dashboard():
    """NVCT analytics dashboard - alias for nvct_analytics_dashboard"""
    return nvct_analytics_dashboard()

@nvct_stablecoin_bp.route('/asset-analytics')
@login_required
def asset_analytics():
    """Asset backing analytics"""
    try:
        asset_data = {
            'total_backing': 235000000.00,
            'backing_ratio': 189.5,
            'asset_allocation': [
                {'type': 'US Treasury Bonds', 'amount': 120000000.00, 'percentage': 51},
                {'type': 'Corporate Bonds', 'amount': 70000000.00, 'percentage': 30},
                {'type': 'Cash Equivalents', 'amount': 45000000.00, 'percentage': 19}
            ]
        }
        return render_template('nvct_stablecoin/asset_analytics.html',
                             asset_data=asset_data,
                             page_title='Asset Analytics')
    except Exception as e:
        logger.error(f"Error loading asset analytics: {e}")
        flash('Error loading asset analytics', 'error')
        return redirect(url_for('nvct_stablecoin.asset_backing'))

# Additional governance routes
@nvct_stablecoin_bp.route('/create-proposal')
@login_required
def create_proposal():
    """Create governance proposal"""
    try:
        proposal_types = [
            {'id': 'parameter', 'name': 'Parameter Change', 'description': 'Modify protocol parameters'},
            {'id': 'upgrade', 'name': 'Protocol Upgrade', 'description': 'Upgrade smart contracts'},
            {'id': 'treasury', 'name': 'Treasury Action', 'description': 'Treasury fund allocation'},
            {'id': 'emergency', 'name': 'Emergency Action', 'description': 'Emergency protocol action'}
        ]
        return render_template('nvct_stablecoin/create_proposal.html',
                             proposal_types=proposal_types,
                             page_title='Create Proposal')
    except Exception as e:
        logger.error(f"Create proposal error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.governance_dashboard'))

@nvct_stablecoin_bp.route('/active-votes')
@login_required
def active_votes():
    """Active governance votes"""
    try:
        votes_data = {
            'active_proposals': [
                {'id': 'PROP-001', 'title': 'Increase Collateral Ratio', 'votes_for': 1250, 'votes_against': 340, 'ends': '2025-01-20'},
                {'id': 'PROP-002', 'title': 'Add New Asset Backing', 'votes_for': 890, 'votes_against': 120, 'ends': '2025-01-18'},
                {'id': 'PROP-003', 'title': 'Protocol Fee Adjustment', 'votes_for': 567, 'votes_against': 234, 'ends': '2025-01-22'}
            ],
            'user_voting_power': 1500,
            'total_voting_power': 10000000
        }
        return render_template('nvct_stablecoin/active_votes.html',
                             votes_data=votes_data,
                             page_title='Active Votes')
    except Exception as e:
        logger.error(f"Active votes error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.governance_dashboard'))

@nvct_stablecoin_bp.route('/active-proposals')
@login_required
def active_proposals():
    """Active governance proposals"""
    try:
        proposals_data = {
            'proposals': [
                {'id': 'PROP-001', 'title': 'Increase Collateral Ratio', 'status': 'Active', 'created': '2025-01-10'},
                {'id': 'PROP-002', 'title': 'Add New Asset Backing', 'status': 'Active', 'created': '2025-01-12'},
                {'id': 'PROP-003', 'title': 'Protocol Fee Adjustment', 'status': 'Pending', 'created': '2025-01-14'}
            ]
        }
        return render_template('nvct_stablecoin/active_proposals.html',
                             proposals_data=proposals_data,
                             page_title='Active Proposals')
    except Exception as e:
        logger.error(f"Active proposals error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.governance_dashboard'))

@nvct_stablecoin_bp.route('/voting-power')
@login_required
def voting_power():
    """Voting power dashboard"""
    try:
        voting_data = {
            'user_voting_power': 1500,
            'delegated_power': 500,
            'total_power': 2000,
            'delegation_history': [
                {'delegate': '0x123...abc', 'power': 300, 'date': '2025-01-10'},
                {'delegate': '0x456...def', 'power': 200, 'date': '2025-01-08'}
            ]
        }
        return render_template('nvct_stablecoin/voting_power.html',
                             voting_data=voting_data,
                             page_title='Voting Power')
    except Exception as e:
        logger.error(f"Voting power error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.governance_dashboard'))

@nvct_stablecoin_bp.route('/treasury-governance')
@login_required
def treasury_governance():
    """Treasury governance dashboard"""
    try:
        treasury_data = {
            'treasury_balance': 25000000.00,
            'allocated_funds': 15000000.00,
            'pending_allocations': 2000000.00,
            'recent_proposals': [
                {'title': 'Development Fund', 'amount': 1000000.00, 'status': 'Approved'},
                {'title': 'Marketing Budget', 'amount': 500000.00, 'status': 'Pending'},
                {'title': 'Security Audit', 'amount': 250000.00, 'status': 'Active'}
            ]
        }
        return render_template('nvct_stablecoin/treasury_governance.html',
                             treasury_data=treasury_data,
                             page_title='Treasury Governance')
    except Exception as e:
        logger.error(f"Treasury governance error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.governance_dashboard'))

# Additional asset backing routes
@nvct_stablecoin_bp.route('/collateral-analytics')
@login_required
def collateral_analytics():
    """Collateral analytics dashboard"""
    try:
        collateral_data = {
            'total_collateral': 235000000.00,
            'collateral_ratio': 189.5,
            'collateral_types': [
                {'type': 'US Treasury Bonds', 'value': 120000000.00, 'percentage': 51.1},
                {'type': 'Corporate Bonds', 'value': 70000000.00, 'percentage': 29.8},
                {'type': 'Cash Equivalents', 'value': 45000000.00, 'percentage': 19.1}
            ],
            'risk_metrics': {
                'duration': 3.2,
                'credit_rating': 'AAA',
                'liquidity_ratio': 95.5
            }
        }
        return render_template('nvct_stablecoin/collateral_analytics.html',
                             collateral_data=collateral_data,
                             page_title='Collateral Analytics')
    except Exception as e:
        logger.error(f"Collateral analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.asset_backing'))

@nvct_stablecoin_bp.route('/risk-analytics')
@login_required
def risk_analytics():
    """Risk analytics dashboard"""
    try:
        risk_data = {
            'overall_risk_score': 'Low',
            'credit_risk': 'Very Low',
            'market_risk': 'Low',
            'liquidity_risk': 'Very Low',
            'operational_risk': 'Low',
            'var_1day': -125000.00,
            'var_1week': -450000.00,
            'stress_test_results': {
                'scenario_1': 'Pass',
                'scenario_2': 'Pass',
                'scenario_3': 'Warning'
            }
        }
        return render_template('nvct_stablecoin/risk_analytics.html',
                             risk_data=risk_data,
                             page_title='Risk Analytics')
    except Exception as e:
        logger.error(f"Risk analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.asset_backing'))

@nvct_stablecoin_bp.route('/allocation-analytics')
@login_required
def allocation_analytics():
    """Asset allocation analytics"""
    try:
        allocation_data = {
            'target_allocation': [
                {'asset': 'Government Bonds', 'target': 50.0, 'current': 51.1, 'variance': 1.1},
                {'asset': 'Corporate Bonds', 'target': 30.0, 'current': 29.8, 'variance': -0.2},
                {'asset': 'Cash', 'target': 20.0, 'current': 19.1, 'variance': -0.9}
            ],
            'rebalancing_needed': False,
            'last_rebalance': '2025-01-10',
            'next_review': '2025-01-25'
        }
        return render_template('nvct_stablecoin/allocation_analytics.html',
                             allocation_data=allocation_data,
                             page_title='Allocation Analytics')
    except Exception as e:
        logger.error(f"Allocation analytics error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.asset_backing'))

@nvct_stablecoin_bp.route('/nvct-reports')
@login_required
def nvct_reports():
    """NVCT reports dashboard"""
    try:
        reports_data = {
            'available_reports': [
                {'name': 'Monthly Supply Report', 'date': '2025-01-01', 'type': 'PDF'},
                {'name': 'Asset Backing Report', 'date': '2025-01-01', 'type': 'PDF'},
                {'name': 'Governance Report', 'date': '2024-12-31', 'type': 'PDF'},
                {'name': 'Risk Assessment', 'date': '2024-12-31', 'type': 'PDF'}
            ],
            'report_schedule': 'Monthly',
            'next_report': '2025-02-01'
        }
        return render_template('nvct_stablecoin/nvct_reports.html',
                             reports_data=reports_data,
                             page_title='NVCT Reports')
    except Exception as e:
        logger.error(f"NVCT reports error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/nvct-transactions')
@login_required
def nvct_transactions():
    """NVCT transactions dashboard"""
    try:
        transactions_data = {
            'recent_transactions': [
                {'type': 'Mint', 'amount': 1000000.00, 'timestamp': '2025-01-15 10:30', 'tx_hash': '0x123...abc'},
                {'type': 'Burn', 'amount': 500000.00, 'timestamp': '2025-01-15 09:15', 'tx_hash': '0x456...def'},
                {'type': 'Transfer', 'amount': 250000.00, 'timestamp': '2025-01-15 08:45', 'tx_hash': '0x789...ghi'}
            ],
            'daily_volume': 5250000.00,
            'transaction_count': 1247,
            'average_size': 4215.78
        }
        return render_template('nvct_stablecoin/nvct_transactions.html',
                             transactions_data=transactions_data,
                             page_title='NVCT Transactions')
    except Exception as e:
        logger.error(f"NVCT transactions error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

# DeFi routes
@nvct_stablecoin_bp.route('/yield-farming')
@login_required
def yield_farming():
    """Yield farming dashboard"""
    try:
        farming_data = {
            'total_staked': 25000000.00,
            'total_rewards': 125000.00,
            'apy': 8.5,
            'active_farms': [
                {'name': 'NVCT-USDC Pool', 'staked': 10000000.00, 'apy': 12.5, 'rewards': 50000.00},
                {'name': 'NVCT-ETH Pool', 'staked': 8000000.00, 'apy': 9.8, 'rewards': 35000.00},
                {'name': 'NVCT-BTC Pool', 'staked': 7000000.00, 'apy': 6.2, 'rewards': 40000.00}
            ]
        }
        return render_template('nvct_stablecoin/yield_farming.html',
                             farming_data=farming_data,
                             page_title='Yield Farming')
    except Exception as e:
        logger.error(f"Yield farming error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/flash-loans')
@login_required
def flash_loans():
    """Flash loans dashboard"""
    try:
        flash_loan_data = {
            'available_liquidity': 50000000.00,
            'flash_loan_fee': 0.09,
            'total_volume_24h': 2500000.00,
            'supported_assets': ['NVCT', 'USDC', 'ETH', 'BTC']
        }
        return render_template('nvct_stablecoin/flash_loans.html',
                             flash_loan_data=flash_loan_data,
                             page_title='Flash Loans')
    except Exception as e:
        logger.error(f"Flash loans error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/amm-trading')
@login_required
def amm_trading():
    """AMM trading dashboard"""
    try:
        amm_data = {
            'total_liquidity': 125000000.00,
            'trading_volume_24h': 5250000.00,
            'trading_pairs': [
                {'pair': 'NVCT/USDC', 'liquidity': 45000000.00, 'volume_24h': 2000000.00},
                {'pair': 'NVCT/ETH', 'liquidity': 35000000.00, 'volume_24h': 1800000.00},
                {'pair': 'NVCT/BTC', 'liquidity': 45000000.00, 'volume_24h': 1450000.00}
            ]
        }
        return render_template('nvct_stablecoin/amm_trading.html',
                             amm_data=amm_data,
                             page_title='AMM Trading')
    except Exception as e:
        logger.error(f"AMM trading error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/staking')
@login_required
def staking():
    """NVCT staking dashboard"""
    try:
        staking_data = {
            'total_staked': 75000000.00,
            'staking_apy': 6.5,
            'user_staked': 10000.00,
            'pending_rewards': 125.50,
            'staking_pools': [
                {'name': '30-Day Pool', 'apy': 4.5, 'min_stake': 1000.00},
                {'name': '90-Day Pool', 'apy': 6.5, 'min_stake': 5000.00},
                {'name': '365-Day Pool', 'apy': 8.5, 'min_stake': 10000.00}
            ]
        }
        return render_template('nvct_stablecoin/staking.html',
                             staking_data=staking_data,
                             page_title='NVCT Staking')
    except Exception as e:
        logger.error(f"Staking error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/api/health')
def health_check():
    """NVCT Stablecoin module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'nvct_stablecoin',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'total_supply': '30000000000000',
        'backing_ratio': '189%'
    })

# Error handlers
@nvct_stablecoin_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within NVCT module"""
    return render_template('404.html'), 404

@nvct_stablecoin_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within NVCT module"""
    logger.error(f"Internal error in NVCT module: {error}")
    return render_template('500.html'), 500

# Additional missing routes referenced in templates
@nvct_stablecoin_bp.route('/governance')
@login_required
def governance():
    """NVCT governance dashboard"""
    try:
        governance_data = {
            'governance_token': 'NVCT-GOV',
            'total_supply': 1000000,
            'circulating_supply': 750000,
            'voting_power_distribution': [
                {'holder': 'Treasury', 'tokens': 250000, 'percentage': 33.3},
                {'holder': 'Community', 'tokens': 400000, 'percentage': 53.3},
                {'holder': 'Team', 'tokens': 100000, 'percentage': 13.4}
            ],
            'active_proposals': [
                {'id': 'PROP-001', 'title': 'Increase Staking Rewards', 'votes_for': 450000, 'votes_against': 125000, 'status': 'Active'},
                {'id': 'PROP-002', 'title': 'New Collateral Type', 'votes_for': 380000, 'votes_against': 200000, 'status': 'Active'},
                {'id': 'PROP-003', 'title': 'Fee Structure Update', 'votes_for': 520000, 'votes_against': 80000, 'status': 'Passed'}
            ],
            'governance_stats': {
                'total_proposals': 25,
                'passed_proposals': 18,
                'rejected_proposals': 4,
                'active_proposals': 3
            }
        }
        return render_template('nvct_stablecoin/governance.html',
                             governance_data=governance_data,
                             page_title='NVCT Governance')
    except Exception as e:
        logger.error(f"Error loading governance data: {e}")
        flash('Error loading governance data', 'error')
        return redirect(url_for('nvct_stablecoin.nvct_dashboard'))

@nvct_stablecoin_bp.route('/nvct-market-data')
@login_required
def nvct_market_data():
    """NVCT market data - alias for market_data"""
    return market_data()