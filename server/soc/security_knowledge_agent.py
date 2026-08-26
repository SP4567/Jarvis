from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    AgentFinding,
    AgentExecutionPhase
)

class SecurityKnowledgeAgent(BaseSocAgent):
    """
    Security Knowledge / RAG Agent
    Retrieves internal security policies, incident response playbooks,
    SOP checklists, and historical incident intelligence.
    """
    def __init__(self):
        super().__init__(
            name="security_knowledge_agent",
            role_title="Security Knowledge & Playbook Specialist",
            description="Retrieves security policies, IR playbooks, NIST procedures, and organizational asset context."
        )

        self.playbooks_kb = {
            "RANSOMWARE": {
                "title": "Enterprise Ransomware Response SOP-SEC-402",
                "phases": [
                    "Immediate endpoint network isolation (Sever Layer 2/3)",
                    "Preserve memory and volatile artifacts prior to reboot",
                    "Identify patient zero via prefetch and event logs",
                    "Scan backup repositories for shadow copy deletion attempts",
                    "Initiate Active Directory krbtgt account double password reset"
                ]
            },
            "CREDENTIAL_DUMP": {
                "title": "LSASS & Kerberos Credential Theft Playbook SOP-SEC-205",
                "phases": [
                    "Identify compromised host and user identities",
                    "Revoke Kerberos TGT and active OAuth tokens",
                    "Enable Credential Guard & Remote Credential Guard on all endpoints",
                    "Force password rotation across compromised administrative group"
                ]
            },
            "C2_BEACONING": {
                "title": "Command and Control Containment Playbook SOP-SEC-310",
                "phases": [
                    "Drop outbound firewall connections to target IOCs",
                    "Sinkhole external domain at authoritative DNS servers",
                    "Extract payload strings to uncover secondary fallback C2 addresses",
                    "Inspect surrounding subnet for lateral SMB / WinRM propagation"
                ]
            }
        }

    def retrieve_playbook(self, incident_type: str) -> Dict[str, Any]:
        """Looks up procedural incident response playbook"""
        key = incident_type.upper()
        if "RANSOM" in key:
            return self.playbooks_kb["RANSOMWARE"]
        elif "CRED" in key or "LSASS" in key or "KERB" in key:
            return self.playbooks_kb["CREDENTIAL_DUMP"]
        else:
            return self.playbooks_kb["C2_BEACONING"]

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        playbook = self.retrieve_playbook(context.title or "C2_BEACONING")
        return {"playbook": playbook}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        pb = telemetry.get("playbook", {})
        return {
            "playbook_matched": pb.get("title", "Standard Incident Response Playbook"),
            "procedural_steps": pb.get("phases", []),
            "confidence": 1.0
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "ATTACH_PLAYBOOK_PROCEDURES",
            "requires_containment": False,
            "recommendations": analysis.get("procedural_steps", [])
        }

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        pb_title = analysis.get("playbook_matched", "Standard Playbook")
        summary = (
            f"Security Knowledge RAG matched incident context to approved organizational playbook: '{pb_title}'. "
            f"Provided {len(analysis.get('procedural_steps', []))} standardized containment steps."
        )
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=1.0,
            summary=summary,
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

security_knowledge_agent = SecurityKnowledgeAgent()
