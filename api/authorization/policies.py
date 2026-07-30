from __future__ import annotations

import re
from typing import Any, Callable


class Policy:
    """A single authorization policy with effect, actions, resources, and conditions."""

    def __init__(
        self,
        name: str,
        effect: str = "DENY",
        actions: list[str] | None = None,
        resources: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.effect = effect.upper()  # ALLOW or DENY
        self.actions = actions or ["*"]
        self.resources = resources or ["*"]
        self.conditions = conditions or {}
        self.description = description
        self._priority = 100 if self.effect == "DENY" else 50

    def applies_to(self, action: str, resource: str) -> bool:
        return (self._matches(self.actions, action) and self._matches(self.resources, resource))

    def _matches(self, patterns: list[str], value: str) -> bool:
        for pattern in patterns:
            if pattern == "*":
                return True
            if pattern.endswith("*") and value.startswith(pattern[:-1]):
                return True
            if pattern.startswith("*") and value.endswith(pattern[1:]):
                return True
            if pattern == value:
                return True
        return False

    def evaluate_conditions(self, context: dict[str, Any]) -> bool:
        for cond_key, cond_value in self.conditions.items():
            context_value = context.get(cond_key)
            if isinstance(cond_value, dict):
                for op, expected in cond_value.items():
                    if not self._evaluate_condition(op, context_value, expected):
                        return False
            elif context_value != cond_value:
                return False
        return True

    def _evaluate_condition(self, op: str, actual: Any, expected: Any) -> bool:
        op_map = {
            "eq": lambda a, e: a == e,
            "neq": lambda a, e: a != e,
            "gt": lambda a, e: a is not None and a > e,
            "gte": lambda a, e: a is not None and a >= e,
            "lt": lambda a, e: a is not None and a < e,
            "lte": lambda a, e: a is not None and a <= e,
            "contains": lambda a, e: a is not None and e in a,
            "in": lambda a, e: a in e if e else False,
            "not_in": lambda a, e: a not in e if e else True,
            "regex": lambda a, e: bool(re.match(e, str(a))) if a else False,
        }
        fn = op_map.get(op)
        if fn is None:
            return True
        try:
            return fn(actual, expected)
        except (TypeError, ValueError, re.error):
            return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "effect": self.effect,
            "actions": self.actions,
            "resources": self.resources,
            "priority": self._priority,
            "description": self.description,
        }


class PolicyBuilder:
    """Fluent builder for creating Policy objects."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._effect = "DENY"
        self._actions: list[str] = []
        self._resources: list[str] = []
        self._conditions: dict[str, Any] = {}
        self._description = ""

    def allow(self) -> PolicyBuilder:
        self._effect = "ALLOW"
        return self

    def deny(self) -> PolicyBuilder:
        self._effect = "DENY"
        return self

    def actions(self, *actions: str) -> PolicyBuilder:
        self._actions = list(actions)
        return self

    def resources(self, *resources: str) -> PolicyBuilder:
        self._resources = list(resources)
        return self

    def condition(self, key: str, value: Any) -> PolicyBuilder:
        self._conditions[key] = value
        return self

    def describe(self, description: str) -> PolicyBuilder:
        self._description = description
        return self

    def build(self) -> Policy:
        return Policy(
            name=self._name,
            effect=self._effect,
            actions=self._actions,
            resources=self._resources,
            conditions=self._conditions,
            description=self._description,
        )


class PolicyEngine:
    """Evaluates multiple policies to reach an authorization decision."""

    def __init__(self) -> None:
        self._policies: list[Policy] = []

    def add(self, policy: Policy) -> None:
        self._policies.append(policy)

    def evaluate(self, action: str, resource: str, context: dict[str, Any] | None = None) -> bool:
        context = context or {}
        applicable = [p for p in self._policies if p.applies_to(action, resource)]
        applicable.sort(key=lambda p: p._priority, reverse=True)

        for policy in applicable:
            if policy.evaluate_conditions(context):
                return policy.effect == "ALLOW"

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "policies": [p.to_dict() for p in self._policies],
            "count": len(self._policies),
        }
