"""Orders rules by priority."""

from __future__ import annotations

from typing import Any

from automation.rules.rule_condition import RuleCondition
from automation.triggers.trigger_evaluator import TriggerEvaluator


class RulePrioritizer:
    """Sorts rules for evaluation order and conflict resolution."""

    def __init__(self, evaluator: TriggerEvaluator | None = None) -> None:
        self.evaluator = evaluator or TriggerEvaluator()

    def sort(self, rules: list[Any]) -> list[Any]:
        """Returns rules sorted by descending priority (stable)."""
        return sorted(rules, key=lambda r: r.priority, reverse=True)

    def first_match(self, fact: dict[str, Any],
                    rules: list[Any]) -> Any | None:
        """Returns the highest-priority rule matching the facts, or None."""
        for rule in self.sort(rules):
            if RuleCondition(rule, self.evaluator).matches(fact):
                return rule
        return None
