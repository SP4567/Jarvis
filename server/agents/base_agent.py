import asyncio
import time
import uuid
from typing import Dict, Any, Callable, List, Optional
from server.core.guardrails import guardrail_engine
from server.core.models import (
    AgentStatus,
    AgentThought,
    ExecutionLifecycleState,
    TaskPlan,
    PlanStep,
    VerificationResult,
    RecoveryAction,
    CommandResponse
)

class BaseAgent:
    """
    JARVIS Autonomous Base Agent 3.0
    Equipped with End-to-End Problem Solving:
    Query Understanding -> Decomposition & Planning -> Execution -> Continuous Verification -> Self-Healing Recovery -> Resolution
    """
    def __init__(self, name: str, display_name: str, description: str):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: List[Dict[str, Any]] = []
        self.status: str = AgentStatus.IDLE.value
        self.current_task: Optional[str] = None
        self.execution_count: int = 0
        self.last_latency_ms: float = 0.0
        self.recovery_count: int = 0
        self.last_verification: Optional[VerificationResult] = None
        self.execution_metrics: Dict[str, int] = {
            "tasks_solved": 0,
            "verifications_passed": 0,
            "recoveries_attempted": 0
        }

    def register_tool(self, name: str, func: Callable, schema: Dict[str, Any]):
        """Registers a callable tool function along with its JSON schema"""
        self.tools[name] = func
        self.tool_schemas.append(schema)

    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        description: str = "",
        session_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Executes a registered tool after passing through the Security Guardrail Interlock.
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found on agent '{self.name}'."
            }

        start_time = time.time()
        self.status = AgentStatus.GUARDRAIL_CHECK.value
        self.current_task = f"Verifying {tool_name}"

        # 1. Guardrail Verification & Interlock
        is_allowed, reason, action_id = await guardrail_engine.verify_and_authorize(
            agent_name=self.name,
            action_name=tool_name,
            params=params,
            description=description or f"{self.display_name} requesting {tool_name}"
        )

        if not is_allowed:
            self.status = AgentStatus.IDLE.value
            self.current_task = None
            return {
                "success": False,
                "action_id": action_id,
                "error": reason,
                "guardrail_blocked": True
            }

        # 2. Execute Tool
        self.status = AgentStatus.EXECUTING.value
        self.current_task = f"Executing {tool_name}"
        try:
            func = self.tools[tool_name]
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = await asyncio.to_thread(func, **params)

            elapsed_ms = (time.time() - start_time) * 1000.0
            self.execution_count += 1
            self.last_latency_ms = round(elapsed_ms, 2)
            self.status = AgentStatus.IDLE.value
            self.current_task = None

            return {
                "success": True,
                "action_id": action_id,
                "result": result,
                "latency_ms": self.last_latency_ms
            }
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000.0
            self.status = AgentStatus.IDLE.value
            self.current_task = None
            return {
                "success": False,
                "action_id": action_id,
                "error": f"Error executing {tool_name}: {str(e)}",
                "latency_ms": round(elapsed_ms, 2)
            }

    async def verify_tool_execution(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Dict[str, Any]
    ) -> VerificationResult:
        """
        Self-Verification Hook: Verifies post-condition state after tool execution.
        Subclasses can override for domain-specific state assertion.
        """
        if not result.get("success"):
            return VerificationResult(
                verified=False,
                verdict=f"Execution failed: {result.get('error', 'Unknown error')}",
                details={"tool": tool_name, "error": result.get("error")}
            )

        # Base generic verification
        return VerificationResult(
            verified=True,
            verdict=f"Tool '{tool_name}' executed and output validated nominal.",
            details={"tool": tool_name, "has_output": result.get("result") is not None}
        )

    async def attempt_recovery(
        self,
        tool_name: str,
        params: Dict[str, Any],
        error_msg: str,
        session_id: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Self-Healing / Recovery Hook: If a tool fails, attempts alternative approach or retry.
        """
        # Base implementation: can be overridden by specialized agents
        return None

    async def solve_task(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> CommandResponse:
        """
        End-to-End Autonomous Execution Loop:
        1. Query Understanding & Planning
        2. Sequential Step Execution
        3. Continuous Verification
        4. Self-Healing Error Recovery
        5. Formatted Resolution
        """
        start_time = time.time()
        self.status = AgentStatus.PLANNING.value
        self.current_task = f"Planning: {query[:40]}"

        plan_id = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
        thoughts: List[AgentThought] = []
        actions_taken: List[Dict[str, Any]] = []
        recovery_actions: List[RecoveryAction] = []

        # Formulate initial plan
        plan = await self.formulate_plan(query, context)
        
        step_thought = AgentThought(
            step=1,
            agent_name=self.display_name,
            thought=f"Formulated {len(plan.steps)}-step execution plan for '{query}'",
            state=ExecutionLifecycleState.PLANNED
        )
        thoughts.append(step_thought)
        if thought_callback:
            thought_callback(step_thought)

        final_text = ""
        overall_success = True

        for step in plan.steps:
            if not step.tool_name or step.tool_name not in self.tools:
                continue

            self.status = AgentStatus.EXECUTING.value
            self.current_task = f"Step {step.step_number}: {step.description}"

            t_entry = AgentThought(
                step=step.step_number + 1,
                agent_name=self.display_name,
                thought=f"Executing {step.tool_name} with params {step.params}",
                tool_name=step.tool_name,
                tool_params=step.params,
                state=ExecutionLifecycleState.ATTEMPTING
            )
            thoughts.append(t_entry)
            if thought_callback:
                thought_callback(t_entry)

            # 1. Execute
            res = await self.execute_tool(step.tool_name, step.params, description=step.description, session_id=session_id)
            actions_taken.append({"tool": step.tool_name, "params": step.params, "result": res.get("result") or res.get("error")})

            # 2. Continuous Verification
            self.status = AgentStatus.VERIFYING.value
            verif = await self.verify_tool_execution(step.tool_name, step.params, res)
            self.last_verification = verif
            step.verification = verif.model_dump()

            if not verif.verified or not res.get("success"):
                # 3. Self-Healing & Recovery
                self.status = AgentStatus.RECOVERING.value
                self.recovery_count += 1
                rec_res = await self.attempt_recovery(step.tool_name, step.params, str(res.get("error")), session_id=session_id)
                if rec_res and rec_res.get("success"):
                    recovery_actions.append(RecoveryAction(
                        original_tool=step.tool_name,
                        error_encountered=str(res.get("error")),
                        recovery_strategy="self_heal_fallback",
                        recovered=True
                    ))
                    res = rec_res
                    actions_taken.append({"tool": f"{step.tool_name}_recovered", "result": rec_res.get("result")})
                else:
                    recovery_actions.append(RecoveryAction(
                        original_tool=step.tool_name,
                        error_encountered=str(res.get("error")),
                        recovery_strategy="escalate",
                        recovered=False
                    ))
                    overall_success = False

            step.status = ExecutionLifecycleState.VERIFIED if (res.get("success") and verif.verified) else ExecutionLifecycleState.FAILED
            step.result = res.get("result")
            step.error = res.get("error")

        # 4. Formulate Final Response
        if overall_success:
            self.execution_metrics["tasks_solved"] += 1
            self.execution_count += 1

        self.status = AgentStatus.COMPLETED.value if overall_success else AgentStatus.ERROR.value
        final_text = self.format_resolution(query, plan, actions_taken)
        self.status = AgentStatus.IDLE.value
        self.current_task = None

        return CommandResponse(
            success=overall_success,
            text=final_text,
            agent_used=self.name,
            actions=actions_taken,
            thoughts=thoughts,
            plan=plan,
            task_plan=plan,
            verification=self.last_verification,
            recovery_actions=recovery_actions,
            latency_ms=round((time.time() - start_time) * 1000.0, 2)
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """
        Decomposes query into execution steps. Subclasses can override for domain reasoning.
        """
        plan_id = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
        return TaskPlan(
            plan_id=plan_id,
            goal=query,
            initiating_agent=self.name,
            steps=[]
        )

    def format_resolution(self, query: str, plan: TaskPlan, actions: List[Dict[str, Any]]) -> str:
        """
        Formats natural language resolution text for the user.
        """
        return f"Directive '{query}' processed by {self.display_name}, Sir."

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live status of this agent for HUD dashboard"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "status": self.status,
            "current_task": self.current_task,
            "execution_count": self.execution_count,
            "recovery_count": self.recovery_count,
            "last_latency_ms": self.last_latency_ms,
            "tools_count": len(self.tools),
            "tools": list(self.tools.keys())
        }
