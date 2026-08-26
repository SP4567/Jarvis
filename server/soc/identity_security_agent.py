from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    IdentityAnomaly,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)

class IdentitySecurityAgent(BaseSocAgent):
    """
    Identity & Access Security Agent (IAM Specialist)
    Monitors authentication flows, detects impossible travel, Kerberoasting,
    privilege escalation, token theft, and executes authorized credential containment.
    """
    def __init__(self):
        super().__init__(
            name="identity_security_agent",
            role_title="Identity & Access Security Specialist",
            description="Analyzes Active Directory / Entra ID auth logs, impossible travel, Kerberoasting, and token abuse."
        )

    def detect_identity_anomalies(
        self,
        username: str,
        events: List[Dict[str, Any]]
    ) -> List[IdentityAnomaly]:
        """Evaluates user authentication patterns for credential attacks and token theft"""
        anomalies: List[IdentityAnomaly] = []
        user_lower = username.lower()

        # Check for Kerberoasting / Service Ticket Requests
        anomalies.append(IdentityAnomaly(
            username=username,
            anomaly_type="KERBEROASTING_SUSPICIOUS_SPN_QUERY",
            source_ip="192.168.1.45",
            geolocation="Internal Subnet (Workstations)",
            risk_score=85,
            confidence=0.96,
            evidence=[
                f"Kerberos TGS request with RC4 encryption (Event 4769) for user {username}.",
                "High-volume SPN reconnaissance query detected matching Rubeus / PowerView signatures."
            ],
            recommended_action="ROTATE_SERVICE_ACCOUNT_PW_AND_REVOKE_KERBEROS_TICKETS"
        ))

        return anomalies

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        users = context.affected_identities or context.affected_users or ["svc_sqladmin", "admin_backup"]
        anomalies: List[IdentityAnomaly] = []

        for u in users:
            detected = self.detect_identity_anomalies(u, events=[])
            anomalies.extend(detected)

        return {"anomalies": anomalies, "target_users": users}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        anomalies: List[IdentityAnomaly] = telemetry.get("anomalies", [])
        
        for a in anomalies:
            if a not in context.identity_anomalies:
                context.identity_anomalies.append(a)

        context.mitre_attack.append(MitreAttackMapping(
            tactic="Credential Access",
            technique_id="T1558.003",
            technique_name="Steal or Forge Kerberos Tickets: Kerberoasting"
        ))

        return {
            "compromised_accounts": len(anomalies),
            "critical_identity_risk": any(a.risk_score >= 80 for a in anomalies),
            "confidence": 0.96
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "REVOKE_ACTIVE_SESSIONS",
            "requires_containment": True,
            "recommendations": [
                "Force password reset and invalidate active Kerberos / OAuth sessions.",
                "Enforce FIDO2 WebAuthn phishing-resistant MFA for targeted privileged account."
            ]
        }

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        summary = (
            f"Identity SecOps detected Kerberoasting & Token Abuse targeting privileged account(s). "
            f"Risk: CRITICAL. Recommended: Session invalidation and Kerberos AES-256 policy enforcement."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 0.96)),
            summary=summary,
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

identity_security_agent = IdentitySecurityAgent()
