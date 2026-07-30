from __future__ import annotations

from typing import Any

from .monitoring_models import (
    Alert,
    LogEntry,
    MetricSample,
    ProfilingSample,
    TelemetryBatch,
    Trace,
)


class MonitoringRepository:
    """In-memory repository for monitoring data.

    Swappable with a persistent backend (Prometheus, Loki, etc.) behind the
    :class:`IStorageBackend` interface.
    """

    def __init__(self) -> None:
        self._metrics: list[MetricSample] = []
        self._logs: list[LogEntry] = []
        self._traces: dict[str, Trace] = {}
        self._alerts: list[Alert] = []
        self._profiles: list[ProfilingSample] = []

    # -- metrics -------------------------------------------------------------

    def store_metric(self, sample: MetricSample) -> None:
        self._metrics.append(sample)

    def query_metrics(self, name: str | None = None, limit: int = 100) -> list[MetricSample]:
        if name:
            return [m for m in self._metrics if m.name == name][-limit:]
        return self._metrics[-limit:]

    # -- logs ----------------------------------------------------------------

    def store_log(self, entry: LogEntry) -> None:
        self._logs.append(entry)

    def query_logs(self, level: str | None = None, limit: int = 100) -> list[LogEntry]:
        if level:
            return [e for e in self._logs if e.level.value == level][-limit:]
        return self._logs[-limit:]

    # -- traces --------------------------------------------------------------

    def store_trace(self, trace: Trace) -> None:
        self._traces[trace.trace_id] = trace

    def get_trace(self, trace_id: str) -> Trace | None:
        return self._traces.get(trace_id)

    # -- alerts --------------------------------------------------------------

    def store_alert(self, alert: Alert) -> None:
        self._alerts.append(alert)

    def query_alerts(self, status: str | None = None, limit: int = 50) -> list[Alert]:
        if status:
            return [a for a in self._alerts if a.status.value == status][-limit:]
        return self._alerts[-limit:]

    # -- profiles ------------------------------------------------------------

    def store_profile(self, sample: ProfilingSample) -> None:
        self._profiles.append(sample)

    def query_profiles(self, limit: int = 50) -> list[ProfilingSample]:
        return self._profiles[-limit:]

    # -- batch ---------------------------------------------------------------

    def store_batch(self, batch: TelemetryBatch) -> None:
        for m in batch.metrics:
            self.store_metric(m)
        for l in batch.logs:
            self.store_log(l)
        for t in batch.traces:
            self.store_trace(t)

    # -- maintenance ---------------------------------------------------------

    def clear(self) -> None:
        self._metrics.clear()
        self._logs.clear()
        self._traces.clear()
        self._alerts.clear()
        self._profiles.clear()


__all__ = ["MonitoringRepository"]
