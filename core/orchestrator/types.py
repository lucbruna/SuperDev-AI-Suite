"""Core type definitions for the SuperDev System Orchestrator.

This module defines the foundational types used across all orchestrator
components: service states, lifecycle events, configuration schemas,
and common data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Protocol, TypeVar

T = TypeVar("T")


# ─── Service States ───────────────────────────────────────────────────────────

class ServiceStatus(Enum):
    """Lifecycle status of any managed service in the platform."""
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNKNOWN = "unknown"


class SystemStatus(Enum):
    """Overall platform health status."""
    STARTING = "starting"
    ONLINE = "online"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    CRASHED = "crashed"


class ServiceCategory(Enum):
    """Categories of services managed by the orchestrator."""
    CORE = auto()
    DATABASE = auto()
    CACHE = auto()
    QUEUE = auto()
    API = auto()
    AI = auto()
    AGENT = auto()
    PLUGIN = auto()
    WORKFLOW = auto()
    MONITORING = auto()
    DASHBOARD = auto()
    SCHEDULER = auto()
    INTEGRATION = auto()
    STORAGE = auto()


class EventPriority(Enum):
    """Priority levels for events."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


# ─── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class ServiceInfo:
    """Metadata about a registered service."""
    name: str
    category: ServiceCategory
    version: str = "1.0.0"
    description: str = ""
    status: ServiceStatus = ServiceStatus.CREATED
    dependencies: list[str] = field(default_factory=list)
    health_endpoint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    started_at: str = ""
    error_count: int = 0


@dataclass
class BootConfig:
    """Configuration for the system boot sequence."""
    sequential: bool = False
    timeout_seconds: float = 300.0
    retry_count: int = 3
    health_check_seconds: float = 30.0
    safe_mode: bool = False
    skip_plugins: bool = False
    skip_ai: bool = False
    dry_run: bool = False


@dataclass
class HealthReport:
    """Health status of a single component."""
    service_name: str
    status: ServiceStatus
    is_healthy: bool
    last_heartbeat: float = 0.0
    error_count: int = 0
    response_time_ms: float = 0.0
    message: str = ""


@dataclass
class SystemMetrics:
    """System-wide metrics snapshot."""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    uptime_seconds: float = 0.0
    active_services: int = 0
    total_services: int = 0
    healthy_services: int = 0
    failed_services: int = 0
    events_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    timestamp: str = ""


@dataclass
class SystemEvent:
    """A typed event in the system event bus."""
    event_type: str
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    event_id: str = ""
    timestamp: str = ""
    correlation_id: str = ""
    user_id: str = ""


# ─── Protocols ────────────────────────────────────────────────────────────────

class ServiceLifecycle(Protocol):
    """Protocol that all manageable services must implement."""

    async def initialize(self) -> bool:
        ...

    async def start(self) -> bool:
        ...

    async def stop(self) -> bool:
        ...

    async def health(self) -> HealthReport:
        ...

    async def status(self) -> ServiceStatus:
        ...


# ─── Helper Functions ─────────────────────────────────────────────────────────

def now_iso() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def generate_event_id() -> str:
    """Generate a unique event ID."""
    import uuid
    return uuid.uuid4().hex[:12]
