from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    GUARDRAIL_CHECK = "guardrail_check"
    ERROR = "error"

class AgentThought(BaseModel):
    step: int
    agent_name: str
    thought: str
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    observation: Optional[Any] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    session_id: str = "default"

class ToolCallResult(BaseModel):
    success: bool
    action_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    guardrail_blocked: bool = False
    latency_ms: float = 0.0

class UserCommandRequest(BaseModel):
    command: str
    session_id: str = "default"
    context: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    success: bool = True
    text: str
    agent_used: str = "orchestrator"
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    thoughts: List[AgentThought] = Field(default_factory=list)
    intent: Optional[str] = None
    confidence: float = 1.0
    audio_base64: Optional[str] = None
    latency_ms: float = 0.0
