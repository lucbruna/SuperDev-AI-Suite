"""Alerting subsystem engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class AlertEngine:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
        self._active_alerts: List[Dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def add_rule(self, name: str, condition: str, severity: str = "medium") -> Dict[str, Any]:
        rule = {"name": name, "condition": condition, "severity": severity, "enabled": True}
        self._rules.append(rule)
        return rule
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        triggered = []
        for rule in self._rules:
            if rule.get("enabled"):
                triggered.append({"rule": rule["name"], "severity": rule["severity"], "timestamp": time.time()})
        return triggered
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "rules": len(self._rules), "active_alerts": len(self._active_alerts)}
