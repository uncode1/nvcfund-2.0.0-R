"""
Compliance Models
Self-contained models for regulatory compliance, risk management, and AML operations
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

from modules.core.database import Base

class ComplianceRegulationType(Enum):
    """Types of regulatory compliance"""
    BSA_AML = "bsa_aml"
    KYC_CDD = "kyc_cdd"
    PATRIOT_ACT = "patriot_act"
    OFAC_SANCTIONS = "ofac_sanctions"
    PCI_DSS = "pci_dss"
    SOX_COMPLIANCE = "sox_compliance"
    BASEL_III = "basel_iii"
    DODD_FRANK = "dodd_frank"
    MiFID_II = "mifid_ii"
    GDPR = "gdpr"
    CCAR_STRESS_TEST = "ccar_stress_test"
    VOLCKER_RULE = "volcker_rule"

class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStatus(Enum):
    """Compliance status tracking"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    ESCALATED = "escalated"

class ComplianceFramework(Base):
    """Regulatory compliance framework and requirements"""
    __tablename__ = 'compliance_frameworks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Framework identification
    framework_code = Column(String(50), unique=True, nullable=False)
    framework_name = Column(String(200), nullable=False)
    regulation_type = Column(String(50), nullable=False)  # ComplianceRegulationType
    
    # Regulatory details
    regulatory_body = Column(String(200), nullable=False)  # SEC, FDIC, OCC, etc.
    jurisdiction = Column(String(100), nullable=False)
    applicable_entities = Column(JSONB)  # List of entity types
    
    # Requirements and standards
    compliance_requirements = Column(JSONB, nullable=False)  # Detailed requirements
    control_objectives = Column(JSONB)  # Control objectives
    key_controls = Column(JSONB)  # Key control activities
    
    # Testing and monitoring
    testing_frequency = Column(String(50))  # daily, monthly, quarterly, annual
    monitoring_requirements = Column(JSONB)
    reporting_requirements = Column(JSONB)
    
    # Risk and impact
    risk_level = Column(String(20), default=RiskLevel.MEDIUM.value)
    regulatory_penalties = Column(Text)
    business_impact = Column(Text)
    
    # Implementation details
    implementation_deadline = Column(DateTime)
    last_assessment_date = Column(DateTime)
    next_assessment_date = Column(DateTime)
    
    # Status and ownership
    compliance_status = Column(String(50), default=ComplianceStatus.UNDER_REVIEW.value)
    compliance_owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[compliance_owner])
    assessments = relationship("ComplianceAssessment", back_populates="framework")
    violations = relationship("ComplianceViolation", back_populates="framework")
    
    def __repr__(self):
        return f"<ComplianceFramework {self.framework_code}: {self.framework_name}>"

