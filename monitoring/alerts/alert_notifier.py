from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from ..monitoring_models import Alert


class AlertNotifier(ABC):
    """Abstract base for alert notification channels."""

    @abstractmethod
    def notify(self, alert: Alert) -> None: ...


class LogAlertNotifier(AlertNotifier):
    """Logs alert events via standard logging."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("superdev.alerts")

    def notify(self, alert: Alert) -> None:
        self._logger.warning(
            "ALERT [%s] %s: %s (value=%.2f, threshold=%.2f)",
            alert.severity.value.upper(),
            alert.name,
            alert.message,
            alert.value,
            alert.threshold,
        )


class ConsoleAlertNotifier(AlertNotifier):
    """Prints alert notifications to stdout."""

    def notify(self, alert: Alert) -> None:
        print(
            f"[{alert.severity.value.upper()}] {alert.name}: "
            f"{alert.message} (value={alert.value:.2f})"
        )


class CallbackAlertNotifier(AlertNotifier):
    """Calls an arbitrary function when an alert fires."""

    def __init__(self, callback: Any) -> None:
        self._callback = callback

    def notify(self, alert: Alert) -> None:
        self._callback(alert)


class MultiAlertNotifier(AlertNotifier):
    """Dispatches to multiple notifiers."""

    def __init__(self, notifiers: list[AlertNotifier] | None = None) -> None:
        self._notifiers: list[AlertNotifier] = notifiers or []

    def add(self, notifier: AlertNotifier) -> None:
        self._notifiers.append(notifier)

    def notify(self, alert: Alert) -> None:
        for notifier in self._notifiers:
            try:
                notifier.notify(alert)
            except Exception:
                pass
