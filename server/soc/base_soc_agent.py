import time
import uuid
from typing import Dict, Any, List, Optional
from server.soc.models import (
    IncidentContext,
    AgentFinding,
    AgentExecutionPhase,
    MitreAttackMapping
)

class BaseSocAgent:
    """
    Universal SOC Autonomous Agent Base Class
    Implements the 11-Stage Security Execution Contract:
    RECEIVE -> UNDERSTAND -> PLAN -> COLLECT -> ANALYZE -> DECIDE -> ACT -> VERIFY -> RECOVER -> REPORT -> ESCALATE
    """
    def __init__(self, name: str, role_title: str, description: str):
        self.name = name
        self.role_title = role_title
        self.description = description
        self.execution_count: int = 0
        self.last_latency_ms: float = 0.0
        self.findings_count: int = 0

    async def execute_lifecycle(
        self,
        context: IncidentContext,
        parameters: Optional[Dict[str, Any]] = None
    ) -> AgentFinding:
        """Executes the full 11-stage autonomous security lifecycle"""
        start_time = time.time()
        self.execution_count += 1
        
        # 1. RECEIVE
        received_data = self.receive(context, parameters)
        
        # 2. UNDERSTAND
        intent_and_scope = self.understand(context, received_data)
        
        # 3. PLAN
        investigation_plan = self.plan(context, intent_and_scope)
        
        # 4. COLLECT
        telemetry = await self.collect(context, investigation_plan)
        
        # 5. ANALYZE
        analysis = self.analyze(context, telemetry)
        
        # 6. DECIDE
        decision = self.decide(context, analysis)
        
        # 7. ACT
        action_results = await self.act(context, decision)
        
        # 8. VERIFY
        verification = self.verify(context, action_results)
        
        # 9. RECOVER (if verification failed)
        if not verification.get('verified', True):
            action_results = await self.recover(context, verification, decision)
        
        # 10. REPORT
        finding = self.report(context, analysis, decision, action_results)
        self.findings_count += 1
        self.last_latency_ms = round((time.time() - start_time) * 1000.0, 2)
        
        # 11. ESCALATE (if criteria met)
        self.escalate(context, finding)
        
        # Append structured finding to shared incident context
        context.agent_findings[self.name] = finding
        return finding

    def receive(self, context: IncidentContext, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return parameters or {}

    def understand(self, context: IncidentContext, received_data: Dict[str, Any]) -> Dict[str, Any]:
        cid = context.incident_id or context.case_id
        return {"scope": "standard_domain_investigation", "incident_id": cid}

    def plan(self, context: IncidentContext, intent_and_scope: Dict[str, Any]) -> List[str]:
        return ["inspect_telemetry", "correlate_threat_intel", "synthesize_finding"]

    async def collect(self, context: IncidentContext, plan: List[str]) -> Dict[str, Any]:
        return {"evidence_count": len(context.evidence_chain)}

    def analyze(self, context: IncidentContext, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        return {"risk_level": "NOMINAL", "confidence": 1.0}

    def decide(self, context: IncidentContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        return {"action": "LOG_FINDING", "requires_containment": False}

    async def act(self, context: IncidentContext, decision: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "executed": decision.get("action")}

    def verify(self, context: IncidentContext, action_results: Dict[str, Any]) -> Dict[str, Any]:
        return {"verified": True, "verdict": "Action outcome verified nominal."}

    async def recover(self, context: IncidentContext, verification: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        return {"recovered": True, "fallback_action": "LOG_AND_NOTIFY"}

    def report(
        self,
        context: IncidentContext,
        analysis: Dict[str, Any],
        decision: Dict[str, Any],
        action_results: Dict[str, Any]
    ) -> AgentFinding:
        cid = context.incident_id or context.case_id
        return AgentFinding(
            agent_name=self.name,
            role_title=self.role_title,
            phase=AgentExecutionPhase.REPORT,
            confidence=float(analysis.get("confidence", 1.0)),
            summary=f"{self.role_title} completed investigation for incident {cid}.",
            structured_data=analysis,
            recommendations=decision.get("recommendations", [])
        )

    def escalate(self, context: IncidentContext, finding: AgentFinding) -> None:
        pass