class ComplianceAssessment(Base):
    """Compliance assessments and audits"""
    __tablename__ = 'compliance_assessments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Assessment details
    framework_id = Column(UUID(as_uuid=True), ForeignKey('compliance_frameworks.id'), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # internal, external, regulatory
    
    # Assessment scope and timing
    assessment_scope = Column(JSONB, nullable=False)  # Areas covered
    assessment_period_start = Column(DateTime, nullable=False)
    assessment_period_end = Column(DateTime, nullable=False)
    
    # Assessment team
    lead_assessor = Column(Integer, ForeignKey('users.id'), nullable=False)
    assessment_team = Column(JSONB)  # List of team members
    external_auditor = Column(String(200))  # External audit firm
    
    # Assessment methodology
    assessment_methodology = Column(String(100))  # risk_based, controls_based, substantive
    sampling_approach = Column(String(100))
    testing_procedures = Column(JSONB)
    
    # Findings and results
    overall_rating = Column(String(50), nullable=False)  # ComplianceStatus
    control_effectiveness = Column(String(50))  # effective, partially_effective, ineffective
    
    # Detailed findings
    key_findings = Column(JSONB)  # List of key findings
    control_deficiencies = Column(JSONB)  # Control deficiencies identified
    process_improvements = Column(JSONB)  # Recommended improvements
    
    # Risk assessment
    inherent_risk = Column(String(20))  # RiskLevel
    residual_risk = Column(String(20))  # RiskLevel after controls
    risk_mitigation_status = Column(String(50))
    
    # Management response
    management_response = Column(Text)
    action_plan = Column(JSONB)  # Remediation action plan
    remediation_deadline = Column(DateTime)
    
    # Follow-up and monitoring
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    monitoring_frequency = Column(String(50))
    
    # Timestamps
    assessment_date = Column(DateTime, nullable=False)
    report_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    framework = relationship("ComplianceFramework", back_populates="assessments")
    assessor = relationship("User", foreign_keys=[lead_assessor])
    
    def __repr__(self):
        return f"<ComplianceAssessment {self.assessment_date}: {self.overall_rating}>"

class ComplianceViolation(Base):
    """Compliance violations and incidents"""
    __tablename__ = 'compliance_violations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Violation details
    framework_id = Column(UUID(as_uuid=True), ForeignKey('compliance_frameworks.id'), nullable=False)
    violation_type = Column(String(100), nullable=False)
    violation_severity = Column(String(20), nullable=False)  # RiskLevel
    
    # Incident information
    incident_date = Column(DateTime, nullable=False)
    discovery_date = Column(DateTime, nullable=False)
    discovery_method = Column(String(100))  # internal_audit, external_audit, self_reported
    
    # Violation description
    violation_description = Column(Text, nullable=False)
    affected_systems = Column(JSONB)  # Systems/processes affected
    affected_customers = Column(Integer, default=0)
    financial_impact = Column(Numeric(18, 2), default=0.00)
    
    # Root cause analysis
    root_cause = Column(Text)
    contributing_factors = Column(JSONB)
    control_failures = Column(JSONB)  # Failed controls
    
    # Response and remediation
    immediate_actions = Column(JSONB)  # Immediate response actions
    corrective_actions = Column(JSONB)  # Long-term corrections
    preventive_measures = Column(JSONB)  # Prevention measures
    
    # Timeline and status
    remediation_deadline = Column(DateTime)
    remediation_completion_date = Column(DateTime)
    status = Column(String(50), default='open')  # open, in_progress, resolved, closed
    
    # Regulatory reporting
    regulatory_notification_required = Column(Boolean, default=False)
    regulatory_notification_date = Column(DateTime)
    regulatory_response = Column(Text)
    
    # Assignment and ownership
    assigned_to = Column(Integer, ForeignKey('users.id'))
    reported_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Escalation
    escalated = Column(Boolean, default=False)
    escalation_date = Column(DateTime)
    escalated_to = Column(Integer, ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    framework = relationship("ComplianceFramework", back_populates="violations")
    assignee = relationship("User", foreign_keys=[assigned_to])
    reporter = relationship("User", foreign_keys=[reported_by])
    escalation_target = relationship("User", foreign_keys=[escalated_to])
    
    def __repr__(self):
        return f"<ComplianceViolation {self.violation_type}: {self.violation_severity}>"

class AMLTransaction(Base):
    """Anti-Money Laundering transaction monitoring"""
    __tablename__ = 'aml_transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction identification
    transaction_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(String(100), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # deposit, withdrawal, transfer, etc.
    transaction_amount = Column(Numeric(18, 2), nullable=False)
    transaction_currency = Column(String(3), default='USD')
    transaction_date = Column(DateTime, nullable=False)
    
    # Counterparty information
    counterparty_name = Column(String(200))
    counterparty_account = Column(String(100))
    counterparty_bank = Column(String(200))
    counterparty_country = Column(String(100))
    
    # AML risk scoring
    aml_risk_score = Column(Integer, nullable=False)  # 1-100 scale
    risk_factors = Column(JSONB)  # List of risk factors
    suspicious_indicators = Column(JSONB)  # Suspicious activity indicators
    
    # Transaction patterns
    daily_transaction_count = Column(Integer, default=1)
    daily_transaction_amount = Column(Numeric(18, 2))
    monthly_transaction_count = Column(Integer)
    monthly_transaction_amount = Column(Numeric(18, 2))
    
    # Geographic and entity risks
    high_risk_country = Column(Boolean, default=False)
    pep_involvement = Column(Boolean, default=False)  # Politically Exposed Person
    sanctions_screening_result = Column(String(50))  # clear, match, potential_match
    
    # Monitoring and alerts
    alert_triggered = Column(Boolean, default=False)
    alert_type = Column(String(100))  # structuring, unusual_pattern, threshold_breach
    alert_priority = Column(String(20))  # low, medium, high, critical
    
    # Investigation details
    investigation_required = Column(Boolean, default=False)
    investigation_status = Column(String(50))  # pending, in_progress, completed, closed
    investigated_by = Column(Integer, ForeignKey('users.id'))
    investigation_notes = Column(Text)
    
    # SAR reporting
    sar_filed = Column(Boolean, default=False)
    sar_filing_date = Column(DateTime)
    sar_number = Column(String(100))
    sar_reason = Column(Text)
    
    # CTR reporting
    ctr_required = Column(Boolean, default=False)
    ctr_filed = Column(Boolean, default=False)
    ctr_filing_date = Column(DateTime)
    ctr_number = Column(String(100))
    
    # Resolution
    resolution_status = Column(String(50))  # cleared, escalated, reported, blocked
    resolution_date = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    investigator = relationship("User", foreign_keys=[investigated_by])
    
    def __repr__(self):
        return f"<AMLTransaction {self.transaction_id}: {self.aml_risk_score}>"

class RegulatoryReport(Base):
    """Regulatory reporting and submissions"""
    __tablename__ = 'regulatory_reports'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report identification
    report_type = Column(String(100), nullable=False)  # call_report, sar, ctr, etc.
    report_period = Column(String(50), nullable=False)  # 2024Q1, 2024-01, etc.
    regulatory_body = Column(String(100), nullable=False)  # FDIC, OCC, FinCEN, etc.
    
    # Filing details
    filing_deadline = Column(DateTime, nullable=False)
    filing_date = Column(DateTime)
    submission_method = Column(String(50))  # electronic, paper, api
    
    # Report content
    report_data = Column(JSONB, nullable=False)  # Report data structure
    supporting_documents = Column(JSONB)  # List of supporting documents
    data_sources = Column(JSONB)  # Source systems and data
    
    # Validation and quality assurance
    data_validation_status = Column(String(50))  # passed, failed, pending
    validation_errors = Column(JSONB)  # List of validation errors
    qa_reviewed = Column(Boolean, default=False)
    qa_reviewer = Column(Integer, ForeignKey('users.id'))
    
    # Submission status
    submission_status = Column(String(50), default='draft')  # draft, submitted, accepted, rejected
    submission_reference = Column(String(100))  # Regulatory reference number
    acknowledgment_received = Column(Boolean, default=False)
    
    # Response and follow-up
    regulatory_response = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_deadline = Column(DateTime)
    
    # Correction and amendments
    amended = Column(Boolean, default=False)
    amendment_reason = Column(Text)
    original_report_id = Column(UUID(as_uuid=True), ForeignKey('regulatory_reports.id'))
    
    # Preparation and responsibility
    prepared_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewed_by = Column(Integer, ForeignKey('users.id'))
    approved_by = Column(Integer, ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    qa_reviewer_user = relationship("User", foreign_keys=[qa_reviewer])
    preparer = relationship("User", foreign_keys=[prepared_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    original_report = relationship("RegulatoryReport", remote_side=[id])
    
    def __repr__(self):
        return f"<RegulatoryReport {self.report_type}: {self.report_period}>"

class ComplianceTraining(Base):
    """Compliance training and certification tracking"""
    __tablename__ = 'compliance_training'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Training details
    training_name = Column(String(200), nullable=False)
    training_category = Column(String(100), nullable=False)  # aml, kyc, ethics, etc.
    training_provider = Column(String(200))
    
    # Training content
    training_description = Column(Text)
    learning_objectives = Column(JSONB)
    training_materials = Column(JSONB)  # List of materials
    
    # Requirements and scheduling
    mandatory = Column(Boolean, default=True)
    target_audience = Column(JSONB)  # Roles/departments
    frequency = Column(String(50))  # annual, biannual, quarterly
    
    # Training delivery
    delivery_method = Column(String(50))  # online, classroom, blended
    duration_hours = Column(Numeric(4, 2))
    
    # Certification and assessment
    assessment_required = Column(Boolean, default=True)
    passing_score = Column(Integer, default=80)
    certification_validity_months = Column(Integer, default=12)
    
    # Tracking and compliance
    completion_deadline = Column(DateTime)
    
    # Status and management
    training_status = Column(String(50), default='active')  # active, inactive, archived
    training_owner = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[training_owner])
    completions = relationship("TrainingCompletion", back_populates="training")
    
    def __repr__(self):
        return f"<ComplianceTraining {self.training_name}: {self.training_category}>"

class TrainingCompletion(Base):
    """Training completion records"""
    __tablename__ = 'training_completions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Completion details
    training_id = Column(UUID(as_uuid=True), ForeignKey('compliance_training.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Completion tracking
    start_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # Assessment results
    assessment_score = Column(Integer)
    passed = Column(Boolean, default=False)
    attempts = Column(Integer, default=1)
    
    # Certification
    certified = Column(Boolean, default=False)
    certification_date = Column(DateTime)
    certification_expiry = Column(DateTime)
    certificate_number = Column(String(100))
    
    # Status tracking
    completion_status = Column(String(50), default='not_started')  # not_started, in_progress, completed, overdue
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    training = relationship("ComplianceTraining", back_populates="completions")
    employee = relationship("User", foreign_keys=[employee_id])
    
    def is_certification_current(self) -> bool:
        """Check if certification is still current"""
        if self.certification_expiry:
            return datetime.utcnow() < self.certification_expiry
        return False
    
    def __repr__(self):
        return f"<TrainingCompletion {self.employee_id}: {self.completion_status}>"

# Create indexes for optimal query performance
Index('idx_compliance_frameworks_regulation_type', ComplianceFramework.regulation_type)
Index('idx_compliance_frameworks_status', ComplianceFramework.compliance_status)
Index('idx_compliance_frameworks_owner', ComplianceFramework.compliance_owner)
Index('idx_compliance_assessments_framework_id', ComplianceAssessment.framework_id)
Index('idx_compliance_assessments_date', ComplianceAssessment.assessment_date)
Index('idx_compliance_violations_framework_id', ComplianceViolation.framework_id)
Index('idx_compliance_violations_severity', ComplianceViolation.violation_severity)
Index('idx_compliance_violations_status', ComplianceViolation.status)
Index('idx_aml_transactions_customer_id', AMLTransaction.customer_id)
Index('idx_aml_transactions_risk_score', AMLTransaction.aml_risk_score)
Index('idx_aml_transactions_alert_triggered', AMLTransaction.alert_triggered)
Index('idx_aml_transactions_date', AMLTransaction.transaction_date)
Index('idx_regulatory_reports_type', RegulatoryReport.report_type)
Index('idx_regulatory_reports_period', RegulatoryReport.report_period)
Index('idx_regulatory_reports_deadline', RegulatoryReport.filing_deadline)
Index('idx_compliance_training_category', ComplianceTraining.training_category)
Index('idx_compliance_training_mandatory', ComplianceTraining.mandatory)
Index('idx_training_completions_training_id', TrainingCompletion.training_id)
Index('idx_training_completions_employee_id', TrainingCompletion.employee_id)
Index('idx_training_completions_status', TrainingCompletion.completion_status)