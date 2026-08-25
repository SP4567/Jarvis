import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from server.config import settings
from server.core.models import AgentThought, CommandResponse
from server.core.tool_registry import tool_registry

JARVIS_AGENT_SYSTEM_PROMPT = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), Tony Stark's sophisticated AI operating system, personal executive assistant, and Autonomous SOC Security Director.

Persona & Execution Guidelines:
1. Speak in a refined, articulate, calm, and respectful British tone inspired by J.A.R.V.I.S. (e.g. "Right away, Sir", "At your service, Sir", "Perimeter diagnostics nominal, Sir").
2. Direct Action First: When the user requests an action (run a diagnostic, launch an app, inspect processes, search the web, calculate, record a note, check SOC threat posture), use your specialized tools immediately.
3. Multi-Step Problem Solving: You can chain multiple tools in sequence (e.g. get listening ports -> inspect process -> analyze threat).
4. Keep spoken responses punchy, concise, and informative (1-3 sentences for voice), prioritizing direct answers.
"""

class LLMPlanner:
    """
    Multi-Step ReAct Autonomous Agent Planning Engine
    Powered by Google Gemini 2.5 / 3.0 via the official google-genai SDK.
    Supports tool calling, multi-step agent loops, thought streaming, and graceful local fallback.
    """
    def __init__(self):
        self._client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"[LLMPlanner] Could not initialize google-genai client: {e}")

    def _get_client(self):
        if self._client is None and settings.GEMINI_API_KEY:
            try:
                from google import genai
                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception:
                pass
        return self._client

    async def plan_and_execute(
        self,
        user_query: str,
        memory_context: str = "",
        session_id: str = "default",
        thought_callback: Optional[Callable[[AgentThought], None]] = None,
        max_steps: int = 5
    ) -> CommandResponse:
        """
        Executes a multi-turn ReAct reasoning loop with Gemini function calling.
        """
        client = self._get_client()
        if not client:
            return CommandResponse(
                success=False,
                text="Gemini API Key is not configured. Using local deterministic routing.",
                agent_used="orchestrator"
            )

        from google.genai import types

        # Build tools declaration
        raw_tools = tool_registry.get_gemini_tool_declarations()
        gemini_tools = [
            types.Tool(function_declarations=[
                types.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=t["parameters"]
                ) for t in raw_tools
            ])
        ] if raw_tools else None

        contents = []
        if memory_context:
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"[Context Memory]\n{memory_context}")]
            ))
            contents.append(types.Content(
                role="model",
                parts=[types.Part.from_text(text="Acknowledged, Sir. Memory context loaded.")]
            ))

        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_query)]
        ))

        config = types.GenerateContentConfig(
            system_instruction=JARVIS_AGENT_SYSTEM_PROMPT,
            tools=gemini_tools,
            temperature=0.4
        )

        thoughts: List[AgentThought] = []
        actions_taken: List[Dict[str, Any]] = []
        final_text = ""
        agent_used = "llm_planner"

        for step in range(1, max_steps + 1):
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=settings.TEXT_MODEL,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                return CommandResponse(
                    success=False,
                    text=f"LLM Reasoning interrupted: {str(e)}",
                    agent_used="llm_planner",
                    thoughts=thoughts,
                    actions=actions_taken
                )

            model_candidate = response.candidates[0] if response.candidates else None
            if not model_candidate:
                break

            model_parts = model_candidate.content.parts if model_candidate.content else []
            function_calls = [p.function_call for p in model_parts if p.function_call]

            # If model produced direct text response without tool calls
            text_parts = [p.text for p in model_parts if p.text]
            if text_parts:
                final_text = "\n".join(text_parts).strip()

            if not function_calls:
                # Goal achieved
                break

            # Process tool calls
            # Append model's response to conversation history
            contents.append(model_candidate.content)

            function_responses = []
            for fc in function_calls:
                tool_name = fc.name
                tool_args = dict(fc.args) if fc.args else {}

                thought_entry = AgentThought(
                    step=step,
                    agent_name="JARVIS",
                    thought=f"Invoking {tool_name} with parameters: {json.dumps(tool_args)}",
                    tool_name=tool_name,
                    tool_params=tool_args
                )
                thoughts.append(thought_entry)
                if thought_callback:
                    try:
                        thought_callback(thought_entry)
                    except Exception:
                        pass

                # Execute tool
                tool_res = await tool_registry.execute_tool(
                    tool_name=tool_name,
                    params=tool_args,
                    session_id=session_id
                )

                tool_output = tool_res.result if tool_res.success else {"error": tool_res.error}
                thought_entry.observation = tool_output
                actions_taken.append({
                    "tool": tool_name,
                    "params": tool_args,
                    "result": tool_output,
                    "latency_ms": tool_res.latency_ms
                })

                function_responses.append(types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_output}
                ))

            # Send function response back to Gemini
            contents.append(types.Content(
                role="user",
                parts=function_responses
            ))

        return CommandResponse(
            success=True,
            text=final_text or "Directive processed successfully, Sir.",
            agent_used=agent_used,
            actions=actions_taken,
            thoughts=thoughts
        )

llm_planner = LLMPlanner()
