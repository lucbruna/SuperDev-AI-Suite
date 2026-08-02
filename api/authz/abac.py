from __future__ import annotations

from typing import Callable


class ABACEngine:
    """Attribute-based access control with per-action predicate rules."""

    def __init__(self) -> None:
        self._rules: dict[str, Callable] = {}

    def add_rule(self, action: str, rule: Callable) -> None:
        self._rules[action] = rule

    def evaluate(self, action: str, user: dict, resource: dict, context: dict) -> bool:
        rule = self._rules.get(action)
        if rule is None:
            return False
        return bool(rule(user, resource, context))

    def remove_rule(self, action: str) -> None:
        self._rules.pop(action, None)

    def to_dict(self) -> dict:
        return {"rules": list(self._rules.keys()), "count": len(self._rules)}
