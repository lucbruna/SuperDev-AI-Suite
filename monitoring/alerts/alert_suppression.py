from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from ..monitoring_models import Alert


@dataclass
class SuppressionRule:
    name: str = ""
    matcher: dict[str, str] = field(default_factory=dict)  # label key: value
    duration: float = 3600.0  # 1 hour
    reason: str = ""


class AlertSuppression:
    """Suppresses alerts matching defined rules."""

    def __init__(self) -> None:
        self._rules: list[SuppressionRule] = []
        self._suppressed_until: dict[str, float] = {}

    def add_rule(self, rule: SuppressionRule) -> None:
        self._rules.append(rule)

    def remove_rule(self, name: str) -> None:
        self._rules = [r for r in self._rules if r.name != name]

    def should_suppress(self, alert: Alert) -> bool:
        now = time.time()

        if alert.name in self._suppressed_until:
            if now < self._suppressed_until[alert.name]:
                return True
            del self._suppressed_until[alert.name]

        for rule in self._rules:
            if self._matches(alert, rule):
                self._suppressed_until[alert.name] = now + rule.duration
                return True
        return False

    def _matches(self, alert: Alert, rule: SuppressionRule) -> bool:
        for key, value in rule.matcher.items():
            if key == "name" and alert.name != value:
                return False
            if key == "severity" and alert.severity.value != value:
                return False
            if key.startswith("label:"):
                label_key = key[6:]
                if alert.labels.get(label_key) != value:
                    return False
        return True

    def unsuppress(self, alert_name: str) -> None:
        self._suppressed_until.pop(alert_name, None)

    def clear(self) -> None:
        self._suppressed_until.clear()
