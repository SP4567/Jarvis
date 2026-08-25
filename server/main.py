import asyncio
import json
import time
from typing import List, Set, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from server.config import settings
from server.db.async_db import async_db
from server.core.orchestrator import orchestrator
from server.core.live_voice import voice_engine
from server.core.guardrails import guardrail_engine
from server.core.smart_memory import smart_memory
from server.agents.system_agent import system_agent

# SOC Multi-Agent Security Grid Imports
from server.soc.soc_orchestrator import soc_orchestrator
from server.soc.case_memory import soc_case_memory
from server.soc.soc_guardrails import soc_guardrail_engine
from server.soc.telemetry_generator import telemetry_generator
from server.soc.live_collector import live_host_collector
from server.soc.background_monitor import background_security_monitor
from server.soc.models import IncidentStatus, SeverityLevel

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="JARVIS Live Voice & Autonomous SOC Multi-Agent Assistant Enterprise Backend"
)

# Strict CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Authentication Verification Dependency
async def verify_auth_header(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    if not settings.REQUIRE_AUTH:
        return True
    
    token = x_api_key
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if token != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing JARVIS API Authentication Key."
        )
    return True

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active_connections.discard(ws)

manager = ConnectionManager()

# Background Telemetry Broadcaster
@app.on_event("startup")
async def startup_event():
    # 1. Initialize Async Database & WAL Pragmas
    await async_db.initialize()
    # 2. Start Live HUD Telemetry Broadcaster
    asyncio.create_task(telemetry_broadcaster())
    # 3. Start Real-Time Background Security Monitor
    asyncio.create_task(background_security_monitor.start())

async def telemetry_broadcaster():
    """Broadcasts system vitals, subagent telemetry, and SOC security status to HUD every 2 seconds"""
    while True:
        try:
            if manager.active_connections:
                vitals = await asyncio.to_thread(system_agent.get_system_vitals)
                agents_telemetry = orchestrator.get_all_telemetry()
                pending_guardrails = guardrail_engine.get_pending_requests()
                soc_metrics = soc_case_memory.get_metrics()
                soc_pending = soc_guardrail_engine.get_pending_actions()
                recent_cases = [c.model_dump() for c in soc_case_memory.list_cases(limit=10)]
                
                payload = {
                    "type": "telemetry_update",
                    "timestamp": time.time(),
                    "vitals": vitals,
                    "agents": agents_telemetry,
                    "pending_guardrails": pending_guardrails,
                    "soc": {
                        "metrics": soc_metrics,
                        "pending_containment": soc_pending,
                        "recent_cases": recent_cases
                    }
                }
                await manager.broadcast(payload)
        except Exception:
            pass
        await asyncio.sleep(2.0)

# WebSocket Real-Time Channel
@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    if settings.REQUIRE_AUTH and token != settings.API_KEY:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    
    # Send initial handshake with SOC state
    vitals_init = await asyncio.to_thread(system_agent.get_system_vitals)
    await websocket.send_json({
        "type": "handshake",
        "status": "online",
        "version": settings.VERSION,
        "agents": orchestrator.get_all_telemetry(),
        "vitals": vitals_init,
        "soc_metrics": soc_case_memory.get_metrics()
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            # 1. User spoken / text message
            if event_type == "user_message":
                text = data.get("text", "")
                session_id = data.get("session_id", "default")
                if not text.strip():
                    continue

                await websocket.send_json({
                    "type": "jarvis_state",
                    "state": "thinking",
                    "user_text": text
                })

                # Thought streaming callback
                def on_thought(thought):
                    asyncio.create_task(websocket.send_json({
                        "type": "agent_thought",
                        "thought": thought.model_dump()
                    }))

                result = await orchestrator.handle_user_command(
                    user_text=text,
                    session_id=session_id,
                    thought_callback=on_thought
                )
                response_text = result.get("text", "")

                await websocket.send_json({
                    "type": "jarvis_state",
                    "state": "speaking",
                    "response_text": response_text,
                    "agent_used": result.get("agent_used"),
                    "actions": result.get("actions", []),
                    "thoughts": result.get("thoughts", []),
                    "latency_ms": result.get("latency_ms", 0.0)
                })

                try:
                    audio_b64 = await voice_engine.synthesize_speech_base64(response_text)
                    await websocket.send_json({
                        "type": "audio_payload",
                        "audio_base64": audio_b64,
                        "text": response_text,
                        "agent_used": result.get("agent_used")
                    })
                except Exception as audio_err:
                    print("TTS Synthesis error:", audio_err)

                await websocket.send_json({
                    "type": "jarvis_state",
                    "state": "idle"
                })

            # 2. Interruption event
            elif event_type == "interrupt":
                await websocket.send_json({
                    "type": "interrupted",
                    "message": "Speech playback halted immediately."
                })

            # 3. Guardrail Human-In-The-Loop Approval
            elif event_type == "guardrail_resolve":
                action_id = data.get("action_id")
                approved = data.get("approved", False)
                approver = data.get("approver", "HUD_OPERATOR")
                success = guardrail_engine.resolve_action(action_id, approved, approver=approver)
                await websocket.send_json({
                    "type": "guardrail_resolved",
                    "action_id": action_id,
                    "approved": approved,
                    "success": success
                })

            # 4. SOC Containment Approval Resolution
            elif event_type == "soc_containment_resolve":
                action_id = data.get("action_id")
                approved = data.get("approved", False)
                approver = data.get("approver", "HUD_OPERATOR")
                if approved:
                    act = soc_guardrail_engine.pending_actions.get(action_id)
                    if act:
                        soc_guardrail_engine.execute_action(act, approver=approver)
                        soc_case_memory.add_containment_action(act.case_id, act)
                else:
                    soc_guardrail_engine.reject_action(action_id, approver=approver)

                await websocket.send_json({
                    "type": "soc_containment_resolved",
                    "action_id": action_id,
                    "approved": approved
                })

            elif event_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# --- REST Endpoints ---

class CommandRequest(BaseModel):
    command: str
    session_id: str = "default"

@app.post("/api/command", dependencies=[Depends(verify_auth_header)])
async def execute_command_endpoint(req: CommandRequest):
    result = await orchestrator.handle_user_command(req.command, session_id=req.session_id)
    audio_b64 = None
    try:
        audio_b64 = await voice_engine.synthesize_speech_base64(result.get("text", ""))
    except Exception:
        pass
    return {
        "success": result.get("success", True),
        "response": result.get("text"),
        "agent_used": result.get("agent_used"),
        "actions": result.get("actions", []),
        "thoughts": result.get("thoughts", []),
        "audio_base64": audio_b64,
        "latency_ms": result.get("latency_ms", 0.0)
    }

@app.get("/api/vitals", dependencies=[Depends(verify_auth_header)])
async def get_vitals_endpoint():
    return await asyncio.to_thread(system_agent.get_system_vitals)

@app.get("/api/agents", dependencies=[Depends(verify_auth_header)])
def get_agents_endpoint():
    return orchestrator.get_all_telemetry()

@app.get("/api/guardrails/pending", dependencies=[Depends(verify_auth_header)])
def get_pending_guardrails_endpoint():
    return guardrail_engine.get_pending_requests()

class GuardrailResolveRequest(BaseModel):
    action_id: str
    approved: bool
    approver: str = "OPERATOR"

@app.post("/api/guardrails/resolve", dependencies=[Depends(verify_auth_header)])
def resolve_guardrail_endpoint(req: GuardrailResolveRequest):
    success = guardrail_engine.resolve_action(req.action_id, req.approved, approver=req.approver)
    return {"success": success, "action_id": req.action_id, "approved": req.approved}

# --- Smart Memory Endpoints ---
@app.get("/api/memory/facts", dependencies=[Depends(verify_auth_header)])
async def list_memory_facts_endpoint():
    return await smart_memory.list_all_facts()

class StoreFactRequest(BaseModel):
    category: str = "user_preference"
    key: str
    value: str

@app.post("/api/memory/facts", dependencies=[Depends(verify_auth_header)])
async def store_memory_fact_endpoint(req: StoreFactRequest):
    success = await smart_memory.store_fact(category=req.category, key=req.key, value=req.value)
    return {"success": success, "key": req.key, "value": req.value}

@app.delete("/api/memory/facts/{key}", dependencies=[Depends(verify_auth_header)])
async def delete_memory_fact_endpoint(key: str):
    success = await smart_memory.delete_fact(key)
    return {"success": success, "key": key}

@app.get("/api/memory/actions", dependencies=[Depends(verify_auth_header)])
async def list_memory_actions_endpoint(limit: int = 15):
    return await smart_memory.list_recent_actions(limit=limit)

# --- SOC Specific Endpoints ---

@app.get("/api/soc/cases", dependencies=[Depends(verify_auth_header)])
def list_soc_cases_endpoint(limit: int = 50):
    cases = soc_case_memory.list_cases(limit=limit)
    return [c.model_dump() for c in cases]

@app.get("/api/soc/cases/{case_id}", dependencies=[Depends(verify_auth_header)])
def get_soc_case_detail_endpoint(case_id: str):
    case = soc_case_memory.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.model_dump()

@app.get("/api/soc/state", dependencies=[Depends(verify_auth_header)])
def get_soc_state_endpoint():
    return {
        "enabled": soc_orchestrator.is_monitoring_active,
        "status": "ACTIVE" if soc_orchestrator.is_monitoring_active else "STANDBY"
    }

class SocToggleRequest(BaseModel):
    enabled: Optional[bool] = None

@app.post("/api/soc/toggle", dependencies=[Depends(verify_auth_header)])
def toggle_soc_endpoint(req: Optional[SocToggleRequest] = None):
    if req and req.enabled is not None:
        new_state = soc_orchestrator.set_soc_state(req.enabled)
    else:
        new_state = soc_orchestrator.toggle_soc_state()
    return {
        "success": True,
        "enabled": new_state,
        "status": "ACTIVE" if new_state else "STANDBY",
        "message": f"SOC Security Monitoring is now {'ACTIVE' if new_state else 'IN STANDBY'}."
    }

@app.get("/api/soc/live_telemetry", dependencies=[Depends(verify_auth_header)])
def get_live_telemetry_endpoint():
    return soc_orchestrator.get_live_security_telemetry()

@app.get("/api/soc/live_processes", dependencies=[Depends(verify_auth_header)])
async def get_live_processes_endpoint(limit: int = 100):
    if not soc_orchestrator.is_monitoring_active:
        return []
    return await asyncio.to_thread(live_host_collector.get_live_processes, limit)

@app.get("/api/soc/live_connections", dependencies=[Depends(verify_auth_header)])
async def get_live_connections_endpoint(limit: int = 100):
    if not soc_orchestrator.is_monitoring_active:
        return []
    return await asyncio.to_thread(live_host_collector.get_live_network_connections, limit)

@app.post("/api/soc/audit_host", dependencies=[Depends(verify_auth_header)])
async def audit_host_endpoint():
    return await asyncio.to_thread(soc_orchestrator.run_live_security_audit)

@app.get("/api/soc/rules", dependencies=[Depends(verify_auth_header)])
def list_soc_rules_endpoint():
    return soc_case_memory.list_detection_rules()

@app.get("/api/soc/pending_actions", dependencies=[Depends(verify_auth_header)])
def list_pending_containment_endpoint():
    return soc_guardrail_engine.get_pending_actions()

class SocActionResolveRequest(BaseModel):
    action_id: str
    approved: bool
    approver: str = "HUMAN_OPERATOR"

@app.post("/api/soc/resolve_action", dependencies=[Depends(verify_auth_header)])
def resolve_soc_action_endpoint(req: SocActionResolveRequest):
    if req.approved:
        action = soc_guardrail_engine.pending_actions.get(req.action_id)
        if not action:
            raise HTTPException(status_code=404, detail="Pending action ID not found.")
        soc_guardrail_engine.execute_action(action, approver=req.approver)
        soc_case_memory.add_containment_action(action.case_id, action)
        return {"success": True, "action_id": req.action_id, "status": "APPROVED"}
    else:
        soc_guardrail_engine.reject_action(req.action_id, approver=req.approver)
        return {"success": True, "action_id": req.action_id, "status": "REJECTED"}

class SocActionRollbackRequest(BaseModel):
    action_id: str
    operator: str = "HUMAN_OPERATOR"

@app.post("/api/soc/rollback_action", dependencies=[Depends(verify_auth_header)])
def rollback_soc_action_endpoint(req: SocActionRollbackRequest):
    return soc_guardrail_engine.rollback_action(req.action_id, operator=req.operator)

class SimulateAttackRequest(BaseModel):
    scenario_id: str

@app.get("/api/soc/scenarios", dependencies=[Depends(verify_auth_header)])
def list_attack_scenarios_endpoint():
    return telemetry_generator.list_available_scenarios()

@app.post("/api/soc/simulate", dependencies=[Depends(verify_auth_header)])
def simulate_attack_endpoint(req: SimulateAttackRequest):
    events = telemetry_generator.trigger_attack_scenario(req.scenario_id)
    generated_cases = []
    for ev in events:
        case = soc_orchestrator.process_incoming_security_event(ev)
        if case:
            generated_cases.append(case.case_id)
    return {
        "success": True,
        "scenario_id": req.scenario_id,
        "events_processed": len(events),
        "cases_created": generated_cases
    }

# --- Notes & Productivity Endpoints ---

@app.get("/api/notes", dependencies=[Depends(verify_auth_header)])
async def list_notes_endpoint(query: Optional[str] = None):
    return await smart_memory.list_notes(query)

class NoteCreateRequest(BaseModel):
    title: str
    content: str
    tags: str = ""

@app.post("/api/notes", dependencies=[Depends(verify_auth_header)])
async def create_note_endpoint(req: NoteCreateRequest):
    note_id = await smart_memory.add_note(req.title, req.content, req.tags)
    return {"success": True, "note_id": note_id}

@app.get("/api/reminders", dependencies=[Depends(verify_auth_header)])
async def list_reminders_endpoint():
    return await smart_memory.list_reminders()

class ReminderCreateRequest(BaseModel):
    task: str
    due_time: Optional[str] = None

@app.post("/api/reminders", dependencies=[Depends(verify_auth_header)])
async def create_reminder_endpoint(req: ReminderCreateRequest):
    rem_id = await smart_memory.add_reminder(req.task, req.due_time)
    return {"success": True, "reminder_id": rem_id}

@app.get("/api/history", dependencies=[Depends(verify_auth_header)])
async def get_history_endpoint(limit: int = 20):
    return await smart_memory.get_conversation_history(limit=limit)

class TTSRequest(BaseModel):
    text: str

@app.post("/api/tts", dependencies=[Depends(verify_auth_header)])
async def generate_tts_endpoint(req: TTSRequest):
    audio_bytes = await voice_engine.synthesize_speech_bytes(req.text)
    return Response(content=audio_bytes, media_type="audio/mp3")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
