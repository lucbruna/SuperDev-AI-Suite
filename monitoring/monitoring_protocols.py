from __future__ import annotations

from typing import Any, Protocol

from .monitoring_models import Alert, LogEntry, MetricSample, TelemetryBatch


class MetricsSource(Protocol):
    async def collect_metrics(self) -> list[MetricSample]: ...


class LogSource(Protocol):
    async def collect_logs(self) -> list[LogEntry]: ...


class AlertChannel(Protocol):
    async def send_alert(self, alert: Alert) -> bool: ...


class ExportTarget(Protocol):
    async def write_batch(self, batch: TelemetryBatch) -> bool: ...


class HealthProbe(Protocol):
    async def probe(self) -> bool: ...


class ObservableComponent(Protocol):
    async def get_status(self) -> dict[str, Any]: ...


__all__ = [
    "MetricsSource", "LogSource", "AlertChannel",
    "ExportTarget", "HealthProbe", "ObservableComponent",
]
