import asyncio
import time
from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel, Field

from server.core.models import ToolCallResult, AgentStatus
from server.core.guardrails import guardrail_engine

class RegisteredTool(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    agent_name: str
    is_async: bool = False
    timeout_seconds: int = 20

class ToolRegistry:
    """
    Centralized Enterprise Tool Registry & Interlock Hub
    Manages all callable functions across subagents, generates Gemini function calling schemas,
    and executes tools through the 3-Tier Security Guardrail.
    """
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, RegisteredTool] = {}
        self._agent_tools: Dict[str, List[str]] = {}

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        agent_name: str,
        timeout_seconds: int = 20
    ):
        """Registers a callable tool function along with its JSON schema and ownership"""
        self._tools[name] = func
        is_async = asyncio.iscoroutinefunction(func)

        # Normalize schema if wrapped in OpenAI/Gemini envelope
        clean_params = dict(parameters) if parameters else {"type": "object", "properties": {}}
        if "parameters" in clean_params and isinstance(clean_params["parameters"], dict):
            clean_params = clean_params["parameters"]
        if "name" in clean_params and "properties" in clean_params:
            clean_params = {k: v for k, v in clean_params.items() if k not in ["name", "description"]}
        if "type" not in clean_params:
            clean_params["type"] = "object"
        if "properties" not in clean_params:
            clean_params["properties"] = {}
        
        reg = RegisteredTool(
            name=name,
            description=description,
            parameters_schema=clean_params,
            agent_name=agent_name,
            is_async=is_async,
            timeout_seconds=timeout_seconds
        )
        self._metadata[name] = reg

        
        if agent_name not in self._agent_tools:
            self._agent_tools[agent_name] = []
        if name not in self._agent_tools[agent_name]:
            self._agent_tools[agent_name].append(name)

    def get_tool_metadata(self, name: str) -> Optional[RegisteredTool]:
        return self._metadata.get(name)

    def list_all_tools(self) -> List[RegisteredTool]:
        return list(self._metadata.values())

    def get_gemini_tool_declarations(self) -> List[Dict[str, Any]]:
        """Formats all registered tools for Gemini Function Calling SDK"""
        declarations = []
        for meta in self._metadata.values():
            declarations.append({
                "name": meta.name,
                "description": meta.description,
                "parameters": meta.parameters_schema
            })
        return declarations

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        description: str = "",
        session_id: str = "default"
    ) -> ToolCallResult:
        """
        Executes a tool with 3-tier guardrail authorization, timeout enforcement,
        and thread offloading for synchronous blocking functions.
        """
        if tool_name not in self._tools:
            return ToolCallResult(
                success=False,
                error=f"Tool '{tool_name}' is not registered in the system ToolRegistry."
            )

        meta = self._metadata[tool_name]
        start_time = time.time()

        # 1. Guardrail Authorization & Interlock
        is_allowed, reason, action_id = await guardrail_engine.verify_and_authorize(
            agent_name=meta.agent_name,
            action_name=tool_name,
            params=params,
            description=description or f"{meta.agent_name} executing {tool_name}"
        )

        if not is_allowed:
            return ToolCallResult(
                success=False,
                action_id=action_id,
                error=reason,
                guardrail_blocked=True,
                latency_ms=round((time.time() - start_time) * 1000.0, 2)
            )

        # 2. Tool Execution with Timeout & Thread Offload
        func = self._tools[tool_name]
        try:
            if meta.is_async:
                result = await asyncio.wait_for(func(**params), timeout=meta.timeout_seconds)
            else:
                # Offload blocking synchronous OS / subprocess calls to worker thread
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, **params),
                    timeout=meta.timeout_seconds
                )

            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
            
            # Log episodic action asynchronously
            from server.core.smart_memory import smart_memory
            asyncio.create_task(smart_memory.log_action_execution(
                action_id=action_id or f"ACT-{int(time.time())}",
                agent_name=meta.agent_name,
                tool_name=tool_name,
                params=params,
                result=result,
                latency_ms=elapsed_ms,
                session_id=session_id
            ))

            return ToolCallResult(
                success=True,
                action_id=action_id,
                result=result,
                latency_ms=elapsed_ms
            )
        except asyncio.TimeoutError:
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
            return ToolCallResult(
                success=False,
                action_id=action_id,
                error=f"Tool '{tool_name}' execution timed out after {meta.timeout_seconds}s.",
                latency_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
            return ToolCallResult(
                success=False,
                action_id=action_id,
                error=f"Execution error in {tool_name}: {str(e)}",
                latency_ms=elapsed_ms
            )

tool_registry = ToolRegistry()
