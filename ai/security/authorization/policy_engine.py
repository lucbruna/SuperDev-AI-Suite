"""Policy engine for authorization rules."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import Any


class Effect(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


class PolicyRule:
    def __init__(self, name: str, effect: Effect, conditions: Callable[..., bool] | None = None) -> None:
        self.name = name
        self.effect = effect
        self.conditions = conditions

    def evaluate(self, context: dict[str, Any]) -> Effect:
        if self.conditions and not self.conditions(context):
            return Effect.DENY
        return self.effect


class PolicyEngine:
    def __init__(self) -> None:
        self._policies: dict[str, PolicyRule] = {}
        self._policy_order: list[str] = []

    def add_policy(self, name: str, effect: Effect, conditions: Callable[..., bool] | None = None) -> None:
        self._policies[name] = PolicyRule(name, effect, conditions)
        self._policy_order.append(name)

    def remove_policy(self, name: str) -> bool:
        if name in self._policies:
            del self._policies[name]
            self._policy_order.remove(name)
            return True
        return False

    def evaluate(self, context: dict[str, Any]) -> Effect:
        for name in self._policy_order:
            rule = self._policies[name]
            result = rule.evaluate(context)
            if result == Effect.DENY:
                return Effect.DENY
        return Effect.ALLOW

    def list_policies(self) -> list[str]:
        return list(self._policy_order)

    def clear(self) -> None:
        self._policies.clear()
        self._policy_order.clear()
