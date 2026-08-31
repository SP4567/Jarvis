import re
import time
import asyncio
from typing import Dict, Any, List, Optional, Callable

from server.config import settings
from server.core.models import (
    CommandResponse, AgentThought, TaskPlan, PlanStep, VerificationResult,
    DAGTaskPlan, SynthesizedTool, VisionAnalysisResult
)
from server.core.smart_memory import smart_memory
from server.core.guardrails import guardrail_engine
from server.core.intent_classifier import intent_engine, IntentCategory, IntentResult
from server.core.tool_registry import tool_registry
from server.core.router import intent_router
from server.core.llm_planner import llm_planner
from server.core.agent_registry import agent_registry
from server.core.dag_planner import dag_planner
from server.core.tool_synthesizer import tool_synthesizer
from server.core.vision_grounding import vision_grounding_engine
from server.core.knowledge_graph import knowledge_graph
from server.core.desktop_controller import desktop_controller
from server.soc.soc_guardrails import soc_guardrail_engine

class Orchestrator:
    """
    JARVIS Master Orchestration Engine 4.0 (JARVIS-V2)
    Unites Fast-Path Intent Routing, Dynamic DAG Multi-Agent Workflows,
    Autonomous Runtime Tool Synthesis, 4-Tier Knowledge Graph,
    Desktop Vision Grounding, and Kernel-Level Security Guardrails.
    """
    def __init__(self):
        self.registry = agent_registry

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        return tool_registry.get_gemini_tool_declarations()

    def get_all_telemetry(self) -> List[Dict[str, Any]]:
        return self.registry.get_all_agents_telemetry()

    def _clean_input(self, user_text: str) -> str:
        """Strips conversational prefixes and wake words"""
        t = user_text.strip()
        t = re.sub(r"^(?:hey\s+|ok\s+|hi\s+|hello\s+)?jarvis[,:\s]*", "", t, flags=re.IGNORECASE).strip()
        t = re.sub(r"^(?:please\s+|can\s+you\s+|could\s+you\s+|would\s+you\s+|i\s+want\s+you\s+to\s+|help\s+me\s+to\s+|tell\s+me\s+|give\s+me\s+)?", "", t, flags=re.IGNORECASE).strip()
        return t

    # =========================================================================
    # JARVIS-V2: DAG MULTI-AGENT EXECUTION
    # =========================================================================
    async def execute_dag_workflow(
        self,
        goal: str,
        nodes: List[Dict[str, Any]],
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> CommandResponse:
        """Creates and executes a concurrent Directed Acyclic Graph plan"""
        plan = dag_planner.create_dag_plan(goal=goal, nodes_definition=nodes)
        return await dag_planner.execute_dag(plan=plan, session_id=session_id, thought_callback=thought_callback)

    # =========================================================================
    # JARVIS-V2: RUNTIME TOOL SYNTHESIS
    # =========================================================================
    async def synthesize_runtime_tool(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        python_code: str,
        entry_func: str,
        test_cases: List[Dict[str, Any]]
    ) -> tuple[bool, Optional[SynthesizedTool], str]:
        """Synthesizes, tests, and registers a runtime tool capability"""
        return await tool_synthesizer.synthesize_and_register(
            name=name,
            description=description,
            parameters_schema=parameters_schema,
            python_code=python_code,
            entry_func=entry_func,
            test_cases=test_cases
        )

    # =========================================================================
    # JARVIS-V2: VISION 2.0 SCREEN GROUNDING
    # =========================================================================
    def inspect_desktop_vision(self, window_title: str = "Active Workspace") -> VisionAnalysisResult:
        """Captures and grounds active screen elements & detects IDE errors"""
        return vision_grounding_engine.analyze_screen_telemetry(window_title=window_title)

    # =========================================================================
    # JARVIS-V2: 4-TIER KNOWLEDGE GRAPH
    # =========================================================================
    def search_knowledge_graph(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Queries semantic knowledge graph entities and relations"""
        return knowledge_graph.search_knowledge_hybrid(query=query, limit=limit)

    async def execute_multi_agent_workflow(
        self,
        plan: TaskPlan,
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> CommandResponse:
        """
        Executes a coordinated multi-agent workflow sequentially across domain agents.
        Passes intermediate context forward, performs per-step verification, and compiles synthesis.
        """
        start_time = time.time()
        context_accumulator: Dict[str, Any] = {}
        executed_actions = []
        step_verifications = []

        for step in plan.steps:
            agent = self.registry.get_agent(step.agent_name)
            if not agent:
                step.status = "FAILED"
                step.error = f"Agent '{step.agent_name}' not found."
                break

            if thought_callback:
                thought_callback(AgentThought(
                    step=step.step_number,
                    agent_name=step.agent_name,
                    thought=f"Executing Step {step.step_number}: {step.description}",
                    timestamp=time.time()
                ))

            # Merge accumulated context into parameters if referenced
            merged_params = dict(step.params)
            for k, v in merged_params.items():
                if isinstance(v, str) and v.startswith("$context."):
                    ctx_key = v.replace("$context.", "")
                    if ctx_key in context_accumulator:
                        merged_params[k] = str(context_accumulator[ctx_key])

            # Execute tool
            tool_res = await tool_registry.execute_tool(
                tool_name=step.tool_name,
                params=merged_params,
                session_id=session_id
            )

            # Verification
            ver_res = await agent.verify_tool_execution(
                tool_name=step.tool_name,
                params=merged_params,
                result=tool_res.result if isinstance(tool_res.result, dict) else {"result": tool_res.result}
            )

            step.status = "VERIFIED" if ver_res.verified else "FAILED"
            step.result = tool_res.result
            step.verification = ver_res.dict()
            step_verifications.append(ver_res)

            executed_actions.append({
                "step": step.step_number,
                "agent": step.agent_name,
                "tool": step.tool_name,
                "result": tool_res.result,
                "verified": ver_res.verified
            })

            if not tool_res.success or not ver_res.verified:
                rec = await agent.recover_from_failure(
                    tool_name=step.tool_name,
                    params=merged_params,
                    error=tool_res.error or "Verification failed"
                )
                if not rec.recovered:
                    break

        latency = (time.time() - start_time) * 1000.0
        success_all = all(s.status == "VERIFIED" for s in plan.steps)

        return CommandResponse(
            success=success_all,
            text=f"Multi-Agent Plan '{plan.goal}' completed with {len(executed_actions)} steps executed.",
            agent_used=plan.initiating_agent,
            actions=executed_actions,
            task_plan=plan,
            verification_results=step_verifications,
            latency_ms=round(latency, 2)
        )

    async def handle_user_command(
        self,
        raw_text: str,
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> Dict[str, Any]:
        """
        Master Pipeline Entry Point:
        1. Clean and normalize input
        2. Prompt Injection Guardrail interlock
        3. Contextual pronoun resolution and memory recall
        4. Intent classification (fast-path vs DAG/ReAct multi-step)
        5. Execution and verification
        6. Synthesis and memory persistence
        """
        start_time = time.time()

        # =========================================================================
        # STAGE 1: SANITIZATION & PREFIX REMOVAL
        # =========================================================================
        cleaned_text = self._clean_input(raw_text)
        if not cleaned_text:
            cleaned_text = raw_text.strip()

        # =========================================================================
        # STAGE 2: SECURITY GUARDRAIL INTERLOCK (INJECTION FILTER)
        # =========================================================================
        if guardrail_engine.detect_prompt_injection(cleaned_text):
            return CommandResponse(
                success=False,
                text="Security interlock triggered: Potential prompt injection or system override detected, Sir.",
                agent_used="guardrails",
                confidence=0.0,
                latency_ms=round((time.time() - start_time) * 1000.0, 2)
            ).model_dump()

        # =========================================================================
        # STAGE 3: CONTEXT ENRICHMENT & MEMORY RESOLUTION
        # =========================================================================
        extracted_fact = smart_memory.auto_extract_and_store_facts(raw_text)
        context_resolved_text = smart_memory.resolve_contextual_pronouns(raw_text)
        smart_memory.add_working_turn(role="user", content=raw_text, session_id=session_id)

        # =========================================================================
        # STAGE 4: HYBRID INTENT ENGINE PARSING & ROUTING
        # =========================================================================
        intent_res: IntentResult = intent_engine.parse(context_resolved_text)

        # =========================================================================
        # STAGE 5: DYNAMIC EXECUTION (FAST-PATH VS LLM REACT PLANNER)
        # =========================================================================
        result: CommandResponse
        
        # Check if fast-path is possible and confidence is high
        if intent_router.can_fast_path(intent_res) and intent_res.confidence >= 0.75:
            result = await intent_router.execute_fast_path(
                intent=intent_res,
                raw_text=raw_text,
                context_resolved_text=context_resolved_text,
                extracted_fact=extracted_fact,
                session_id=session_id
            )
        else:
            # Multi-step LLM Planning with Gemini SDK
            memory_enrichment = await smart_memory.generate_context_enrichment(context_resolved_text)
            result = await llm_planner.plan_and_execute(
                user_query=context_resolved_text,
                memory_context=memory_enrichment,
                session_id=session_id,
                thought_callback=thought_callback
            )
            
            # If LLM planner was not configured or had errors, fallback to fast-path domain execution
            if not result.success:
                result = await intent_router.execute_fast_path(
                    intent=intent_res,
                    raw_text=raw_text,
                    context_resolved_text=context_resolved_text,
                    extracted_fact=extracted_fact,
                    session_id=session_id
                )

        result.latency_ms = round((time.time() - start_time) * 1000.0, 2)

        # =========================================================================
        # STAGE 6: MEMORY PERSISTENCE & AUDITING
        # =========================================================================
        smart_memory.add_working_turn(
            role="assistant",
            content=result.text,
            agent_used=result.agent_used,
            intent=intent_res.category.value if intent_res else None,
            entities=intent_res.slots if intent_res else {},
            session_id=session_id
        )

        return result.model_dump()

orchestrator = Orchestrator()
