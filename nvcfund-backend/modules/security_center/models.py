"""
Security Center Models
Database models for security events, incidents, and monitoring
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from modules.core.extensions import db
import uuid
from datetime import datetime

class SecurityEvent(db.Model):
    """Security events and incidents tracking"""
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Event identification
    event_type = Column(String(50), nullable=False)  # authentication, authorization, threat, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    category = Column(String(50))  # intrusion, malware, data_breach, etc.
    
    # Event details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    source = Column(String(100))  # IDS, firewall, application, etc.
    
    # Context information
    source_ip = Column(String(45))  # IPv4 or IPv6
    target_system = Column(String(100))
    user_agent = Column(Text)
    
    # Event data
    event_data = Column(JSONB)  # Additional event-specific data
    indicators = Column(ARRAY(String))  # IOCs, signatures, etc.
    
    # Status and resolution
    status = Column(String(20), default='open')  # open, investigating, resolved, false_positive
    assigned_to = Column(String(100))
    resolution_notes = Column(Text)
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<SecurityEvent {self.event_type}: {self.title}>"

class ThreatIntelligence(db.Model):
    """Threat intelligence data and indicators"""
    __tablename__ = 'threat_intelligence'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Threat identification
    threat_type = Column(String(50), nullable=False)  # malware, phishing, botnet, etc.
    threat_name = Column(String(200))
    threat_family = Column(String(100))
    
    # Indicators
    ioc_type = Column(String(50))  # ip, domain, hash, url, etc.
    ioc_value = Column(String(500), nullable=False)
    confidence_score = Column(Integer)  # 0-100
    
    # Threat details
    severity = Column(String(20))  # low, medium, high, critical
    description = Column(Text)
    tags = Column(ARRAY(String))
    
    # Source information
    source = Column(String(100))  # internal, external feed, etc.
    source_reliability = Column(String(20))  # a, b, c, d (analyst rating)
    
    # Status and lifecycle
    status = Column(String(20), default='active')  # active, expired, false_positive
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ThreatIntelligence {self.threat_type}: {self.ioc_value}>"

class SecurityIncident(db.Model):
    """Security incidents and response tracking"""
    __tablename__ = 'security_incidents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Incident identification
    incident_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Classification
    incident_type = Column(String(50), nullable=False)  # data_breach, malware, dos, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    priority = Column(String(20))  # p1, p2, p3, p4
    
    # Status and workflow
    status = Column(String(20), default='new')  # new, assigned, investigating, resolved, closed
    assigned_to = Column(String(100))
    escalated = Column(Boolean, default=False)
    
    # Impact assessment
    affected_systems = Column(ARRAY(String))
    affected_users = Column(Integer)
    business_impact = Column(String(20))  # none, low, medium, high, critical
    
    # Timeline
    detected_at = Column(DateTime)
    reported_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Response details
    response_actions = Column(JSONB)
    lessons_learned = Column(Text)
    follow_up_actions = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Temporarily removed problematic secondary table relationship
    # security_events = relationship("SecurityEvent", secondary="incident_events", back_populates="incidents")
    
    def __repr__(self):
        return f"<SecurityIncident {self.incident_id}: {self.title}>"