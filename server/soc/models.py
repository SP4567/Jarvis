from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class SeverityLevel(str, Enum):
    P0 = "P0"  # Enterprise Catastrophe / Global Incident
    P1 = "P1"  # Critical / Active Breach
    P2 = "P2"  # Confirmed Security Incident
    P3 = "P3"  # Suspicious / Low Risk
    P4 = "P4"  # Informational / Benign

class IncidentStatus(str, Enum):
    NEW = "NEW"
    TRIAGING = "TRIAGING"
    INVESTIGATING = "INVESTIGATING"
    CONTAINMENT_PENDING = "CONTAINMENT_PENDING"
    CONTAINED = "CONTAINED"
    REMEDIATED = "REMEDIATED"
    CLOSED = "CLOSED"

class ActionRiskLevel(str, Enum):
    LOW = "LOW"        # Read-only, enrichment, deduplication (Auto)
    MEDIUM = "MEDIUM"  # Low-impact containment (Policy Controlled)
    HIGH = "HIGH"      # Disruptive (Mandatory Human Signoff)

class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    AUTO_EXECUTED = "AUTO_EXECUTED"
    ROLLED_BACK = "ROLLED_BACK"

class MitreAttackMapping(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str

class SecurityEvent(BaseModel):
    event_id: str
    timestamp: str
    source_type: str  # SIEM | EDR | NDR | CLOUD_IAM | FIREWALL | HONEYPOT
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    user_identity: Optional[str] = None
    process_name: Optional[str] = None
    command_line: Optional[str] = None
    file_hash: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)

class ThreatIntelResult(BaseModel):
    ioc: str
    ioc_type: str  # IP | DOMAIN | SHA256 | URL
    reputation: str  # MALICIOUS | SUSPICIOUS | CLEAN | UNKNOWN
    score: int = 0
    threat_actor: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class Tier1Decision(BaseModel):
    alert_id: str
    timestamp: str
    source: str
    classification: str  # FALSE_POSITIVE | BENIGN | SUSPICIOUS | MALICIOUS
    confidence_score: float = 0.0  # 0.0 to 1.0
    risk_score: int = 0  # 0 to 100
    severity: SeverityLevel = SeverityLevel.P3
    affected_assets: List[Dict[str, Any]] = Field(default_factory=list)
    affected_identities: List[str] = Field(default_factory=list)
    threat_intel: List[ThreatIntelResult] = Field(default_factory=list)
    mitre_attack: List[MitreAttackMapping] = Field(default_factory=list)
    evidence_chain: List[str] = Field(default_factory=list)
    escalate_to_tier2: bool = False
    escalation_reason: Optional[str] = None

class InvestigationTimelineEntry(BaseModel):
    timestamp: str
    source: str
    description: str
    entity: str
    provenance: str = "OBSERVED_EVIDENCE"  # OBSERVED_EVIDENCE | INFERENCE | ACTION_RESULT

class InvestigationHypothesis(BaseModel):
    hypothesis_id: str
    statement: str
    confidence: float
    supporting_evidence: List[str] = Field(default_factory=list)
    refuting_evidence: List[str] = Field(default_factory=list)
    status: str = "VALIDATED"  # VALIDATED | REJECTED | PENDING

class ContainmentAction(BaseModel):
    action_id: str
    case_id: str
    action_name: str
    target: Dict[str, Any]
    reason: str
    evidence: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    risk_level: ActionRiskLevel
    expected_impact: str
    required_approval: str = "HUMAN_ANALYST"
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    timestamp_proposed: str
    timestamp_executed: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    rollback_strategy: str
    is_rolled_back: bool = False

class DetectionRule(BaseModel):
    rule_id: str
    title: str
    rule_type: str = "SIGMA"  # SIGMA | YARA | SURICATA
    description: str
    severity: str
    mitre_tags: List[str] = Field(default_factory=list)
    rule_content: str
    created_at: str

class ExplainabilityReport(BaseModel):
    what_happened: str
    supporting_evidence: List[str]
    alternative_explanations_considered: List[str]
    confidence_calculation: str
    affected_entities: Dict[str, List[str]]
    mitre_techniques: List[str]
    recommended_next_actions: List[str]
    invalidation_conditions: str

class IncidentCase(BaseModel):
    case_id: str
    title: str
    status: IncidentStatus = IncidentStatus.NEW
    severity: SeverityLevel = SeverityLevel.P3
    risk_score: int = 50
    created_at: str
    updated_at: str
    assigned_tier: str = "Tier 1"
    initial_alert: Tier1Decision
    timeline: List[InvestigationTimelineEntry] = Field(default_factory=list)
    hypotheses: List[InvestigationHypothesis] = Field(default_factory=list)
    containment_actions: List[ContainmentAction] = Field(default_factory=list)
    detection_rules: List[DetectionRule] = Field(default_factory=list)
    explainability: Optional[ExplainabilityReport] = None
    post_incident_summary: Optional[str] = None
