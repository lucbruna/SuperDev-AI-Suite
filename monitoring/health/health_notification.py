from __future__ import annotations

import logging
from typing import Any, Callable

from ..monitoring_models import HealthStatus


class HealthNotification:
    """Notifies handlers when health status changes."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[str, HealthStatus, str], None]] = []
        self._logger = logging.getLogger("superdev.health")

    def on_change(self, handler: Callable[[str, HealthStatus, str], None]) -> None:
        self._handlers.append(handler)

    def notify(self, component: str, status: HealthStatus, message: str = "") -> None:
        for handler in self._handlers:
            try:
                handler(component, status, message)
            except Exception as e:
                self._logger.error("Health notification handler error: %s", e)

        self._log(component, status, message)

    def _log(self, component: str, status: HealthStatus, message: str) -> None:
        log_msg = f"Health [{status.value.upper()}] {component}: {message}"
        if status == HealthStatus.UNHEALTHY:
            self._logger.error(log_msg)
        elif status == HealthStatus.DEGRADED:
            self._logger.warning(log_msg)
        else:
            self._logger.info(log_msg)
