"""High-level monitoring manager."""
from __future__ import annotations

from typing import Any

from .monitoring_config import ObservabilityConfig
from .monitoring_factory import MonitoringFactory
from .monitoring_logger import LogLevel, MonitoringLogger
from .monitoring_metrics import MetricsCollector


class MonitoringManager:
    def __init__(self, config: ObservabilityConfig | None = None) -> None:
        self._factory = MonitoringFactory(config)
        self._logger = self._factory.create_logger()
        self._metrics = self._factory.create_metrics()
        self._events = self._factory.create_events()
        self._registry = self._factory.create_registry()
        self._runtime = self._factory.create_runtime()
    def log(self, level: LogLevel, message: str, source: str = "") -> dict[str, Any]:
        return self._logger.log(level, message, source)
    def record_metric(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._metrics.record(name, value, labels)
    def get_metric(self, name: str) -> float | None:
        return self._metrics.get_latest(name)
    def register_component(self, name: str, component_type: str = "") -> dict[str, Any]:
        return self._registry.register(name, component_type)
    def get_component_health(self, name: str) -> dict[str, Any] | None:
        return self._registry.get_health(name)
    def start(self) -> None:
        self._runtime.start()
        self._logger.info("Monitoring started", "MonitoringManager")
    def stop(self) -> None:
        self._runtime.stop()
        self._logger.info("Monitoring stopped", "MonitoringManager")
    def get_status(self) -> dict[str, Any]:
        return {"running": self._runtime.is_running(), "components": self._registry.count(), "log_count": self._logger.count(), "metrics": len(self._metrics.get_all_names())}
    def get_logger(self) -> MonitoringLogger:
        return self._logger
    def get_metrics(self) -> MetricsCollector:
        return self._metrics
