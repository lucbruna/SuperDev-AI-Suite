"""Registry of business rules."""

from __future__ import annotations

from typing import Any

from automation.rules.rule_models import RuleDefinition


class RuleManager:
    """Stores rule definitions."""

    def __init__(self) -> None:
        self._rules: dict[str, RuleDefinition] = {}

    def add(self, rule: RuleDefinition) -> None:
        self._rules[rule.rule_id] = rule

    def get(self, rule_id: str) -> RuleDefinition | None:
        return self._rules.get(rule_id)

    def list(self) -> list[RuleDefinition]:
        return list(self._rules.values())

    def ids(self) -> list[str]:
        return list(self._rules)

    def remove(self, rule_id: str) -> bool:
        return self._rules.pop(rule_id, None) is not None

    def set_enabled(self, rule_id: str, enabled: bool) -> bool:
        rule = self._rules.get(rule_id)
        if rule is None:
            return False
        rule.enabled = enabled
        return True
