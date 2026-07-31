"""Monitoring component factory."""
from __future__ import annotations

from .monitoring_config import ObservabilityConfig
from .monitoring_context import MonitoringContext
from .monitoring_events import MonitoringEvents
from .monitoring_logger import MonitoringLogger
from .monitoring_metrics import MetricsCollector
from .monitoring_registry import MonitoringRegistry
from .monitoring_runtime import MonitoringRuntime


class MonitoringFactory:
    def __init__(self, config: ObservabilityConfig | None = None) -> None:
        self._config = config or ObservabilityConfig()
        self._logger: MonitoringLogger | None = None
        self._metrics: MetricsCollector | None = None
        self._events: MonitoringEvents | None = None
        self._context: MonitoringContext | None = None
        self._registry: MonitoringRegistry | None = None
        self._runtime: MonitoringRuntime | None = None
    def create_logger(self) -> MonitoringLogger:
        if not self._logger:
            self._logger = MonitoringLogger(self._config.logging.max_entries)
        return self._logger
    def create_metrics(self) -> MetricsCollector:
        if not self._metrics:
            self._metrics = MetricsCollector(self._config.metrics.max_series)
        return self._metrics
    def create_events(self) -> MonitoringEvents:
        if not self._events:
            self._events = MonitoringEvents()
        return self._events
    def create_context(self) -> MonitoringContext:
        if not self._context:
            self._context = MonitoringContext()
        return self._context
    def create_registry(self) -> MonitoringRegistry:
        if not self._registry:
            self._registry = MonitoringRegistry()
        return self._registry
    def create_runtime(self) -> MonitoringRuntime:
        if not self._runtime:
            self._runtime = MonitoringRuntime()
        return self._runtime
    def get_config(self) -> ObservabilityConfig:
        return self._config
