from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import Alert, AlertSeverity, AlertStatus
from .alert_rule import AlertRule


@dataclass
class AlertEvaluatorConfig:
    evaluation_interval: float = 60.0
    cooldown: float = 60.0
    enabled: bool = True


class AlertEvaluator:
    """Runs alert rules on a schedule and fires alerts via manager."""

    def __init__(
        self,
        config: AlertEvaluatorConfig | None = None,
    ) -> None:
        self._config = config or AlertEvaluatorConfig()
        self._rules: list[AlertRule] = []
        self._last_evaluation: float = 0.0

    def add_rule(self, rule: AlertRule) -> None:
        self._rules.append(rule)

    def remove_rule(self, rule_name: str) -> None:
        self._rules = [r for r in self._rules if r.name != rule_name]

    def evaluate(self, manager: Any) -> list[Alert]:
        now = time.time()
        if (now - self._last_evaluation) < self._config.evaluation_interval:
            return []
        self._last_evaluation = now

        fired: list[Alert] = []
        for rule in self._rules:
            if not rule.enabled:
                continue
            if (now - rule.last_fired) < rule.cooldown:
                continue

            result = self._evaluate_rule(rule, manager)
            if result:
                fired.append(result)
        return fired

    def _evaluate_rule(self, rule: AlertRule, manager: Any) -> Alert | None:
        if not rule.condition:
            return None

        try:
            is_firing, value = rule.condition()
        except Exception:
            return None

        if is_firing:
            alert = Alert(
                name=rule.name,
                severity=rule.severity,
                status=AlertStatus.FIRING,
                message=rule.description or f"Alert: {rule.name}",
                labels=dict(rule.labels),
                value=value,
            )
            manager.fire(alert)
            rule.last_fired = time.time()
            return alert
        else:
            manager.resolve(rule.name)
            return None

    def get_rules(self) -> list[AlertRule]:
        return list(self._rules)
