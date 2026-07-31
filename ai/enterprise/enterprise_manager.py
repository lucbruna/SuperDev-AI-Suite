"""High-level enterprise manager."""
from __future__ import annotations

from typing import Any

from .enterprise_config import EnterpriseConfig
from .enterprise_factory import EnterpriseFactory
from .enterprise_logger import EnterpriseLogger, LogLevel
from .enterprise_metrics import EnterpriseMetrics


class EnterpriseManager:
    def __init__(self, config: EnterpriseConfig | None = None) -> None:
        self._factory = EnterpriseFactory(config)
        self._logger = self._factory.create_logger()
        self._metrics = self._factory.create_metrics()
        self._events = self._factory.create_events()
        self._registry = self._factory.create_registry()
        self._runtime = self._factory.create_runtime()
        self._security = self._factory.create_security()
    def log(self, level: LogLevel, message: str, source: str = "") -> dict[str, Any]:
        return self._logger.log(level, message, source)
    def record_metric(self, name: str, value: float) -> None:
        self._metrics.set_gauge(name, value)
    def get_metric(self, name: str) -> float:
        return self._metrics.get_gauge(name)
    def register_component(self, name: str, component_type: str = "") -> dict[str, Any]:
        return self._registry.register(name, component_type)
    def start(self) -> None:
        self._runtime.start()
        self._logger.info("Enterprise engine started", "EnterpriseManager")
    def stop(self) -> None:
        self._runtime.stop()
        self._logger.info("Enterprise engine stopped", "EnterpriseManager")
    def get_status(self) -> dict[str, Any]:
        return {"running": self._runtime.is_running(), "components": self._registry.count(), "log_count": self._logger.count()}
    def get_logger(self) -> EnterpriseLogger:
        return self._logger
    def get_metrics(self) -> EnterpriseMetrics:
        return self._metrics
    def get_security(self) -> Any:
        return self._security
