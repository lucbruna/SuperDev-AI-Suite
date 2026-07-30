from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Protocol

from .monitoring_models import (
    Alert,
    DashboardWidget,
    HealthCheckResult,
    LogEntry,
    MetricSample,
    Span,
    TelemetryBatch,
    Trace,
)


class IMetricsCollector(ABC):
    @abstractmethod
    def record(self, sample: MetricSample) -> None: ...
    @abstractmethod
    def get_snapshot(self) -> list[MetricSample]: ...
    @abstractmethod
    def reset(self) -> None: ...


class ILogCollector(ABC):
    @abstractmethod
    async def emit(self, entry: LogEntry) -> None: ...
    @abstractmethod
    async def query(self, query: str, limit: int = 100) -> list[LogEntry]: ...


class ITracer(ABC):
    @abstractmethod
    def start_span(self, operation: str, trace_id: str = "") -> Span: ...
    @abstractmethod
    def end_span(self, span: Span) -> None: ...
    @abstractmethod
    def get_trace(self, trace_id: str) -> Trace | None: ...


class IAlertEngine(ABC):
    @abstractmethod
    async def evaluate(self, metric: MetricSample) -> list[Alert]: ...
    @abstractmethod
    async def notify(self, alert: Alert) -> None: ...


class IHealthChecker(ABC):
    @abstractmethod
    async def check(self) -> HealthCheckResult: ...
    @abstractmethod
    async def check_readiness(self) -> bool: ...
    @abstractmethod
    async def check_liveness(self) -> bool: ...


class IStorageBackend(ABC):
    @abstractmethod
    async def store_metrics(self, batch: list[MetricSample]) -> None: ...
    @abstractmethod
    async def store_logs(self, batch: list[LogEntry]) -> None: ...
    @abstractmethod
    async def store_traces(self, batch: list[Trace]) -> None: ...
    @abstractmethod
    async def query_metrics(self, query: str) -> list[MetricSample]: ...
    @abstractmethod
    async def query_logs(self, query: str) -> list[LogEntry]: ...


class IDashboardEngine(ABC):
    @abstractmethod
    async def render(self, dashboard_id: str) -> dict[str, Any]: ...
    @abstractmethod
    def register_widget(self, widget: DashboardWidget) -> None: ...


class IAnomalyDetector(ABC):
    @abstractmethod
    async def analyze(self, sample: MetricSample) -> float: ...
    @abstractmethod
    def get_threshold(self, metric: str) -> float: ...


class IRecoveryEngine(ABC):
    @abstractmethod
    async def execute(self, action_type: str, target: str) -> str: ...
    @abstractmethod
    async def status(self, action_id: str) -> str: ...


class ITelemetryExporter(ABC):
    @abstractmethod
    async def export(self, batch: TelemetryBatch) -> bool: ...
    @abstractmethod
    async def health(self) -> bool: ...


class IProfiler(ABC):
    @abstractmethod
    async def snapshot(self) -> dict[str, Any]: ...
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...


# -- Protocols ---------------------------------------------------------------

class CollectableProtocol(Protocol):
    async def collect(self) -> list[MetricSample]: ...


class ExportableProtocol(Protocol):
    async def export(self, batch: TelemetryBatch) -> bool: ...


class AlertableProtocol(Protocol):
    async def alert(self, alert: Alert) -> None: ...


class RecoverableProtocol(Protocol):
    async def recover(self) -> bool: ...


class ObservableProtocol(Protocol):
    async def observe(self) -> dict[str, Any]: ...


__all__ = [
    "IMetricsCollector", "ILogCollector", "ITracer", "IAlertEngine",
    "IHealthChecker", "IStorageBackend", "IDashboardEngine",
    "IAnomalyDetector", "IRecoveryEngine", "ITelemetryExporter", "IProfiler",
    "CollectableProtocol", "ExportableProtocol", "AlertableProtocol",
    "RecoverableProtocol", "ObservableProtocol",
]
