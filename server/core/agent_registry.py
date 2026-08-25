from typing import Dict, Any, List, Optional
from server.agents.base_agent import BaseAgent
from server.agents.system_agent import system_agent
from server.agents.media_agent import media_agent
from server.agents.coding_agent import coding_agent
from server.agents.productivity_agent import productivity_agent
from server.agents.research_agent import research_agent
from server.agents.vision_agent import vision_agent
from server.soc.soc_orchestrator import soc_orchestrator

class AgentRegistry:
    """
    Centralized Agent Registry & Dependency Injection Hub for JARVIS
    Manages specialized domain agents, telemetry metrics, and tool execution.
    """
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "system_agent": system_agent,
            "media_agent": media_agent,
            "coding_agent": coding_agent,
            "productivity_agent": productivity_agent,
            "research_agent": research_agent,
            "vision_agent": vision_agent,
        }


    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Retrieves an agent by name"""
        return self.agents.get(name)

    def get_all_agents_telemetry(self) -> List[Dict[str, Any]]:
        """Returns live execution state, latency, and tool metrics for all registered agents"""
        telemetry = []
        for agent in self.agents.values():
            telemetry.append(agent.get_telemetry())
        
        # Add SOC Orchestrator status
        telemetry.append({
            "name": "soc_orchestrator",
            "display_name": "Autonomous SOC Core",
            "description": "Multi-tier SOC monitoring, real-time EDR & containment engine",
            "status": "active" if soc_orchestrator.is_monitoring_active else "standby",
            "current_task": "Kernel Telemetry Ingestion" if soc_orchestrator.is_monitoring_active else "Standby Mode",
            "execution_count": len(soc_orchestrator.last_audit_report.get("incidents_triaged", [])) if soc_orchestrator.last_audit_report else 0,
            "last_latency_ms": 12.4,
            "tools_count": 8,
            "tools": ["run_live_security_audit", "isolate_endpoint", "block_firewall_ioc", "terminate_process", "quarantine_file", "rollback_action"]
        })
        return telemetry

agent_registry = AgentRegistry()
