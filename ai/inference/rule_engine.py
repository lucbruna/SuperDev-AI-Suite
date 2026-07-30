from __future__ import annotations

from typing import Any


class Rule:
    """A single inference rule with conditions and actions."""

    def __init__(
        self,
        name: str,
        conditions: list[dict[str, Any]],
        actions: list[dict[str, Any]],
        priority: int = 0,
    ):
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.priority = priority


class RuleEngine:
    """Rule engine for forward and backward chaining."""

    def __init__(self) -> None:
        self._rules: list[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self._rules.append(rule)

    async def apply(self, rules: list[Rule], facts: list[Any]) -> list[Any]:
        derived = list(facts)
        for rule in sorted(rules, key=lambda r: r.priority, reverse=True):
            if all(self._eval_condition(c, derived) for c in rule.conditions):
                for action in rule.actions:
                    derived.append(action)
        return derived

    async def forward_chain(self, facts: list[Any], rules: list[Rule]) -> list[Any]:
        return await self.apply(rules, facts)

    async def backward_chain(self, goal: Any, rules: list[Rule]) -> list[Any]:
        chain: list[Rule] = []
        for rule in rules:
            if any(a.get("consequent") == goal for a in rule.actions):
                chain.append(rule)
        return chain

    @staticmethod
    def _eval_condition(condition: dict[str, Any], facts: list[Any]) -> bool:
        value = condition.get("value")
        if value is None:
            return True
        return value in facts
