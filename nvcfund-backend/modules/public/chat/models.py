"""
Live Chat Module - Database Models
NVC Banking Platform - Interactive Multi-Agent Chat System
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship, foreign
from datetime import datetime
import enum
import uuid

from modules.core.database import Base


class AgentType(enum.Enum):
    """Types of specialized chat agents"""
    GENERAL_BANKING = "general_banking"
    TREASURY = "treasury"
    COMPLIANCE = "compliance"
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_SERVICES = "account_services"
    LOANS_CREDIT = "loans_credit"
    INVESTMENTS = "investments"
    INTERNATIONAL = "international"
    ISLAMIC_BANKING = "islamic_banking"
    BUSINESS_BANKING = "business_banking"
    SOVEREIGN_BANKING = "sovereign_banking"
    NVCT_STABLECOIN = "nvct_stablecoin"


class ChatSessionStatus(enum.Enum):
    """Chat session status"""
    ACTIVE = "active"
    WAITING = "waiting"
    TRANSFERRED = "transferred"
    ENDED = "ended"
    ABANDONED = "abandoned"


class MessageType(enum.Enum):
    """Types of chat messages"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TRANSFER = "transfer"


class Agent(Base):
    """Chat agent model with specializations and availability"""
    __tablename__ = 'chat_agents'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:8])
    name = Column(String(100), nullable=False)
    agent_type = Column(Enum(AgentType), nullable=False)
    specializations = Column(Text)  # JSON list of specialization topics
    description = Column(Text)
    is_available = Column(Boolean, default=True)
    max_concurrent_sessions = Column(Integer, default=5)
    current_sessions = Column(Integer, default=0)
    response_time_avg = Column(Float, default=0.0)  # Average response time in seconds
    satisfaction_rating = Column(Float, default=0.0)  # Average satisfaction rating
    total_sessions = Column(Integer, default=0)
    
    # Access control
    min_user_role = Column(String(50), default='standard')  # Minimum user role required
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="agent", foreign_keys="[ChatSession.agent_id]")
    
    def to_dict(self):
        """Convert agent to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'name': self.name,
            'agent_type': self.agent_type.value,
            'specializations': self.specializations,
            'description': self.description,
            'is_available': self.is_available,
            'current_sessions': self.current_sessions,
            'max_concurrent_sessions': self.max_concurrent_sessions,
            'response_time_avg': self.response_time_avg,
            'satisfaction_rating': self.satisfaction_rating,
            'total_sessions': self.total_sessions
        }


class ChatSession(Base):
    """Chat session between user and agent"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=True)  # Allow null for public users
    agent_id = Column(Integer, ForeignKey('chat_agents.id'), nullable=False)
    
    # Session details
    status = Column(Enum(ChatSessionStatus), default=ChatSessionStatus.ACTIVE)
    initial_question = Column(Text)
    topic_category = Column(String(100))
    priority_level = Column(String(20), default='normal')  # low, normal, high, urgent
    contact_info = Column(Text)  # JSON string with contact information for public users
    
    # Transfer information
    previous_agent_id = Column(Integer, ForeignKey('chat_agents.id'))
    transfer_reason = Column(Text)
    transfer_count = Column(Integer, default=0)
    
    # Session metrics
    message_count = Column(Integer, default=0)
    user_satisfaction = Column(Integer)  # 1-5 rating
    session_feedback = Column(Text)
    resolution_status = Column(String(50), default='pending')  # pending, resolved, escalated
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="sessions", foreign_keys=[agent_id])
    previous_agent = relationship("Agent", foreign_keys=[previous_agent_id])
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'status': self.status.value,
            'initial_question': self.initial_question,
            'topic_category': self.topic_category,
            'priority_level': self.priority_level,
            'transfer_count': self.transfer_count,
            'message_count': self.message_count,
            'user_satisfaction': self.user_satisfaction,
            'resolution_status': self.resolution_status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String(50), unique=True, nullable=False, default=lambda: str(uuid.uuid4())[:12])
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    
    # Message details
    message_type = Column(Enum(MessageType), nullable=False)
    sender_id = Column(Integer)  # user_id for user messages, agent_id for agent messages
    message_text = Column(Text, nullable=False)
    
    # Message metadata
    is_edited = Column(Boolean, default=False)
    edit_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    
    # Agent response metadata
    response_time = Column(Float)  # Time taken to respond (for agent messages)
    confidence_score = Column(Float)  # AI confidence in response (0-1)
    requires_followup = Column(Boolean, default=False)
    
    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime)
    read_at = Column(DateTime)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'session_id': self.session_id,
            'message_type': self.message_type.value,
            'sender_id': self.sender_id,
            'message_text': self.message_text,
            'is_edited': self.is_edited,
            'edit_count': self.edit_count,
            'response_time': self.response_time,
            'confidence_score': self.confidence_score,
            'requires_followup': self.requires_followup,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }


class ChatAnalytics(Base):
    """Chat system analytics and metrics"""
    __tablename__ = 'chat_analytics'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Daily metrics
    total_sessions = Column(Integer, default=0)
    active_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    abandoned_sessions = Column(Integer, default=0)
    
    # Agent metrics
    total_agents = Column(Integer, default=0)
    active_agents = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    
    # User satisfaction
    avg_satisfaction = Column(Float, default=0.0)
    satisfaction_responses = Column(Integer, default=0)
    
    # Popular topics
    top_categories = Column(Text)  # JSON list of popular categories
    common_questions = Column(Text)  # JSON list of common questions
    
    def to_dict(self):
        """Convert analytics to dictionary"""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'total_sessions': self.total_sessions,
            'active_sessions': self.active_sessions,
            'completed_sessions': self.completed_sessions,
            'abandoned_sessions': self.abandoned_sessions,
            'total_agents': self.total_agents,
            'active_agents': self.active_agents,
            'avg_response_time': self.avg_response_time,
            'avg_session_duration': self.avg_session_duration,
            'avg_satisfaction': self.avg_satisfaction,
            'satisfaction_responses': self.satisfaction_responses
        }