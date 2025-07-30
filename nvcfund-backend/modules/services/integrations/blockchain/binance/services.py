"""
Binance Integration Services
OAuth 2.0 authentication and API services for Binance integration
"""

import os
import logging
import secrets
import hashlib
import base64
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
import json

logger = logging.getLogger(__name__)

class BinanceOAuthService:
    """
    Binance OAuth 2.0 authentication service
    Handles authorization flow, token management, and secure API access
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Binance OAuth endpoints
        self.auth_base_url = "https://accounts.binance.com/en/oauth/authorize"
        self.token_url = "https://accounts.binance.com/oauth/token"
        self.api_base_url = "https://www.binanceapis.com/oauth-api/v1"
        
        # Binance API configuration from Replit secrets
        self.api_key = os.environ.get('BINANCE_API_KEY')
        self.secret_key = os.environ.get('BINANCE_SECRET_KEY')
        self.base_url = "https://api.binance.com"
        
        # OAuth configuration
        self.client_id = os.environ.get('BINANCE_CLIENT_ID')
        self.client_secret = os.environ.get('BINANCE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('BINANCE_REDIRECT_URI', 'http://localhost:5000/binance/callback')
        
        # Supported scopes
        self.available_scopes = [
            'user:openId',
            'user:email',
            'create:apikey',
            'read:account',
            'trade:spot',
            'trade:futures'
        ]
        
    def generate_authorization_url(self, scopes: List[str], state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate OAuth authorization URL with PKCE or standard flow
        
        Args:
            scopes: List of requested permission scopes
            state: CSRF protection token
            
        Returns:
            Dictionary containing authorization URL and verification data
        """
        try:
            # Generate CSRF state token if not provided
            if not state:
                state = secrets.token_urlsafe(32)
            
            # Generate PKCE code verifier and challenge for browser/mobile apps
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)
            
            # Validate requested scopes
            invalid_scopes = [scope for scope in scopes if scope not in self.available_scopes]
            if invalid_scopes:
                raise ValueError(f"Invalid scopes requested: {invalid_scopes}")
            
            # Build authorization parameters
            auth_params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'state': state,
                'scope': ','.join(scopes),
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            
            authorization_url = f"{self.auth_base_url}?{urlencode(auth_params)}"
            
            self.logger.info(f"Generated Binance OAuth authorization URL for scopes: {scopes}")
            
            return {
                'authorization_url': authorization_url,
                'state': state,
                'code_verifier': code_verifier,
                'scopes_requested': scopes
            }
            
        except Exception as e:
            self.logger.error(f"Error generating authorization URL: {e}")
            raise
    
    def exchange_code_for_tokens(self, authorization_code: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            authorization_code: Code received from OAuth callback
            code_verifier: PKCE code verifier (for PKCE flow)
            
        Returns:
            Token response with access_token, refresh_token, and metadata
        """
        try:
            if not self.client_id or not self.client_secret:
                raise ValueError("Binance client credentials not configured")
            
            # Prepare token exchange request
            token_data = {
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri
            }
            
            # Add PKCE code verifier if provided
            if code_verifier:
                token_data['code_verifier'] = code_verifier
            
            # Make token exchange request
            response = requests.post(
                self.token_url,
                data=token_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # Add token metadata
                token_response['created_at'] = datetime.utcnow().isoformat()
                token_response['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_response.get('expires_in', 3600))
                ).isoformat()
                
                self.logger.info("Successfully exchanged authorization code for tokens")
                return token_response
            else:
                error_msg = f"Token exchange failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
        """
        try:
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(
                self.token_url,
                data=refresh_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                # Add token metadata
                token_response['created_at'] = datetime.utcnow().isoformat()
                token_response['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_response.get('expires_in', 3600))
                ).isoformat()
                
                self.logger.info("Successfully refreshed access token")
                return token_response
            else:
                error_msg = f"Token refresh failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error refreshing access token: {e}")
            raise
    
    def revoke_access_token(self, access_token: str) -> bool:
        """
        Revoke access token to invalidate session
        
        Args:
            access_token: Valid access token to revoke
            
        Returns:
            True if revocation successful
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/revoke-token",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', False) and result.get('data', False)
                
                if success:
                    self.logger.info("Successfully revoked access token")
                    return True
                else:
                    self.logger.warning(f"Token revocation returned unsuccessful: {result}")
                    return False
            else:
                self.logger.error(f"Token revocation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error revoking access token: {e}")
            return False
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class BinanceAPIService:
    """
    Binance API service for authenticated requests
    Handles user data retrieval and trading operations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.api_key = os.environ.get('BINANCE_API_KEY')
        self.secret_key = os.environ.get('BINANCE_SECRET_KEY')
        self.base_url = "https://api.binance.com"
        
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information using API key
        
        Returns:
            Account information from Binance API
        """
        try:
            if not self.api_key or not self.secret_key:
                return {
                    'status': 'error',
                    'error': 'API credentials not configured'
                }
            
            import hmac
            import hashlib
            import time
            
            timestamp = int(time.time() * 1000)
            query_string = f'timestamp={timestamp}'
            
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            url = f"{self.base_url}/api/v3/account"
            headers = {
                'X-MBX-APIKEY': self.api_key
            }
            params = {
                'timestamp': timestamp,
                'signature': signature
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                account_data = response.json()
                self.logger.info("Successfully retrieved account info")
                return {
                    'status': 'success',
                    'account_data': account_data,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_ticker_prices(self) -> Dict[str, Any]:
        """
        Get live cryptocurrency prices (using CoinGecko API as fallback for geo-restrictions)
        
        Returns:
            Live cryptocurrency price data
        """
        try:
            # Try Binance first
            url = f"{self.base_url}/api/v3/ticker/24hr"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                ticker_data = response.json()
                self.logger.info(f"Successfully retrieved {len(ticker_data)} ticker prices from Binance")
                # Prioritize major cryptocurrencies for display
                priority_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT',
                                  'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT', 'LINKUSDT', 'LTCUSDT']
                priority_tickers = []
                other_tickers = []

                for ticker in ticker_data:
                    if ticker.get('symbol') in priority_symbols:
                        priority_tickers.append(ticker)
                    else:
                        other_tickers.append(ticker)

                # Combine priority tickers first, then fill with others up to 20 total
                display_tickers = priority_tickers + other_tickers[:20-len(priority_tickers)]

                return {
                    'status': 'success',
                    'source': 'binance',
                    'ticker_data': display_tickers,
                    'total_symbols': len(ticker_data),
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            elif response.status_code == 451:
                # Geo-restricted, use CoinGecko fallback
                self.logger.info("Binance geo-restricted, using CoinGecko fallback")
                return self._get_coingecko_prices()
            else:
                error_msg = f"Binance API request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                # Try CoinGecko fallback
                return self._get_coingecko_prices()
                
        except Exception as e:
            self.logger.error(f"Error getting ticker prices from Binance: {e}")
            # Try CoinGecko fallback
            return self._get_coingecko_prices()
    
    def _get_coingecko_prices(self) -> Dict[str, Any]:
        """
        Get cryptocurrency prices from CoinGecko API (fallback)
        
        Returns:
            Live cryptocurrency price data from CoinGecko
        """
        try:
            # Get top 50 cryptocurrencies by market cap
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 50,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                coin_data = response.json()
                
                # Convert to Binance-like format
                ticker_data = []
                for coin in coin_data:
                    ticker_data.append({
                        'symbol': f"{coin['symbol'].upper()}USDT",
                        'lastPrice': str(coin['current_price']),
                        'priceChangePercent': str(coin['price_change_percentage_24h'] or 0),
                        'volume': str(coin['total_volume'] or 0),
                        'openPrice': str(coin['current_price'] - (coin['price_change_24h'] or 0)),
                        'highPrice': str(coin['high_24h'] or coin['current_price']),
                        'lowPrice': str(coin['low_24h'] or coin['current_price']),
                        'name': coin['name']
                    })
                
                self.logger.info(f"Successfully retrieved {len(ticker_data)} prices from CoinGecko")
                return {
                    'status': 'success',
                    'source': 'coingecko',
                    'ticker_data': ticker_data,
                    'total_symbols': len(ticker_data),
                    'retrieved_at': datetime.utcnow().isoformat(),
                    'note': 'Using CoinGecko API due to Binance geo-restrictions'
                }
            else:
                error_msg = f"CoinGecko API request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error getting prices from CoinGecko: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current price for a specific symbol
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            
        Returns:
            Price data for the symbol
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                price_data = response.json()
                self.logger.info(f"Successfully retrieved price for {symbol}")
                return {
                    'status': 'success',
                    'price_data': price_data,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'status': 'error',
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def validate_token(self, access_token: str) -> Dict[str, Any]:
        """
        Validate access token by making a test API call
        
        Args:
            access_token: Access token to validate
            
        Returns:
            Validation result with token status
        """
        try:
            user_info = self.get_user_info(access_token)
            
            if user_info['status'] == 'success':
                return {
                    'valid': True,
                    'user_id': user_info['user_data'].get('userId'),
                    'email': user_info['user_data'].get('email'),
                    'validated_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'valid': False,
                    'error': user_info.get('error', 'Token validation failed'),
                    'validated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            return {
                'valid': False,
                'error': str(e),
                'validated_at': datetime.utcnow().isoformat()
            }
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get current exchange trading rules and symbol information"""
        try:
            url = f"{self.base_url}/api/v3/exchangeInfo"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                exchange_data = response.json()
                active_symbols = [s for s in exchange_data.get('symbols', []) if s.get('status') == 'TRADING']
                
                self.logger.info(f"Successfully retrieved exchange info for {len(active_symbols)} active symbols")
                return {
                    'status': 'success',
                    'exchange_data': {
                        'timezone': exchange_data.get('timezone'),
                        'server_time': exchange_data.get('serverTime'),
                        'symbols': active_symbols[:100],
                        'total_symbols': len(active_symbols)
                    },
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                return self._get_coingecko_exchange_info()
        except Exception as e:
            self.logger.error(f"Error getting exchange info: {e}")
            return self._get_coingecko_exchange_info()
    
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book depth for a symbol"""
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {'symbol': symbol, 'limit': limit}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                order_book = response.json()
                self.logger.info(f"Successfully retrieved order book for {symbol}")
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'order_book': order_book,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"Order book API failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {'status': 'error', 'error': error_msg, 'status_code': response.status_code}
        except Exception as e:
            self.logger.error(f"Error getting order book for {symbol}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_recent_trades(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get recent trades for a symbol"""
        try:
            url = f"{self.base_url}/api/v3/trades"
            params = {'symbol': symbol, 'limit': limit}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                trades = response.json()
                self.logger.info(f"Successfully retrieved {len(trades)} recent trades for {symbol}")
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'trades': trades,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"Recent trades API failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {'status': 'error', 'error': error_msg, 'status_code': response.status_code}
        except Exception as e:
            self.logger.error(f"Error getting recent trades for {symbol}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_kline_data(self, symbol: str, interval: str = '1h', limit: int = 24) -> Dict[str, Any]:
        """Get kline/candlestick data for a symbol"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                klines = response.json()
                formatted_klines = []
                for kline in klines:
                    formatted_klines.append({
                        'open_time': kline[0],
                        'open_price': float(kline[1]),
                        'high_price': float(kline[2]),
                        'low_price': float(kline[3]),
                        'close_price': float(kline[4]),
                        'volume': float(kline[5]),
                        'close_time': kline[6],
                        'quote_volume': float(kline[7]),
                        'trades_count': kline[8]
                    })
                
                self.logger.info(f"Successfully retrieved {len(formatted_klines)} klines for {symbol}")
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'interval': interval,
                    'klines': formatted_klines,
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"Kline data API failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {'status': 'error', 'error': error_msg, 'status_code': response.status_code}
        except Exception as e:
            self.logger.error(f"Error getting kline data for {symbol}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _get_coingecko_exchange_info(self) -> Dict[str, Any]:
        """Get exchange info from CoinGecko (fallback)"""
        try:
            url = "https://api.coingecko.com/api/v3/exchanges/binance"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                exchange_data = response.json()
                self.logger.info("Successfully retrieved exchange info from CoinGecko")
                return {
                    'status': 'success',
                    'source': 'coingecko',
                    'exchange_data': {
                        'name': exchange_data.get('name'),
                        'year_established': exchange_data.get('year_established'),
                        'country': exchange_data.get('country'),
                        'trust_score': exchange_data.get('trust_score'),
                        'trade_volume_24h_btc': exchange_data.get('trade_volume_24h_btc'),
                        'url': exchange_data.get('url')
                    },
                    'note': 'Using CoinGecko API due to Binance geo-restrictions',
                    'retrieved_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"CoinGecko exchange API failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {'status': 'error', 'error': error_msg, 'status_code': response.status_code}
        except Exception as e:
            self.logger.error(f"Error getting exchange info from CoinGecko: {e}")
            return {'status': 'error', 'error': str(e)}


class BinanceIntegrationService:
    """
    Main Binance integration service
    Combines OAuth and API services for complete integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.oauth_service = BinanceOAuthService()
        self.api_service = BinanceAPIService()
        
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get current integration status and configuration
        
        Returns:
            Integration status information
        """
        try:
            has_credentials = bool(
                os.environ.get('BINANCE_CLIENT_ID') and 
                os.environ.get('BINANCE_CLIENT_SECRET')
            )
            
            return {
                'status': 'configured' if has_credentials else 'not_configured',
                'has_credentials': has_credentials,
                'redirect_uri': self.oauth_service.redirect_uri,
                'available_scopes': self.oauth_service.available_scopes,
                'api_endpoints': [
                    'user-info',
                    'revoke-token'
                ],
                'oauth_flows_supported': [
                    'authorization_code',
                    'pkce'
                ],
                'last_checked': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_checked': datetime.utcnow().isoformat()
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data for Binance integration overview
        
        Returns:
            Dashboard data with integration metrics
        """
        try:
            integration_status = self.get_integration_status()
            
            return {
                'integration_status': integration_status,
                'oauth_endpoints': {
                    'authorization': self.oauth_service.auth_base_url,
                    'token': self.oauth_service.token_url,
                    'api_base': self.oauth_service.api_base_url
                },
                'security_features': [
                    'OAuth 2.0 Authorization Code Flow',
                    'PKCE (Proof Key for Code Exchange)',
                    'CSRF Protection with State Parameter',
                    'Secure Token Storage',
                    'Token Refresh and Revocation'
                ],
                'supported_operations': [
                    'User Authentication',
                    'Account Information Retrieval',
                    'Token Management',
                    'Secure API Access'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }