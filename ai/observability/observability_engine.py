"""Central observability engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .monitoring_config import ObservabilityConfig
from .monitoring_manager import MonitoringManager
from .monitoring_logger import LogLevel
from .monitoring_models import HealthStatus

class ObservabilityEngine:
    def __init__(self, config: Optional[ObservabilityConfig] = None) -> None:
        self._config = config or ObservabilityConfig()
        self._manager = MonitoringManager(self._config)
        self._started = False
    def start(self) -> None:
        if not self._started:
            self._manager.start()
            self._started = True
    def stop(self) -> None:
        if self._started:
            self._manager.stop()
            self._started = False
    def is_running(self) -> bool:
        return self._started
    def log_info(self, message: str, source: str = "") -> Dict[str, Any]:
        return self._manager.log(LogLevel.INFO, message, source)
    def log_error(self, message: str, source: str = "") -> Dict[str, Any]:
        return self._manager.log(LogLevel.ERROR, message, source)
    def log_warning(self, message: str, source: str = "") -> Dict[str, Any]:
        return self._manager.log(LogLevel.WARNING, message, source)
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        self._manager.record_metric(name, value, labels)
    def get_metric(self, name: str) -> Optional[float]:
        return self._manager.get_metric(name)
    def get_status(self) -> Dict[str, Any]:
        return {**self._manager.get_status(), "started": self._started, "config_enabled": self._config.enabled}
    def get_manager(self) -> MonitoringManager:
        return self._manager
    def get_config(self) -> ObservabilityConfig:
        return self._config
