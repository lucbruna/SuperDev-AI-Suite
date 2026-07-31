"""Monitoring abstract interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LogCollectorInterface(ABC):
    @abstractmethod
    def collect(self, entry: dict[str, Any]) -> bool: ...
    @abstractmethod
    def flush(self) -> int: ...


class MetricsProviderInterface(ABC):
    @abstractmethod
    def record(self, name: str, value: float, labels: dict[str, str] | None = None) -> None: ...
    @abstractmethod
    def query(self, name: str, start: float, end: float) -> list[dict[str, Any]]: ...


class TraceProviderInterface(ABC):
    @abstractmethod
    def start_span(self, name: str, trace_id: str = "") -> str: ...
    @abstractmethod
    def end_span(self, span_id: str, status: str = "ok") -> bool: ...
    @abstractmethod
    def get_trace(self, trace_id: str) -> list[dict[str, Any]]: ...


class AlertProviderInterface(ABC):
    @abstractmethod
    def create_alert(self, title: str, severity: str, message: str = "") -> dict[str, Any]: ...
    @abstractmethod
    def resolve_alert(self, alert_id: str) -> bool: ...


class HealthCheckInterface(ABC):
    @abstractmethod
    def check(self, component: str) -> dict[str, Any]: ...
    @abstractmethod
    def check_all(self) -> list[dict[str, Any]]: ...


class DiagnosticsInterface(ABC):
    @abstractmethod
    def diagnose(self, problem: str) -> dict[str, Any]: ...
    @abstractmethod
    def suggest_fix(self, diagnosis: dict[str, Any]) -> list[str]: ...
