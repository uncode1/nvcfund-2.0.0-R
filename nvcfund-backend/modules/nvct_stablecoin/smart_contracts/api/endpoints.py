"""
Smart Contracts API Endpoints
RESTful API for blockchain smart contract operations
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import logging
from ..services import SmartContractService, BlockchainNetworkService

# Create API blueprint
smart_contracts_api_bp = Blueprint(
    'smartcontracts_api',
    __name__,
    url_prefix='/api/v1/smartcontracts'
)

logger = logging.getLogger(__name__)

# Initialize services
contract_service = SmartContractService()
network_service = BlockchainNetworkService()

@smart_contracts_api_bp.route('/overview', methods=['GET'])
@login_required
def get_contracts_overview():
    """Get smart contracts overview and statistics"""
    try:
        overview = contract_service.get_contract_overview()
        return jsonify({
            'status': 'success',
            'data': overview
        })
    except Exception as e:
        logger.error(f"Error getting contracts overview: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve contracts overview'
        }), 500

@smart_contracts_api_bp.route('/deployed', methods=['GET'])
@login_required
def get_deployed_contracts():
    """Get list of deployed smart contracts"""
    try:
        contracts = contract_service.get_deployed_contracts()
        return jsonify({
            'status': 'success',
            'data': contracts,
            'total': len(contracts)
        })
    except Exception as e:
        logger.error(f"Error getting deployed contracts: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve deployed contracts'
        }), 500

@smart_contracts_api_bp.route('/templates', methods=['GET'])
@login_required
def get_contract_templates():
    """Get available smart contract templates"""
    try:
        templates = contract_service.get_contract_templates()
        return jsonify({
            'status': 'success',
            'data': templates
        })
    except Exception as e:
        logger.error(f"Error getting contract templates: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve contract templates'
        }), 500

@smart_contracts_api_bp.route('/deploy', methods=['POST'])
@login_required
def deploy_contract():
    """Deploy a new smart contract"""
    try:
        contract_data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'network']
        for field in required_fields:
            if field not in contract_data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Deploy contract
        deployment_result = contract_service.deploy_contract(contract_data)
        
        if deployment_result.get('success'):
            logger.info(f"Contract deployed successfully by {current_user.username}: {deployment_result['contract_address']}")
            return jsonify({
                'status': 'success',
                'data': deployment_result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': deployment_result.get('error', 'Deployment failed')
            }), 400
            
    except Exception as e:
        logger.error(f"Error deploying contract: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Contract deployment failed'
        }), 500

@smart_contracts_api_bp.route('/validate', methods=['POST'])
@login_required
def validate_contract():
    """Validate smart contract code before deployment"""
    try:
        data = request.get_json()
        
        if 'code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Contract code is required'
            }), 400
        
        validation_result = contract_service.validate_contract_code(
            data['code'], 
            data.get('type', 'general')
        )
        
        return jsonify({
            'status': 'success',
            'data': validation_result
        })
        
    except Exception as e:
        logger.error(f"Error validating contract: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Contract validation failed'
        }), 500

@smart_contracts_api_bp.route('/audits', methods=['GET'])
@login_required
def get_audit_reports():
    """Get smart contract audit reports"""
    try:
        audits = contract_service.get_audit_reports()
        return jsonify({
            'status': 'success',
            'data': audits
        })
    except Exception as e:
        logger.error(f"Error getting audit reports: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve audit reports'
        }), 500

@smart_contracts_api_bp.route('/monitoring', methods=['GET'])
@login_required
def get_monitoring_data():
    """Get real-time contract monitoring data"""
    try:
        metrics = contract_service.get_monitoring_metrics()
        return jsonify({
            'status': 'success',
            'data': metrics
        })
    except Exception as e:
        logger.error(f"Error getting monitoring data: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve monitoring data'
        }), 500

@smart_contracts_api_bp.route('/networks', methods=['GET'])
@login_required
def get_supported_networks():
    """Get supported blockchain networks"""
    try:
        networks = network_service.get_supported_networks()
        return jsonify({
            'status': 'success',
            'data': networks
        })
    except Exception as e:
        logger.error(f"Error getting supported networks: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve supported networks'
        }), 500

@smart_contracts_api_bp.route('/networks/<network_id>/status', methods=['GET'])
@login_required
def get_network_status(network_id):
    """Get status of a specific blockchain network"""
    try:
        status = network_service.get_network_status(network_id)
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve network status'
        }), 500

@smart_contracts_api_bp.route('/contracts/<contract_address>/interactions', methods=['GET'])
@login_required
def get_contract_interactions(contract_address):
    """Get recent interactions with a specific contract"""
    try:
        interactions = contract_service.get_contract_interactions(contract_address)
        return jsonify({
            'status': 'success',
            'data': interactions
        })
    except Exception as e:
        logger.error(f"Error getting contract interactions: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve contract interactions'
        }), 500

@smart_contracts_api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Smart Contracts API"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'smart_contracts_api',
        'version': '1.0.0',
        'endpoints': [
            '/overview',
            '/deployed',
            '/templates',
            '/deploy',
            '/validate',
            '/audits',
            '/monitoring',
            '/networks',
            '/health'
        ]
    })

# Error handlers
@smart_contracts_api_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request'
    }), 400

@smart_contracts_api_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 Unauthorized errors"""
    return jsonify({
        'status': 'error',
        'message': 'Unauthorized access'
    }), 401

@smart_contracts_api_bp.errorhandler(403)
def forbidden(error):
    """Handle 403 Forbidden errors"""
    return jsonify({
        'status': 'error',
        'message': 'Access forbidden'
    }), 403

@smart_contracts_api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@smart_contracts_api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors"""
    logger.error(f"Internal error in smart contracts API: {error}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500