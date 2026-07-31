from __future__ import annotations

import logging
from typing import Any


class AnalyticsAlerts:
    """Alerting rules and their current state."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.alerts")
        self._rules: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"rules": self.list(), "count": len(self._rules)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"rule_id": rule_id, **rule}
            for rule_id, rule in self._rules.items()
        ]

    def create(self, rule: dict[str, Any]) -> str:
        rule_id = f"rule-{len(self._rules) + 1}"
        self._rules[rule_id] = {"enabled": True, **rule}
        return rule_id

    def delete(self, rule_id: str) -> bool:
        return self._rules.pop(rule_id, None) is not None
