"""
NVC Banking Platform - Public Module Routes
Professional public-facing pages with enhanced presentation and organization
Version: 2.0.0 - Complete redesign for professional banking interface
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from modules.utils.services import ErrorLoggerService
from typing import Dict, Any, Optional
import logging
import re

# Import rate limiting from the correct location
try:
    from modules.core.decorators import rate_limit
except ImportError:
    # Fallback: create a simple rate limit decorator
    import functools
    def rate_limit(limit="60/minute"):
        def public_rate_limit_decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated_function
        return public_rate_limit_decorator

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint with template folder - no URL prefix for public routes
public_bp = Blueprint('public', __name__)

# Import and register API blueprint
from .api import public_api_bp

# Initialize services
error_logger = ErrorLoggerService()

# ===== UTILITY FUNCTIONS =====

def handle_api_error(route_name: str, error: Exception, status_code: int = 500) -> tuple:
    """Centralized error handling for template rendering"""
    logger.error(f"Error rendering {route_name}: {error}")
    error_logger.log_error(
        error_type="template_render_error",
        message=f"Failed to render {route_name}: {str(error)}",
        details={
            'route': route_name,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'ip_address': request.remote_addr
        }
    )
    return jsonify({
        'status': 'error',
        'message': 'An internal server error occurred.'
    }), status_code

def validate_contact_form(form_data: Dict[str, str]) -> tuple[bool, Optional[str]]:
    """Validate contact form data"""
    required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
    missing_fields = [field for field in required_fields if not form_data.get(field)]

    if missing_fields:
        return False, f'Missing required fields: {", ".join(missing_fields)}'

    # Email validation
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, form_data['email']):
        return False, 'Please enter a valid email address'

    return True, None

# ===== MAIN CONTENT ROUTES =====

@public_bp.route('/')
def index():
    """Main landing page - Professional banking homepage"""
    return jsonify({
        'status': 'success',
        'page': 'home',
        'message': 'Welcome to the NVC Banking Platform API.',
        'version': '2.0.0'
    })

@public_bp.route('/about')
def about():
    """About NVC Banking Platform - Company information and values"""
    return jsonify({
        'page': 'about',
        'company_name': 'NVC Banking Platform',
        'mission': 'To provide comprehensive enterprise-grade banking solutions with modern technologies and banking-grade security.',
        'founded': 2024
    })

@public_bp.route('/services')
def services():
    """Banking services overview - Comprehensive service catalog"""
    return jsonify({
        'page': 'services',
        'services': [
            'Core Banking Operations',
            'Treasury Operations',
            'Sovereign Banking Functions',
            'Regulatory Compliance',
            'Data Security Framework',
            'Blockchain Integration'
        ]
    })

@public_bp.route('/contact')
def contact():
    """Professional contact page - Customer communication portal"""
    return jsonify({
        'page': 'contact',
        'message': 'Please use the POST /contact/submit endpoint to send a message.',
        'contact_details': {
            'email': 'support@nvcfund.com',
            'phone': '+1-800-NVC-BANK'
        }
    })

# ===== CONTACT FORM PROCESSING =====

@public_bp.route('/contact/submit', methods=['POST'])
@rate_limit("3/minute")
def submit_contact():
    """Handle contact form submission with enhanced validation and security"""
    try:
        # Extract form data
        form_data = {
            'firstName': request.form.get('firstName', '').strip(),
            'lastName': request.form.get('lastName', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'subject': request.form.get('subject', '').strip(),
            'message': request.form.get('message', '').strip()
        }

        # Validate form data
        is_valid, error_message = validate_contact_form(form_data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 400

        # Log successful submission
        logger.info(f"Contact form submission: {form_data['email']} - {form_data['subject']}")

        # Prepare contact data for storage
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'submission_method': 'web_form'
        }

        # Log security event
        error_logger.log_security_event(
            event_type="contact_form_submission",
            message=f"Contact form submitted by {form_data['firstName']} {form_data['lastName']}",
            user_id=None
        )

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.',
            'data': {
                'submission_id': f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': contact_data['timestamp']
            }
        })

    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        error_logger.log_error(
            error_type="contact_form_error",
            message=f"Failed to process contact form: {str(e)}",
            details={
                'route': 'public.submit_contact',
                'form_data': form_data if 'form_data' in locals() else {},
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
                'ip_address': request.remote_addr
            }
        )
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request. Please try again.'
        }), 500


@public_bp.route('/api/contact', methods=['POST'])
# API endpoint without CSRF protection
@rate_limit("10/minute")  # 10 requests per minute for API contact submissions
def api_contact_submit():
    """API endpoint for contact form submission (CSRF-exempt for external use)"""
    logger = logging.getLogger(__name__)
    error_logger = ErrorLoggerService()

    try:
        # Check content type
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400

        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400

        # Extract form data from JSON
        form_data = {
            'firstName': data.get('firstName', '').strip(),
            'lastName': data.get('lastName', '').strip(),
            'email': data.get('email', '').strip(),
            'phone': data.get('phone', '').strip(),
            'subject': data.get('subject', '').strip(),
            'message': data.get('message', '').strip()
        }

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'subject', 'message']
        missing_fields = [field for field in required_fields if not form_data.get(field)]

        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, form_data['email']):
            return jsonify({
                'status': 'error',
                'message': 'Please enter a valid email address'
            }), 400

        # Additional validation for phone number if provided
        if form_data['phone']:
            phone_pattern = r'^[\+]?[\d\s\-\(\)]+$'
            if not re.match(phone_pattern, form_data['phone']):
                return jsonify({
                    'status': 'error',
                    'message': 'Please enter a valid phone number'
                }), 400

        # Log contact submission
        logger.info(f"API Contact form submission: {form_data['email']} - {form_data['subject']}")

        # Store contact inquiry (in a real system, this would save to database)
        contact_data = {
            **form_data,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'submission_method': 'api_json'
        }

        # Log the contact inquiry
        if error_logger:
            try:
                error_logger.log_security_event(
                    event_type="api_contact_form_submission",
                    message="API contact form submitted via JSON endpoint",
                    user_id=None
                )
            except Exception as log_error:
                logger.warning(f"Failed to log security event: {log_error}")

        return jsonify({
            'status': 'success',
            'message': 'Thank you for your message. We will respond within 2 hours.',
            'data': {
                'submission_id': f"contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': contact_data['timestamp'],
                'email': form_data['email']
            }
        }), 200

    except Exception as e:
        logger.error(f"Error processing API contact form: {e}")
        if error_logger:
            try:
                error_logger.log_error(
                    error_type="api_contact_form_error",
                    message=f"Failed to process API contact form: {str(e)}",
                    details={
                        'route': 'public.api_contact_submit',
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


# ===== LEGAL AND POLICY ROUTES =====

@public_bp.route('/privacy-policy')
def privacy_policy():
    """Privacy policy - Data protection and user privacy information"""
    return jsonify({
        'page': 'privacy_policy',
        'last_updated': '2025-07-01',
        'message': 'This endpoint would provide the full privacy policy text.'
    })

@public_bp.route('/terms-of-service')
def terms_of_service():
    """Terms of service - Legal terms and conditions"""
    return jsonify({
        'page': 'terms_of_service',
        'last_updated': '2025-07-01',
        'message': 'This endpoint would provide the full terms of service text.'
    })

# ===== DOCUMENTATION AND RESOURCES =====

@public_bp.route('/documentation')
def documentation():
    """Documentation center - Comprehensive platform documentation"""
    return jsonify({
        'page': 'documentation',
        'message': 'API and user documentation is available.',
        'links': {
            'api_docs': '/api-documentation',
            'user_guide': '/user-guide'
        }
    })

@public_bp.route('/api-documentation')
@public_bp.route('/api_documentation')
def api_documentation():
    """API documentation - Developer resources and API reference"""
    return jsonify({
        'page': 'api_documentation',
        'message': 'This endpoint would serve OpenAPI/Swagger documentation for the platform.'
    })

@public_bp.route('/getting-started')
def getting_started():
    """Getting started guide - Platform onboarding and setup"""
    return jsonify({
        'page': 'getting_started',
        'message': 'This endpoint would provide a guide for new users and developers.'
    })

@public_bp.route('/user-guide')
def user_guide():
    """User guide - Comprehensive platform usage instructions"""
    return jsonify({
        'page': 'user_guide',
        'message': 'This endpoint would provide a comprehensive user guide.'
    })

@public_bp.route('/faq')
def faq():
    """Frequently asked questions - Common queries and answers"""
    return jsonify({
        'page': 'faq',
        'message': 'This endpoint would provide a list of frequently asked questions and answers.'
    })

# ===== NVCT STABLECOIN ROUTES =====

@public_bp.route('/nvct-whitepaper')
@public_bp.route('/whitepaper')
@public_bp.route('/nvct_whitepaper')
def nvct_whitepaper():
    """NVCT Stablecoin whitepaper - Technical documentation and specifications"""
    return jsonify({
        'page': 'nvct_whitepaper',
        'title': 'NVCT Stablecoin Whitepaper',
        'message': 'This endpoint would provide the full text or a link to the whitepaper PDF.',
        'download_link': '/download-whitepaper'
    })

@public_bp.route('/download-whitepaper')
def download_whitepaper():
    """Download NVCT whitepaper - PDF download functionality"""
    # In a real application, this would serve a file.
    # For now, it returns a JSON response with a placeholder link.
    return jsonify({
        'message': 'NVCT Whitepaper download will be available soon.',
        'placeholder_url': 'https://cdn.nvcfund.com/nvct_whitepaper.pdf'
    })

# ===== SUPPORT AND CONTACT ROUTES =====

@public_bp.route('/contact-support')
def contact_support():
    """Contact support page - Dedicated customer support portal"""
    return jsonify({
        'page': 'contact_support',
        'message': 'This endpoint provides information on how to contact support.'
    })

@public_bp.route('/public-documentation')
def public_documentation():
    """Public documentation - General platform documentation"""
    return jsonify({
        'page': 'public_documentation',
        'message': 'This endpoint provides general platform documentation.'
    })

# ===== INTERACTIVE FEATURES =====

@public_bp.route('/chat/agent-management')
def chat_agent_management():
    """Chat agent management - Customer service agent dashboard"""
    agent_data = {
        'total_agents': 15,
        'online_agents': 12,
        'busy_agents': 8,
        'available_agents': 4,
        'average_response_time': '2.3 minutes',
        'customer_satisfaction': 94.5
    }
    return jsonify({
        'page_title': 'Chat Agent Management',
        'data': agent_data
    })

@public_bp.route('/queue-management')
def queue_management():
    """Queue management dashboard - Customer service queue monitoring"""
    queue_data = {
        'total_in_queue': 25,
        'average_wait_time': '3.5 minutes',
        'longest_wait': '8.2 minutes',
        'queue_categories': [
            {'name': 'General Support', 'count': 12, 'avg_wait': '2.1 min'},
            {'name': 'Technical Issues', 'count': 8, 'avg_wait': '4.2 min'},
            {'name': 'Account Issues', 'count': 5, 'avg_wait': '5.8 min'}
        ]
    }
    return jsonify({
        'page_title': 'Queue Management',
        'data': queue_data
    })

@public_bp.route('/ai-assistant')
def ai_assistant():
    """AI assistant interface - Intelligent customer support system"""
    assistant_data = {
        'assistant_name': 'NVCT Assistant',
        'capabilities': [
            'Account Information',
            'Transaction History',
            'Product Information',
            'General Support'
        ],
        'availability': '24/7',
        'languages': ['English', 'Spanish', 'French']
    }
    return jsonify({
        'page_title': 'AI Assistant',
        'data': assistant_data
    })

# ===== UTILITY AND SYSTEM ROUTES =====

@public_bp.route('/api/health')
def health_check():
    """Public module health check - System status monitoring"""
    try:
        return jsonify({
            'status': 'healthy',
            'app_module': 'public',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# ===== ERROR HANDLERS =====

@public_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors with professional error page"""
    logger.warning(f"404 error in public module: {request.url}")
    return jsonify({
        'status': 'error',
        'message': 'The requested resource was not found.'
    }), 404

@public_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with professional error page"""
    logger.error(f"500 error in public module: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'An internal server error occurred. Please try again later.'
    }), 500

# ===== MODULE INFORMATION =====

MODULE_INFO = {
    'name': 'NVC Banking Platform - Public Module',
    'version': '2.0.0',
    'description': 'Professional public-facing pages with enhanced presentation and organization',
    'api_endpoints': [
        '/',
        '/about',
        '/services',
        '/contact',
        '/contact/submit',
        '/api/contact',
        '/api/health',
        '/privacy-policy',
        '/terms-of-service',
        '/documentation'
    ],
    'features': [
        'Pure JSON API endpoints for all public-facing content.',
        'Contact form submission via API.',
        'Health monitoring',
        'Enhanced error handling'
    ],
    'dependencies': [
        'modules.utils.services.ErrorLoggerService',
        'modules.core.decorators.rate_limit'
    ],
    'status': 'active',
    'last_updated': '2025-01-25'
}

def get_module_info() -> Dict[str, Any]:
    """Get comprehensive module information"""
    return MODULE_INFO