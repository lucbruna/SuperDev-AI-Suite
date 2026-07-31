"""Access rules definition and evaluation."""

from __future__ import annotations

from enum import Enum
from typing import Any


class AccessAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"


class AccessRule:
    def __init__(
        self,
        name: str,
        user_pattern: str,
        resource_pattern: str,
        action: AccessAction,
        conditions: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.user_pattern = user_pattern
        self.resource_pattern = resource_pattern
        self.action = action
        self.conditions = conditions or {}


class AccessRuleEngine:
    def __init__(self) -> None:
        self._rules: list[AccessRule] = []
        self._default_action = AccessAction.DENY

    def add_rule(
        self,
        name: str,
        user_pattern: str,
        resource_pattern: str,
        action: AccessAction,
        conditions: dict[str, Any] | None = None,
    ) -> AccessRule:
        rule = AccessRule(name, user_pattern, resource_pattern, action, conditions)
        self._rules.append(rule)
        return rule

    def remove_rule(self, name: str) -> bool:
        for i, r in enumerate(self._rules):
            if r.name == name:
                del self._rules[i]
                return True
        return False

    def evaluate(self, user_id: str, resource: str, context: dict[str, Any] | None = None) -> AccessAction:
        for rule in self._rules:
            if self._match(rule.user_pattern, user_id) and self._match(rule.resource_pattern, resource):
                return rule.action
        return self._default_action

    def _match(self, pattern: str, value: str) -> bool:
        if pattern == "*":
            return True
        return value == pattern

    def set_default(self, action: AccessAction) -> None:
        self._default_action = action

    def list_rules(self) -> list[str]:
        return [r.name for r in self._rules]
