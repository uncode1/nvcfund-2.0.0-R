"""
Communications Models
NVC Banking Platform - Communication and Messaging Database Models

This module defines the database models for communication functionality:
- Communication logs for audit trails
- Email template management
- Scheduled communication tracking
- User communication preferences
"""

from modules.core.extensions import db
from datetime import datetime
from sqlalchemy import Index, UUID
import uuid


class CommunicationLog(db.Model):
    """
    Log of all communications sent to users
    Essential for compliance and audit requirements
    """
    __tablename__ = 'communication_logs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Recipient Information
    recipient_email = db.Column(db.String(255), nullable=False)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Message Details
    subject = db.Column(db.Text, nullable=False)
    template_name = db.Column(db.String(100), nullable=False)
    message_type = db.Column(db.String(50), nullable=False, default='email')  # 'email', 'sms', 'push'
    
    # Delivery Information
    status = db.Column(db.String(20), nullable=False)  # 'sent', 'failed', 'pending', 'delivered', 'bounced'
    provider = db.Column(db.String(50), nullable=False, default='sendgrid')
    provider_message_id = db.Column(db.String(255), nullable=True)
    
    # Context and Metadata
    context_data = db.Column(db.JSON, nullable=True)  # Template variables used
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    recipient_user = db.relationship('User', backref='communication_logs', lazy=True)
    
    def __repr__(self):
        return f'<CommunicationLog {self.id}: {self.subject} to {self.recipient_email}>'
    
    @staticmethod
    def log_communication(recipient_email, subject, template_name, status, 
                         recipient_user_id=None, context_data=None, 
                         provider='sendgrid', error_message=None):
        """Create a new communication log entry"""
        log_entry = CommunicationLog(
            recipient_email=recipient_email,
            recipient_user_id=recipient_user_id,
            subject=subject,
            template_name=template_name,
            status=status,
            provider=provider,
            context_data=context_data,
            error_message=error_message
        )
        db.session.add(log_entry)
        try:
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            import logging
            logging.error(f"Failed to create communication log: {str(e)}")
            return None


class EmailTemplate(db.Model):
    """
    Email template management for consistent messaging
    """
    __tablename__ = 'email_templates'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template Information
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # 'transactional', 'marketing', 'system'
    
    # Template Content
    subject_template = db.Column(db.Text, nullable=False)
    html_content = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text, nullable=True)
    
    # Configuration
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    requires_approval = db.Column(db.Boolean, default=False, nullable=False)
    
    # Variables and Validation
    required_variables = db.Column(db.JSON, nullable=True)  # List of required template variables
    optional_variables = db.Column(db.JSON, nullable=True)  # List of optional template variables
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    
    # Usage Statistics
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    success_rate = db.Column(db.Float, default=0.0, nullable=False)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}: {self.display_name}>'
    
    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()


