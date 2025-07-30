"""
Live Chat Module Services - Simplified Database Implementation
NVC Banking Platform - Interactive Multi-Agent Chat System
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, or_, desc
from flask import current_app

from modules.core.database import SessionLocal
try:
    from modules.core.logging import BankingLogger
    logger = BankingLogger('chat')
except ImportError:
    # Fallback logging
    import logging
    logger = logging.getLogger('chat')

from .models import Agent, ChatSession, ChatMessage, ChatAnalytics, AgentType, ChatSessionStatus, MessageType


class ChatService:
    """Main chat service for session management and messaging"""
    
    def create_session(self, user_id: int, agent_type: str, initial_question: str = '') -> str:
        """Create new chat session with appropriate agent"""
        session_local = SessionLocal()
        try:
            # Find available agent
            agent = self._find_available_agent(agent_type, user_id, session_local)
            if not agent:
                raise Exception(f"No available agents for type: {agent_type}")
            
            # Create session
            session = ChatSession(
                user_id=user_id,
                agent_id=agent.id,
                initial_question=initial_question,
                topic_category=self._categorize_question(initial_question)
            )
            
            session_local.add(session)
            
            # Update agent session count
            agent.current_sessions += 1
            agent.last_active = datetime.utcnow()
            
            session_local.commit()
            
            # Send welcome message
            self._send_welcome_message(session.session_id, agent, session_local)
            
            logger.info(f"Chat session created: {session.session_id} with agent {agent.name}")
            return session.session_id
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error creating chat session: {e}")
            raise
        finally:
            session_local.close()
    
    def create_public_session(self, agent_type: str, initial_question: str = '', contact_info: Dict = None) -> str:
        """Create new chat session for public (non-authenticated) users"""
        session_local = SessionLocal()
        try:
            # Find available agent
            agent = self._find_available_agent(agent_type, None, session_local)
            if not agent:
                raise Exception(f"No available agents for type: {agent_type}")
            
            # Create session without user_id
            session = ChatSession(
                user_id=None,  # No user_id for public sessions
                agent_id=agent.id,
                initial_question=initial_question,
                topic_category=self._categorize_question(initial_question),
                contact_info=json.dumps(contact_info) if contact_info else None
            )
            
            session_local.add(session)
            
            # Update agent session count
            agent.current_sessions += 1
            agent.last_active = datetime.utcnow()
            
            session_local.commit()
            
            # Send welcome message
            self._send_welcome_message(session.session_id, agent, session_local)
            
            logger.info(f"Public chat session created: {session.session_id} with agent {agent.name}")
            return session.session_id
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error creating public chat session: {e}")
            raise
        finally:
            session_local.close()
    
    def send_message(self, session_id: str, user_id: int, message: str) -> str:
        """Send user message in chat session"""
        session_local = SessionLocal()
        try:
            # Validate session
            session = session_local.query(ChatSession).filter_by(
                session_id=session_id, user_id=user_id, status=ChatSessionStatus.ACTIVE
            ).first()
            
            if not session:
                raise Exception("Invalid or inactive session")
            
            # Create message
            message_obj = ChatMessage(
                session_id=session.id,
                message_type=MessageType.USER,
                sender_id=user_id,
                message_text=message
            )
            
            session_local.add(message_obj)
            
            # Update session
            session.message_count += 1
            session.last_activity = datetime.utcnow()
            
            session_local.commit()
            
            logger.info(f"User message sent in session {session_id}")
            return message_obj.message_id
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error sending message: {e}")
            raise
        finally:
            session_local.close()
    
    def get_agent_response(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Generate agent response to user message"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                return None
            
            agent = session.agent
            
            # Generate response based on agent type and message
            response_text = self._generate_agent_response(agent.agent_type, user_message, session)
            
            # Create agent message
            agent_message = ChatMessage(
                session_id=session.id,
                message_type=MessageType.AGENT,
                sender_id=agent.id,
                message_text=response_text,
                response_time=2.5,  # Simulated response time
                confidence_score=0.85
            )
            
            session_local.add(agent_message)
            session.message_count += 1
            session.last_activity = datetime.utcnow()
            
            session_local.commit()
            
            return {
                'response': response_text,
                'agent_name': agent.name,
                'message_id': agent_message.message_id,
                'confidence': agent_message.confidence_score
            }
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error generating agent response: {e}")
            return None
        finally:
            session_local.close()
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all sessions for user"""
        session_local = SessionLocal()
        try:
            return session_local.query(ChatSession).filter_by(
                user_id=user_id
            ).order_by(desc(ChatSession.started_at)).all()
        finally:
            session_local.close()
    
    def get_session_messages(self, session_id: str, user_id: int) -> List[Dict[str, Any]]:
        """Get messages for specific session"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                return []
            
            return session_local.query(ChatMessage).filter_by(
                session_id=session.id
            ).order_by(ChatMessage.sent_at).all()
        finally:
            session_local.close()
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active chat sessions"""
        session_local = SessionLocal()
        try:
            return session_local.query(ChatSession).filter_by(
                status=ChatSessionStatus.ACTIVE
            ).all()
        finally:
            session_local.close()
    
    def transfer_session(self, session_id: str, new_agent_id: int, reason: str) -> bool:
        """Transfer session to different agent"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                return False
            
            # Record transfer
            old_agent_id = session.agent_id
            session.previous_agent_id = old_agent_id
            session.agent_id = new_agent_id
            session.transfer_reason = reason
            session.transfer_count += 1
            session.status = ChatSessionStatus.TRANSFERRED
            
            # Create transfer message
            transfer_message = ChatMessage(
                session_id=session.id,
                message_type=MessageType.TRANSFER,
                sender_id=new_agent_id,
                message_text=f"Session transferred. Reason: {reason}"
            )
            
            session_local.add(transfer_message)
            session_local.commit()
            
            logger.info(f"Session {session_id} transferred from agent {old_agent_id} to {new_agent_id}")
            return True
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error transferring session: {e}")
            return False
        finally:
            session_local.close()
    
    def end_session(self, session_id: str, satisfaction_rating: int = None, feedback: str = None) -> bool:
        """End chat session"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(session_id=session_id).first()
            if not session:
                return False
            
            # Update session
            session.status = ChatSessionStatus.ENDED
            session.ended_at = datetime.utcnow()
            session.user_satisfaction = satisfaction_rating
            session.session_feedback = feedback
            
            # Decrease agent session count
            agent = session.agent
            if agent.current_sessions > 0:
                agent.current_sessions -= 1
            
            # Update agent statistics
            if satisfaction_rating:
                total_ratings = agent.total_sessions * agent.satisfaction_rating
                agent.total_sessions += 1
                agent.satisfaction_rating = (total_ratings + satisfaction_rating) / agent.total_sessions
            
            session_local.commit()
            
            logger.info(f"Session {session_id} ended")
            return True
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error ending session: {e}")
            return False
        finally:
            session_local.close()
    
    def get_session_count(self) -> int:
        """Get total active session count"""
        session_local = SessionLocal()
        try:
            return session_local.query(ChatSession).filter_by(status=ChatSessionStatus.ACTIVE).count()
        finally:
            session_local.close()
    
    def get_active_session_count(self) -> int:
        """Get total active session count (alias for get_session_count)"""
        return self.get_session_count()
    
    def get_recent_sessions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions for user"""
        session_local = SessionLocal()
        try:
            sessions = session_local.query(ChatSession).filter_by(
                user_id=user_id
            ).order_by(desc(ChatSession.started_at)).limit(limit).all()
            
            return [session.to_dict() for session in sessions]
        finally:
            session_local.close()
    
    def send_public_message(self, session_id: str, message: str, contact_info: Dict = None) -> str:
        """Send message in public chat session"""
        session_local = SessionLocal()
        try:
            # Find session (public sessions have user_id=None)
            session = session_local.query(ChatSession).filter_by(
                session_id=session_id, user_id=None, status=ChatSessionStatus.ACTIVE
            ).first()
            
            if not session:
                raise Exception("Invalid or inactive public session")
            
            # Update contact info if provided
            if contact_info:
                session.contact_info = json.dumps(contact_info)
            
            # Create message
            message_obj = ChatMessage(
                session_id=session.id,
                message_type=MessageType.USER,
                sender_id=None,  # No sender_id for public messages
                message_text=message
            )
            
            session_local.add(message_obj)
            
            # Update session
            session.message_count += 1
            session.last_activity = datetime.utcnow()
            
            session_local.commit()
            
            logger.info(f"Public user message sent in session {session_id}")
            return message_obj.message_id
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error sending public message: {e}")
            raise
        finally:
            session_local.close()
    
    def validate_session_access(self, session_id: str, user_id: int) -> bool:
        """Validate that user has access to session"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(
                session_id=session_id, user_id=user_id
            ).first()
            return session is not None
        finally:
            session_local.close()
    
    def validate_public_session(self, session_id: str) -> bool:
        """Validate public session access"""
        session_local = SessionLocal()
        try:
            session = session_local.query(ChatSession).filter_by(
                session_id=session_id, user_id=None, status=ChatSessionStatus.ACTIVE
            ).first()
            return session is not None
        except Exception as e:
            logger.error(f"Error validating public session: {e}")
            return False
        finally:
            session_local.close()
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        session_local = SessionLocal()
        try:
            agents = session_local.query(Agent).filter(
                Agent.is_available == True
            ).all()
            
            stats = {
                'total_agents': len(agents),
                'available_agents': len([a for a in agents if a.current_sessions < a.max_concurrent_sessions]),
                'agents': []
            }
            
            for agent in agents:
                stats['agents'].append({
                    'id': agent.id,
                    'name': agent.name,
                    'type': agent.agent_type.value,
                    'current_sessions': agent.current_sessions,
                    'max_sessions': agent.max_concurrent_sessions,
                    'rating': agent.satisfaction_rating,
                    'total_sessions': agent.total_sessions
                })
            
            return stats
        finally:
            session_local.close()
    
    def _find_available_agent(self, agent_type: str, user_id: Optional[int], session_local) -> Optional[Agent]:
        """Find available agent of specified type"""
        try:
            # Convert string to enum
            if isinstance(agent_type, str):
                agent_type_enum = AgentType(agent_type)
            else:
                agent_type_enum = agent_type
            
            # Find agent with current sessions less than max
            agent = session_local.query(Agent).filter(
                Agent.agent_type == agent_type_enum,
                Agent.is_available == True,
                Agent.current_sessions < Agent.max_concurrent_sessions
            ).first()
            
            # If no agent found, create a default one
            if not agent:
                agent = self._create_default_agent(agent_type_enum, session_local)
            
            return agent
        except Exception as e:
            logger.error(f"Error finding agent: {e}")
            return None
    
    def _create_default_agent(self, agent_type: AgentType, session_local) -> Agent:
        """Create a default agent for the specified type"""
        try:
            agent_configs = {
                AgentType.GENERAL_BANKING: {
                    'name': 'Sarah Johnson',
                    'description': 'General banking specialist with expertise in account management and basic banking services'
                },
                AgentType.TREASURY: {
                    'name': 'Michael Chen',
                    'description': 'Treasury operations specialist focused on liquidity management and risk assessment'
                },
                AgentType.COMPLIANCE: {
                    'name': 'Lisa Rodriguez',
                    'description': 'Compliance officer specialized in regulatory matters and risk management'
                },
                AgentType.TECHNICAL_SUPPORT: {
                    'name': 'David Kim',
                    'description': 'Technical support specialist for platform and system assistance'
                },
                AgentType.ACCOUNT_SERVICES: {
                    'name': 'Emily Watson',
                    'description': 'Account services specialist for account management and customer support'
                },
                AgentType.LOANS_CREDIT: {
                    'name': 'Robert Thompson',
                    'description': 'Credit and lending specialist for loan products and financing solutions'
                },
                AgentType.INVESTMENTS: {
                    'name': 'Jennifer Lee',
                    'description': 'Investment advisor specialized in portfolio management and market analysis'
                },
                AgentType.INTERNATIONAL: {
                    'name': 'Carlos Martinez',
                    'description': 'International banking specialist for global transactions and foreign exchange'
                },
                AgentType.ISLAMIC_BANKING: {
                    'name': 'Fatima Al-Zahra',
                    'description': 'Islamic banking specialist for Sharia-compliant financial products'
                },
                AgentType.BUSINESS_BANKING: {
                    'name': 'James Wilson',
                    'description': 'Business banking specialist for commercial and corporate banking services'
                },
                AgentType.SOVEREIGN_BANKING: {
                    'name': 'Maria Gonzalez',
                    'description': 'Sovereign banking specialist for government and central banking operations'
                },
                AgentType.NVCT_STABLECOIN: {
                    'name': 'Alex Turner',
                    'description': 'NVCT stablecoin specialist for digital asset management and blockchain operations'
                }
            }
            
            config = agent_configs.get(agent_type, agent_configs[AgentType.GENERAL_BANKING])
            
            agent = Agent(
                name=config['name'],
                agent_type=agent_type,
                description=config['description'],
                is_available=True,
                max_concurrent_sessions=10,
                current_sessions=0,
                response_time_avg=2.5,
                satisfaction_rating=4.5,
                total_sessions=0
            )
            
            session_local.add(agent)
            session_local.commit()
            
            logger.info(f"Created default agent: {agent.name} for type {agent_type.value}")
            return agent
            
        except Exception as e:
            logger.error(f"Error creating default agent: {e}")
            raise
    
    def _send_welcome_message(self, session_id: str, agent: Agent, session_local):
        """Send welcome message from agent"""
        try:
            session = session_local.query(ChatSession).filter_by(session_id=session_id).first()
            if session:
                welcome_message = ChatMessage(
                    session_id=session.id,
                    message_type=MessageType.AGENT,
                    sender_id=agent.id,
                    message_text=f"Hello! I'm {agent.name}, your {agent.agent_type.value} specialist. How can I help you today?"
                )
                session_local.add(welcome_message)
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
    
    def _categorize_question(self, question: str) -> str:
        """Categorize user question for routing"""
        if not question:
            return 'general'
        
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['account', 'balance', 'deposit', 'withdraw']):
            return 'account_services'
        elif any(word in question_lower for word in ['transfer', 'payment', 'send', 'receive']):
            return 'transfers'
        elif any(word in question_lower for word in ['loan', 'credit', 'mortgage', 'borrow']):
            return 'loans_credit'
        elif any(word in question_lower for word in ['investment', 'portfolio', 'stocks', 'bonds']):
            return 'investments'
        elif any(word in question_lower for word in ['card', 'debit', 'credit card', 'atm']):
            return 'cards'
        elif any(word in question_lower for word in ['compliance', 'regulation', 'kyc', 'aml']):
            return 'compliance'
        elif any(word in question_lower for word in ['treasury', 'liquidity', 'risk']):
            return 'treasury'
        else:
            return 'general_banking'
    
    def _generate_agent_response(self, agent_type: AgentType, message: str, session: ChatSession) -> str:
        """Generate agent response based on type and message"""
        responses = {
            AgentType.GENERAL_BANKING: self._general_banking_response,
            AgentType.TREASURY: self._treasury_response,
            AgentType.COMPLIANCE: self._compliance_response,
            AgentType.TECHNICAL_SUPPORT: self._technical_response,
            AgentType.ACCOUNT_SERVICES: self._account_services_response,
            AgentType.LOANS_CREDIT: self._loans_credit_response,
            AgentType.INVESTMENTS: self._investments_response,
            AgentType.INTERNATIONAL: self._international_response,
            AgentType.ISLAMIC_BANKING: self._islamic_banking_response,
            AgentType.BUSINESS_BANKING: self._business_banking_response,
            AgentType.SOVEREIGN_BANKING: self._sovereign_banking_response,
            AgentType.NVCT_STABLECOIN: self._nvct_stablecoin_response
        }
        
        response_func = responses.get(agent_type, self._general_banking_response)
        return response_func(message, session)
    
    def _general_banking_response(self, message: str, session: ChatSession) -> str:
        """Generate general banking response"""
        return f"Thank you for your inquiry about general banking services. I'm here to help with your banking needs. Could you please provide more details about what you'd like to know?"
    
    def _treasury_response(self, message: str, session: ChatSession) -> str:
        """Generate treasury response"""
        return f"I can assist with treasury operations, liquidity management, and risk assessment. What specific treasury matter can I help you with today?"
    
    def _compliance_response(self, message: str, session: ChatSession) -> str:
        """Generate compliance response"""
        return f"I'm here to help with compliance, regulatory matters, and risk management. Please let me know what compliance topic you'd like assistance with."
    
    def _technical_response(self, message: str, session: ChatSession) -> str:
        """Generate technical support response"""
        return f"I can help with technical issues, system problems, and platform navigation. What technical challenge are you experiencing?"
    
    def _account_services_response(self, message: str, session: ChatSession) -> str:
        """Generate account services response"""
        return f"I'm here to assist with account management, balance inquiries, and account-related services. How can I help with your account today?"
    
    def _loans_credit_response(self, message: str, session: ChatSession) -> str:
        """Generate loans and credit response"""
        return f"I can help with loan applications, credit services, and financing options. What type of credit or loan information do you need?"
    
    def _investments_response(self, message: str, session: ChatSession) -> str:
        """Generate investments response"""
        return f"I'm here to assist with investment services, portfolio management, and market insights. What investment topic interests you?"
    
    def _international_response(self, message: str, session: ChatSession) -> str:
        """Generate international banking response"""
        return f"I can help with international transfers, foreign exchange, and global banking services. What international banking service do you need?"
    
    def _islamic_banking_response(self, message: str, session: ChatSession) -> str:
        """Generate Islamic banking response"""
        return f"I'm here to assist with Sharia-compliant banking products and Islamic finance solutions. How can I help with your Islamic banking needs?"
    
    def _business_banking_response(self, message: str, session: ChatSession) -> str:
        """Generate business banking response"""
        return f"I can assist with business accounts, commercial lending, and corporate banking services. What business banking service interests you?"
    
    def _sovereign_banking_response(self, message: str, session: ChatSession) -> str:
        """Generate sovereign banking response"""
        return f"I'm here to help with sovereign debt, central banking operations, and government financial services. What sovereign banking matter can I assist with?"
    
    def _nvct_stablecoin_response(self, message: str, session: ChatSession) -> str:
        """Generate NVCT stablecoin response"""
        return f"I can help with NVCT stablecoin operations, blockchain transactions, and digital asset management. What NVCT-related question do you have?"


