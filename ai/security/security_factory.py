"""Security factory for creating security components."""
from __future__ import annotations

from typing import Any

from .security_config import SecurityConfig
from .security_context import SecurityContext
from .security_events import SecurityEvents
from .security_logger import SecurityLogger
from .security_metrics import SecurityMetrics
from .security_registry import SecurityRegistry
from .security_runtime import SecurityRuntime


class SecurityFactory:
    """Factory for creating and configuring security components."""

    def __init__(self, config: SecurityConfig | None = None) -> None:
        self._config = config or SecurityConfig()
        self._events = SecurityEvents()
        self._metrics = SecurityMetrics()
        self._logger = SecurityLogger(self._config.audit.log_level)
        self._registry = SecurityRegistry()
        self._runtime = SecurityRuntime()

    def create_context(self) -> SecurityContext:
        return SecurityContext()

    def create_events(self) -> SecurityEvents:
        return self._events

    def create_metrics(self) -> SecurityMetrics:
        return self._metrics

    def create_logger(self) -> SecurityLogger:
        return self._logger

    def create_registry(self) -> SecurityRegistry:
        return self._registry

    def create_runtime(self) -> SecurityRuntime:
        return self._runtime

    def get_config(self) -> SecurityConfig:
        return self._config

    def snapshot(self) -> dict[str, Any]:
        return {
            "config_level": self._config.level.value,
            "registry": self._registry.count(),
            "runtime": self._runtime.snapshot(),
            "log_count": self._logger.count(),
        }
