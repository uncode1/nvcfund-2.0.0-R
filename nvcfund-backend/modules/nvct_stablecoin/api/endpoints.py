"""
NVCT Stablecoin API Endpoints
RESTful API for $30 trillion stablecoin operations and management
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging
from datetime import datetime
from ..services import NVCTStablecoinService, AssetBackingService, CrossChainService

# Create API blueprint
nvct_stablecoin_api_bp = Blueprint(
    'nvct_stablecoin_api',
    __name__,
    url_prefix='/api/v1/nvct'
)

logger = logging.getLogger(__name__)

# Initialize services
nvct_service = NVCTStablecoinService()
asset_service = AssetBackingService()
crosschain_service = CrossChainService()

@nvct_stablecoin_api_bp.route('/overview', methods=['GET'])
@login_required
def get_nvct_overview():
    """Get comprehensive NVCT overview"""
    try:
        overview = nvct_service.get_nvct_overview()
        return jsonify({
            'status': 'success',
            'data': overview
        })
    except Exception as e:
        logger.error(f"Error getting NVCT overview: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve NVCT overview'
        }), 500

@nvct_stablecoin_api_bp.route('/supply', methods=['GET'])
@login_required
def get_supply_metrics():
    """Get NVCT supply metrics"""
    try:
        supply_data = nvct_service.get_supply_metrics()
        detailed_data = nvct_service.get_detailed_supply_data()
        
        return jsonify({
            'status': 'success',
            'data': {
                'metrics': supply_data,
                'detailed': detailed_data
            }
        })
    except Exception as e:
        logger.error(f"Error getting supply metrics: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve supply metrics'
        }), 500

@nvct_stablecoin_api_bp.route('/supply/history', methods=['GET'])
@login_required
def get_supply_history():
    """Get minting and burning history"""
    try:
        operation_type = request.args.get('type', 'all')
        
        if operation_type == 'mint':
            history = nvct_service.get_minting_history()
        elif operation_type == 'burn':
            history = nvct_service.get_burn_history()
        else:
            minting = nvct_service.get_minting_history()
            burning = nvct_service.get_burn_history()
            history = {
                'minting': minting,
                'burning': burning
            }
        
        return jsonify({
            'status': 'success',
            'data': history
        })
    except Exception as e:
        logger.error(f"Error getting supply history: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve supply history'
        }), 500

@nvct_stablecoin_api_bp.route('/assets/backing', methods=['GET'])
@login_required
def get_asset_backing():
    """Get asset backing information"""
    try:
        backing_status = asset_service.get_asset_backing_status()
        portfolio = asset_service.get_backing_portfolio()
        allocation = asset_service.get_asset_allocation()
        
        return jsonify({
            'status': 'success',
            'data': {
                'backing_status': backing_status,
                'portfolio': portfolio,
                'allocation': allocation
            }
        })
    except Exception as e:
        logger.error(f"Error getting asset backing: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve asset backing information'
        }), 500

@nvct_stablecoin_api_bp.route('/assets/reports', methods=['GET'])
@login_required
def get_valuation_reports():
    """Get asset valuation reports"""
    try:
        reports = asset_service.get_valuation_reports()
        compliance = asset_service.get_compliance_status()
        
        return jsonify({
            'status': 'success',
            'data': {
                'valuation_reports': reports,
                'compliance_status': compliance
            }
        })
    except Exception as e:
        logger.error(f"Error getting valuation reports: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve valuation reports'
        }), 500

@nvct_stablecoin_api_bp.route('/networks/status', methods=['GET'])
@login_required
def get_network_status():
    """Get network deployment status"""
    try:
        deployment_status = crosschain_service.get_deployment_status()
        network_metrics = crosschain_service.get_network_metrics()
        
        return jsonify({
            'status': 'success',
            'data': {
                'deployment_status': deployment_status,
                'network_metrics': network_metrics
            }
        })
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve network status'
        }), 500

@nvct_stablecoin_api_bp.route('/bridge/operations', methods=['GET'])
@login_required
def get_bridge_operations():
    """Get cross-chain bridge operations"""
    try:
        operations = crosschain_service.get_bridge_operations()
        fees = crosschain_service.get_bridge_fees()
        supported_chains = crosschain_service.get_supported_chains()
        
        return jsonify({
            'status': 'success',
            'data': {
                'operations': operations,
                'fees': fees,
                'supported_chains': supported_chains
            }
        })
    except Exception as e:
        logger.error(f"Error getting bridge operations: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve bridge operations'
        }), 500

@nvct_stablecoin_api_bp.route('/bridge/transfer', methods=['POST'])
@login_required
def initiate_bridge_transfer():
    """Initiate cross-chain bridge transfer"""
    try:
        data = request.get_json()
        
        required_fields = ['from_network', 'to_network', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Check if target network is deployed
        supported_chains = crosschain_service.get_supported_chains()
        to_network = data['to_network']
        
        target_chain = next((chain for chain in supported_chains if chain['id'] == to_network), None)
        if not target_chain:
            return jsonify({
                'status': 'error',
                'message': f'Network {to_network} not supported'
            }), 400
        
        if target_chain['status'] != 'Active':
            return jsonify({
                'status': 'error',
                'message': f'Network {to_network} deployment pending'
            }), 400
        
        # Simulate bridge transfer initiation
        transfer_result = {
            'success': True,
            'transfer_id': f'BRG-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'from_network': data['from_network'],
            'to_network': data['to_network'],
            'amount': data['amount'],
            'estimated_time': '2-5 minutes',
            'fee': str(float(data['amount']) * 0.001),  # 0.1% fee
            'status': 'Initiated',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Bridge transfer initiated by {current_user.username}: {data['amount']} NVCT")
        
        return jsonify({
            'status': 'success',
            'data': transfer_result
        })
        
    except Exception as e:
        logger.error(f"Error initiating bridge transfer: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Bridge transfer initiation failed'
        }), 500

@nvct_stablecoin_api_bp.route('/governance/proposals', methods=['GET'])
@login_required
def get_governance_proposals():
    """Get governance proposals"""
    try:
        governance_data = nvct_service.get_governance_data()
        active_proposals = nvct_service.get_active_proposals()
        voting_history = nvct_service.get_voting_history()
        
        return jsonify({
            'status': 'success',
            'data': {
                'governance_info': governance_data,
                'active_proposals': active_proposals,
                'voting_history': voting_history
            }
        })
    except Exception as e:
        logger.error(f"Error getting governance proposals: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve governance proposals'
        }), 500

@nvct_stablecoin_api_bp.route('/governance/vote', methods=['POST'])
@login_required
def submit_vote():
    """Submit governance vote"""
    try:
        data = request.get_json()
        
        required_fields = ['proposal_id', 'vote']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        if data['vote'] not in ['yes', 'no', 'abstain']:
            return jsonify({
                'status': 'error',
                'message': 'Vote must be yes, no, or abstain'
            }), 400
        
        # Simulate vote submission
        vote_result = {
            'success': True,
            'vote_id': f'VOTE-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'proposal_id': data['proposal_id'],
            'vote': data['vote'],
            'voter': current_user.username,
            'voting_power': '0.1%',  # Simulated voting power
            'timestamp': datetime.now().isoformat(),
            'status': 'Recorded'
        }
        
        logger.info(f"Governance vote submitted by {current_user.username}: {data['vote']} on {data['proposal_id']}")
        
        return jsonify({
            'status': 'success',
            'data': vote_result
        })
        
    except Exception as e:
        logger.error(f"Error submitting vote: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Vote submission failed'
        }), 500

@nvct_stablecoin_api_bp.route('/analytics/market', methods=['GET'])
@login_required
def get_market_analytics():
    """Get market analytics data"""
    try:
        market_data = nvct_service.get_market_analytics()
        price_stability = nvct_service.get_price_stability_metrics()
        volume_data = nvct_service.get_volume_analytics()
        holder_metrics = nvct_service.get_holder_analytics()
        
        return jsonify({
            'status': 'success',
            'data': {
                'market_data': market_data,
                'price_stability': price_stability,
                'volume_analytics': volume_data,
                'holder_metrics': holder_metrics
            }
        })
    except Exception as e:
        logger.error(f"Error getting market analytics: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve market analytics'
        }), 500

@nvct_stablecoin_api_bp.route('/operations/mint', methods=['POST'])
@login_required
def mint_tokens():
    """Mint NVCT tokens (restricted access)"""
    try:
        # Check minting permissions
        if not nvct_service.user_can_mint(current_user):
            return jsonify({
                'status': 'error',
                'message': 'Insufficient permissions for NVCT minting'
            }), 403
        
        data = request.get_json()
        required_fields = ['amount', 'recipient', 'justification']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Execute minting
        result = nvct_service.mint_tokens(
            amount=float(data['amount']),
            recipient=data['recipient'],
            justification=data['justification'],
            authorized_by=current_user.username
        )
        
        if result['success']:
            logger.info(f"NVCT minting API: {data['amount']} tokens by {current_user.username}")
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error in API minting: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Minting operation failed'
        }), 500

@nvct_stablecoin_api_bp.route('/operations/burn', methods=['POST'])
@login_required
def burn_tokens():
    """Burn NVCT tokens"""
    try:
        # Check burning permissions
        if not nvct_service.user_can_burn(current_user):
            return jsonify({
                'status': 'error',
                'message': 'Insufficient permissions for NVCT burning'
            }), 403
        
        data = request.get_json()
        required_fields = ['amount', 'justification']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Execute burning
        result = nvct_service.burn_tokens(
            amount=float(data['amount']),
            justification=data['justification'],
            authorized_by=current_user.username
        )
        
        if result['success']:
            logger.info(f"NVCT burning API: {data['amount']} tokens by {current_user.username}")
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error in API burning: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Burning operation failed'
        }), 500

@nvct_stablecoin_api_bp.route('/networks/deploy', methods=['POST'])
@login_required
def deploy_network():
    """Deploy NVCT to new network"""
    try:
        # Check deployment permissions
        if not crosschain_service.user_can_deploy(current_user):
            return jsonify({
                'status': 'error',
                'message': 'Insufficient permissions for network deployment'
            }), 403
        
        data = request.get_json()
        if 'network' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Network specification required'
            }), 400
        
        # Execute deployment
        result = crosschain_service.deploy_to_network(
            network=data['network'],
            deployed_by=current_user.username
        )
        
        if result['success']:
            logger.info(f"Network deployment API: {data['network']} by {current_user.username}")
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 400
            
    except Exception as e:
        logger.error(f"Error in API deployment: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Network deployment failed'
        }), 500

@nvct_stablecoin_api_bp.route('/health', methods=['GET'])
def health_check():
    """NVCT Stablecoin API health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'nvct_stablecoin_api',
        'version': '1.0.0',
        'endpoints': [
            '/overview',
            '/supply',
            '/supply/history',
            '/assets/backing',
            '/assets/reports',
            '/networks/status',
            '/bridge/operations',
            '/bridge/transfer',
            '/governance/proposals',
            '/governance/vote',
            '/analytics/market',
            '/operations/mint',
            '/operations/burn',
            '/networks/deploy',
            '/health'
        ],
        'total_supply': '30000000000000',
        'backing_ratio': '189%',
        'networks_deployed': 1,
        'networks_pending': 4
    })

# Error handlers
@nvct_stablecoin_api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request'
    }), 400

@nvct_stablecoin_api_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    return jsonify({
        'status': 'error',
        'message': 'Unauthorized access'
    }), 401

@nvct_stablecoin_api_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return jsonify({
        'status': 'error',
        'message': 'Access forbidden'
    }), 403

@nvct_stablecoin_api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@nvct_stablecoin_api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f"Internal error in NVCT API: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500