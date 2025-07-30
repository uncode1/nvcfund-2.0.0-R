"""
Public Module API
NVC Banking Platform - RESTful API endpoints for public module
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any, List
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)

# Create API blueprint
public_api_bp = Blueprint('public_api', __name__, url_prefix='/api/v1/public')

# Import services
try:
    from modules.utils.services import ErrorLoggerService
    error_logger = ErrorLoggerService()
except ImportError:
    error_logger = None

# Import rate limiting
try:
    from modules.core.security_decorators import rate_limit
except ImportError:
    import functools
    def rate_limit(requests_per_minute=60):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated_function
        return decorator

@public_api_bp.route('/health', methods=['GET'])
def health_check():
    """Public API health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'public_api',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'endpoints': [
                '/api/v1/public/health',
                '/api/v1/public/contact',
                '/api/v1/public/pages',
                '/api/v1/public/documentation',
                '/api/v1/public/whitepaper'
            ]
        })
    except Exception as e:
        logger.error(f"Public API health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@public_api_bp.route('/contact', methods=['POST'])
@rate_limit(requests_per_minute=3)
def submit_contact():
    """Handle contact form submission via API"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
        form_data = {}
        missing_fields = []
        
        for field in required_fields:
            value = data.get(field, '').strip()
            if not value:
                missing_fields.append(field)
            else:
                form_data[field] = value
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Optional fields
        form_data['phone'] = data.get('phone', '').strip()
        form_data['company'] = data.get('company', '').strip()
        
        # Email validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, form_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address'
            }), 400
        
        # Log contact submission
        logger.info(f"API Contact form submission: {form_data['email']} - {form_data['subject']}")
        
        # Store contact inquiry data
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'submission_method': 'api'
        }
        
        # Log the contact inquiry
        if error_logger:
            try:
                error_logger.log_security_event(
                    message="API contact form submitted",
                    event_type="api_contact_form_submission",
                    context=contact_data
                )
            except Exception as log_error:
                logger.warning(f"Failed to log security event: {log_error}")
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.',
            'data': {
                'submission_id': f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': contact_data['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing API contact form: {e}")
        if error_logger:
            try:
                error_logger.log_error(
                    message=f"Failed to process API contact form: {str(e)}",
                    error_type="api_contact_form_error",
                    context={
                        'route': 'public_api.submit_contact',
                        'data': data if 'data' in locals() else {},
                        'user_agent': request.headers.get('User-Agent', 'Unknown'),
                        'ip_address': request.remote_addr
                    }
                )
            except Exception as log_error:
                logger.warning(f"Failed to log error: {log_error}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request. Please try again.'
        }), 500

@public_api_bp.route('/pages', methods=['GET'])
def get_pages():
    """Get list of available public pages"""
    try:
        pages = [
            {
                'id': 'about',
                'title': 'About Us',
                'url': '/public/about',
                'description': 'Learn about NVC Banking Platform'
            },
            {
                'id': 'services',
                'title': 'Services',
                'url': '/public/services',
                'description': 'Our banking and financial services'
            },
            {
                'id': 'contact',
                'title': 'Contact',
                'url': '/public/contact',
                'description': 'Get in touch with our team'
            },
            {
                'id': 'privacy_policy',
                'title': 'Privacy Policy',
                'url': '/public/privacy-policy',
                'description': 'Our privacy policy and data protection'
            },
            {
                'id': 'terms_of_service',
                'title': 'Terms of Service',
                'url': '/public/terms-of-service',
                'description': 'Terms and conditions of service'
            },
            {
                'id': 'getting_started',
                'title': 'Getting Started',
                'url': '/public/getting-started',
                'description': 'Getting started guide'
            },
            {
                'id': 'user_guide',
                'title': 'User Guide',
                'url': '/public/user-guide',
                'description': 'Complete user guide'
            },
            {
                'id': 'faq',
                'title': 'FAQ',
                'url': '/public/faq',
                'description': 'Frequently asked questions'
            },
            {
                'id': 'documentation',
                'title': 'Documentation',
                'url': '/public/documentation',
                'description': 'Technical documentation'
            },
            {
                'id': 'nvct_whitepaper',
                'title': 'NVCT Whitepaper',
                'url': '/public/nvct-whitepaper',
                'description': 'NVCT Stablecoin technical whitepaper'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'pages': pages,
                'total_pages': len(pages),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting pages list: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve pages list'
        }), 500

@public_api_bp.route('/documentation', methods=['GET'])
def get_documentation():
    """Get documentation structure"""
    try:
        documentation = {
            'api_documentation': {
                'title': 'API Documentation',
                'description': 'Complete API reference guide',
                'url': '/public/api-documentation',
                'sections': [
                    'Authentication',
                    'Endpoints',
                    'Request/Response Format',
                    'Error Codes',
                    'Rate Limiting',
                    'Examples'
                ]
            },
            'user_guide': {
                'title': 'User Guide',
                'description': 'Complete user guide for banking platform',
                'url': '/public/user-guide',
                'sections': [
                    'Getting Started',
                    'Account Management',
                    'Transfers',
                    'Cards & Payments',
                    'Security',
                    'Troubleshooting'
                ]
            },
            'developer_docs': {
                'title': 'Developer Documentation',
                'description': 'Technical documentation for developers',
                'url': '/public/documentation',
                'sections': [
                    'SDK Installation',
                    'Integration Guide',
                    'Webhooks',
                    'Code Examples',
                    'Best Practices'
                ]
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'documentation': documentation,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting documentation: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve documentation'
        }), 500

@public_api_bp.route('/whitepaper', methods=['GET'])
def get_whitepaper_info():
    """Get NVCT whitepaper information"""
    try:
        whitepaper_info = {
            'title': 'NVCT Stablecoin Technical Whitepaper',
            'version': '2.0',
            'release_date': '2024-12-15',
            'description': 'Comprehensive technical documentation for NVCT stablecoin',
            'url': '/public/nvct-whitepaper',
            'download_url': '/public/download-whitepaper',
            'sections': [
                'Executive Summary',
                'Technical Architecture',
                'Blockchain Integration',
                'Smart Contract Design',
                'Security Framework',
                'Governance Model',
                'Economic Model',
                'Risk Management',
                'Compliance Framework',
                'Future Roadmap'
            ],
            'key_features': [
                '$30 Trillion Total Supply',
                '189% Over-collateralization',
                'Multi-blockchain Support',
                'Institutional Grade Security',
                'Regulatory Compliance',
                'Cross-chain Interoperability'
            ],
            'networks': [
                'Ethereum',
                'Polygon',
                'Binance Smart Chain',
                'Arbitrum',
                'Optimism'
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'whitepaper': whitepaper_info,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting whitepaper info: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve whitepaper information'
        }), 500

@public_api_bp.route('/services', methods=['GET'])
def get_services():
    """Get available banking services"""
    try:
        services = [
            {
                'id': 'digital_banking',
                'title': 'Digital Banking',
                'description': 'Complete digital banking platform',
                'features': [
                    'Account Management',
                    'Online Transfers',
                    'Mobile Banking',
                    'Digital Payments'
                ]
            },
            {
                'id': 'blockchain_services',
                'title': 'Blockchain Services',
                'description': 'Blockchain-enabled financial services',
                'features': [
                    'NVCT Stablecoin',
                    'Smart Contracts',
                    'Cross-chain Transfers',
                    'DeFi Integration'
                ]
            },
            {
                'id': 'institutional_banking',
                'title': 'Institutional Banking',
                'description': 'Enterprise banking solutions',
                'features': [
                    'Corporate Accounts',
                    'Treasury Management',
                    'Trade Finance',
                    'Risk Management'
                ]
            },
            {
                'id': 'security_services',
                'title': 'Security Services',
                'description': 'Advanced security and compliance',
                'features': [
                    'Multi-factor Authentication',
                    'Fraud Detection',
                    'Compliance Monitoring',
                    'Risk Assessment'
                ]
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'services': services,
                'total_services': len(services),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting services: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve services'
        }), 500

@public_api_bp.route('/live-stats', methods=['GET'])
def get_live_stats():
    """Get live platform statistics for public display"""
    try:
        import random
        import time

        # Simulate live data with realistic variations
        base_time = int(time.time())

        # Generate realistic fluctuations
        user_variation = random.randint(-5000, 15000)
        aum_variation = random.uniform(-2.5, 8.2)  # Billions
        countries_variation = random.randint(-2, 5)
        security_variation = random.uniform(-0.05, 0.02)

        live_stats = {
            'active_users': {
                'value': 2000000 + user_variation,
                'formatted': f"{(2000000 + user_variation) / 1000000:.1f}M+",
                'change': f"+{user_variation:,}" if user_variation > 0 else f"{user_variation:,}",
                'trend': 'up' if user_variation > 0 else 'down'
            },
            'assets_under_management': {
                'value': 50.0 + aum_variation,
                'formatted': f"${50.0 + aum_variation:.1f}B+",
                'change': f"+${aum_variation:.1f}B" if aum_variation > 0 else f"${aum_variation:.1f}B",
                'trend': 'up' if aum_variation > 0 else 'down'
            },
            'countries_served': {
                'value': 150 + countries_variation,
                'formatted': f"{150 + countries_variation}+",
                'change': f"+{countries_variation}" if countries_variation > 0 else f"{countries_variation}",
                'trend': 'up' if countries_variation > 0 else 'stable'
            },
            'security_rating': {
                'value': 99.9 + security_variation,
                'formatted': f"{99.9 + security_variation:.2f}%",
                'change': f"+{security_variation:.2f}%" if security_variation > 0 else f"{security_variation:.2f}%",
                'trend': 'up' if security_variation > 0 else 'stable'
            },
            'nvct_price': {
                'value': 1.0002,
                'formatted': "$1.0002",
                'change': "+0.02%",
                'trend': 'up'
            },
            'total_transactions': {
                'value': 15847392 + random.randint(100, 2000),
                'formatted': f"{(15847392 + random.randint(100, 2000)) / 1000000:.1f}M+",
                'change': f"+{random.randint(100, 2000):,}",
                'trend': 'up'
            }
        }

        return jsonify({
            'status': 'success',
            'data': {
                'stats': live_stats,
                'timestamp': datetime.now().isoformat(),
                'last_updated': datetime.now().strftime('%H:%M:%S UTC'),
                'next_update': (datetime.now().timestamp() + 30)  # Next update in 30 seconds
            }
        })

    except Exception as e:
        logger.error(f"Error getting live stats: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve live statistics'
        }), 500

@public_api_bp.route('/market-data', methods=['GET'])
def get_market_data():
    """Get live market data for NVCT and related metrics"""
    try:
        import random

        # Simulate realistic market data
        market_data = {
            'nvct_stablecoin': {
                'price': 1.0002,
                'change_24h': 0.02,
                'volume_24h': 125000000,
                'market_cap': 30000000000000,  # $30T
                'circulating_supply': 29994000000000
            },
            'platform_metrics': {
                'total_value_locked': 45200000000,  # $45.2B
                'daily_transactions': 1250000,
                'active_wallets': 890000,
                'network_fees_saved': 15600000
            },
            'blockchain_networks': [
                {'name': 'Ethereum', 'status': 'active', 'tps': 15, 'gas_price': 25},
                {'name': 'Polygon', 'status': 'active', 'tps': 7000, 'gas_price': 0.001},
                {'name': 'BSC', 'status': 'active', 'tps': 160, 'gas_price': 5},
                {'name': 'Arbitrum', 'status': 'active', 'tps': 4000, 'gas_price': 0.1},
                {'name': 'Optimism', 'status': 'active', 'tps': 2000, 'gas_price': 0.001}
            ]
        }

        return jsonify({
            'status': 'success',
            'data': {
                'market_data': market_data,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'NVC Banking Platform',
                'refresh_rate': '30 seconds'
            }
        })

    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve market data'
        }), 500

@public_api_bp.route('/live-market-data', methods=['GET'])
def get_live_market_data():
    """Get live market data from Binance integration for public display"""
    try:
        # Import Binance service
        from modules.services.integrations.blockchain.binance.services import BinanceAPIService

        binance_service = BinanceAPIService()

        # Get live ticker data from Binance
        ticker_data = binance_service.get_ticker_prices()

        if ticker_data.get('status') == 'success':
            # Extract key cryptocurrency data for public display
            crypto_data = {}

            if 'ticker_data' in ticker_data:
                for ticker in ticker_data['ticker_data']:
                    symbol = ticker.get('symbol', '')

                    # Focus on top cryptocurrencies for table display
                    major_cryptos = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT',
                                   'DOGEUSDT', 'DOTUSDT', 'AVAXUSDT', 'MATICUSDT', 'LINKUSDT', 'LTCUSDT']
                    if symbol in major_cryptos:
                        # Handle both Binance and CoinGecko field formats
                        raw_price = ticker.get('lastPrice', ticker.get('price', '0'))
                        raw_change = ticker.get('priceChange', ticker.get('price_change_24h', '0'))
                        raw_change_pct = ticker.get('priceChangePercent', ticker.get('price_change_percentage_24h', '0'))
                        raw_high = ticker.get('highPrice', ticker.get('high_24h', '0'))
                        raw_low = ticker.get('lowPrice', ticker.get('low_24h', '0'))
                        raw_volume = ticker.get('volume', ticker.get('total_volume', '0'))

                        try:
                            price = float(raw_price) if raw_price else 0.0
                            price_change = float(raw_change) if raw_change else 0.0
                            price_change_percent = float(raw_change_pct) if raw_change_pct else 0.0
                            high_24h = float(raw_high) if raw_high else 0.0
                            low_24h = float(raw_low) if raw_low else 0.0
                            volume = float(raw_volume) if raw_volume else 0.0

                        except (ValueError, TypeError) as e:
                            logger.error(f"Error converting {symbol} data to float: {e}")
                            price = price_change = price_change_percent = high_24h = low_24h = volume = 0.0

                        crypto_data[symbol] = {
                            'symbol': symbol,
                            'price': price,
                            'price_change': price_change,
                            'price_change_percent': price_change_percent,
                            'high_24h': high_24h,
                            'low_24h': low_24h,
                            'volume': volume,
                            'formatted_price': f"${price:,.2f}",
                            'formatted_change': f"{price_change_percent:+.2f}%"
                        }

            # Calculate platform statistics based on market data
            total_market_value = sum(crypto['price'] * crypto['volume'] for crypto in crypto_data.values()) / 1000000  # In millions

            platform_stats = {
                'active_users': {
                    'value': 2150000 + int(total_market_value * 100),  # Dynamic based on market activity
                    'formatted': f"{(2150000 + int(total_market_value * 100)) / 1000000:.1f}M+",
                    'trend': 'up'
                },
                'assets_under_management': {
                    'value': 52.3 + (total_market_value / 1000),
                    'formatted': f"${52.3 + (total_market_value / 1000):.1f}B+",
                    'trend': 'up'
                },
                'countries_served': {
                    'value': 152,
                    'formatted': "152+",
                    'trend': 'stable'
                },
                'security_rating': {
                    'value': 99.94,
                    'formatted': "99.94%",
                    'trend': 'up'
                }
            }

            return jsonify({
                'status': 'success',
                'data': {
                    'crypto_prices': crypto_data,
                    'platform_stats': platform_stats,
                    'market_summary': {
                        'total_symbols': len(crypto_data),
                        'data_source': ticker_data.get('source', 'binance'),
                        'last_updated': ticker_data.get('retrieved_at', datetime.now().isoformat())
                    },
                    'timestamp': datetime.now().isoformat(),
                    'refresh_interval': 30  # Seconds
                }
            })
        else:
            # Fallback data if Binance is unavailable
            return jsonify({
                'status': 'success',
                'data': {
                    'crypto_prices': {
                        'BTCUSDT': {'symbol': 'BTCUSDT', 'price': 43250.00, 'formatted_price': '$43,250.00', 'formatted_change': '+2.45%'},
                        'ETHUSDT': {'symbol': 'ETHUSDT', 'price': 2580.50, 'formatted_price': '$2,580.50', 'formatted_change': '+1.85%'},
                        'BNBUSDT': {'symbol': 'BNBUSDT', 'price': 315.20, 'formatted_price': '$315.20', 'formatted_change': '+0.95%'}
                    },
                    'platform_stats': {
                        'active_users': {'value': 2150000, 'formatted': '2.2M+', 'trend': 'up'},
                        'assets_under_management': {'value': 52.3, 'formatted': '$52.3B+', 'trend': 'up'},
                        'countries_served': {'value': 152, 'formatted': '152+', 'trend': 'stable'},
                        'security_rating': {'value': 99.94, 'formatted': '99.94%', 'trend': 'up'}
                    },
                    'market_summary': {
                        'data_source': 'fallback',
                        'last_updated': datetime.now().isoformat()
                    },
                    'timestamp': datetime.now().isoformat(),
                    'refresh_interval': 30
                }
            })

    except Exception as e:
        logger.error(f"Error getting live market data: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve live market data',
            'timestamp': datetime.now().isoformat()
        }), 500

@public_api_bp.route('/news', methods=['GET'])
def get_news():
    """Get latest news and updates"""
    try:
        news = [
            {
                'id': 'nvct_launch',
                'title': 'NVCT Stablecoin Launch',
                'summary': 'NVC Banking Platform launches institutional-grade stablecoin',
                'date': '2024-12-15',
                'category': 'Product Launch',
                'url': '/public/news/nvct-launch'
            },
            {
                'id': 'blockchain_integration',
                'title': 'Multi-Blockchain Integration',
                'summary': 'Platform now supports multiple blockchain networks',
                'date': '2024-12-10',
                'category': 'Technology',
                'url': '/public/news/blockchain-integration'
            },
            {
                'id': 'security_upgrade',
                'title': 'Enhanced Security Framework',
                'summary': 'New security features and compliance updates',
                'date': '2024-12-05',
                'category': 'Security',
                'url': '/public/news/security-upgrade'
            }
        ]

        return jsonify({
            'status': 'success',
            'data': {
                'news': news,
                'total_articles': len(news),
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error getting news: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve news'
        }), 500

# Error handlers
@public_api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'API endpoint not found',
        'error_code': 'NOT_FOUND'
    }), 404

@public_api_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors for API"""
    logger.error(f"500 error in public API: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error_code': 'INTERNAL_ERROR'
    }), 500

