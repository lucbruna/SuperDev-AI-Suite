from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import Alert, AlertSeverity, AlertStatus

EscalationAction = Callable[[Alert], None]


@dataclass
class EscalationLevel:
    level: int = 1
    after_seconds: float = 300.0  # 5 minutes
    severity: AlertSeverity = AlertSeverity.WARN
    notify: list[str] = field(default_factory=list)
    action: EscalationAction | None = None


class AlertEscalation:
    """Escalates unresolved alerts through severity levels over time."""

    def __init__(self) -> None:
        self._levels: list[EscalationLevel] = []
        self._escalated: dict[str, int] = {}

    def add_level(self, level: EscalationLevel) -> None:
        self._levels.append(level)

    def process(self, alert: Alert) -> Alert | None:
        if alert.status != AlertStatus.FIRING:
            return None

        now = time.time()
        elapsed = now - alert.fired_at
        current_level = self._escalated.get(alert.name, 0)

        for level in self._levels:
            if level.level > current_level and elapsed >= level.after_seconds:
                alert.severity = level.severity
                self._escalated[alert.name] = level.level
                if level.action:
                    level.action(alert)
                return alert
        return None

    def reset(self, alert_name: str) -> None:
        self._escalated.pop(alert_name, None)
