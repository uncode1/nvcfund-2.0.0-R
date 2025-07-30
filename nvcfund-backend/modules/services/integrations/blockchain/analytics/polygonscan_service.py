"""
Polygonscan API Service for NVC Banking Platform
Provides comprehensive token analytics and ERC-20 token management for Polygon network
"""

import os
import requests
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from modules.core.constants import APIHealthStatus


@dataclass
class PolygonTokenInfo:
    """Polygon token information data structure"""
    contract_address: str
    name: str
    symbol: str
    decimals: int
    total_supply: str
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None


@dataclass
class PolygonTokenBalance:
    """Polygon token balance data structure"""
    contract_address: str
    token_name: str
    token_symbol: str
    balance: str
    decimals: int
    value_usd: Optional[float] = None


@dataclass
class PolygonTokenHolder:
    """Polygon token holder data structure"""
    address: str
    balance: str
    percentage: float
    rank: int


class PolygonscanService:
    """Comprehensive Polygonscan API integration service"""
    
    def __init__(self):
        self.api_key = os.getenv('POLYGONSCAN_API_KEY', 'YourApiKeyToken')
        self.base_url = 'https://api.polygonscan.com/api'
        self.rate_limit_delay = 0.2  # 5 requests per second for free tier
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make API request with rate limiting and error handling"""
        self._rate_limit()
        
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1':
                return data
            else:
                print(f"Polygonscan API error: {data.get('message', 'Unknown error')}")
                # Return fallback data when API is unavailable
                return {
                    'status': '0',
                    'message': 'API temporarily unavailable',
                    'result': []
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health and connectivity"""
        try:
            # Test with a simple API call
            params = {
                'app_module': 'stats',
                'action': 'tokenbalance',
                'contractaddress': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',  # USDC on Polygon
                'address': '0x0000000000000000000000000000000000000000',
                'tag': 'latest'
            }
            
            response = self._make_request(params)
            
            if response is not None:
                return {
                    'status': APIHealthStatus.HEALTHY,
                    'message': 'Polygonscan API accessible',
                    'api_key_configured': bool(self.api_key and self.api_key != 'YourApiKeyToken'),
                    'rate_limit': '5 requests/second (free tier)'
                }
            else:
                return {
                    'status': APIHealthStatus.UNHEALTHY,
                    'message': 'Polygonscan API not accessible',
                    'api_key_configured': bool(self.api_key and self.api_key != 'YourApiKeyToken'),
                    'rate_limit': '5 requests/second (free tier)'
                }
                
        except Exception as e:
            return {
                'status': APIHealthStatus.UNHEALTHY,
                'message': f'Health check failed: {str(e)}',
                'api_key_configured': bool(self.api_key and self.api_key != 'YourApiKeyToken'),
                'rate_limit': '5 requests/second (free tier)'
            }
    
    def get_token_info(self, contract_address: str) -> Optional[PolygonTokenInfo]:
        """Get comprehensive token information"""
        try:
            # Get token name
            name_params = {
                'app_module': 'token',
                'action': 'tokeninfo',
                'contractaddress': contract_address
            }
            
            response = self._make_request(name_params)
            if not response or 'result' not in response:
                return None
            
            token_data = response['result'][0] if response['result'] else {}
            
            # Get token supply
            supply_params = {
                'app_module': 'stats',
                'action': 'tokensupply',
                'contractaddress': contract_address
            }
            
            supply_response = self._make_request(supply_params)
            total_supply = supply_response.get('result', '0') if supply_response else '0'
            
            return PolygonTokenInfo(
                contract_address=contract_address,
                name=token_data.get('tokenName', 'Unknown'),
                symbol=token_data.get('symbol', 'UNK'),
                decimals=int(token_data.get('divisor', 18)),
                total_supply=total_supply
            )
            
        except Exception as e:
            print(f"Error getting token info: {e}")
            return None
    
    def get_token_balance(self, contract_address: str, wallet_address: str) -> Optional[str]:
        """Get token balance for a specific wallet"""
        try:
            params = {
                'app_module': 'account',
                'action': 'tokenbalance',
                'contractaddress': contract_address,
                'address': wallet_address,
                'tag': 'latest'
            }
            
            response = self._make_request(params)
            if response and 'result' in response:
                return response['result']
            return None
            
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return None
    
    def get_token_holders(self, contract_address: str, page: int = 1, offset: int = 100) -> List[PolygonTokenHolder]:
        """Get token holders (requires Pro API subscription)"""
        try:
            params = {
                'app_module': 'token',
                'action': 'tokenholderlist',
                'contractaddress': contract_address,
                'page': page,
                'offset': offset
            }
            
            response = self._make_request(params)
            if not response or 'result' not in response:
                return []
            
            holders = []
            for i, holder_data in enumerate(response['result'], 1):
                holders.append(PolygonTokenHolder(
                    address=holder_data.get('TokenHolderAddress', ''),
                    balance=holder_data.get('TokenHolderQuantity', '0'),
                    percentage=float(holder_data.get('TokenHolderPercentage', 0)),
                    rank=i
                ))
            
            return holders
            
        except Exception as e:
            print(f"Error getting token holders: {e}")
            return []
    
    def get_token_transfers(self, contract_address: str, page: int = 1, offset: int = 100) -> List[Dict[str, Any]]:
        """Get token transfer history"""
        try:
            params = {
                'app_module': 'account',
                'action': 'tokentx',
                'contractaddress': contract_address,
                'page': page,
                'offset': offset,
                'sort': 'desc'
            }
            
            response = self._make_request(params)
            if not response or 'result' not in response:
                return []
            
            transfers = []
            for transfer in response['result']:
                transfers.append({
                    'hash': transfer.get('hash', ''),
                    'from': transfer.get('from', ''),
                    'to': transfer.get('to', ''),
                    'value': transfer.get('value', '0'),
                    'timestamp': transfer.get('timeStamp', '0'),
                    'token_name': transfer.get('tokenName', ''),
                    'token_symbol': transfer.get('tokenSymbol', ''),
                    'token_decimal': transfer.get('tokenDecimal', '18')
                })
            
            return transfers
            
        except Exception as e:
            print(f"Error getting token transfers: {e}")
            return []
    
    def get_multiple_token_balances(self, wallet_address: str, contract_addresses: List[str]) -> List[PolygonTokenBalance]:
        """Get balances for multiple tokens"""
        balances = []
        
        for contract_address in contract_addresses:
            try:
                balance = self.get_token_balance(contract_address, wallet_address)
                if balance:
                    token_info = self.get_token_info(contract_address)
                    if token_info:
                        balances.append(PolygonTokenBalance(
                            contract_address=contract_address,
                            token_name=token_info.name,
                            token_symbol=token_info.symbol,
                            balance=balance,
                            decimals=token_info.decimals
                        ))
            except Exception as e:
                print(f"Error getting balance for {contract_address}: {e}")
                continue
        
        return balances
    
    def get_popular_tokens(self) -> List[Dict[str, Any]]:
        """Get popular Polygon tokens"""
        # Popular tokens on Polygon network
        popular_tokens = [
            {
                'contract_address': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174',
                'name': 'USD Coin',
                'symbol': 'USDC',
                'description': 'Stablecoin pegged to USD'
            },
            {
                'contract_address': '0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
                'name': 'Tether USD',
                'symbol': 'USDT',
                'description': 'Stablecoin pegged to USD'
            },
            {
                'contract_address': '0x7ceb23fd6f88b2c5c7c5fc3c0a8cf8e8c0e5ab9e',
                'name': 'Wrapped Ether',
                'symbol': 'WETH',
                'description': 'Wrapped Ethereum on Polygon'
            },
            {
                'contract_address': '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6',
                'name': 'Wrapped Bitcoin',
                'symbol': 'WBTC',
                'description': 'Wrapped Bitcoin on Polygon'
            },
            {
                'contract_address': '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063',
                'name': 'Dai Stablecoin',
                'symbol': 'DAI',
                'description': 'Decentralized stablecoin'
            }
        ]
        
        return popular_tokens
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get Polygon network statistics"""
        try:
            # Get MATIC price
            params = {
                'app_module': 'stats',
                'action': 'maticprice'
            }
            
            response = self._make_request(params)
            matic_price = 0.0
            if response and 'result' in response:
                matic_price = float(response['result'].get('maticusd', 0))
            
            return {
                'network': 'Polygon',
                'native_token': 'MATIC',
                'matic_price_usd': matic_price,
                'block_time': '~2 seconds',
                'consensus': 'Proof of Stake',
                'explorer': 'https://polygonscan.com'
            }
            
        except Exception as e:
            print(f"Error getting network stats: {e}")
            return {
                'network': 'Polygon',
                'native_token': 'MATIC',
                'matic_price_usd': 0.0,
                'block_time': '~2 seconds',
                'consensus': 'Proof of Stake',
                'explorer': 'https://polygonscan.com'
            }
    
    def convert_wei_to_readable(self, wei_amount: str, decimals: int) -> str:
        """Convert wei amount to readable format"""
        try:
            if not wei_amount or wei_amount == '0':
                return '0'
            
            # Convert to float and adjust for decimals
            amount = float(wei_amount) / (10 ** decimals)
            
            # Format with appropriate decimal places
            if amount < 0.01:
                return f"{amount:.8f}"
            elif amount < 1:
                return f"{amount:.6f}"
            elif amount < 1000:
                return f"{amount:.4f}"
            else:
                return f"{amount:,.2f}"
                
        except (ValueError, TypeError):
            return wei_amount