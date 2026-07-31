"""Monitoring data models."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class LogEntry:
    timestamp: float = field(default_factory=time.time)
    level: LogLevel = LogLevel.INFO
    source: str = ""
    message: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

@dataclass
class MetricPoint:
    name: str = ""
    value: float = 0.0
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"

@dataclass
class TraceSpan:
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trace_id: str = ""
    parent_span_id: str = ""
    name: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    status: str = "ok"
    attributes: dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    severity: AlertSeverity = AlertSeverity.LOW
    title: str = ""
    message: str = ""
    source: str = ""
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class HealthCheck:
    component: str = ""
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    latency_ms: float = 0.0
    checked_at: float = field(default_factory=time.time)

@dataclass
class Incident:
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    severity: AlertSeverity = AlertSeverity.LOW
    status: str = "open"
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    description: str = ""
    timeline: list[dict[str, Any]] = field(default_factory=list)