class AgentService:
    """Service for managing chat agents"""
    
    def get_available_agents(self, user_role: str = 'standard') -> List[Dict[str, Any]]:
        """Get agents available to user based on role"""
        session_local = SessionLocal()
        try:
            agents = session_local.query(Agent).filter(
                Agent.is_available == True
            ).all()
            
            # Convert agents to dictionary format for easy template use
            agent_list = []
            for agent in agents:
                agent_dict = {
                    'id': agent.id,
                    'name': agent.name,
                    'agent_type': agent.agent_type.value if hasattr(agent.agent_type, 'value') else str(agent.agent_type),
                    'description': agent.description,
                    'specializations': agent.specializations,
                    'current_sessions': agent.current_sessions,
                    'max_sessions': agent.max_concurrent_sessions,
                    'available': agent.current_sessions < agent.max_concurrent_sessions
                }
                agent_list.append(agent_dict)
            
            return agent_list
        finally:
            session_local.close()
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents"""
        session_local = SessionLocal()
        try:
            return session_local.query(Agent).all()
        finally:
            session_local.close()
    
    def initialize_default_agents(self):
        """Initialize default chat agents if none exist"""
        session_local = SessionLocal()
        try:
            if session_local.query(Agent).count() > 0:
                return
            
            default_agents = [
                {
                    'name': 'Sarah Johnson',
                    'agent_type': AgentType.GENERAL_BANKING,
                    'description': 'General banking specialist for everyday banking needs',
                    'specializations': '["account management", "basic transactions", "general inquiries"]',
                    'min_user_role': 'standard'
                },
                {
                    'name': 'Michael Chen',
                    'agent_type': AgentType.TREASURY,
                    'description': 'Treasury operations specialist for institutional clients',
                    'specializations': '["liquidity management", "risk assessment", "treasury operations"]',
                    'min_user_role': 'treasury'
                },
                {
                    'name': 'Emma Rodriguez',
                    'agent_type': AgentType.COMPLIANCE,
                    'description': 'Compliance and regulatory specialist',
                    'specializations': '["AML compliance", "KYC verification", "regulatory reporting"]',
                    'min_user_role': 'compliance'
                },
                {
                    'name': 'David Kim',
                    'agent_type': AgentType.TECHNICAL_SUPPORT,
                    'description': 'Technical support specialist for platform issues',
                    'specializations': '["platform navigation", "technical troubleshooting", "system support"]',
                    'min_user_role': 'standard'
                },
                {
                    'name': 'Lisa Thompson',
                    'agent_type': AgentType.ACCOUNT_SERVICES,
                    'description': 'Account services specialist for account management',
                    'specializations': '["account opening", "account maintenance", "balance inquiries"]',
                    'min_user_role': 'standard'
                },
                {
                    'name': 'James Wilson',
                    'agent_type': AgentType.LOANS_CREDIT,
                    'description': 'Loans and credit specialist',
                    'specializations': '["loan applications", "credit assessment", "financing options"]',
                    'min_user_role': 'standard'
                },
                {
                    'name': 'Maria Garcia',
                    'agent_type': AgentType.INVESTMENTS,
                    'description': 'Investment services specialist',
                    'specializations': '["portfolio management", "investment advice", "market analysis"]',
                    'min_user_role': 'business'
                },
                {
                    'name': 'Ahmed Hassan',
                    'agent_type': AgentType.ISLAMIC_BANKING,
                    'description': 'Islamic banking specialist for Sharia-compliant services',
                    'specializations': '["Sharia compliance", "Islamic finance", "halal investments"]',
                    'min_user_role': 'standard'
                },
                {
                    'name': 'Robert Davis',
                    'agent_type': AgentType.BUSINESS_BANKING,
                    'description': 'Business banking specialist for commercial clients',
                    'specializations': '["commercial lending", "business accounts", "corporate services"]',
                    'min_user_role': 'business'
                },
                {
                    'name': 'Alexandra Putin',
                    'agent_type': AgentType.SOVEREIGN_BANKING,
                    'description': 'Sovereign banking specialist for government entities',
                    'specializations': '["sovereign debt", "central banking", "government services"]',
                    'min_user_role': 'sovereign'
                },
                {
                    'name': 'Dr. Crypto Zhang',
                    'agent_type': AgentType.NVCT_STABLECOIN,
                    'description': 'NVCT stablecoin specialist for digital asset operations',
                    'specializations': '["NVCT operations", "blockchain transactions", "digital assets"]',
                    'min_user_role': 'treasury'
                }
            ]
            
            for agent_data in default_agents:
                agent = Agent(**agent_data)
                session_local.add(agent)
            
            session_local.commit()
            logger.info("Default chat agents initialized")
            
        except Exception as e:
            session_local.rollback()
            logger.error(f"Error initializing agents: {e}")
        finally:
            session_local.close()