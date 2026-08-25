import re
import time
from typing import Dict, Any, List, Optional, Callable

from server.config import settings
from server.core.models import CommandResponse, AgentThought
from server.core.smart_memory import smart_memory
from server.core.guardrails import guardrail_engine
from server.core.intent_classifier import intent_engine, IntentCategory, IntentResult
from server.core.tool_registry import tool_registry
from server.core.router import intent_router
from server.core.llm_planner import llm_planner
from server.core.agent_registry import agent_registry
from server.soc.soc_guardrails import soc_guardrail_engine

class Orchestrator:
    """
    JARVIS Master Orchestration Engine 3.0
    Modular, Enterprise-Grade Coordinator uniting Fast-Path Intent Routing,
    Gemini 2.5/3.0 Multi-Step ReAct Planning, 3-Tier Security Guardrails, and Async Multi-Tier Memory.
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

    async def handle_user_command(
        self,
        user_text: str,
        session_id: str = "default",
        context: Optional[Dict[str, Any]] = None,
        thought_callback: Optional[Callable[[AgentThought], None]] = None
    ) -> Dict[str, Any]:
        """
        Unified 7-Stage Execution Pipeline for user commands.
        """
        raw_text = user_text.strip()
        start_time = time.time()
        
        # =========================================================================
        # STAGE 1: PRE-EXECUTION SAFETY & PROMPT INJECTION CHECK
        # =========================================================================
        is_safe, safe_text, threat = guardrail_engine.sanitize_prompt_input(raw_text)
        if not is_safe:
            smart_memory.add_working_turn(role="user", content=raw_text, session_id=session_id)
            smart_memory.add_working_turn(role="assistant", content=safe_text, agent_used="guardrails", session_id=session_id)
            return {
                "success": False,
                "text": safe_text,
                "agent_used": "guardrails",
                "actions": [],
                "thoughts": [],
                "guardrail_blocked": True,
                "latency_ms": round((time.time() - start_time) * 1000.0, 2)
            }

        # =========================================================================
        # STAGE 2: QUICK HUMAN-IN-THE-LOOP AUTHORIZATION / CANCELLATION HOOKS
        # =========================================================================
        cleaned_text = self._clean_input(raw_text)
        if re.search(r"^(authorize|approve|yes\s+execute|confirm|proceed)", cleaned_text, re.IGNORECASE) or re.search(r"^(jarvis\s+)?(authorize|approve|yes\s+execute)", raw_text, re.IGNORECASE):
            # Check SOC Containment first
            soc_resolved = soc_guardrail_engine.resolve_latest_pending(approved=True, approver="VOICE_AUTHORIZATION")
            if soc_resolved:
                target_str = str(soc_resolved.target.get("hostname") or soc_resolved.target.get("ip") or "target")
                reply = f"SOC Containment Authorized, Sir. Executing '{soc_resolved.action_name}' on target {target_str}."
                smart_memory.add_working_turn(role="assistant", content=reply, agent_used="soc_guardrails", session_id=session_id)
                return {
                    "success": True,
                    "text": reply,
                    "agent_used": "soc_guardrails",
                    "action_executed": soc_resolved.action_name,
                    "status": "approved",
                    "latency_ms": round((time.time() - start_time) * 1000.0, 2)
                }

            # Check general system guardrails
            resolved = guardrail_engine.resolve_latest_pending(approved=True, approver="VOICE_AUTHORIZATION")
            if resolved:
                reply = f"Authorization confirmed, Sir. Proceeding with '{resolved.action_name}'."
                smart_memory.add_working_turn(role="assistant", content=reply, agent_used="guardrails", session_id=session_id)
                return {
                    "success": True,
                    "text": reply,
                    "agent_used": "guardrails",
                    "action_executed": resolved.action_name,
                    "status": "approved",
                    "latency_ms": round((time.time() - start_time) * 1000.0, 2)
                }

        if re.search(r"^(cancel|abort|reject|no\s+stop|deny)", cleaned_text, re.IGNORECASE) or re.search(r"^(jarvis\s+)?(cancel|abort|reject)", raw_text, re.IGNORECASE):
            soc_resolved = soc_guardrail_engine.resolve_latest_pending(approved=False, approver="VOICE_AUTHORIZATION")
            if soc_resolved:
                reply = f"SOC Containment Action '{soc_resolved.action_name}' has been aborted, Sir."
                smart_memory.add_working_turn(role="assistant", content=reply, agent_used="soc_guardrails", session_id=session_id)
                return {
                    "success": True,
                    "text": reply,
                    "agent_used": "soc_guardrails",
                    "action_executed": soc_resolved.action_name,
                    "status": "rejected",
                    "latency_ms": round((time.time() - start_time) * 1000.0, 2)
                }

            resolved = guardrail_engine.resolve_latest_pending(approved=False, approver="VOICE_AUTHORIZATION")
            if resolved:
                reply = f"Action '{resolved.action_name}' has been aborted as per your instruction, Sir."
                smart_memory.add_working_turn(role="assistant", content=reply, agent_used="guardrails", session_id=session_id)
                return {
                    "success": True,
                    "text": reply,
                    "agent_used": "guardrails",
                    "action_executed": resolved.action_name,
                    "status": "rejected",
                    "latency_ms": round((time.time() - start_time) * 1000.0, 2)
                }

        # =========================================================================
        # STAGE 3: SMART MEMORY CONTEXT ENRICHMENT & AUTO FACT EXTRACTION
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
            if not result.success and "Gemini API Key is not configured" in result.text:
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
