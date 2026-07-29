"""
Core data models for Enterprise AI Core
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"


class AgentType(Enum):
    REACTIVE = "reactive"
    PLANNING = "planning"
    HYBRID = "hybrid"
    WORKFLOW = "workflow"
    CHAT = "chat"
    ANALYSIS = "analysis"
    CODE = "code"
    RESEARCH = "research"


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    PAUSED = "paused"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"
    TRANSFORM = "transform"


class PolicyScope(Enum):
    GLOBAL = "global"
    AGENT = "agent"
    WORKFLOW = "workflow"
    TASK = "task"
    USER = "user"
    RESOURCE = "resource"


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    VECTOR = "vector"
    KNOWLEDGE = "knowledge"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class EventType(Enum):
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_ERROR = "agent.error"
    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    POLICY_VIOLATION = "policy.violation"
    POLICY_EVALUATED = "policy.evaluated"
    DECISION_MADE = "decision.made"
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"
    SECURITY_EVENT = "security.event"
    AUDIT_LOGGED = "audit.logged"
    HEALTH_CHECK = "health.check"
    ERROR = "error"


class Severity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Agent:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: AgentType = AgentType.REACTIVE
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    config: Dict[str, any] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: Optional[datetime] = None
    current_task_id: Optional[UUID] = None
    version: str = "1.0.0"
    health_score: float = 1.0


@dataclass
class Task:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    agent_id: Optional[UUID] = None
    workflow_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    input_data: Dict[str, any] = field(default_factory=dict)
    output_data: Dict[str, any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    dependencies: List[UUID] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent_id: Optional[UUID] = None


@dataclass
class Workflow:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: List[Dict] = field(default_factory=list)
    variables: Dict[str, any] = field(default_factory=dict)
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class Policy:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    scope: PolicyScope = PolicyScope.GLOBAL
    action: PolicyAction = PolicyAction.ALLOW
    conditions: Dict[str, any] = field(default_factory=dict)
    rules: List[Dict] = field(default_factory=list)
    priority: int = 100
    enabled: bool = True
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[UUID] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class PolicyEvaluation:
    policy_id: UUID
    policy_name: str
    action: PolicyAction
    matched: bool
    reason: str = ""
    context: Dict[str, any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Decision:
    id: UUID = field(default_factory=uuid4)
    context: Dict[str, any] = field(default_factory=dict)
    options: List[Dict] = field(default_factory=list)
    selected_option: Optional[Dict] = None
    rationale: str = ""
    confidence: float = 0.0
    policy_evaluations: List[PolicyEvaluation] = field(default_factory=list)
    made_by: Optional[UUID] = None
    made_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class MemoryEntry:
    id: UUID = field(default_factory=uuid4)
    type: MemoryType = MemoryType.SHORT_TERM
    key: str = ""
    value: Any = None
    embedding: Optional[List[float]] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    agent_id: Optional[UUID] = None
    workflow_id: Optional[UUID] = None
    task_id: Optional[UUID] = None


@dataclass
class Event:
    id: UUID = field(default_factory=uuid4)
    type: EventType = EventType.TASK_CREATED
    source_id: Optional[UUID] = None
    source_type: str = ""
    payload: Dict[str, any] = field(default_factory=dict)
    severity: Severity = Severity.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass
class AgentHealth:
    agent_id: UUID
    status: AgentStatus
    health_score: float
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time: float = 0.0
    last_error: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    checks: Dict[str, any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    actor_id: Optional[UUID] = None
    actor_type: str = ""
    action: str = ""
    resource_type: str = ""
    resource_id: Optional[UUID] = None
    outcome: str = "success"
    details: Dict[str, any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    compliance_tags: List[str] = field(default_factory=list)
    severity: Severity = Severity.INFO


@dataclass
class SecurityContext:
    user_id: Optional[UUID] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    mfa_verified: bool = False


@dataclass
class Permission:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    resource: str = ""
    action: str = ""
    conditions: Dict[str, any] = field(default_factory=dict)


@dataclass
class Role:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    permissions: List[UUID] = field(default_factory=list)
    parent_role_id: Optional[UUID] = None
    is_system: bool = False


@dataclass
class WorkflowStep:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: str = "task"
    agent_type: Optional[AgentType] = None
    agent_id: Optional[UUID] = None
    config: Dict[str, any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    condition: Optional[str] = None
    retry_policy: Dict[str, any] = field(default_factory=dict)
    timeout_seconds: int = 300
    depends_on: List[UUID] = field(default_factory=list)
    parallel: bool = False


@dataclass
class WorkflowExecution:
    workflow_id: UUID
    execution_id: UUID = field(default_factory=uuid4)
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    variables: Dict[str, any] = field(default_factory=dict)
    step_results: Dict[str, any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class MetricsSnapshot:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    agent_metrics: Dict[str, any] = field(default_factory=dict)
    workflow_metrics: Dict[str, any] = field(default_factory=dict)
    system_metrics: Dict[str, any] = field(default_factory=dict)
    custom_metrics: Dict[str, any] = field(default_factory=dict)