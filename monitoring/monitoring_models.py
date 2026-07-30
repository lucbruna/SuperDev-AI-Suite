from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SUPPRESSED = "suppressed"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


@dataclass
class MetricSample:
    name: str = ""
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class LogEntry:
    message: str = ""
    level: LogLevel = LogLevel.INFO
    logger: str = ""
    timestamp: float = field(default_factory=time.time)
    trace_id: str = ""
    span_id: str = ""
    correlation_id: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    trace_id: str = ""
    parent_span_id: str = ""
    operation_name: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    status: SpanStatus = SpanStatus.UNSET
    tags: dict[str, str] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    spans: list[Span] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: float = 0.0
    service_name: str = ""


@dataclass
class Alert:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    severity: AlertSeverity = AlertSeverity.INFO
    status: AlertStatus = AlertStatus.FIRING
    message: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    threshold: float = 0.0
    fired_at: float = field(default_factory=time.time)
    resolved_at: float | None = None


@dataclass
class DashboardWidget:
    widget_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    title: str = ""
    widget_type: str = "chart"  # chart, table, stat, heatmap, log
    metric: str = ""
    position: tuple[int, int] = (0, 0)
    size: tuple[int, int] = (1, 1)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckResult:
    component: str = ""
    status: HealthStatus = HealthStatus.HEALTHY
    latency_ms: float = 0.0
    message: str = ""
    dependencies: dict[str, Any] = field(default_factory=dict)
    last_checked: float = field(default_factory=time.time)


@dataclass
class TelemetryBatch:
    metrics: list[MetricSample] = field(default_factory=list)
    logs: list[LogEntry] = field(default_factory=list)
    traces: list[Trace] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    source: str = ""


@dataclass
class ProfilingSample:
    timestamp: float = field(default_factory=time.time)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0
    thread_count: int = 0
    gc_count: int = 0
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class AnomalyScore:
    metric: str = ""
    score: float = 0.0
    baseline: float = 0.0
    current: float = 0.0
    deviation: float = 0.0
    detected_at: float = field(default_factory=time.time)
    is_anomaly: bool = False


@dataclass
class RecoveryAction:
    action_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    action_type: str = ""  # restart, rollback, failover, circuit_break
    target: str = ""
    status: str = "pending"  # pending, running, succeeded, failed
    reason: str = ""
    started_at: float = field(default_factory=time.time)
    completed_at: float | None = None


__all__ = [
    "MetricType", "LogLevel", "AlertSeverity", "AlertStatus",
    "HealthStatus", "SpanStatus",
    "MetricSample", "LogEntry", "Span", "Trace", "Alert",
    "DashboardWidget", "HealthCheckResult", "TelemetryBatch",
    "ProfilingSample", "AnomalyScore", "RecoveryAction",
]
