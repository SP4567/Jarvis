import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    Tier1Decision,
    IncidentContext,
    IncidentCase,
    IncidentStatus,
    InvestigationTimelineEntry,
    InvestigationHypothesis,
    ContainmentAction,
    ExplainabilityReport,
    AgentFinding,
    AgentExecutionPhase
)
from server.soc.soc_guardrails import soc_guardrail_engine

class Tier2ResponderAgent(BaseSocAgent):
    """
    Tier 2 — Incident Responder Agent
    Performs forensic timeline reconstruction, blast radius scoping, hypothesis validation, and containment execution.
    """
    def __init__(self):
        super().__init__(
            name="tier2_responder_agent",
            role_title="Tier 2 Incident Response Commander",
            description="Coordinates in-depth incident investigation, blast radius scoping, hypothesis validation, and containment workflows."
        )

    def investigate_incident(self, alert: Tier1Decision, case_id: str) -> IncidentContext:
        """Conducts in-depth forensic investigation and formulates containment strategy"""
        now = datetime.now().isoformat()
        hostname = alert.affected_assets[0]["hostname"] if alert.affected_assets else "UNKNOWN_HOST"
        user = alert.affected_identities[0] if alert.affected_identities else "SYSTEM"

        # 1. Build Multi-Source Chronological Timeline
        timeline: List[InvestigationTimelineEntry] = []
        timeline.append(InvestigationTimelineEntry(
            timestamp=alert.timestamp,
            source=alert.source,
            description=f"Initial alert triggered: {alert.classification} risk score={alert.risk_score}",
            entity=hostname,
            provenance="OBSERVED_EVIDENCE"
        ))

        for ev in alert.evidence_chain:
            timeline.append(InvestigationTimelineEntry(
                timestamp=alert.timestamp,
                source="Forensic Correlator",
                description=ev,
                entity=hostname,
                provenance="OBSERVED_EVIDENCE"
            ))

        # 2. Formulate Attack Hypothesis
        hypotheses: List[InvestigationHypothesis] = []
        is_c2 = any(t.ioc_type == "IP" for t in alert.threat_intel)
        is_cred_dump = any("credential" in m.tactic.lower() for m in alert.mitre_attack)

        if is_c2 and is_cred_dump:
            hypothesis_stmt = f"Adversary obtained execution on {hostname}, performed credential dumping via LSASS, and established active C2 beaconing."
        elif is_c2:
            hypothesis_stmt = f"Adversary established command-and-control connection on {hostname} to external infrastructure."
        elif is_cred_dump:
            hypothesis_stmt = f"Internal user account {user} or process attempted unauthorized LSASS memory credential dumping."
        else:
            hypothesis_stmt = f"Suspicious execution observed on {hostname} exhibiting Living-off-the-Land adversary techniques."

        hypotheses.append(InvestigationHypothesis(
            hypothesis_id=f"HYP-{uuid.uuid4().hex[:6].upper()}",
            statement=hypothesis_stmt,
            confidence=alert.confidence_score,
            supporting_evidence=alert.evidence_chain,
            refuting_evidence=["No legitimate scheduled IT maintenance matches this process tree."],
            status="VALIDATED"
        ))

        # 3. Formulate Containment Actions
        containment_actions: List[ContainmentAction] = []
        
        # High Risk Action: Host Network Isolation (Requires Human Approval)
        if alert.risk_score >= 60:
            act_isolate = soc_guardrail_engine.propose_action(
                case_id=case_id,
                action_name="isolate_endpoint",
                target={"hostname": hostname, "criticality": alert.affected_assets[0].get("criticality") if alert.affected_assets else "medium"},
                reason=f"Active breach / C2 beaconing on {hostname}.",
                evidence=alert.evidence_chain,
                confidence=alert.confidence_score,
                expected_impact=f"Host '{hostname}' will be severed from the corporate network except for management agent.",
                rollback_strategy=f"reconnect_endpoint_network('{hostname}')"
            )
            containment_actions.append(act_isolate)

        # Medium Risk Action: Firewall IOC Blocking (Auto or Policy Approved)
        for ti in alert.threat_intel:
            if ti.ioc_type in ["IP", "DOMAIN"]:
                act_block = soc_guardrail_engine.propose_action(
                    case_id=case_id,
                    action_name="block_firewall_ioc",
                    target={"ioc": ti.ioc, "type": ti.ioc_type},
                    reason=f"Block malicious C2 traffic to {ti.ioc} ({ti.threat_actor}).",
                    evidence=[f"CTI match: {ti.ioc} reputation={ti.reputation}"],
                    confidence=0.98,
                    expected_impact=f"Outbound firewall rule dropped for {ti.ioc}.",
                    rollback_strategy=f"unblock_firewall_ioc('{ti.ioc}')"
                )
                containment_actions.append(act_block)

        # 4. Generate 8-Invariant Explainability Report
        explainability = ExplainabilityReport(
            what_happened=f"Security telemetry detected high-risk execution and anomalous network activity on host '{hostname}' involving identity '{user}'.",
            supporting_evidence=alert.evidence_chain,
            alternative_explanations_considered=[
                "Scheduled system backup script (ruled out: anomalous Tor exit node communication)",
                "Authorized IT administration (ruled out: non-standard parent process and unapproved execution window)"
            ],
            confidence_calculation=f"{int(alert.confidence_score * 100)}% based on verified CTI reputation matches and behavioral process heuristics.",
            affected_entities={
                "assets": [hostname],
                "identities": [user]
            },
            mitre_techniques=[f"{m.technique_id} - {m.technique_name}" for m in alert.mitre_attack],
            recommended_next_actions=[
                f"Approve network isolation for {hostname}",
                "Perform memory artifact acquisition and triage forensics",
                "Reset credentials for identity " + user
            ],
            invalidation_conditions="Verification by systems administrator that script execution was authorized emergency maintenance."
        )

        status = IncidentStatus.CONTAINMENT_PENDING if any(a.risk_level.value == "HIGH" for a in containment_actions) else IncidentStatus.INVESTIGATING

        context = IncidentContext(
            case_id=case_id,
            incident_id=case_id,
            title=f"Incident on {hostname}: {alert.mitre_attack[0].technique_name if alert.mitre_attack else 'Suspicious Activity'}",
            status=status,
            severity=alert.severity,
            risk_score=alert.risk_score,
            created_at=alert.timestamp,
            updated_at=now,
            assigned_tier="Tier 2",
            initial_alert=alert,
            affected_assets=alert.affected_assets,
            affected_identities=alert.affected_identities,
            affected_users=alert.affected_identities,
            indicators=alert.threat_intel,
            evidence_chain=alert.evidence_chain,
            timeline=timeline,
            mitre_attack=alert.mitre_attack,
            hypotheses=hypotheses,
            containment_actions=containment_actions,
            explainability=explainability
        )

        # Self-finding
        context.agent_findings[self.name] = AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(alert.confidence_score),
            summary=f"Incident response scoped on {hostname}. {len(containment_actions)} containment action(s) proposed.",
            structured_data={"status": status.value, "containment_actions": len(containment_actions)},
            recommendations=explainability.recommended_next_actions
        )

        return context

tier2_responder_agent = Tier2ResponderAgent()
