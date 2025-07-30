"""
Binance Integration API Endpoints
Health check and status monitoring endpoints for Binance integration
"""

from flask import Blueprint, jsonify
from ..services import BinanceOAuthService, BinanceAPIService

# Create API blueprint with /api prefix
binance_api_bp = Blueprint(
    'binance_integration_api', 
    __name__, 
    url_prefix='/api'
)

@binance_api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Binance Integration module"""
    try:
        # Basic health check
        oauth_service = BinanceOAuthService()
        api_service = BinanceAPIService()
        
        return jsonify({
            'status': 'healthy',
            'app_module': 'binance_integration',
            'version': '1.0.0',
            'services': {
                'oauth': 'available',
                'api': 'available'
            },
            'endpoints': [
                '/binance/',
                '/binance/connect',
                '/binance/callback',
                '/binance/disconnect',
                '/binance/user-info',
                '/binance/status',
                '/binance/api/health'
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500

@binance_api_bp.route('/status', methods=['GET'])
def status():
    """Get detailed status of Binance integration"""
    try:
        oauth_service = BinanceOAuthService()
        api_service = BinanceAPIService()
        
        return jsonify({
            'status': 'operational',
            'app_module': 'binance_integration',
            'oauth_service': {
                'status': 'ready',
                'client_configured': oauth_service.client_id is not None
            },
            'api_service': {
                'status': 'ready',
                'base_url': 'https://api.binance.com'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'app_module': 'binance_integration',
            'error': str(e)
        }), 500