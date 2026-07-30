from __future__ import annotations

from typing import Any


class AlertManager:
    """Manages alert rules and generates alerts."""

    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}
        self._alerts: list[dict[str, Any]] = []

    def add_rule(self, name: str, condition: str, severity: str = "medium") -> str:
        self._rules[name] = {"name": name, "condition": condition, "severity": severity}
        return name

    def get_rule(self, name: str) -> dict[str, Any] | None:
        return self._rules.get(name)

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    def check_rules(self, metrics: dict[str, float]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for rule in self._rules.values():
            metric_name = rule["condition"].split()[0] if rule["condition"] else ""
            if metric_name in metrics:
                results.append({
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "triggered": True,
                    "metric_value": metrics[metric_name],
                })
        self._alerts.extend(results)
        return results

    @property
    def alert_count(self) -> int:
        return len(self._alerts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rules": list(self._rules.values()),
            "alerts": self._alerts,
            "rule_count": self.rule_count,
        }
