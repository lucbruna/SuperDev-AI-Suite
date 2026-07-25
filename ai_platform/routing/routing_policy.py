from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuleCondition:
    capability: str | None = None
    model_size: str | None = None
    cost_max: float | None = None
    latency_max: float | None = None


@dataclass
class RuleAction:
    provider: str = ""
    model: str = ""


@dataclass
class Rule:
    conditions: RuleCondition = field(default_factory=RuleCondition)
    action: RuleAction = field(default_factory=RuleAction)
    priority: int = 0


class RoutingPolicy:
    def __init__(self, rules: list[Rule] | None = None):
        self.rules = sorted(rules or [], key=lambda r: r.priority, reverse=True)

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def evaluate(self, context: dict[str, Any]) -> tuple[str, str]:
        capability = context.get("capability", "")
        model_size = context.get("model_size", "medium")
        cost_max = context.get("cost_max", float("inf"))
        latency_max = context.get("latency_max", float("inf"))

        for rule in self.rules:
            c = rule.conditions
            if c.capability and c.capability != capability:
                continue
            if c.cost_max is not None and cost_max > c.cost_max:
                continue
            if c.latency_max is not None and latency_max > c.latency_max:
                continue
            if c.model_size and c.model_size != model_size:
                continue
            return rule.action.provider, rule.action.model

        return context.get("provider", "openai"), context.get("model", "gpt-4o")
