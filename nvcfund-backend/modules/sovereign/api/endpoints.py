"""
Sovereign Banking API Endpoints
RESTful API for central banking operations and sovereign debt management
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from typing import Dict, Any
import logging

from ..services import SovereignBankingService

# Initialize service
sovereign_service = SovereignBankingService()

# Create API blueprint
sovereign_api_bp = Blueprint('sovereign_api', __name__, url_prefix='/api/v1/sovereign')

@sovereign_api_bp.route('/overview', methods=['GET'])
@login_required
def get_sovereign_overview():
    """Get sovereign banking dashboard overview"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access to sovereign banking API'}), 403
        
        overview_data = sovereign_service.get_dashboard_overview()
        
        return jsonify({
            'status': 'success',
            'data': overview_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Sovereign overview API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve sovereign banking overview',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/central-bank/operations', methods=['GET'])
@login_required
def get_central_bank_operations():
    """Get central bank operations data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        operations_data = sovereign_service.get_central_bank_operations()
        
        return jsonify({
            'status': 'success',
            'data': operations_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Central bank operations API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve central bank operations',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/monetary-policy', methods=['GET'])
@login_required
def get_monetary_policy():
    """Get monetary policy data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        policy_data = sovereign_service.get_monetary_policy_data()
        
        return jsonify({
            'status': 'success',
            'data': policy_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Monetary policy API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve monetary policy data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/sovereign-debt', methods=['GET'])
@login_required
def get_sovereign_debt():
    """Get sovereign debt management data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        debt_data = sovereign_service.get_sovereign_debt_data()
        
        return jsonify({
            'status': 'success',
            'data': debt_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Sovereign debt API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve sovereign debt data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/foreign-exchange', methods=['GET'])
@login_required
def get_foreign_exchange():
    """Get foreign exchange operations data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        fx_data = sovereign_service.get_foreign_exchange_data()
        
        return jsonify({
            'status': 'success',
            'data': fx_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Foreign exchange API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve foreign exchange data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/reserves', methods=['GET'])
@login_required
def get_reserves():
    """Get international reserves data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        reserves_data = sovereign_service.get_reserves_data()
        
        return jsonify({
            'status': 'success',
            'data': reserves_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Reserves API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve reserves data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/regulatory', methods=['GET'])
@login_required
def get_regulatory():
    """Get banking regulation and supervision data"""
    try:
        if not _has_sovereign_api_access(current_user):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        regulatory_data = sovereign_service.get_regulatory_data()
        
        return jsonify({
            'status': 'success',
            'data': regulatory_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Regulatory API error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to retrieve regulatory data',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/policy-rate', methods=['POST'])
@login_required
def update_policy_rate():
    """Update monetary policy rate (restricted to authorized users)"""
    try:
        if not _has_sovereign_write_access(current_user):
            return jsonify({'error': 'Unauthorized to modify policy rates'}), 403
        
        data = request.get_json()
        new_rate = data.get('rate')
        
        if not new_rate or not isinstance(new_rate, (int, float)):
            return jsonify({'error': 'Invalid rate value'}), 400
        
        if new_rate < 0 or new_rate > 25:
            return jsonify({'error': 'Rate must be between 0% and 25%'}), 400
        
        # In production, this would update the actual policy rate
        # For now, return success with the new rate
        return jsonify({
            'status': 'success',
            'message': f'Policy rate updated to {new_rate}%',
            'new_rate': new_rate,
            'effective_date': datetime.utcnow().isoformat(),
            'updated_by': current_user.username
        })
    
    except Exception as e:
        logging.error(f"Policy rate update error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to update policy rate',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/debt-issuance', methods=['POST'])
@login_required
def create_debt_issuance():
    """Create new sovereign debt issuance"""
    try:
        if not _has_sovereign_write_access(current_user):
            return jsonify({'error': 'Unauthorized to create debt issuance'}), 403
        
        data = request.get_json()
        required_fields = ['instrument_type', 'amount', 'maturity', 'expected_yield']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In production, this would create actual debt issuance
        issuance_id = f"SOVEREIGN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            'status': 'success',
            'message': 'Debt issuance created successfully',
            'issuance_id': issuance_id,
            'details': {
                'instrument_type': data['instrument_type'],
                'amount_billions': data['amount'],
                'maturity': data['maturity'],
                'expected_yield': data['expected_yield'],
                'auction_date': data.get('auction_date'),
                'settlement_date': data.get('settlement_date')
            },
            'created_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"Debt issuance creation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to create debt issuance',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@sovereign_api_bp.route('/fx-intervention', methods=['POST'])
@login_required
def create_fx_intervention():
    """Create foreign exchange intervention"""
    try:
        if not _has_sovereign_write_access(current_user):
            return jsonify({'error': 'Unauthorized to perform FX interventions'}), 403
        
        data = request.get_json()
        required_fields = ['currency_pair', 'direction', 'amount', 'target_rate']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In production, this would execute actual FX intervention
        intervention_id = f"FX-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            'status': 'success',
            'message': 'FX intervention executed successfully',
            'intervention_id': intervention_id,
            'details': {
                'currency_pair': data['currency_pair'],
                'direction': data['direction'],
                'amount_millions': data['amount'],
                'target_rate': data['target_rate'],
                'execution_strategy': data.get('strategy', 'market_order')
            },
            'executed_by': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logging.error(f"FX intervention error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'Failed to execute FX intervention',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def _has_sovereign_api_access(user) -> bool:
    """Check if user has sovereign banking API access"""
    if not user or not user.is_authenticated:
        return False
    
    sovereign_roles = [
        'central_bank_governor',
        'sovereign_banker',
        'monetary_policy_committee',
        'treasury_officer',
        'admin',
        'super_admin'
    ]
    
    user_role = getattr(user, 'role', None)
    return user_role in sovereign_roles

def _has_sovereign_write_access(user) -> bool:
    """Check if user has sovereign banking write access"""
    if not user or not user.is_authenticated:
        return False
    
    write_roles = [
        'central_bank_governor',
        'monetary_policy_committee',
        'super_admin'
    ]
    
    user_role = getattr(user, 'role', None)
    return user_role in write_roles