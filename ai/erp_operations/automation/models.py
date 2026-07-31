"""Automation models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class AutomationStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class TriggerType(Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    THRESHOLD = "threshold"


class ActionType(Enum):
    EMAIL = "email"
    API_CALL = "api_call"
    DATA_TRANSFORM = "data_transform"
    NOTIFICATION = "notification"
    SCRIPT = "script"


@dataclass
class AutomationRule:
    rule_id: str
    name: str = ""
    description: str = ""
    status: AutomationStatus = AutomationStatus.INACTIVE
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    created_by: str = ""
    run_count: int = 0
    last_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AutomationExecution:
    execution_id: str
    rule_id: str = ""
    status: str = "success"
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class ScheduledTask:
    task_id: str
    rule_id: str = ""
    cron: str = ""
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    enabled: bool = True


@dataclass
class AutomationMetrics:
    total_executions: int = 0
    success_rate: float = 0.0
    avg_duration_ms: float = 0.0
    active_rules: int = 0
    failed_executions: int = 0
