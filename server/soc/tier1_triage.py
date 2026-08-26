import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    SecurityEvent,
    Tier1Decision,
    SeverityLevel,
    ThreatIntelResult,
    MitreAttackMapping,
    IncidentContext,
    AgentFinding,
    AgentExecutionPhase
)
from server.soc.cti_feed import cti_feed_manager

class Tier1TriageAgent(BaseSocAgent):
    """
    Tier 1 — Triage Analyst Agent
    High-volume alert ingestion, normalization, enrichment, deduplication, and initial risk classification.
    """
    def __init__(self):
        super().__init__(
            name="tier1_triage_agent",
            role_title="Tier 1 Security Triage Analyst",
            description="Performs high-volume alert ingestion, event normalization, CTI enrichment, and alert-to-disposition triage."
        )
        
        # Asset Criticality Registry
        self.asset_registry = {
            "PROD-DB-01": {"criticality": "high", "tier": "tier_1_core", "owner": "DBA_Team"},
            "CORP-DC-01": {"criticality": "critical", "tier": "domain_controller", "owner": "SecOps"},
            "APP-SERVER-04": {"criticality": "medium", "tier": "production_api", "owner": "DevOps"},
            "WS-FINANCE-12": {"criticality": "high", "tier": "workstation", "owner": "Finance_Dept"},
            "DEV-SANDBOX-09": {"criticality": "low", "tier": "dev_cluster", "owner": "Engineering"}
        }

    def normalize_event(self, raw_event: Dict[str, Any]) -> SecurityEvent:
        """Normalizes heterogeneous telemetry into common schema"""
        return SecurityEvent(
            event_id=raw_event.get("event_id", f"EVT-{uuid.uuid4().hex[:6].upper()}"),
            timestamp=raw_event.get("timestamp", datetime.now().isoformat()),
            source_type=raw_event.get("source_type", "EDR"),
            hostname=raw_event.get("hostname", "UNKNOWN_HOST"),
            ip_address=raw_event.get("ip_address"),
            user_identity=raw_event.get("user_identity", "SYSTEM"),
            process_name=raw_event.get("process_name"),
            command_line=raw_event.get("command_line"),
            file_hash=raw_event.get("file_hash"),
            raw_payload=raw_event
        )

    def triage_event(self, event: SecurityEvent) -> Tier1Decision:
        """Performs automated enrichment, risk scoring, MITRE mapping, and triage decision"""
        alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
        evidence: List[str] = []
        threat_intel: List[ThreatIntelResult] = []
        mitre_mappings: List[MitreAttackMapping] = []
        risk_score = 15  # Base baseline
        
        # 1. Asset Criticality Check
        asset_info = self.asset_registry.get(event.hostname or "", {"criticality": "medium", "tier": "standard"})
        if asset_info["criticality"] == "critical":
            risk_score += 35
            evidence.append(f"Target host '{event.hostname}' is designated CRITICAL ({asset_info['tier']}).")
        elif asset_info["criticality"] == "high":
            risk_score += 20
            evidence.append(f"Target host '{event.hostname}' is designated HIGH criticality.")

        # 2. Threat Intel Enrichment via CTI Feed Manager
        if event.ip_address:
            ti = cti_feed_manager._lookup_offline_heuristic(event.ip_address, "IP")
            if ti.reputation in ["MALICIOUS", "SUSPICIOUS"]:
                threat_intel.append(ti)
                risk_score += 40
                evidence.append(f"Outbound connection matches CTI indicator: {event.ip_address} ({ti.threat_actor or 'Flagged IOC'}).")
                mitre_mappings.append(MitreAttackMapping(
                    tactic="Command and Control",
                    technique_id="T1071.001",
                    technique_name="Application Layer Protocol: Web Protocols"
                ))

        if event.file_hash:
            ti = cti_feed_manager._lookup_offline_heuristic(event.file_hash, "SHA256")
            if ti.reputation in ["MALICIOUS", "SUSPICIOUS"]:
                threat_intel.append(ti)
                risk_score += 45
                evidence.append(f"File hash matches verified malware signature: {ti.threat_actor or 'Malicious Hash'}.")
                mitre_mappings.append(MitreAttackMapping(
                    tactic="Credential Access",
                    technique_id="T1003.001",
                    technique_name="OS Credential Dumping: LSASS Memory"
                ))

        # Check payload threat intel if passed from background monitor
        if event.raw_payload and "threat_intel" in event.raw_payload:
            ti_data = event.raw_payload["threat_intel"]
            if isinstance(ti_data, dict) and ti_data.get("reputation") in ["MALICIOUS", "SUSPICIOUS"]:
                ti_obj = ThreatIntelResult.model_validate(ti_data)
                threat_intel.append(ti_obj)
                risk_score += 40
                evidence.append(f"Live CTI Feed Alert: {ti_obj.ioc} ({ti_obj.threat_actor}).")

        # 3. Behavioral Process & Command Inspection
        cmd = (event.command_line or "").lower()
        proc = (event.process_name or "").lower()

        if "powershell" in proc or "pwsh" in proc or "-enc" in cmd or "encodedcommand" in cmd:
            risk_score += 25
            evidence.append("Obfuscated or base64-encoded PowerShell process execution observed.")
            mitre_mappings.append(MitreAttackMapping(
                tactic="Execution",
                technique_id="T1059.001",
                technique_name="Command and Scripting Interpreter: PowerShell"
            ))

        if "mimikatz" in cmd or "sekurlsa" in cmd or "lsass" in cmd:
            risk_score += 50
            evidence.append("LSASS memory dumping / credential harvesting command syntax detected.")
            mitre_mappings.append(MitreAttackMapping(
                tactic="Credential Access",
                technique_id="T1003.001",
                technique_name="OS Credential Dumping: LSASS Memory"
            ))

        if "whoami" in cmd or "net user" in cmd or "net group" in cmd or "nltest" in cmd:
            risk_score += 15
            evidence.append("Discovery command executed indicating post-compromise reconnaissance.")
            mitre_mappings.append(MitreAttackMapping(
                tactic="Discovery",
                technique_id="T1087.002",
                technique_name="Account Discovery: Domain Account"
            ))

        # Cap risk score
        risk_score = min(100, risk_score)

        # 4. Severity & Escalation Classification
        if risk_score >= 85:
            severity = SeverityLevel.P1
            classification = "MALICIOUS"
            confidence = 0.94
            escalate = True
            reason = "High-confidence active attack indicator on production asset."
        elif risk_score >= 60:
            severity = SeverityLevel.P2
            classification = "SUSPICIOUS"
            confidence = 0.85
            escalate = True
            reason = "Suspicious behavior matching known attack TTPs requiring forensic scoping."
        elif risk_score >= 35:
            severity = SeverityLevel.P3
            classification = "SUSPICIOUS"
            confidence = 0.65
            escalate = True
            reason = "Anomalous execution requiring Tier 2 validation."
        else:
            severity = SeverityLevel.P4
            classification = "BENIGN"
            confidence = 0.90
            escalate = False
            reason = "Routine or low-risk operational telemetry."

        return Tier1Decision(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            source=event.source_type,
            classification=classification,
            confidence_score=confidence,
            risk_score=risk_score,
            severity=severity,
            affected_assets=[{"hostname": event.hostname, "criticality": asset_info["criticality"]}],
            affected_identities=[event.user_identity] if event.user_identity else [],
            threat_intel=threat_intel,
            mitre_attack=mitre_mappings,
            evidence_chain=evidence or ["Baseline normal telemetry."],
            escalate_to_tier2=escalate,
            escalation_reason=reason
        )

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=0.94,
            summary=f"Tier 1 Triage processed alert: Risk {context.risk_score}/100, Severity {context.severity.value}.",
            structured_data={"risk_score": context.risk_score, "severity": context.severity.value},
            recommendations=["Escalate to Tier 2 Incident Responder." if context.risk_score >= 35 else "Close benign."]
        )

tier1_triage_agent = Tier1TriageAgent()