class CommunicationPreference(db.Model):
    """
    User preferences for different types of communications
    """
    __tablename__ = 'communication_preferences'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Email Preferences
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)
    marketing_emails = db.Column(db.Boolean, default=True, nullable=False)
    transaction_alerts = db.Column(db.Boolean, default=True, nullable=False)
    security_alerts = db.Column(db.Boolean, default=True, nullable=False)
    account_statements = db.Column(db.Boolean, default=True, nullable=False)
    birthday_messages = db.Column(db.Boolean, default=True, nullable=False)
    holiday_messages = db.Column(db.Boolean, default=True, nullable=False)
    
    # SMS Preferences (if implemented)
    sms_enabled = db.Column(db.Boolean, default=False, nullable=False)
    sms_transaction_alerts = db.Column(db.Boolean, default=False, nullable=False)
    sms_security_alerts = db.Column(db.Boolean, default=False, nullable=False)
    sms_marketing = db.Column(db.Boolean, default=False, nullable=False)
    
    # Push Notification Preferences (if implemented)
    push_enabled = db.Column(db.Boolean, default=False, nullable=False)
    push_transaction_alerts = db.Column(db.Boolean, default=False, nullable=False)
    push_security_alerts = db.Column(db.Boolean, default=False, nullable=False)
    push_marketing = db.Column(db.Boolean, default=False, nullable=False)
    
    # Communication Frequency
    daily_digest = db.Column(db.Boolean, default=False, nullable=False)
    weekly_summary = db.Column(db.Boolean, default=True, nullable=False)
    monthly_statements = db.Column(db.Boolean, default=True, nullable=False)
    
    # Preferred Communication Times
    preferred_time_start = db.Column(db.Time, nullable=True)  # e.g., 09:00
    preferred_time_end = db.Column(db.Time, nullable=True)    # e.g., 18:00
    timezone = db.Column(db.String(50), nullable=True, default='UTC')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='communication_preferences', lazy=True)
    
    def __repr__(self):
        return f'<CommunicationPreference {self.user_id}>'
    
    @staticmethod
    def get_or_create_preferences(user_id):
        """Get or create communication preferences for a user"""
        preferences = CommunicationPreference.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = CommunicationPreference(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        return preferences


class ScheduledCommunication(db.Model):
    """
    Scheduled communications for automated messaging
    """
    __tablename__ = 'scheduled_communications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Communication Details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    template_name = db.Column(db.String(100), nullable=False)
    communication_type = db.Column(db.String(50), nullable=False)  # 'birthday', 'holiday', 'statement', 'reminder'
    
    # Scheduling Information
    schedule_type = db.Column(db.String(20), nullable=False)  # 'once', 'daily', 'weekly', 'monthly', 'yearly'
    scheduled_date = db.Column(db.DateTime, nullable=True)  # For one-time communications
    cron_expression = db.Column(db.String(100), nullable=True)  # For recurring communications
    
    # Target Audience
    target_all_users = db.Column(db.Boolean, default=False, nullable=False)
    target_user_ids = db.Column(db.JSON, nullable=True)  # List of specific user IDs
    target_criteria = db.Column(db.JSON, nullable=True)  # Criteria for dynamic targeting
    
    # Status and Control
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_run_at = db.Column(db.DateTime, nullable=True)
    next_run_at = db.Column(db.DateTime, nullable=True)
    run_count = db.Column(db.Integer, default=0, nullable=False)
    success_count = db.Column(db.Integer, default=0, nullable=False)
    failure_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Template Variables
    template_context = db.Column(db.JSON, nullable=True)  # Default context variables
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ScheduledCommunication {self.name}: {self.communication_type}>'
    
    def update_run_stats(self, success=True):
        """Update run statistics after execution"""
        self.run_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.last_run_at = datetime.utcnow()
        db.session.commit()


class CommunicationAttachment(db.Model):
    """
    Attachments for communications (e.g., statements, receipts)
    """
    __tablename__ = 'communication_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    communication_log_id = db.Column(UUID(as_uuid=True), db.ForeignKey('communication_logs.id'), nullable=False)
    
    # File Information
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)  # 'pdf', 'csv', 'xlsx', etc.
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    
    # Storage Information
    storage_path = db.Column(db.String(500), nullable=True)  # Path to file if stored locally
    storage_url = db.Column(db.String(500), nullable=True)   # URL if stored in cloud
    checksum = db.Column(db.String(64), nullable=True)       # MD5 or SHA256 checksum
    
    # Metadata
    attachment_type = db.Column(db.String(50), nullable=False)  # 'statement', 'receipt', 'report', 'document'
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    communication_log = db.relationship('CommunicationLog', backref='attachments', lazy=True)
    
    def __repr__(self):
        return f'<CommunicationAttachment {self.filename}: {self.attachment_type}>'


# Database indexes for performance
Index('idx_comm_logs_recipient_email', CommunicationLog.recipient_email)
Index('idx_comm_logs_recipient_user_id', CommunicationLog.recipient_user_id)
Index('idx_comm_logs_sent_at', CommunicationLog.sent_at)
Index('idx_comm_logs_status', CommunicationLog.status)
Index('idx_comm_logs_template_name', CommunicationLog.template_name)

Index('idx_email_templates_name', EmailTemplate.name)
Index('idx_email_templates_category', EmailTemplate.category)
Index('idx_email_templates_is_active', EmailTemplate.is_active)

Index('idx_comm_prefs_user_id', CommunicationPreference.user_id)

Index('idx_scheduled_comm_is_active', ScheduledCommunication.is_active)
Index('idx_scheduled_comm_next_run_at', ScheduledCommunication.next_run_at)
Index('idx_scheduled_comm_communication_type', ScheduledCommunication.communication_type)

Index('idx_comm_attachments_comm_log_id', CommunicationAttachment.communication_log_id)
Index('idx_comm_attachments_attachment_type', CommunicationAttachment.attachment_type)