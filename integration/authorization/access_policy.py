from __future__ import annotations

import logging
from typing import Any


class AccessPolicy:
    """Declarative access policies: conditions over a context dict."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.authorization.policy")
        self._rules: list[dict[str, Any]] = []

    def allow(self, action: str, resource: str = "*", conditions: dict[str, Any] | None = None) -> None:
        self._rules.append(
            {"effect": "allow", "action": action, "resource": resource,
             "conditions": conditions or {}}
        )

    def deny(self, action: str, resource: str = "*", conditions: dict[str, Any] | None = None) -> None:
        self._rules.append(
            {"effect": "deny", "action": action, "resource": resource,
             "conditions": conditions or {}}
        )

    def evaluate(self, action: str, resource: str, context: dict[str, Any] | None = None) -> bool:
        """Evaluates the policy for an action on a resource. Deny wins over allow."""
        context = context or {}
        decision: bool | None = None
        for rule in self._rules:
            if not self._matches(rule, action, resource, context):
                continue
            decision = rule["effect"] == "allow"
        return decision if decision is not None else False

    def check(self, action: str, resource: str, context: dict[str, Any] | None = None) -> None:
        if not self.evaluate(action, resource, context):
            raise PermissionError(f"policy denies {action} on {resource}")

    @staticmethod
    def _matches(rule: dict[str, Any], action: str, resource: str,
                 context: dict[str, Any]) -> bool:
        if rule["action"] != "*" and rule["action"] != action:
            return False
        if rule["resource"] != "*" and rule["resource"] != resource:
            return False
        for key, expected in rule["conditions"].items():
            if context.get(key) != expected:
                return False
        return True

    def rules(self) -> list[dict[str, Any]]:
        return [dict(rule) for rule in self._rules]
