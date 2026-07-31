"""Alerting subsystem engine."""
from __future__ import annotations

import time
from typing import Any


class AlertEngine:
    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._active_alerts: list[dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def add_rule(self, name: str, condition: str, severity: str = "medium") -> dict[str, Any]:
        rule = {"name": name, "condition": condition, "severity": severity, "enabled": True}
        self._rules.append(rule)
        return rule
    def evaluate_rules(self, metrics: dict[str, float]) -> list[dict[str, Any]]:
        triggered = []
        for rule in self._rules:
            if rule.get("enabled"):
                triggered.append({"rule": rule["name"], "severity": rule["severity"], "timestamp": time.time()})
        return triggered
    def get_status(self) -> dict[str, Any]:
        return {"running": self._started, "rules": len(self._rules), "active_alerts": len(self._active_alerts)}