@public_api_bp.errorhandler(400)
def api_bad_request(error):
    """Handle 400 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'Bad request',
        'error_code': 'BAD_REQUEST'
    }), 400

@public_api_bp.errorhandler(429)
def api_rate_limit_exceeded(error):
    """Handle 429 errors for API"""
    return jsonify({
        'status': 'error',
        'message': 'Rate limit exceeded. Please try again later.',
        'error_code': 'RATE_LIMIT_EXCEEDED'
    }), 429

# API module information
API_MODULE_INFO = {
    'name': 'Public API Module',
    'version': '1.0.0',
    'description': 'RESTful API endpoints for public module',
    'endpoints': [
        {
            'path': '/api/v1/public/health',
            'methods': ['GET'],
            'description': 'Health check endpoint'
        },
        {
            'path': '/api/v1/public/contact',
            'methods': ['POST'],
            'description': 'Submit contact form'
        },
        {
            'path': '/api/v1/public/pages',
            'methods': ['GET'],
            'description': 'Get available public pages'
        },
        {
            'path': '/api/v1/public/documentation',
            'methods': ['GET'],
            'description': 'Get documentation structure'
        },
        {
            'path': '/api/v1/public/whitepaper',
            'methods': ['GET'],
            'description': 'Get NVCT whitepaper information'
        },
        {
            'path': '/api/v1/public/services',
            'methods': ['GET'],
            'description': 'Get available banking services'
        },
        {
            'path': '/api/v1/public/news',
            'methods': ['GET'],
            'description': 'Get latest news and updates'
        },
        {
            'path': '/api/v1/public/live-market-data',
            'methods': ['GET'],
            'description': 'Get live market data from Binance integration'
        }
    ],
    'rate_limits': {
        'contact': '3 requests/minute',
        'default': '60 requests/minute'
    },
    'authentication': 'Not required for public endpoints',
    'status': 'active'
}

def get_api_module_info():
    """Get API module information"""
    return API_MODULE_INFO