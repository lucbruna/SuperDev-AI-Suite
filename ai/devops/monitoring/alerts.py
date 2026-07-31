"""Alert manager."""

from __future__ import annotations

import time
from typing import Any


class AlertManager:
    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}
        self._alerts: list[dict[str, Any]] = []

    def create_rule(
        self, name: str, condition: str, severity: str = "warning", channels: list[str] = None
    ) -> dict[str, Any]:
        rule = {
            "name": name,
            "condition": condition,
            "severity": severity,
            "channels": channels or ["email"],
            "enabled": True,
        }
        self._rules[name] = rule
        return rule

    def trigger(self, rule_name: str, message: str = "") -> dict[str, Any]:
        if rule_name not in self._rules:
            return {"error": "not_found"}
        rule = self._rules[rule_name]
        alert = {"rule": rule_name, "severity": rule["severity"], "message": message, "timestamp": time.time()}
        self._alerts.append(alert)
        return alert

    def get_alerts(self, severity: str = "", limit: int = 50) -> list[dict[str, Any]]:
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        return alerts[-limit:]

    def list_rules(self) -> list[dict[str, Any]]:
        return list(self._rules.values())

    def acknowledge(self, alert_index: int) -> bool:
        if 0 <= alert_index < len(self._alerts):
            self._alerts[alert_index]["acknowledged"] = True
            return True
        return False

    def count(self) -> int:
        return len(self._alerts)
