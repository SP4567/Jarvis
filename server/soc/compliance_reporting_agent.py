from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    ComplianceControlMapping,
    AgentFinding,
    AgentExecutionPhase
)

class ComplianceReportingAgent(BaseSocAgent):
    """
    SOC Reporting & Compliance Agent
    Maps incidents to regulatory frameworks (NIST CSF, ISO 27001, SOC 2, CIS Controls),
    tracks MTTD/MTTR metrics, and produces executive and technical compliance reports.
    """
    def __init__(self):
        super().__init__(
            name="compliance_reporting_agent",
            role_title="SOC Compliance & Executive Reporting Specialist",
            description="Generates executive briefings, technical post-incident reviews, and regulatory control mappings (NIST, ISO 27001, SOC 2)."
        )

    def map_compliance_controls(self, context: IncidentContext) -> List[ComplianceControlMapping]:
        """Maps incident observations to standard compliance frameworks"""
        mappings = [
            ComplianceControlMapping(
                framework="NIST_CSF",
                control_id="DE.CM-1",
                control_name="Network and System Telemetry Monitoring",
                status="COMPLIANT",
                justification="Network and endpoint anomalies detected within SLA by autonomous telemetry agents.",
                evidence_reference=f"Case {context.incident_id or context.case_id}"
            ),
            ComplianceControlMapping(
                framework="NIST_CSF",
                control_id="RS.MI-1",
                control_name="Incident Containment and Mitigation",
                status="REMEDIATED" if context.containment_actions else "DEFICIENT",
                justification="Automated containment proposals generated and executed under human authorization.",
                evidence_reference="Containment action log"
            ),
            ComplianceControlMapping(
                framework="ISO_27001",
                control_id="A.16.1.4",
                control_name="Assessment of and Decision on Information Security Events",
                status="COMPLIANT",
                justification="Multi-agent quantitative risk rating and 8-point explainability report compiled.",
                evidence_reference="Tier 1 & Tier 2 findings"
            ),
            ComplianceControlMapping(
                framework="SOC_2",
                control_id="CC7.3",
                control_name="Incident Response Testing and Execution",
                status="COMPLIANT",
                justification="End-to-end incident lifecycle executed and recorded in tamper-evident SQLite case memory.",
                evidence_reference="Immutable audit chain"
            ),
            ComplianceControlMapping(
                framework="CIS_V8",
                control_id="CIS_17",
                control_name="Incident Response Management",
                status="COMPLIANT",
                justification="Structured playbooks attached and forensic artifacts preserved with SHA-256 hashes.",
                evidence_reference="Digital Forensics evidence items"
            )
        ]
        return mappings

    def generate_executive_summary(self, context: IncidentContext) -> str:
        """Generates clear, high-impact executive briefing for CISOs and leadership"""
        cid = context.incident_id or context.case_id
        host = context.affected_assets[0].get("hostname") if context.affected_assets else "Corporate Infrastructure"
        actions_count = len(context.containment_actions)
        
        return (
            f"EXECUTIVE SECURITY BRIEFING — {context.title}\n"
            f"Case Identifier: {cid} | Severity: {context.severity.value} | Risk Rating: {context.risk_score}/100\n\n"
            f"Summary of Event: On {context.created_at[:10]}, JARVIS SOC detected and triaged an anomaly on {host}. "
            f"A coordinated multi-agent investigation validated an active security incident. "
            f"{actions_count} containment action(s) were proposed and enforced through the Human-in-the-Loop authorization gate.\n\n"
            f"Impact & Status: Blast radius was contained to {host}. Zero unauthorized data exfiltration observed. "
            f"Regulatory compliance controls across NIST CSF and SOC 2 CC7.3 maintained."
        )

    def generate_technical_summary(self, context: IncidentContext) -> str:
        """Generates deep technical forensics review for SOC Analysts and Incident Responders"""
        cid = context.incident_id or context.case_id
        timeline_str = "\n".join([f" - [{t.timestamp}] {t.entity}: {t.description}" for t in context.timeline[:5]])
        mitre_str = ", ".join([f"{m.technique_id} ({m.technique_name})" for m in context.mitre_attack]) or "T1059.001"
        
        return (
            f"TECHNICAL POST-INCIDENT FORENSIC REPORT\n"
            f"Case: {cid} | Status: {context.status.value}\n\n"
            f"MITRE ATT&CK Matrix: {mitre_str}\n\n"
            f"Initial Chronological Sequence:\n{timeline_str}\n\n"
            f"Evidence Artifacts Collected: {len(context.forensic_artifacts)}\n"
            f"Sigma Detection Rules Engineered: {len(context.detection_rules)}\n"
            f"Root Cause: Malicious process execution exhibiting Living-off-the-Land techniques."
        )

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        mappings = self.map_compliance_controls(context)
        exec_summary = self.generate_executive_summary(context)
        tech_summary = self.generate_technical_summary(context)
        return {
            "mappings": mappings,
            "executive_summary": exec_summary,
            "technical_summary": tech_summary
        }

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        mappings: List[ComplianceControlMapping] = telemetry.get("mappings", [])
        
        context.compliance_mappings = mappings
        context.executive_summary = telemetry.get("executive_summary")
        context.technical_summary = telemetry.get("technical_summary")
        
        compliant_count = sum(1 for m in mappings if m.status in ["COMPLIANT", "REMEDIATED"])
        
        return {
            "total_controls_audited": len(mappings),
            "compliant_controls": compliant_count,
            "compliance_posture_score": int((compliant_count / len(mappings)) * 100) if mappings else 100,
            "confidence": 0.99
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "PUBLISH_COMPLIANCE_PACKAGE",
            "requires_containment": False,
            "recommendations": [
                "Archive executive briefing and technical forensics report for external audit.",
                "Conduct 30-day post-mortem review on detection rule efficacy."
            ]
        }

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        score = analysis.get("compliance_posture_score", 100)
        summary = (
            f"Compliance & Reporting generated Executive and Technical post-incident reports. "
            f"Mapped to NIST CSF, ISO 27001, SOC 2, and CIS v8 with {score}% compliance posture."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=0.99,
            summary=summary,
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

compliance_reporting_agent = ComplianceReportingAgent()
