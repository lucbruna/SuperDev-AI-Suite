"""Observability configuration."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field

class MonitoringLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class LoggingConfig:
    level: MonitoringLevel = MonitoringLevel.INFO
    max_entries: int = 100000
    rotation_size_mb: int = 100
    retention_days: int = 30
    enable_console: bool = True
    enable_file: bool = True
    log_dir: str = "logs"

@dataclass
class MetricsConfig:
    collection_interval: int = 10
    max_series: int = 10000
    aggregation_window: int = 60
    export_enabled: bool = False
    export_format: str = "prometheus"

@dataclass
class TracingConfig:
    enabled: bool = True
    sample_rate: float = 0.1
    max_spans: int = 1000
    max_depth: int = 10
    propagation_format: str = "w3c"

@dataclass
class AlertingConfig:
    enabled: bool = True
    check_interval: int = 30
    max_alerts: int = 100
    escalation_enabled: bool = True
    suppression_window: int = 300

@dataclass
class HealthConfig:
    check_interval: int = 60
    timeout: int = 10
    retries: int = 3
    recovery_enabled: bool = True

@dataclass
class ObservabilityConfig:
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    tracing: TracingConfig = field(default_factory=TracingConfig)
    alerting: AlertingConfig = field(default_factory=AlertingConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    enabled: bool = True
    debug_mode: bool = False
