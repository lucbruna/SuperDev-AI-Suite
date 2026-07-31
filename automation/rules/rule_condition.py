"""Rule condition adapter implementing the core Rule interface."""

from __future__ import annotations

from typing import Any

from automation.automation_interfaces import Rule
from automation.rules.rule_models import RuleDefinition
from automation.triggers.trigger_evaluator import TriggerEvaluator


class RuleCondition(Rule):
    """Wraps a RuleDefinition for condition matching and consequence."""

    def __init__(self, definition: RuleDefinition,
                 evaluator: TriggerEvaluator | None = None) -> None:
        self.definition = definition
        self.evaluator = evaluator or TriggerEvaluator()

    def matches(self, fact: dict[str, Any]) -> bool:
        if self.definition.condition:
            return self.evaluator.evaluate_condition(
                self.definition.condition, fact)
        if self.definition.predicate:
            return bool(self.definition.predicate(fact))
        return False

    def apply(self, fact: dict[str, Any]) -> Any:
        if self.definition.action is None:
            return None
        return self.definition.action(fact)
