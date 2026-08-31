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
    step: int = 1
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

# ==========================================
# JARVIS-V2: DAG PLANNING & GRAPH MODELS
# ==========================================

class DAGNode(BaseModel):
    node_id: str
    description: str
    agent_name: str
    tool_name: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # list of node_ids
    expected_outcome: Optional[str] = None
    status: ExecutionLifecycleState = ExecutionLifecycleState.PLANNED
    result: Optional[Any] = None
    error: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class DAGTaskPlan(BaseModel):
    plan_id: str
    goal: str
    initiating_agent: str = "orchestrator"
    nodes: Dict[str, DAGNode] = Field(default_factory=dict)
    concurrency_limit: int = 4
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    status: ExecutionLifecycleState = ExecutionLifecycleState.PLANNED
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)

# ==========================================
# JARVIS-V2: DYNAMIC TOOL SYNTHESIS
# ==========================================

class SynthesizedTool(BaseModel):
    tool_id: str
    name: str
    description: str
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    python_code: str
    verified_ast: bool = False
    sandbox_tested: bool = False
    test_results: Optional[Dict[str, Any]] = None
    created_by: str = "coding_agent"
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    execution_count: int = 0

# ==========================================
# JARVIS-V2: VISION 2.0 & SCREEN GROUNDING
# ==========================================

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class VisionGroundingToken(BaseModel):
    token_id: str
    text: str
    bbox: BoundingBox
    element_type: str = "text" # text | button | input | window | icon | alert
    confidence: float = 1.0
    interactive: bool = False

class VisionAnalysisResult(BaseModel):
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    active_window_title: str = "Desktop"
    screen_width: int = 1920
    screen_height: int = 1080
    detected_elements: List[VisionGroundingToken] = Field(default_factory=list)
    ocr_text_summary: str = ""
    detected_errors: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)

# ==========================================
# JARVIS-V2: 4-TIER KNOWLEDGE GRAPH
# ==========================================

class KnowledgeEntity(BaseModel):
    entity_id: str
    name: str
    entity_type: str  # person | project | host | tool | cve | file | preference
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())

class KnowledgeRelation(BaseModel):
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str  # OWNS | USES | LOCATED_IN | AFFECTS | PREFERS | RUNS_ON
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())

# ==========================================
# JARVIS-V2: ACTION JOURNAL & ROLLBACK
# ==========================================

class ActionJournalEntry(BaseModel):
    action_id: str
    agent_name: str
    action_type: str
    description: str
    target_resource: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    snapshot_state: Optional[Dict[str, Any]] = None
    reversible: bool = True
    rollback_handler: Optional[str] = None
    rollback_params: Optional[Dict[str, Any]] = None
    status: str = "EXECUTED" # EXECUTED | ROLLED_BACK | FAILED
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

# ==========================================
# BASE COMMAND & VERIFICATION MODELS
# ==========================================

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
    dag_plan: Optional[DAGTaskPlan] = None
    verification: Optional[VerificationResult] = None
    verification_results: List[VerificationResult] = Field(default_factory=list)
    recovery_actions: List[RecoveryAction] = Field(default_factory=list)
    intent: Optional[str] = None
    confidence: float = 1.0
    audio_base64: Optional[str] = None
    latency_ms: float = 0.0
