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

class AgentExecutionPhase(str, Enum):
    RECEIVE = "RECEIVE"
    UNDERSTAND = "UNDERSTAND"
    PLAN = "PLAN"
    COLLECT = "COLLECT"
    ANALYZE = "ANALYZE"
    DECIDE = "DECIDE"
    ACT = "ACT"
    VERIFY = "VERIFY"
    RECOVER = "RECOVER"
    REPORT = "REPORT"
    ESCALATE = "ESCALATE"

class MitreAttackMapping(BaseModel):
    tactic: str
    technique_id: str
    technique_name: str

class SecurityEvent(BaseModel):
    event_id: str
    timestamp: str
    source_type: str  # SIEM | EDR | NDR | CLOUD_IAM | FIREWALL | HONEYPOT | APP_WAF
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    user_identity: Optional[str] = None
    process_name: Optional[str] = None
    command_line: Optional[str] = None
    file_hash: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)

class ThreatIntelResult(BaseModel):
    ioc: str
    ioc_type: str  # IP | DOMAIN | SHA256 | URL | CVE
    reputation: str  # MALICIOUS | SUSPICIOUS | CLEAN | UNKNOWN
    score: int = 0
    threat_actor: Optional[str] = None
    cve_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class AgentFinding(BaseModel):
    agent_name: str
    role_title: str
    phase: AgentExecutionPhase = AgentExecutionPhase.REPORT
    confidence: float = 1.0
    summary: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    iocs_identified: List[str] = Field(default_factory=list)
    mitre_techniques: List[MitreAttackMapping] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ForensicEvidenceItem(BaseModel):
    artifact_id: str
    artifact_type: str  # PREFETCH | SHIMCACHE | AMCACHE | EVENT_LOG | MEMORY_DUMP | MFT | REGISTRY
    source_host: str
    file_path: Optional[str] = None
    sha256_hash: str
    collected_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    provenance_chain: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MalwareReport(BaseModel):
    sample_hash: str
    file_name: Optional[str] = None
    file_size_bytes: int = 0
    entropy: float = 0.0
    is_packed_or_obfuscated: bool = False
    pe_sections: List[Dict[str, Any]] = Field(default_factory=list)
    suspicious_imports: List[str] = Field(default_factory=list)
    extracted_strings: List[str] = Field(default_factory=list)
    extracted_c2_endpoints: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    mitre_mappings: List[MitreAttackMapping] = Field(default_factory=list)

class VulnerabilityFinding(BaseModel):
    cve_id: str
    title: str
    cvss_score: float = 0.0
    epss_score: float = 0.0
    affected_package: str
    exploit_available_in_wild: bool = False
    business_impact_score: int = 50
    remediation_guidance: str
    fixed_version: Optional[str] = None

class IdentityAnomaly(BaseModel):
    username: str
    anomaly_type: str  # IMPOSSIBLE_TRAVEL | KERBEROASTING | AS_REP_ROASTING | MFA_FATIGUE | TOKEN_THEFT | PASSWORD_SPRAY
    source_ip: Optional[str] = None
    geolocation: Optional[str] = None
    risk_score: int = 0
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    recommended_action: str = "REVOKE_SESSION_AND_MFA"

class NetworkAnomaly(BaseModel):
    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str = "TCP"
    anomaly_type: str  # C2_BEACON | DNS_TUNNELING | LATERAL_SMB | PORT_SCAN | DATA_EXFILTRATION
    beacon_interval_sec: Optional[float] = None
    jitter_percentage: Optional[float] = None
    bytes_transferred: int = 0
    confidence: float = 0.0

class CloudAnomaly(BaseModel):
    cloud_provider: str = "AWS"  # AWS | GCP | AZURE
    account_id: Optional[str] = None
    region: Optional[str] = None
    service_name: str
    resource_id: str
    anomaly_type: str  # IAM_PRIVILEGE_ESCALATION | PUBLIC_BUCKET_EXPOSURE | ANOMALOUS_API_CALL | SG_WIDE_OPEN
    actor_principal: str
    attack_path_summary: str
    remediation_cli_command: str

class AppSecAnomaly(BaseModel):
    endpoint_url: str
    http_method: str = "POST"
    attack_type: str  # SQLI | XSS | SSRF | IDOR | CMD_INJECTION | BROKEN_AUTH | RATE_LIMIT_ABUSE
    owasp_category: str = "A03:2021-Injection"
    payload_snippet: str
    client_ip: str
    recommended_waf_rule: str

class ComplianceControlMapping(BaseModel):
    framework: str  # NIST_CSF | ISO_27001 | SOC_2 | CIS_V8
    control_id: str
    control_name: str
    status: str = "DEFICIENT"  # COMPLIANT | DEFICIENT | VIOLATED | REMEDIATED
    justification: str
    evidence_reference: str

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

class IncidentContext(BaseModel):
    """
    Unified Shared Incident Context Graph & Event Bus State
    Maintains all multi-agent investigative evidence, findings, timeline, and remediation states.
    """
    case_id: str = Field(default_factory=lambda: f"CASE-{datetime.now().strftime('%H%M%S')}")
    incident_id: Optional[str] = None
    title: str
    status: IncidentStatus = IncidentStatus.NEW
    severity: SeverityLevel = SeverityLevel.P3
    risk_score: int = 50
    created_at: str
    updated_at: str
    assigned_tier: str = "Tier 1"
    initial_alert: Optional[Tier1Decision] = None
    affected_assets: List[Dict[str, Any]] = Field(default_factory=list)
    affected_identities: List[str] = Field(default_factory=list)
    affected_users: List[str] = Field(default_factory=list)
    indicators: List[ThreatIntelResult] = Field(default_factory=list)
    evidence_chain: List[str] = Field(default_factory=list)
    timeline: List[InvestigationTimelineEntry] = Field(default_factory=list)
    agent_findings: Dict[str, AgentFinding] = Field(default_factory=dict)
    mitre_attack: List[MitreAttackMapping] = Field(default_factory=list)
    hypotheses: List[InvestigationHypothesis] = Field(default_factory=list)
    containment_actions: List[ContainmentAction] = Field(default_factory=list)
    forensic_artifacts: List[ForensicEvidenceItem] = Field(default_factory=list)
    malware_reports: List[MalwareReport] = Field(default_factory=list)
    vulnerability_findings: List[VulnerabilityFinding] = Field(default_factory=list)
    identity_anomalies: List[IdentityAnomaly] = Field(default_factory=list)
    network_anomalies: List[NetworkAnomaly] = Field(default_factory=list)
    cloud_anomalies: List[CloudAnomaly] = Field(default_factory=list)
    appsec_anomalies: List[AppSecAnomaly] = Field(default_factory=list)
    detection_rules: List[DetectionRule] = Field(default_factory=list)
    compliance_mappings: List[ComplianceControlMapping] = Field(default_factory=list)
    explainability: Optional[ExplainabilityReport] = None
    post_incident_summary: Optional[str] = None
    executive_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    verification_results: List[Dict[str, Any]] = Field(default_factory=list)
    final_disposition: Optional[str] = None

# Backward compatibility alias
IncidentCase = IncidentContext

