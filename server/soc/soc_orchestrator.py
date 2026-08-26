import asyncio
import uuid
import time
import socket
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.models import (
    SecurityEvent,
    Tier1Decision,
    IncidentContext,
    IncidentCase,
    IncidentStatus,
    SeverityLevel
)
from server.soc.tier1_triage import tier1_triage_agent
from server.soc.tier2_responder import tier2_responder_agent
from server.soc.tier3_hunter import tier3_hunter_agent
from server.soc.threat_intel_agent import threat_intel_agent
from server.soc.detection_engineering_agent import detection_engineering_agent
from server.soc.digital_forensics_agent import digital_forensics_agent
from server.soc.malware_analysis_agent import malware_analysis_agent
from server.soc.vulnerability_agent import vulnerability_agent
from server.soc.identity_security_agent import identity_security_agent
from server.soc.endpoint_security_agent import endpoint_security_agent
from server.soc.network_security_agent import network_security_agent
from server.soc.cloud_security_agent import cloud_security_agent
from server.soc.appsec_agent import appsec_agent
from server.soc.security_knowledge_agent import security_knowledge_agent
from server.soc.compliance_reporting_agent import compliance_reporting_agent

from server.soc.case_memory import soc_case_memory
from server.soc.soc_guardrails import soc_guardrail_engine
from server.soc.live_collector import live_host_collector
from server.core.tool_registry import tool_registry

