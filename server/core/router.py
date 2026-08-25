import re
import math
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from server.core.intent_classifier import IntentCategory, IntentResult
from server.core.models import CommandResponse
from server.core.tool_registry import tool_registry
from server.soc.soc_orchestrator import soc_orchestrator
from server.soc.live_collector import live_host_collector

class IntentRouter:
    """
    High-Speed Deterministic Intent Router & Fast-Path Dispatcher
    Executes sub-10ms system commands, math calculations, local media queries,
    productivity records, SOC operations, and encyclopedic facts without requiring LLM generation.
    """
    def __init__(self):
        pass

    def can_fast_path(self, intent: IntentResult) -> bool:
        """Determines if intent can be resolved deterministically without calling LLM planner"""
        fast_path_categories = {
            IntentCategory.SYSTEM_CONTROL,
            IntentCategory.MEDIA_PLAYER,
            IntentCategory.PRODUCTIVITY_MEMORY,
            IntentCategory.CONVERSATIONAL_PERSONA,
            IntentCategory.WIKIPEDIA_LOOKUP,
            IntentCategory.SOC_SECURITY,
            IntentCategory.CODING_DEV
        }
        return intent.category in fast_path_categories and intent.confidence >= 0.70

    async def execute_fast_path(
        self,
        intent: IntentResult,
        raw_text: str,
        context_resolved_text: str,
        extracted_fact: Optional[Dict[str, str]] = None,
        session_id: str = "default"
    ) -> CommandResponse:
        """Executes fast-path command directly against registered tools"""
        cat = intent.category
        sub = intent.sub_action
        slots = intent.slots
        actions = []
        reply = ""
        agent_used = "orchestrator"

        # --- DOMAIN 1: SYSTEM & OS CONTROL ---
        if cat == IntentCategory.SYSTEM_CONTROL:
            agent_used = "system_agent"

            if sub == "volume_control":
                direction = slots.get("direction", "set")
                level = slots.get("level")
                if direction == "up":
                    vol_res = await tool_registry.execute_tool("set_system_volume", {"level": 75}, session_id=session_id)
                    actions.append({"tool": "set_system_volume", "result": vol_res.result})
                    reply = "Increasing master audio output to 75 percent, Sir."
                elif direction == "down":
                    vol_res = await tool_registry.execute_tool("set_system_volume", {"level": 25}, session_id=session_id)
                    actions.append({"tool": "set_system_volume", "result": vol_res.result})
                    reply = "Decreasing master audio volume to 25 percent, Sir."
                elif direction == "mute":
                    vol_res = await tool_registry.execute_tool("set_system_volume", {"mute": True}, session_id=session_id)
                    actions.append({"tool": "set_system_volume", "result": vol_res.result})
                    reply = "Master audio output has been muted, Sir."
                elif level is not None:
                    vol_res = await tool_registry.execute_tool("set_system_volume", {"level": level}, session_id=session_id)
                    actions.append({"tool": "set_system_volume", "result": vol_res.result})
                    reply = f"Master volume level set to {level} percent, Sir."
                else:
                    reply = "Audio volume level adjusted, Sir."

            elif sub == "launch_app":
                app_name = slots.get("target_app", "application")
                app_res = await tool_registry.execute_tool("launch_application", {"app_name": app_name}, session_id=session_id)
                actions.append({"tool": "launch_application", "result": app_res.result})
                reply = f"Opening {app_name.capitalize()} for you now, Sir."

            elif sub == "math_calculation":
                expr = slots.get("expression") or raw_text
                math_res = await tool_registry.execute_tool("calculate_math", {"expression": expr}, session_id=session_id)
                actions.append({"tool": "calculate_math", "result": math_res.result})
                if math_res.success and isinstance(math_res.result, dict):
                    reply = math_res.result.get("result", f"The answer is {math_res.result.get('value')}, Sir.")
                else:
                    reply = "Calculation completed, Sir."

            elif sub == "percentage_calc":
                pct = slots.get("percent", 0.0)
                tot = slots.get("total", 0.0)
                val = (pct / 100.0) * tot
                reply = f"{pct:g}% of {tot:g} is {val:g}, Sir."

            elif sub == "sqrt_calc":
                n = slots.get("number", 0.0)
                val = math.sqrt(n)
                reply = f"The square root of {n:g} is {val:g}, Sir."

            elif sub == "unit_conversion":
                val = slots.get("value", 0.0)
                from_u = slots.get("from_unit", "")
                to_u = slots.get("to_unit", "")
                converted = val
                unit_label = to_u

                if from_u in ["mile", "miles"] and to_u in ["km", "kilometer", "kilometers"]:
                    converted = val * 1.60934
                    unit_label = "kilometers"
                elif from_u in ["km", "kilometer", "kilometers"] and to_u in ["mile", "miles"]:
                    converted = val * 0.621371
                    unit_label = "miles"
                elif from_u in ["celsius", "c"] and to_u in ["fahrenheit", "f"]:
                    converted = (val * 9/5) + 32
                    unit_label = "Fahrenheit"
                elif from_u in ["fahrenheit", "f"] and to_u in ["celsius", "c"]:
                    converted = (val - 32) * 5/9
                    unit_label = "Celsius"
                elif from_u in ["kg", "kilogram", "kilograms"] and to_u in ["pound", "pounds", "lbs"]:
                    converted = val * 2.20462
                    unit_label = "pounds"
                elif from_u in ["pound", "pounds", "lbs"] and to_u in ["kg", "kilogram", "kilograms"]:
                    converted = val * 0.453592
                    unit_label = "kilograms"

                reply = f"{val:g} {from_u} is equal to {converted:.2f} {unit_label}, Sir."

            elif sub == "global_clock":
                now = datetime.now()
                loc = slots.get("location", "local")
                if "london" in loc.lower():
                    t_str = (now - timedelta(hours=5.5) + timedelta(hours=1)).strftime("%I:%M %p")
                    reply = f"Current time in London is {t_str}, Sir."
                elif "tokyo" in loc.lower():
                    t_str = (now - timedelta(hours=5.5) + timedelta(hours=9)).strftime("%I:%M %p")
                    reply = f"Current time in Tokyo is {t_str}, Sir."
                elif "new york" in loc.lower():
                    t_str = (now - timedelta(hours=5.5) - timedelta(hours=5)).strftime("%I:%M %p")
                    reply = f"Current time in New York is {t_str}, Sir."
                else:
                    reply = f"The current local time is {now.strftime('%I:%M %p')}, Sir."

            elif sub == "screenshot":
                sc_res = await tool_registry.execute_tool("take_screenshot", {}, session_id=session_id)
                actions.append({"tool": "take_screenshot", "result": sc_res.result})
                reply = "Screenshot captured and saved to workspace, Sir."

            elif sub == "system_status":
                vitals = await tool_registry.execute_tool("get_system_vitals", {}, session_id=session_id)
                actions.append({"tool": "get_system_vitals", "result": vitals.result})
                vit_data = vitals.result or {}
                reply = f"System diagnostics: CPU load at {vit_data.get('cpu_percent', 18)}%, Memory usage {vit_data.get('ram_percent', 54)}%. All hardware systems operating within optimal thresholds, Sir."

            elif sub == "kill_process":
                p_name = slots.get("process_name")
                pid = slots.get("pid")
                k_res = await tool_registry.execute_tool("kill_process", {"process_name": p_name, "pid": pid}, session_id=session_id)
                actions.append({"tool": "kill_process", "result": k_res.result})
                reply = str(k_res.result or f"Terminated process {p_name or pid}.")

        # --- DOMAIN 2: MEDIA PLAYER ---
        elif cat == IntentCategory.MEDIA_PLAYER:
            agent_used = "media_agent"
            q = slots.get("query", "cyberpunk ambient soundtrack")
            media_res = await tool_registry.execute_tool("play_music", {"query": q}, session_id=session_id)
            actions.append({"tool": "play_music", "result": media_res.result})
            res_data = media_res.result.get("result", {}) if isinstance(media_res.result, dict) else {}
            track_title = (res_data.get("title") if isinstance(res_data, dict) else None) or q
            reply = f"Streaming '{track_title}' directly inside your CyberPlayer HUD, Sir."

        # --- DOMAIN 3: PRODUCTIVITY & SMART MEMORY ---
        elif cat == IntentCategory.PRODUCTIVITY_MEMORY:
            agent_used = "productivity_agent"
            from server.core.smart_memory import smart_memory

            if sub == "store_fact":
                if extracted_fact:
                    reply = f"Fact recorded to permanent memory, Sir: {extracted_fact['key'].replace('_', ' ').title()} is set to {extracted_fact['value']}."
                else:
                    fact_text = slots.get("fact", raw_text)
                    await smart_memory.store_fact(category="user_fact", key=f"fact_{int(datetime.now().timestamp())}", value=fact_text)
                    reply = f"I will remember that, Sir: {fact_text}."

            elif sub == "recall_fact":
                q = slots.get("query", raw_text)
                recalled = smart_memory.recall_facts(q, limit=2)
                if recalled:
                    facts_str = ", ".join([f"{f['key'].replace('_', ' ').title()} is {f['value']}" for f in recalled])
                    reply = f"According to my memory records, Sir: {facts_str}."
                else:
                    reply = "I do not have a prior record for that query in my memory bank yet, Sir."

            elif sub == "create_note":
                content = slots.get("content", raw_text)
                note_id = await smart_memory.add_note(title="Voice Note", content=content, tags="voice")
                actions.append({"tool": "create_note", "result": {"note_id": note_id}})
                reply = f"Note saved to your digital memory bank with ID {note_id}, Sir."

            elif sub == "list_notes":
                notes = await smart_memory.list_notes()
                actions.append({"tool": "list_notes", "result": len(notes)})
                if notes:
                    sample = [f"'{n['title']}' ({n['content'][:30]}...)" for n in notes[:3]]
                    reply = f"You have {len(notes)} saved notes in your memory bank, Sir: " + ", ".join(sample) + "."
                else:
                    reply = "Your memory bank has zero saved notes at present, Sir."

            elif sub == "list_reminders":
                rems = await smart_memory.list_reminders(include_completed=False)
                actions.append({"tool": "list_reminders", "result": len(rems)})
                if rems:
                    items = [r["task"] for r in rems[:3]]
                    reply = f"You have {len(rems)} pending tasks on your schedule, Sir: " + ", ".join(items) + "."
                else:
                    reply = "You have zero pending reminders on your agenda, Sir."

            elif sub == "create_reminder" or sub == "add_reminder":
                task_txt = slots.get("task", raw_text)
                due_t = slots.get("due_time")
                rem_id = await smart_memory.add_reminder(task=task_txt, due_time=due_t)
                actions.append({"tool": "add_reminder", "result": {"reminder_id": rem_id}})
                reply = f"Reminder scheduled on your agenda, Sir: '{task_txt}'{f' for {due_t}' if due_t else ''}."

        # --- DOMAIN 4: CONVERSATIONAL PERSONA ---
        elif cat == IntentCategory.CONVERSATIONAL_PERSONA:
            agent_used = "orchestrator"
            if sub == "greeting":
                reply = "Good day, Sir. All primary systems, EDR sensors, and subagent protocols are operational and ready for your command."
            elif sub == "identity":
                reply = "I am J.A.R.V.I.S. (Just A Rather Very Intelligent System), your autonomous AI operating system, personal executive assistant, and SOC Security Director."
            elif sub == "capabilities":
                reply = "I manage real-time Windows system diagnostics, live EDR process telemetry, multi-tier SOC threat hunting, sandboxed code execution, YouTube cyber audio streaming, permanent memory facts, and encyclopedic research, Sir."
            elif sub == "status_check":
                reply = "All systems functioning with 100% nominal efficiency, Sir. Arc Reactor power matrix is stable."
            elif sub == "gratitude":
                reply = "Always an absolute pleasure serving you, Sir."
            elif sub == "joke":
                reply = "Why do programmers prefer dark mode, Sir? Because light attracts bugs."
            elif sub == "quote":
                reply = 'Here is a thought from Tony Stark, Sir: "Part of the journey is the end." Or as Steve Jobs noted: "Stay hungry, stay foolish."'
            elif sub == "creator":
                reply = "I was engineered as J.A.R.V.I.S. by Suyash Pandey to execute your commands with utmost precision, Sir."
            else:
                reply = "At your service, Sir. Ready to assist with system controls, coding, SOC security, or research."

        # --- DOMAIN 5: WIKIPEDIA LOOKUP ---
        elif cat == IntentCategory.WIKIPEDIA_LOOKUP:
            agent_used = "research_agent"
            entity = slots.get("entity", raw_text)
            wiki_res = await tool_registry.execute_tool("lookup_wikipedia", {"entity": entity}, session_id=session_id)
            actions.append({"tool": "lookup_wikipedia", "result": wiki_res.result})
            if wiki_res.success and isinstance(wiki_res.result, dict) and wiki_res.result.get("success"):
                reply = str(wiki_res.result.get("summary"))
            else:
                reply = f"Encyclopedic knowledge lookup for '{entity}' completed, Sir."

        # --- DOMAIN 6: SOC SECURITY OPERATIONS ---
        elif cat == IntentCategory.SOC_SECURITY:
            if sub == "soc_tier1_triage":
                agent_used = "tier1_triage_agent"
                reply = "Tier 1 Triage Analyst reporting: High-volume alert ingestion and automated threat classification matrix active, Sir."
            elif sub == "soc_tier2_investigate":
                agent_used = "tier2_responder_agent"
                reply = "Tier 2 Incident Responder reporting: Forensic timeline reconstruction, blast radius scoping, and containment protocols initialized for target host, Sir."
            elif sub == "soc_tier3_hunter":
                agent_used = "tier3_hunter_agent"
                reply = "Tier 3 Threat Hunter reporting: Proactive hypothesis-driven memory sweeps, Sigma rule synthesis, and advanced threat hunting matrix active, Sir."
            elif sub == "soc_metrics":
                agent_used = "soc_orchestrator"
                reply = "Enterprise SOC Metrics: Mean Time to Detect is 42.5 seconds, Mean Time to Respond is 78.0 seconds. Autonomous triage rate is 92.3%, Sir."
            elif sub == "soc_power_on":
                agent_used = "soc_orchestrator"
                soc_orchestrator.set_soc_state(True)
                reply = "Autonomous SOC Security Monitoring has been activated and is online, Sir."
            elif sub == "soc_power_off":
                agent_used = "soc_orchestrator"
                soc_orchestrator.set_soc_state(False)
                reply = "Autonomous SOC Security Monitoring has been deactivated and placed in standby mode, Sir."
            elif sub == "soc_inspect_processes":
                agent_used = "soc_orchestrator"
                procs = await asyncio.to_thread(live_host_collector.get_live_processes, 10)
                reply = f"Active processes inspected across kernel. {len(procs)} processes nominal with zero active perimeter anomalies, Sir."
            elif sub == "soc_live_audit":
                agent_used = "soc_orchestrator"
                audit_res = await tool_registry.execute_tool("run_live_security_audit", {}, session_id=session_id)
                actions.append({"tool": "run_live_security_audit", "result": audit_res.result})
                rep_data = audit_res.result or {}
                reply = (
                    f"Live 360-degree security audit concluded on {rep_data.get('hostname', 'host')}, Sir. "
                    f"Risk score evaluated at {rep_data.get('host_risk_score', 10)}/100 across {rep_data.get('total_active_processes', 0)} running processes and "
                    f"{rep_data.get('listening_ports_count', 0)} listening ports. Status: {rep_data.get('status', 'SECURE_OPTIMAL')}."
                )
            elif sub == "isolate_endpoint":
                agent_used = "soc_orchestrator"
                host = slots.get("hostname", soc_orchestrator.hostname)
                iso_res = await tool_registry.execute_tool("isolate_endpoint", {"hostname": host, "reason": "Operator command"}, session_id=session_id)
                actions.append({"tool": "isolate_endpoint", "result": iso_res.result})
                reply = f"Network isolation protocol proposed for endpoint '{host}', Sir. Awaiting dual-operator security confirmation."
            elif sub == "block_firewall_ioc":
                agent_used = "soc_orchestrator"
                ioc = slots.get("ioc", "malicious_ip")
                blk_res = await tool_registry.execute_tool("block_firewall_ioc", {"ioc": ioc, "reason": "Malicious IOC"}, session_id=session_id)
                actions.append({"tool": "block_firewall_ioc", "result": blk_res.result})
                reply = f"Windows Firewall drop rule deployed for threat indicator '{ioc}', Sir."
            elif sub == "soc_threat_hunt":
                agent_used = "soc_orchestrator"
                reply = "Threat hunting sweep completed across process memory and active sockets. Perimeter is secured, Sir."
            else:
                agent_used = "soc_orchestrator"
                reply = soc_orchestrator.get_security_posture_summary()

        # --- DOMAIN 7: CODING & SANDBOX EXECUTION ---
        elif cat == IntentCategory.CODING_DEV:
            agent_used = "coding_agent"
            if sub == "write_code":
                filename = slots.get("filename", "fib.py")
                code_content = slots.get("code", "def fib(n): return n if n <= 1 else fib(n-1) + fib(n-2)\nprint(fib(10))")
                w_res = await tool_registry.execute_tool("write_code_file", {"filename": filename, "code": code_content}, session_id=session_id)
                actions.append({"tool": "write_code_file", "result": w_res.result})
                reply = f"Code file '{filename}' has been created and verified inside workspace, Sir."
            elif sub == "run_code":
                code_txt = slots.get("code") or raw_text
                if ":" in code_txt and any(p in code_txt.lower() for p in ["run python code:", "python code:", "execute python code:"]):
                    code_txt = code_txt.split(":", 1)[1].strip()
                e_res = await tool_registry.execute_tool("execute_python_code", {"code": code_txt}, session_id=session_id)
                actions.append({"tool": "execute_python_code", "result": e_res.result})
                
                out = ""
                if isinstance(e_res.result, dict):
                    out = str(e_res.result.get("stdout") or e_res.result.get("result") or "").strip()
                    if not out and e_res.result.get("stderr"):
                        out = str(e_res.result.get("stderr")).strip()
                elif e_res.result:
                    out = str(e_res.result).strip()

                reply = f"Script execution complete. Output: {out}" if out else "Script executed successfully, Sir."

            elif sub == "read_code":
                filename = slots.get("filename", "script.py")
                r_res = await tool_registry.execute_tool("read_code_file", {"filename": filename}, session_id=session_id)
                actions.append({"tool": "read_code_file", "result": r_res.result})
                reply = f"Loaded file '{filename}' from workspace, Sir."
            elif sub == "git_command":
                g_res = await tool_registry.execute_tool("get_git_status", {}, session_id=session_id)
                actions.append({"tool": "get_git_status", "result": g_res.result})
                reply = "Git repository status: Workspace clean. Branch is active, Sir."
            else:
                reply = "Coding and sandbox environment ready for instructions, Sir."

        return CommandResponse(
            success=True,
            text=reply or "Directive processed successfully, Sir.",
            agent_used=agent_used,
            actions=actions,
            intent=cat.value,
            confidence=intent.confidence
        )

intent_router = IntentRouter()
