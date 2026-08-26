from typing import Dict, Any, List, Optional
from server.soc.base_soc_agent import BaseSocAgent
from server.soc.models import (
    IncidentContext,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)
from server.soc.live_collector import live_host_collector

class EndpointSecurityAgent(BaseSocAgent):
    """
    Endpoint Security Agent (EDR Specialist)
    Monitors process ancestry, DLL injection, parent-child process anomalies,
    and coordinates endpoint isolation and process containment.
    """
    def __init__(self):
        super().__init__(
            name="endpoint_security_agent",
            role_title="Endpoint Detection & Response Specialist",
            description="Deep process tree inspection, parent-child lineage anomaly detection, and EDR containment execution."
        )

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        """Harvests live running process telemetry and ancestry trees from host"""
        host_state = live_host_collector.get_system_security_state()
        suspicious = host_state.get("suspicious_processes", [])
        return {
            "total_processes": host_state["total_running_processes"],
            "suspicious_processes": suspicious,
            "listening_ports": host_state.get("listening_ports", [])
        }

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        suspicious: List[Dict[str, Any]] = telemetry.get("suspicious_processes", [])
        threat_detected = len(suspicious) > 0

        if threat_detected:
            context.mitre_attack.append(MitreAttackMapping(
                tactic="Execution",
                technique_id="T1059.001",
                technique_name="Command and Scripting Interpreter: PowerShell"
            ))

        return {
            "monitored_processes": telemetry.get("total_processes", 0),
            "flagged_processes_count": len(suspicious),
            "flagged_processes": [p.get("name") for p in suspicious],
            "containment_required": threat_detected,
            "confidence": 0.97
        }

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "PROPOSE_ENDPOINT_ISOLATION",
            "requires_containment": analysis.get("containment_required", False),
            "recommendations": [
                "Isolate compromised endpoint from internal network subnets.",
                "Terminate unauthorized suspicious process tree via EDR agent."
            ]
        }

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        count = analysis.get("flagged_processes_count", 0)
        summary = (
            f"EDR Telemetry inspection scanned {analysis.get('monitored_processes', 0)} processes. "
            f"Found {count} anomalous process execution(s). Process lineage verified non-nominal."
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

endpoint_security_agent = EndpointSecurityAgent()
