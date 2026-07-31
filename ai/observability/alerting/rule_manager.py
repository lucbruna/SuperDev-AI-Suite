"""Alert rule management."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class AlertRule:
    def __init__(self, name: str, condition: Callable[[dict[str, float]], bool], severity: str = "medium") -> None:
        self.name = name
        self.condition = condition
        self.severity = severity
        self.enabled = True
        self.trigger_count = 0
        self.last_triggered = 0.0


class RuleManager:
    def __init__(self) -> None:
        self._rules: dict[str, AlertRule] = {}

    def add_rule(self, name: str, condition: Callable[[dict[str, float]], bool], severity: str = "medium") -> AlertRule:
        rule = AlertRule(name, condition, severity)
        self._rules[name] = rule
        return rule

    def remove_rule(self, name: str) -> bool:
        if name in self._rules:
            del self._rules[name]
            return True
        return False

    def enable_rule(self, name: str) -> bool:
        if name in self._rules:
            self._rules[name].enabled = True
            return True
        return False

    def disable_rule(self, name: str) -> bool:
        if name in self._rules:
            self._rules[name].enabled = False
            return True
        return False

    def evaluate(self, metrics: dict[str, float]) -> list[dict[str, Any]]:
        triggered = []
        for rule in self._rules.values():
            if rule.enabled:
                try:
                    if rule.condition(metrics):
                        rule.trigger_count += 1
                        rule.last_triggered = time.time()
                        triggered.append(
                            {"name": rule.name, "severity": rule.severity, "trigger_count": rule.trigger_count}
                        )
                except Exception:
                    pass
        return triggered

    def list_rules(self) -> list[dict[str, Any]]:
        return [
            {"name": r.name, "severity": r.severity, "enabled": r.enabled, "trigger_count": r.trigger_count}
            for r in self._rules.values()
        ]
