import time
from typing import Dict, Any, Callable, List, Optional
from server.core.guardrails import guardrail_engine

class BaseAgent:
    """
    Base Agent Interface with Tool Registration, Guardrail Verification, and Telemetry
    """
    def __init__(self, name: str, display_name: str, description: str):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.status: str = "idle"  # idle | thinking | executing | guardrail_check
        self.current_task: Optional[str] = None
        self.execution_count: int = 0
        self.last_latency_ms: float = 0.0

    def register_tool(self, name: str, func: Callable, schema: Dict[str, Any]):
        """Registers a callable tool function along with its JSON schema for LLM calling"""
        self.tools[name] = func
        self.tool_schemas.append(schema)

    async def execute_tool(self, tool_name: str, params: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        """
        Executes a registered tool after passing through the 3-Tier Security Guardrail.
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found on agent '{self.name}'."
            }

        start_time = time.time()
        self.status = "guardrail_check"
        self.current_task = f"Verifying {tool_name}"

        # 1. Guardrail Verification & Interlock
        is_allowed, reason, action_id = await guardrail_engine.verify_and_authorize(
            agent_name=self.name,
            action_name=tool_name,
            params=params,
            description=description or f"{self.display_name} requesting {tool_name}"
        )

        if not is_allowed:
            self.status = "idle"
            self.current_task = None
            return {
                "success": False,
                "action_id": action_id,
                "error": reason,
                "guardrail_blocked": True
            }

        # 2. Execute Tool
        self.status = "executing"
        self.current_task = f"Executing {tool_name}"
        try:
            func = self.tools[tool_name]
            import asyncio
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = func(**params)

            elapsed_ms = (time.time() - start_time) * 1000.0
            self.execution_count += 1
            self.last_latency_ms = round(elapsed_ms, 2)
            self.status = "idle"
            self.current_task = None

            return {
                "success": True,
                "action_id": action_id,
                "result": result,
                "latency_ms": self.last_latency_ms
            }
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.status = "idle"
            self.current_task = None
            return {
                "success": False,
                "action_id": action_id,
                "error": f"Error executing {tool_name}: {str(e)}",
                "latency_ms": round(elapsed_ms, 2)
            }

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live status of this agent for HUD dashboard"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "status": self.status,
            "current_task": self.current_task,
            "execution_count": self.execution_count,
            "last_latency_ms": self.last_latency_ms,
            "tools_count": len(self.tools)
        }