class SocAgentOrchestrator:
    """
    JARVIS Autonomous SOC Core Master Orchestration Brain
    Coordinates the 16-agent fleet across the entire incident lifecycle:
    Detection -> Triage -> CTI -> Forensics -> Response -> Detection Engineering -> Compliance
    """
    def __init__(self):
        self.hostname = socket.gethostname()
        self.is_monitoring_active = True
        self.last_audit_report: Optional[Dict[str, Any]] = None
        self.fleet_agents = {
            "tier1_triage_agent": tier1_triage_agent,
            "tier2_responder_agent": tier2_responder_agent,
            "tier3_hunter_agent": tier3_hunter_agent,
            "threat_intel_agent": threat_intel_agent,
            "detection_engineering_agent": detection_engineering_agent,
            "digital_forensics_agent": digital_forensics_agent,
            "malware_analysis_agent": malware_analysis_agent,
            "vulnerability_agent": vulnerability_agent,
            "identity_security_agent": identity_security_agent,
            "endpoint_security_agent": endpoint_security_agent,
            "network_security_agent": network_security_agent,
            "cloud_security_agent": cloud_security_agent,
            "appsec_agent": appsec_agent,
            "security_knowledge_agent": security_knowledge_agent,
            "compliance_reporting_agent": compliance_reporting_agent
        }
        self._register_soc_tools()

    def _register_soc_tools(self):
        tool_registry.register_tool(
            name="run_live_security_audit",
            func=self.run_live_security_audit,
            description="Execute a full 360-degree security audit scanning running processes, open ports, startup persistence, and Windows system logs.",
            parameters={"type": "object", "properties": {}},
            agent_name="soc_orchestrator"
        )
        tool_registry.register_tool(
            name="isolate_endpoint",
            func=self.isolate_endpoint_tool,
            description="Isolate an endpoint by severing outbound network traffic using Windows Firewall. Requires Tier 3 / Dual Authorization.",
            parameters={
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Hostname to isolate."},
                    "reason": {"type": "string", "description": "Security justification for network isolation."}
                },
                "required": ["hostname"]
            },
            agent_name="soc_orchestrator"
        )
        tool_registry.register_tool(
            name="block_firewall_ioc",
            func=self.block_firewall_ioc_tool,
            description="Add a Windows Firewall drop rule for a specific malicious IP or domain indicator of compromise.",
            parameters={
                "type": "object",
                "properties": {
                    "ioc": {"type": "string", "description": "Malicious IP or domain to block."},
                    "reason": {"type": "string", "description": "Threat reason."}
                },
                "required": ["ioc"]
            },
            agent_name="soc_orchestrator"
        )
        tool_registry.register_tool(
            name="get_soc_fleet_status",
            func=self.get_soc_fleet_status,
            description="Retrieve real-time operational status, throughput, and latency across all 16 autonomous SOC agents.",
            parameters={"type": "object", "properties": {}},
            agent_name="soc_orchestrator"
        )

    def get_soc_fleet_status(self) -> Dict[str, Any]:
        """Returns live telemetry across all 16 specialized SOC agents"""
        nodes = []
        for name, ag in self.fleet_agents.items():
            nodes.append({
                "name": ag.name,
                "role_title": ag.role_title,
                "description": ag.description,
                "execution_count": ag.execution_count,
                "last_latency_ms": ag.last_latency_ms,
                "status": "ACTIVE" if self.is_monitoring_active else "STANDBY"
            })
        return {
            "master_orchestrator": "JARVIS SOC Core Brain",
            "fleet_size": len(nodes) + 1,
            "soc_enabled": self.is_monitoring_active,
            "nodes": nodes
        }

    def set_soc_state(self, enabled: bool) -> bool:
        self.is_monitoring_active = bool(enabled)
        return self.is_monitoring_active

    def toggle_soc_state(self) -> bool:
        self.is_monitoring_active = not self.is_monitoring_active
        return self.is_monitoring_active

    def isolate_endpoint_tool(self, hostname: str, reason: str = "Manual SOC Containment") -> Dict[str, Any]:
        action_prop = soc_guardrail_engine.propose_action(
            case_id="CASE-MANUAL-ISOLATION",
            action_name="isolate_endpoint",
            target={"hostname": hostname, "criticality": "high"},
            reason=reason,
            evidence=["Manual operator containment dispatch"],
            confidence=0.98,
            expected_impact="Host network severed from external subnets.",
            rollback_strategy=""
        )
        return {"action_id": action_prop.action_id, "status": "PROPOSED_PENDING_CONFIRMATION", "target": hostname}

    def block_firewall_ioc_tool(self, ioc: str, reason: str = "Malicious C2 Address") -> Dict[str, Any]:
        action_prop = soc_guardrail_engine.propose_action(
            case_id="CASE-MANUAL-IOC-BLOCK",
            action_name="block_firewall_ioc",
            target={"ioc": ioc, "type": "IP"},
            reason=reason,
            evidence=["Manual operator IOC block dispatch"],
            confidence=0.95,
            expected_impact=f"Outbound network drop rule created for {ioc}.",
            rollback_strategy=""
        )
        return {"action_id": action_prop.action_id, "status": "EXECUTED", "target": ioc}

    def run_live_security_audit(self) -> Dict[str, Any]:
        """Executes a 360-degree security audit scanning live processes, open sockets, startup keys, and event logs"""
        if not self.is_monitoring_active:
            return {
                "audit_id": "AUDIT-STANDBY",
                "hostname": self.hostname,
                "soc_enabled": False,
                "timestamp": datetime.now().isoformat(),
                "host_risk_score": 0,
                "total_active_processes": 0,
                "suspicious_process_count": 0,
                "suspicious_processes": [],
                "active_network_connections": 0,
                "listening_ports_count": 0,
                "listening_ports": [],
                "startup_persistence_items": [],
                "recent_system_logs": [],
                "incidents_triaged": [],
                "status": "SOC_DISABLED_STANDBY"
            }

        audit_state = live_host_collector.get_system_security_state()
        suspicious_procs = audit_state.get("suspicious_processes", [])
        listening_ports = audit_state.get("listening_ports", [])
        startup_items = audit_state.get("startup_items", [])
        event_logs = audit_state.get("recent_event_logs", [])

        created_cases = []
        for proc in suspicious_procs:
            raw_event = {
                "source_type": "LIVE_EDR_PROCESS_MONITOR",
                "hostname": self.hostname,
                "process_name": proc.get("name"),
                "command_line": proc.get("cmdline"),
                "user_identity": proc.get("username"),
                "raw_payload": proc
            }
            case = self.process_incoming_security_event(raw_event)
            if case:
                created_cases.append(case.case_id)

        host_risk_score = 10
        if suspicious_procs:
            host_risk_score += len(suspicious_procs) * 25
        if len(listening_ports) > 30:
            host_risk_score += 15
        host_risk_score = min(100, host_risk_score)

        report = {
            "audit_id": f"AUDIT-{uuid.uuid4().hex[:6].upper()}",
            "hostname": self.hostname,
            "soc_enabled": self.is_monitoring_active,
            "timestamp": datetime.now().isoformat(),
            "host_risk_score": host_risk_score,
            "total_active_processes": audit_state["total_running_processes"],
            "suspicious_process_count": len(suspicious_procs),
            "suspicious_processes": suspicious_procs,
            "active_network_connections": audit_state["active_connections_count"],
            "listening_ports_count": len(listening_ports),
            "listening_ports": listening_ports[:10],
            "startup_persistence_items": startup_items,
            "recent_system_logs": event_logs,
            "incidents_triaged": created_cases,
            "status": "ELEVATED_RISK" if host_risk_score >= 50 else "SECURE_OPTIMAL"
        }
        self.last_audit_report = report
        return report

    def process_incoming_security_event(self, raw_event_data: Dict[str, Any]) -> Optional[IncidentContext]:
        """
        Executes the End-to-End Autonomous Multi-Agent Investigation Pipeline:
        1. Ingest & Normalize (Tier 1)
        2. Triage & Risk Score (Tier 1)
        3. Incident Response & Timeline (Tier 2)
        4. Threat Intelligence Correlation (CTI Specialist)
        5. Threat Hunting & Script Deobfuscation (Tier 3 SME)
        6. Digital Forensics Artifact Acquisition (DFIR)
        7. Malware Reverse Engineering (Malware Analyst)
        8. Detection Engineering (Sigma Rule synthesis)
        9. Vulnerability Impact Analysis (Vulnerability Specialist)
        10. Identity & Access Analysis (IAM Specialist)
        11. Endpoint & Network Telemetry Verification (EDR/NDR)
        12. Cloud & AppSec Verification (CSPM / WAF)
        13. Playbook Retrieval (Knowledge Agent)
        14. Executive & Technical Reporting with Compliance Control Mapping (Compliance Specialist)
        """
        if not self.is_monitoring_active:
            return None

        # Step 1: Normalize & Triage
        event = tier1_triage_agent.normalize_event(raw_event_data)
        triage_decision: Tier1Decision = tier1_triage_agent.triage_event(event)

        if not triage_decision.escalate_to_tier2 and triage_decision.severity == SeverityLevel.P4:
            return None

        case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"

        # Step 2: Initialize Shared Incident Context via Tier 2 Responder
        context: IncidentContext = tier2_responder_agent.investigate_incident(triage_decision, case_id)

        # Step 3: Run Threat Hunting on elevated incidents
        if triage_decision.severity in [SeverityLevel.P0, SeverityLevel.P1, SeverityLevel.P2]:
            context = tier3_hunter_agent.conduct_threat_hunt(context)

        # Step 4: Synchronous execution of specialized domain findings
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except Exception:
            pass

        # Execute remaining agent lifecycles
        async def run_fleet_investigation():
            await threat_intel_agent.execute_lifecycle(context)
            await digital_forensics_agent.execute_lifecycle(context)
            await malware_analysis_agent.execute_lifecycle(context)
            await detection_engineering_agent.execute_lifecycle(context)
            await vulnerability_agent.execute_lifecycle(context)
            await identity_security_agent.execute_lifecycle(context)
            await endpoint_security_agent.execute_lifecycle(context)
            await network_security_agent.execute_lifecycle(context)
            await cloud_security_agent.execute_lifecycle(context)
            await appsec_agent.execute_lifecycle(context)
            await security_knowledge_agent.execute_lifecycle(context)
            await compliance_reporting_agent.execute_lifecycle(context)

        if loop and loop.is_running():
            asyncio.create_task(run_fleet_investigation())
        else:
            asyncio.run(run_fleet_investigation())

        # Save to SQLite case memory
        soc_case_memory.save_case(context)
        return context

    def get_live_security_telemetry(self) -> Dict[str, Any]:
        """Returns live host defense telemetry for the HUD and API"""
        if not self.is_monitoring_active:
            return {
                "hostname": self.hostname,
                "soc_enabled": False,
                "soc_status": "STANDBY",
                "timestamp": datetime.now().isoformat(),
                "total_processes": 0,
                "active_sockets": 0,
                "listening_ports_count": 0,
                "suspicious_processes_count": 0,
                "suspicious_processes": [],
                "startup_persistence_count": 0,
                "recent_event_logs": [],
                "metrics": soc_case_memory.get_metrics(),
                "pending_containment": [],
                "fleet_status": self.get_soc_fleet_status()
            }

        state = live_host_collector.get_system_security_state()
        metrics = soc_case_memory.get_metrics()
        pending_containment = soc_guardrail_engine.get_pending_actions()
        
        return {
            "hostname": self.hostname,
            "soc_enabled": self.is_monitoring_active,
            "soc_status": "ACTIVE" if self.is_monitoring_active else "STANDBY",
            "timestamp": datetime.now().isoformat(),
            "total_processes": state["total_running_processes"],
            "active_sockets": state["active_connections_count"],
            "listening_ports_count": state["listening_ports_count"],
            "suspicious_processes_count": state["suspicious_process_count"],
            "suspicious_processes": state["suspicious_processes"],
            "startup_persistence_count": state["startup_persistence_count"],
            "recent_event_logs": state["recent_event_logs"],
            "metrics": metrics,
            "pending_containment": pending_containment,
            "fleet_status": self.get_soc_fleet_status()
        }

    def get_security_posture_summary(self) -> str:
        """Generates concise spoken executive briefing based on REAL host defense data"""
        if not self.is_monitoring_active:
            return (
                f"Autonomous SOC Security Monitoring is currently switched OFF in standby mode on {self.hostname}, Sir. "
                f"Perimeter defense agents and continuous telemetry ingestion are paused."
            )

        state = live_host_collector.get_system_security_state()
        cases = soc_case_memory.list_cases(limit=10)
        active_cases = [c for c in cases if c.status != IncidentStatus.CLOSED]
        pending_approvals = soc_guardrail_engine.get_pending_actions()

        if active_cases:
            top_c = active_cases[0]
            host = top_c.affected_assets[0].get("hostname", self.hostname) if top_c.affected_assets else self.hostname
            return (
                f"Warning, Sir. Live security monitoring detected {len(active_cases)} active incident on {self.hostname}. "
                f"Most critical is {top_c.case_id} ({top_c.title}) with a risk score of {top_c.risk_score}. "
                f"There are {len(pending_approvals)} containment actions pending your authorization across the 16-agent fleet."
            )
        else:
            return (
                f"Enterprise SecOps Fleet is fully ACTIVE and nominal on {self.hostname}, Sir. "
                f"All 16 security subagents report nominal baseline across {state['total_running_processes']} processes and {state['active_connections_count']} sockets."
            )

soc_orchestrator = SocAgentOrchestrator()
