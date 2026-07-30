from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import Alert, AlertSeverity, AlertStatus

AlertEvalFn = Callable[[], tuple[bool, float]]


@dataclass
class AlertRule:
    """Defines a rule that produces alerts when conditions are met."""

    name: str
    description: str = ""
    severity: AlertSeverity = AlertSeverity.WARN
    condition: AlertEvalFn | None = None
    labels: dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    cooldown: float = 60.0
    last_fired: float = 0.0

    def evaluate(self, manager: Any) -> None:
        if not self.enabled or not self.condition:
            return

        import time
        now = time.time()
        if (now - self.last_fired) < self.cooldown:
            return

        try:
            is_firing, value = self.condition()
        except Exception:
            return

        if is_firing:
            alert = Alert(
                name=self.name,
                severity=self.severity,
                status=AlertStatus.FIRING,
                message=self.description or f"Alert: {self.name}",
                labels=self.labels,
                value=value,
                threshold=0.0,
            )
            manager.fire(alert)
            self.last_fired = now
        else:
            manager.resolve(self.name)
