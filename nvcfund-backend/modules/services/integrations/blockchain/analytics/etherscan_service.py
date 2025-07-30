"""
Etherscan API Service for NVC Banking Platform
Provides comprehensive token analytics and ERC-20 token management
"""

import os
import requests
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from modules.core.constants import APIHealthStatus


@dataclass
class TokenInfo:
    """Token information data structure"""
    contract_address: str
    name: str
    symbol: str
    decimals: int
    total_supply: str
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None


@dataclass
class TokenBalance:
    """Token balance data structure"""
    contract_address: str
    token_name: str
    token_symbol: str
    balance: str
    decimals: int
    value_usd: Optional[float] = None


@dataclass
class TokenHolder:
    """Token holder data structure"""
    address: str
    balance: str
    percentage: float
    rank: int


class EtherscanService:
    """Comprehensive Etherscan API integration service"""
    
    def __init__(self):
        self.api_key = os.getenv('ETHERSCAN_API_KEY')
        self.base_url = "https://api.etherscan.io/api"
        self.rate_limit_delay = 0.2  # 5 requests per second for free tier
        self.last_request_time = 0
        
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited request to Etherscan API"""
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'status': '0',
                'message': f'Request failed: {str(e)}',
                'result': None
            }
    
    def get_token_info(self, contract_address: str) -> Optional[TokenInfo]:
        """Get comprehensive token information"""
        params = {
            'app_module': 'token',
            'action': 'tokeninfo',
            'contractaddress': contract_address
        }
        
        response = self._make_request(params)
        if response.get('status') == '1' and response.get('result'):
            result = response['result'][0] if isinstance(response['result'], list) else response['result']
            return TokenInfo(
                contract_address=contract_address,
                name=result.get('tokenName', ''),
                symbol=result.get('symbol', ''),
                decimals=int(result.get('decimals', 0)),
                total_supply=result.get('totalSupply', '0')
            )
        return None
    
    def get_token_supply(self, contract_address: str) -> Optional[str]:
        """Get token total supply"""
        params = {
            'app_module': 'stats',
            'action': 'tokensupply',
            'contractaddress': contract_address
        }
        
        response = self._make_request(params)
        if response.get('status') == '1':
            return response.get('result', '0')
        return None
    
    def get_token_balance(self, contract_address: str, address: str) -> Optional[str]:
        """Get token balance for specific address"""
        params = {
            'app_module': 'account',
            'action': 'tokenbalance',
            'contractaddress': contract_address,
            'address': address,
            'tag': 'latest'
        }
        
        response = self._make_request(params)
        if response.get('status') == '1':
            return response.get('result', '0')
        return None
    
    def get_token_holders(self, contract_address: str, page: int = 1, offset: int = 100) -> List[TokenHolder]:
        """Get token holders list (requires Pro API)"""
        params = {
            'app_module': 'token',
            'action': 'tokenholderlist',
            'contractaddress': contract_address,
            'page': page,
            'offset': offset
        }
        
        response = self._make_request(params)
        holders = []
        
        if response.get('status') == '1' and response.get('result'):
            for idx, holder in enumerate(response['result']):
                holders.append(TokenHolder(
                    address=holder.get('TokenHolderAddress', ''),
                    balance=holder.get('TokenHolderQuantity', '0'),
                    percentage=float(holder.get('TokenHolderPercentage', 0)),
                    rank=idx + 1 + (page - 1) * offset
                ))
        
        return holders
    
    def get_token_transfers(self, contract_address: str, address: Optional[str] = None, 
                          start_block: int = 0, end_block: int = 99999999, 
                          page: int = 1, offset: int = 100) -> List[Dict[str, Any]]:
        """Get token transfer events"""
        params = {
            'app_module': 'account',
            'action': 'tokentx',
            'contractaddress': contract_address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'desc'
        }
        
        if address:
            params['address'] = address
        
        response = self._make_request(params)
        if response.get('status') == '1' and response.get('result'):
            return response['result']
        return []
    
    def get_address_token_balances(self, address: str) -> List[TokenBalance]:
        """Get all token balances for an address"""
        params = {
            'app_module': 'account',
            'action': 'addresstokenbalance',
            'address': address,
            'page': 1,
            'offset': 100
        }
        
        response = self._make_request(params)
        balances = []
        
        if response.get('status') == '1' and response.get('result'):
            for token in response['result']:
                balances.append(TokenBalance(
                    contract_address=token.get('TokenAddress', ''),
                    token_name=token.get('TokenName', ''),
                    token_symbol=token.get('TokenSymbol', ''),
                    balance=token.get('TokenQuantity', '0'),
                    decimals=int(token.get('TokenDivisor', 0))
                ))
        
        return balances
    
    def get_historical_token_data(self, contract_address: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical token transfer data for analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get recent blocks (approximate)
        current_block = self._get_latest_block_number()
        if not current_block:
            return []
        
        # Approximate blocks per day (assuming 13.5 second block time)
        blocks_per_day = 86400 // 13.5
        start_block = int(current_block - (days * blocks_per_day))
        
        transfers = self.get_token_transfers(
            contract_address=contract_address,
            start_block=start_block,
            end_block=current_block,
            offset=1000
        )
        
        return transfers
    
    def _get_latest_block_number(self) -> Optional[int]:
        """Get the latest block number"""
        params = {
            'app_module': 'proxy',
            'action': 'eth_blockNumber'
        }
        
        response = self._make_request(params)
        if response.get('status') == '1':
            return int(response.get('result', '0x0'), 16)
        return None
    
    def get_token_analytics(self, contract_address: str) -> Dict[str, Any]:
        """Get comprehensive token analytics"""
        token_info = self.get_token_info(contract_address)
        if not token_info:
            return {'error': 'Token not found'}
        
        # Get recent transfers for activity analysis
        recent_transfers = self.get_token_transfers(
            contract_address=contract_address,
            offset=100
        )
        
        # Calculate basic metrics
        total_transfers = len(recent_transfers)
        unique_addresses = len(set(
            [tx['from'] for tx in recent_transfers] + 
            [tx['to'] for tx in recent_transfers]
        ))
        
        # Get holders (if available)
        holders = self.get_token_holders(contract_address, offset=50)
        
        return {
            'token_info': {
                'name': token_info.name,
                'symbol': token_info.symbol,
                'decimals': token_info.decimals,
                'total_supply': token_info.total_supply,
                'contract_address': contract_address
            },
            'activity_metrics': {
                'recent_transfers': total_transfers,
                'unique_addresses': unique_addresses,
                'holders_count': len(holders)
            },
            'recent_transfers': recent_transfers[:10],  # Last 10 transfers
            'top_holders': holders[:10] if holders else [],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_multi_token_balances(self, address: str, contract_addresses: List[str]) -> List[TokenBalance]:
        """Get balances for multiple tokens for a single address"""
        balances = []
        
        for contract_address in contract_addresses:
            balance = self.get_token_balance(contract_address, address)
            if balance:
                token_info = self.get_token_info(contract_address)
                if token_info:
                    balances.append(TokenBalance(
                        contract_address=contract_address,
                        token_name=token_info.name,
                        token_symbol=token_info.symbol,
                        balance=balance,
                        decimals=token_info.decimals
                    ))
        
        return balances
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Etherscan API is accessible"""
        if not self.api_key:
            return {
                'status': 'unhealthy',
                'message': 'ETHERSCAN_API_KEY not configured'
            }
        
        # Simple API test
        params = {
            'app_module': 'stats',
            'action': 'ethsupply'
        }
        
        response = self._make_request(params)
        if response.get('status') == '1':
            return {
                'status': APIHealthStatus.HEALTHY,
                'message': 'Etherscan API accessible',
                'api_key_configured': True,
                'rate_limit': '5 requests/second (free tier)'
            }
        else:
            return {
                'status': 'unhealthy',
                'message': response.get('message', 'API request failed'),
                'api_key_configured': True
            }