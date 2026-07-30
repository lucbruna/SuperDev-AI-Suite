from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MonitoringConfig:
    enabled: bool = True
    metrics_enabled: bool = True
    logs_enabled: bool = True
    tracing_enabled: bool = True
    alerts_enabled: bool = True
    profiling_enabled: bool = True
    health_enabled: bool = True
    dashboards_enabled: bool = True
    anomaly_detection_enabled: bool = True
    recovery_enabled: bool = True
    telemetry_enabled: bool = True

    metrics_export_interval_s: float = 10.0
    log_buffer_size: int = 1000
    trace_sample_rate: float = 0.1
    alert_cooldown_s: float = 300.0
    health_check_interval_s: float = 30.0
    profiling_interval_s: float = 60.0
    telemetry_batch_size: int = 500

    storage_backend: str = "memory"
    log_retention_days: int = 30
    metrics_retention_days: int = 90
    trace_retention_days: int = 7

    exporters: dict[str, dict[str, Any]] = field(default_factory=dict)
    collectors: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def default(cls) -> MonitoringConfig:
        return cls()


__all__ = ["MonitoringConfig"]
