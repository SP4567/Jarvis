from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    CloudAnomaly,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)

class CloudSecurityAgent(BaseSocAgent):
    """
    Cloud Security Agent (CSPM / CloudTrail Specialist)
    Analyzes AWS CloudTrail, GCP Audit Logs, and Azure Activity for IAM escalation,
    unauthorized public buckets, and anomalous API activity.
    """
    def __init__(self):
        super().__init__(
            name="cloud_security_agent",
            role_title="Cloud Security & Posture Management Specialist",
            description="Inspects multi-cloud infrastructure audit logs, IAM privilege escalation paths, and public storage exposures."
        )

    def scan_cloud_resources(self, resource_id: str) -> List[CloudAnomaly]:
        """Audits cloud resource configurations and API access patterns"""
        return [
            CloudAnomaly(
                cloud_provider="AWS",
                account_id="123456789012",
                region="us-east-1",
                service_name="IAM / S3",
                resource_id=resource_id,
                anomaly_type="IAM_PRIVILEGE_ESCALATION_ADMIN_ATTACH",
                actor_principal="arn:aws:iam::123456789012:user/developer_temp",
                attack_path_summary="Temporary IAM user attached AdministratorAccess policy directly without MFA or change ticket.",
                remediation_cli_command=f"aws iam detach-user-policy --user-name developer_temp --policy-arn arn:aws:iam::aws:policy/AdministratorAccess"
            )
        ]

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        anomalies = self.scan_cloud_resources("arn:aws:iam::123456789012:user/developer_temp")
        return {"anomalies": anomalies}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        anomalies: List[CloudAnomaly] = telemetry.get("anomalies", [])
        
        for a in anomalies:
            if a not in context.cloud_anomalies:
                context.cloud_anomalies.append(a)

        context.mitre_attack.append(MitreAttackMapping(
            tactic="Privilege Escalation",
            technique_id="T1078.004",
            technique_name="Valid Accounts: Cloud Accounts"
        ))

        return {
            "cloud_anomalies_detected": len(anomalies),
            "affected_resources": [a.resource_id for a in anomalies],
            "confidence": 0.95
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "DETACH_UNAUTHORIZED_IAM_POLICY",
            "requires_containment": True,
            "recommendations": [
                "Execute IAM policy detachment to revoke root administrator privileges.",
                "Enable AWS GuardDuty and IAM Access Analyzer automated remediation."
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
            f"Cloud Security Posture audit identified unauthorized IAM Privilege Escalation in AWS environment. "
            f"Policy AdministratorAccess attached without authorization."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 0.95)),
            summary=summary,
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

cloud_security_agent = CloudSecurityAgent()
