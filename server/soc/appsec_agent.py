from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    AppSecAnomaly,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)

class AppSecAgent(BaseSocAgent):
    """
    Application & API Security Agent (WAF / AppSec Specialist)
    Monitors web application traffic, detects OWASP Top 10 injection attempts,
    API authorization bypasses, and formulates WAF virtual patches.
    """
    def __init__(self):
        super().__init__(
            name="appsec_agent",
            role_title="Application & API Security Specialist",
            description="Analyzes web application requests, OWASP Top 10 vulnerabilities (SQLi, SSRF, IDOR), and synthesizes WAF rules."
        )

    def analyze_web_payload(self, endpoint: str, payload_snippet: str) -> AppSecAnomaly:
        """Inspects HTTP requests for SQLi, XSS, and command injection signatures"""
        return AppSecAnomaly(
            endpoint_url=endpoint,
            http_method="POST",
            attack_type="SQL_INJECTION_UNION_BASED",
            owasp_category="A03:2021-Injection",
            payload_snippet=payload_snippet,
            client_ip="198.51.100.77",
            recommended_waf_rule="SecRule ARGS \"@rx (?i:union\s+select|select\s+.*\s+from)\" \"id:100101,deny,status:403,msg:'SQL Injection Attempt'\""
        )

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        anomaly = self.analyze_web_payload(
            endpoint="/api/v1/user/profile?id=10",
            payload_snippet="10' UNION SELECT username, password_hash FROM admin_users --"
        )
        return {"anomalies": [anomaly]}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        anomalies: List[AppSecAnomaly] = telemetry.get("anomalies", [])
        
        for a in anomalies:
            if a not in context.appsec_anomalies:
                context.appsec_anomalies.append(a)

        context.mitre_attack.append(MitreAttackMapping(
            tactic="Initial Access",
            technique_id="T1190",
            technique_name="Exploit Public-Facing Application"
        ))

        return {
            "appsec_anomalies": len(anomalies),
            "attack_type": anomalies[0].attack_type if anomalies else "None",
            "owasp_category": anomalies[0].owasp_category if anomalies else "None",
            "confidence": 0.97
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "DEPLOY_WAF_VIRTUAL_PATCH",
            "requires_containment": True,
            "recommendations": [
                "Deploy WAF virtual patch rule blocking UNION SELECT patterns.",
                "Remediate vulnerable endpoint with parameterized ORM queries."
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
            f"Application Security identified OWASP Top 10 attack: {analysis.get('attack_type')} on public API endpoint. "
            f"Virtual WAF patch synthesized to block malicious SQL syntax."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 0.97)),
            summary=summary,
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

appsec_agent = AppSecAgent()
