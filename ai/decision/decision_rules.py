from __future__ import annotations

from collections.abc import Callable
from typing import Any


class DecisionRule:
    """A single decision rule with condition and action."""

    def __init__(self, name: str, condition: Callable[..., bool], action: Callable[..., Any]):
        self.name = name
        self.condition = condition
        self.action = action

    def evaluate(self, context: dict[str, Any]) -> Any | None:
        try:
            if self.condition(**context):
                return self.action(**context)
        except Exception:
            pass
        return None


class DecisionRules:
    """Collection of decision rules evaluated in order."""

    def __init__(self):
        self._rules: list[DecisionRule] = []

    def add_rule(self, rule: DecisionRule) -> None:
        self._rules.append(rule)

    def evaluate(self, context: dict[str, Any]) -> list[Any]:
        results: list[Any] = []
        for rule in self._rules:
            result = rule.evaluate(context)
            if result is not None:
                results.append({"rule": rule.name, "result": result})
        return results

    def clear(self) -> None:
        self._rules.clear()

    def count(self) -> int:
        return len(self._rules)
