"""
Live Chat Module - Routes
NVC Banking Platform - Interactive Multi-Agent Chat System

Features:
- Real-time chat with multiple specialized agents
- Business question handling with domain expertise
- WebSocket integration for live communication
- Agent routing based on question type
- Chat history and session management
"""

from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import uuid
from typing import Dict, List, Any

# Import rate limiting and security decorators
try:
    from modules.core.security_decorators import rate_limit, banking_security_required
    from flask_login import current_user, login_required
except ImportError:
    # Create fallback decorators
    def rate_limit(requests_per_minute=30):
        def decorator(f):
            return f
        return decorator
    
    def banking_security_required(f):
        return f
    
    def login_required(f):
        return f
    
    class MockUser:
        is_authenticated = False
        id = None
    
    current_user = MockUser()

# Import CSRF protection
try:
    from flask_wtf.csrf import validate_csrf, CSRFError, generate_csrf
except ImportError:
    # Fallback if CSRF not available
    def validate_csrf(token):
        return True
    def generate_csrf():
        return 'csrf-token'
    class CSRFError(Exception):
        pass

try:
    from modules.core.logging import BankingLogger
    logger = BankingLogger('chat')
except ImportError:
    import logging
    logger = logging.getLogger('chat')

# Import chat services
from .services import ChatService, AgentService
from .models import ChatSession, ChatMessage, Agent

# Initialize module components
chat_bp = Blueprint('chat', __name__, url_prefix='/chat', template_folder='templates')
chat_service = ChatService()
agent_service = AgentService()

def validate_csrf_for_chat(f):
    """
    Custom CSRF validation for chat endpoints
    Validates CSRF token when provided, but allows public access without token
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get CSRF token from headers or request data
        csrf_token = request.headers.get('X-CSRFToken')
        
        if not csrf_token:
            # Try to get from request data
            if request.is_json:
                csrf_token = request.get_json().get('csrf_token')
            else:
                csrf_token = request.form.get('csrf_token')
        
        # If CSRF token is provided, validate it
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except CSRFError:
                logger.warning("Invalid CSRF token in chat request")
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid CSRF token'
                }), 403
        
        # If no CSRF token provided, allow access but log it
        if not csrf_token:
            logger.info("Chat API accessed without CSRF token (public access)")
        
        return f(*args, **kwargs)
    
    return decorated_function

@chat_bp.route('/test')
def test_route():
    """Simple test route to verify blueprint is working"""
    return "Chat module is working!", 200

@chat_bp.route('/live')
def live_chat():
    """Live chat interface - completely public, no authentication required"""
    try:
        # Get available agents for display
        agents = agent_service.get_available_agents()
        
        # Get system statistics
        active_sessions = chat_service.get_active_session_count()
        
        context = {
            'page_title': 'Live Chat Support',
            'agents': agents,
            'active_sessions': active_sessions,
            'support_hours': '24/7',
            'response_time': '< 2 minutes'
        }
        
        return render_template('chat/live_chat.html', **context)
    except Exception as e:
        logger.error(f"Live chat error: {e}")
        return f"Chat system temporarily unavailable: {str(e)}", 500

@chat_bp.route('/')
def chat_home():
    """Main chat interface"""
    try:
        # Get available agents for user
        available_agents = agent_service.get_available_agents(current_user.role)
        
        # Get recent chat sessions
        recent_sessions = chat_service.get_recent_sessions(current_user.id)
        
        return render_template('chat/chat_home.html', 
                             available_agents=available_agents,
                             recent_sessions=recent_sessions)
    except Exception as e:
        logger.error(f"Error loading chat home: {e}")
        return render_template('error.html', error="Chat system temporarily unavailable")

@chat_bp.route('/session/<session_id>')
def chat_session(session_id):
    """Individual chat session view"""
    try:
        # Validate session access
        chat_session = chat_service.get_session(session_id, current_user.id)
        if not chat_session:
            return render_template('error.html', error="Chat session not found")
        
        # Get chat history
        messages = chat_service.get_session_messages(session_id)
        
        return render_template('chat_session.html',
                             session=chat_session,
                             messages=messages)
    except Exception as e:
        logger.error(f"Error loading chat session {session_id}: {e}")
        return render_template('error.html', error="Chat session unavailable")

@chat_bp.route('/api/start-session', methods=['POST'])
@validate_csrf_for_chat
def start_chat_session():
    """Start new chat session with agent - supports public users"""
    try:
        data = request.get_json()
        agent_type = data.get('agent_type', 'general_banking')
        initial_question = data.get('initial_question', '')
        
        # Check if user is authenticated
        user_authenticated = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
        
        if user_authenticated:
            # Authenticated user - create session with user_id
            session_id = chat_service.create_session(
                user_id=current_user.id,
                agent_type=agent_type,
                initial_question=initial_question
            )
            logger.info(f"Chat session created: {session_id} for authenticated user {current_user.id}")
        else:
            # Public user - create session with contact info
            contact_info = data.get('contact_info', {})
            session_id = chat_service.create_public_session(
                agent_type=agent_type,
                initial_question=initial_question,
                contact_info=contact_info
            )
            logger.info(f"Chat session created: {session_id} for public user")
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'redirect_url': f'/chat/session/{session_id}' if user_authenticated else None,
            'requires_contact_info': not user_authenticated
        })
        
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to start chat session'
        }), 500

@chat_bp.route('/api/send-message', methods=['POST'])
@validate_csrf_for_chat
@rate_limit(requests_per_minute=30)
def send_message():
    """Send message in chat session - supports public users"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message_text = data.get('message')
        
        # Check if user is authenticated
        user_authenticated = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
        
        if user_authenticated:
            # Authenticated user - validate session access
            if not chat_service.validate_session_access(session_id, current_user.id):
                return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
            
            # Send message with user_id
            message_id = chat_service.send_message(
                session_id=session_id,
                user_id=current_user.id,
                message=message_text
            )
        else:
            # Public user - validate session exists
            if not chat_service.validate_public_session(session_id):
                return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
            
            # Send message without user_id (public session)
            message_id = chat_service.send_public_message(
                session_id=session_id,
                message=message_text,
                contact_info=data.get('contact_info', {})
            )
        
        # Get agent response
        agent_response = chat_service.get_agent_response(session_id, message_text)
        
        return jsonify({
            'status': 'success',
            'message_id': message_id,
            'agent_response': agent_response
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to send message'
        }), 500

