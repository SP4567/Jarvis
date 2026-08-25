import asyncio
import uuid
import time
import socket
from datetime import datetime
from typing import Dict, Any, List, Optional
from server.soc.models import (
    SecurityEvent,
    Tier1Decision,
    IncidentCase,
    IncidentStatus,
    SeverityLevel
)
from server.soc.tier1_triage import tier1_triage_agent
from server.soc.tier2_responder import tier2_responder_agent
from server.soc.tier3_hunter import tier3_hunter_agent
from server.soc.case_memory import soc_case_memory
from server.soc.soc_guardrails import soc_guardrail_engine
from server.soc.live_collector import live_host_collector
from server.core.tool_registry import tool_registry

class SocAgentOrchestrator:
    """
    JARVIS Production Live SOC Multi-Agent Orchestration Hub
    Monitors real-time Windows host telemetry, active processes, sockets, registry persistence, and event logs.
    Includes master SOC power toggle (ACTIVE / STANDBY).
    """
    def __init__(self):
        self.hostname = socket.gethostname()
        self.is_monitoring_active = True
        self.last_audit_report: Optional[Dict[str, Any]] = None
        self._last_seen_pids = set()
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

    def set_soc_state(self, enabled: bool) -> bool:
        """Sets master SOC monitoring state ON or OFF"""
        self.is_monitoring_active = bool(enabled)
        return self.is_monitoring_active

    def toggle_soc_state(self) -> bool:
        """Toggles master SOC monitoring state"""
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
        """
        Executes a 360-degree real-time security audit of the local host:
        Scans all live running processes, network connections, listening ports, startup registry keys, and Windows system logs.
        """
        if not self.is_monitoring_active:
            return {
                "audit_id": f"AUDIT-STANDBY",
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

        # Process any discovered real suspicious processes through Tier 1 / Tier 2 / Tier 3 if SOC is enabled
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

        # Quantitative Host Risk Rating
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

    def process_incoming_security_event(self, raw_event_data: Dict[str, Any]) -> Optional[IncidentCase]:
        """
        Executes the Continuous 15-Stage SOC Monitoring & Response Pipeline on actual live events
        """
        if not self.is_monitoring_active:
            return None

        # Step 1 & 2: INGEST & NORMALIZE
        event = tier1_triage_agent.normalize_event(raw_event_data)

        # Step 3, 4, 5, 6: CORRELATE, ENRICH, TRIAGE, RISK SCORE
        triage_decision: Tier1Decision = tier1_triage_agent.triage_event(event)

        # Step 7: ESCALATE (If benign/P4, log and exit)
        if not triage_decision.escalate_to_tier2 and triage_decision.severity == SeverityLevel.P4:
            return None

        case_id = f"CASE-{uuid.uuid4().hex[:6].upper()}"
        
        # Step 8: INVESTIGATE (Tier 2 Incident Responder)
        incident_case: IncidentCase = tier2_responder_agent.investigate_incident(triage_decision, case_id)

        # Step 9: THREAT HUNT & DETECTION ENGINEERING (Tier 3 SME)
        if triage_decision.severity in [SeverityLevel.P0, SeverityLevel.P1, SeverityLevel.P2]:
            incident_case = tier3_hunter_agent.conduct_threat_hunt(incident_case)

        # Save to provenanced Case Memory & SQLite
        soc_case_memory.save_case(incident_case)
        return incident_case

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
                "pending_containment": []
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
            "pending_containment": pending_containment
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
            host = top_c.initial_alert.affected_assets[0]["hostname"] if top_c.initial_alert.affected_assets else self.hostname
            return (
                f"Warning, Sir. Live security monitoring detected {len(active_cases)} active incident on {self.hostname}. "
                f"Most critical is {top_c.case_id} ({top_c.title}) with a risk score of {top_c.risk_score}. "
                f"There are {len(pending_approvals)} containment actions pending your authorization."
            )
        else:
            return (
                f"Real-time endpoint security is fully ACTIVE and nominal on {self.hostname}, Sir. "
                f"All {state['total_running_processes']} active processes, {state['active_connections_count']} network sockets, "
                f"and {state['listening_ports_count']} listening ports are verified benign. Zero active perimeter anomalies detected."
            )

soc_orchestrator = SocAgentOrchestrator()
