from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    THINKING = "thinking"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    GUARDRAIL_CHECK = "guardrail_check"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    ERROR = "error"

class ExecutionLifecycleState(str, Enum):
    PLANNED = "planned"
    ATTEMPTING = "attempting"
    EXECUTED = "executed"
    VERIFIED = "verified"
    RECOVERED = "recovered"
    FAILED = "failed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"

class AgentThought(BaseModel):
    step: int
    agent_name: str
    thought: str
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    observation: Optional[Any] = None
    state: ExecutionLifecycleState = ExecutionLifecycleState.EXECUTED
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class PlanStep(BaseModel):
    step_number: int
    description: str
    agent_name: str
    tool_name: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    expected_outcome: Optional[str] = None
    status: ExecutionLifecycleState = ExecutionLifecycleState.PLANNED
    result: Optional[Any] = None
    error: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None

class TaskPlan(BaseModel):
    plan_id: str
    goal: str
    initiating_agent: str
    steps: List[PlanStep] = Field(default_factory=list)
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    is_multi_agent: bool = False

class VerificationResult(BaseModel):
    verified: bool
    verdict: str
    details: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0

class RecoveryAction(BaseModel):
    original_tool: str
    error_encountered: str
    recovery_strategy: str
    fallback_tool: Optional[str] = None
    adjusted_params: Optional[Dict[str, Any]] = None
    recovered: bool = False

class SafetyTier(str, Enum):
    TIER_1_SAFE = "tier_1_safe"            # Read-only queries, telemetry, conversions
    TIER_2_SENSITIVE = "tier_2_sensitive"  # Non-destructive writes (notes, reminders)
    TIER_3_DANGEROUS = "tier_3_dangerous"  # Shell execution, kill process, code write, containment
    BLOCKED = "blocked"                    # Malicious or fatal commands (always rejected)

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
    verification: Optional[VerificationResult] = None
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
    plan: Optional[TaskPlan] = None
    task_plan: Optional[TaskPlan] = None
    verification: Optional[VerificationResult] = None
    verification_results: List[VerificationResult] = Field(default_factory=list)
    recovery_actions: List[RecoveryAction] = Field(default_factory=list)
    intent: Optional[str] = None
    confidence: float = 1.0
    audio_base64: Optional[str] = None
    latency_ms: float = 0.0