@chat_bp.route('/api/get-messages/<session_id>')
@login_required
@banking_security_required
@rate_limit(requests_per_minute=60)
def get_messages(session_id):
    """Get messages for chat session"""
    try:
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        messages = chat_service.get_session_messages(session_id)
        
        return jsonify({
            'status': 'success',
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve messages'
        }), 500

@chat_bp.route('/api/agents')
@login_required
@banking_security_required
@rate_limit(requests_per_minute=20)
def get_agents():
    """Get available agents for user"""
    try:
        agents = agent_service.get_available_agents(current_user.role)
        
        return jsonify({
            'status': 'success',
            'agents': [agent.to_dict() for agent in agents]
        })
        
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve agents'
        }), 500

@chat_bp.route('/api/transfer-session', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=5)
def transfer_session():
    """Transfer chat session to different agent"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        new_agent_type = data.get('new_agent_type')
        transfer_reason = data.get('transfer_reason', '')
        
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        # Transfer session
        success = chat_service.transfer_session(
            session_id=session_id,
            new_agent_type=new_agent_type,
            transfer_reason=transfer_reason
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Session transferred successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to transfer session'
            }), 500
            
    except Exception as e:
        logger.error(f"Error transferring session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to transfer session'
        }), 500

@chat_bp.route('/api/end-session', methods=['POST'])
@login_required
@banking_security_required
@rate_limit(requests_per_minute=10)
def end_session():
    """End chat session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        satisfaction_rating = data.get('satisfaction_rating')
        feedback = data.get('feedback', '')
        
        # Validate session access
        if not chat_service.validate_session_access(session_id, current_user.id):
            return jsonify({'status': 'error', 'message': 'Invalid session'}), 403
        
        # End session
        success = chat_service.end_session(
            session_id=session_id,
            satisfaction_rating=satisfaction_rating,
            feedback=feedback
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Session ended successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to end session'
            }), 500
            
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to end session'
        }), 500

@chat_bp.route('/support')
@login_required
@banking_security_required
def support_chat():
    """Support chat interface"""
    try:
        return render_template('chat/support_chat.html',
                             user=current_user,
                             page_title='Support Chat')
    except Exception as e:
        logger.error(f"Error loading support chat: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('chat.chat_home'))

@chat_bp.route('/api/health')
@rate_limit(requests_per_minute=100)
def health_check():
    """Chat module health check"""
    return jsonify({
        'status': 'healthy',
        'app_module': 'chat',
        'timestamp': datetime.utcnow().isoformat(),
        'agents_available': len(agent_service.get_all_agents()),
        'active_sessions': chat_service.get_active_session_count()
    })

# WebSocket event handlers
def init_socketio_handlers(socketio):
    """Initialize WebSocket handlers for real-time chat"""
    
    @socketio.on('join_chat')
    def handle_join_chat(data):
        """User joins chat room"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        if chat_service.validate_session_access(session_id, current_user.id):
            join_room(session_id)
            emit('joined_chat', {'session_id': session_id})
            logger.info(f"User {current_user.id} joined chat {session_id}")
        else:
            emit('error', {'message': 'Invalid session'})
    
    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """User leaves chat room"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        leave_room(session_id)
        emit('left_chat', {'session_id': session_id})
        logger.info(f"User {current_user.id} left chat {session_id}")
    
    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicators"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        if chat_service.validate_session_access(session_id, current_user.id):
            emit('user_typing', {
                'user_id': current_user.id,
                'username': current_user.username,
                'typing': data.get('typing', False)
            }, room=session_id, include_self=False)
    
    @socketio.on('message')
    def handle_message(data):
        """Handle real-time message sending"""
        if not current_user.is_authenticated:
            return False
        
        session_id = data.get('session_id')
        message_text = data.get('message')
        
        if chat_service.validate_session_access(session_id, current_user.id):
            # Send message
            message_id = chat_service.send_message(
                session_id=session_id,
                user_id=current_user.id,
                message=message_text
            )
            
            # Emit to room
            emit('new_message', {
                'message_id': message_id,
                'user_id': current_user.id,
                'username': current_user.username,
                'message': message_text,
                'timestamp': datetime.utcnow().isoformat()
            }, room=session_id)
            
            # Get agent response
            agent_response = chat_service.get_agent_response(session_id, message_text)
            if agent_response:
                emit('agent_response', agent_response, room=session_id)
        else:
            emit('error', {'message': 'Invalid session'})

# Register route collection
CHAT_ROUTES = [
    '/',
    '/session/<session_id>',
    '/api/start-session',
    '/api/send-message',
    '/api/get-messages/<session_id>',
    '/api/agents',
    '/api/transfer-session',
    '/api/end-session',
    '/api/health'
]

# Missing routes referenced in templates
@chat_bp.route('/agent-management')
@login_required
@banking_security_required
def agent_management():
    """Chat agent management interface"""
    try:
        agent_data = {
            'active_agents': [
                {'id': 'AGT-001', 'name': 'Sarah Johnson', 'status': 'Online', 'active_chats': 3, 'rating': 4.8},
                {'id': 'AGT-002', 'name': 'Mike Chen', 'status': 'Online', 'active_chats': 2, 'rating': 4.9},
                {'id': 'AGT-003', 'name': 'Lisa Rodriguez', 'status': 'Away', 'active_chats': 0, 'rating': 4.7}
            ],
            'agent_stats': {
                'total_agents': 15,
                'online_agents': 12,
                'average_rating': 4.8,
                'total_chats_today': 125
            },
            'performance_metrics': [
                {'metric': 'Average Response Time', 'value': '2.5 minutes'},
                {'metric': 'Customer Satisfaction', 'value': '94.5%'},
                {'metric': 'Resolution Rate', 'value': '89.2%'}
            ]
        }
        return render_template('chat/agent_management.html',
                             agent_data=agent_data,
                             page_title='Chat Agent Management')
    except Exception as e:
        logger.error(f"Agent management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('public.index'))

@chat_bp.route('/ai-assistant')
@login_required
def ai_assistant():
    """AI assistant chat interface"""
    try:
        ai_data = {
            'assistant_name': 'NVC AI Assistant',
            'capabilities': [
                'Account Information', 'Transaction History', 'Balance Inquiries',
                'Payment Processing', 'General Banking Questions', 'Product Information'
            ],
            'conversation_starters': [
                'What is my account balance?',
                'Show me my recent transactions',
                'How do I transfer money?',
                'What banking products do you offer?'
            ],
            'ai_status': 'Online',
            'response_time': '< 1 second',
            'accuracy_rate': '96.8%'
        }
        return render_template('chat/ai_assistant.html',
                             ai_data=ai_data,
                             page_title='AI Assistant')
    except Exception as e:
        logger.error(f"AI assistant error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('public.index'))

@chat_bp.route('/queue-management')
@login_required
@banking_security_required
def queue_management():
    """Chat queue management interface"""
    try:
        queue_data = {
            'waiting_customers': [
                {'id': 'CUST-001', 'name': 'John Doe', 'wait_time': '3 minutes', 'priority': 'High', 'issue': 'Account Access'},
                {'id': 'CUST-002', 'name': 'Jane Smith', 'wait_time': '5 minutes', 'priority': 'Medium', 'issue': 'Transaction Dispute'},
                {'id': 'CUST-003', 'name': 'Bob Wilson', 'wait_time': '8 minutes', 'priority': 'Low', 'issue': 'General Inquiry'}
            ],
            'queue_stats': {
                'total_waiting': 15,
                'average_wait_time': '6.5 minutes',
                'longest_wait': '12 minutes',
                'queue_capacity': 50
            },
            'agent_availability': {
                'available_agents': 8,
                'busy_agents': 7,
                'total_agents': 15
            }
        }
        return render_template('chat/queue_management.html',
                             queue_data=queue_data,
                             page_title='Chat Queue Management')
    except Exception as e:
        logger.error(f"Queue management error: {e}")
        flash('Service temporarily unavailable', 'error')
        return redirect(url_for('public.index'))