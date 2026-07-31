"""Rule engine: facade for the rules subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.rules.rule_condition import RuleCondition
from automation.rules.rule_history import RuleHistory
from automation.rules.rule_manager import RuleManager
from automation.rules.rule_models import RuleDefinition, RuleResult
from automation.rules.rule_prioritizer import RulePrioritizer
from automation.triggers.trigger_evaluator import TriggerEvaluator


class RuleEngine:
    """Registers rules and fires them against facts."""

    def __init__(self, manager: RuleManager | None = None,
                 prioritizer: RulePrioritizer | None = None,
                 history: RuleHistory | None = None,
                 evaluator: TriggerEvaluator | None = None) -> None:
        self.manager = manager or RuleManager()
        self.prioritizer = prioritizer or RulePrioritizer()
        self.history = history or RuleHistory()
        self.evaluator = evaluator or TriggerEvaluator()

    # -- registration ------------------------------------------------------
    def add_rule(self, rule_id: str, name: str,
                 condition: dict[str, Any] | None = None,
                 predicate: Callable[[dict[str, Any]], bool] | None = None,
                 action: Callable[[dict[str, Any]], Any] | None = None,
                 priority: int = 0,
                 params: dict[str, Any] | None = None) -> RuleDefinition:
        rule = RuleDefinition(rule_id=rule_id, name=name,
                              condition=condition, predicate=predicate,
                              action=action, priority=priority,
                              params=params or {})
        self.manager.add(rule)
        return rule

    def add(self, rule: RuleDefinition) -> None:
        self.manager.add(rule)

    def get(self, rule_id: str) -> RuleDefinition | None:
        return self.manager.get(rule_id)

    def list(self) -> list[str]:
        return self.manager.ids()

    def remove(self, rule_id: str) -> bool:
        return self.manager.remove(rule_id)

    def enable(self, rule_id: str) -> bool:
        return self.manager.set_enabled(rule_id, True)

    def disable(self, rule_id: str) -> bool:
        return self.manager.set_enabled(rule_id, False)

    # -- evaluation --------------------------------------------------------
    def evaluate(self, fact: dict[str, Any]) -> list[str]:
        """Returns ids of enabled rules matching the facts (priority order)."""
        matched: list[str] = []
        rules = [r for r in self.manager.list() if r.enabled]
        for rule in self.prioritizer.sort(rules):
            if RuleCondition(rule, self.evaluator).matches(fact):
                matched.append(rule.rule_id)
        return matched

    def fire(self, fact: dict[str, Any]) -> list[RuleResult]:
        """Applies all matching rules and returns their results."""
        results: list[RuleResult] = []
        rules = [r for r in self.manager.list() if r.enabled]
        for rule in self.prioritizer.sort(rules):
            condition = RuleCondition(rule, self.evaluator)
            if not condition.matches(fact):
                self.history.record(rule.rule_id, False)
                results.append(RuleResult(rule.rule_id, False))
                continue
            try:
                consequence = condition.apply(fact)
                results.append(RuleResult(rule.rule_id, True,
                                          consequence=consequence))
                self.history.record(rule.rule_id, True, consequence)
            except Exception as exc:  # noqa: BLE001
                results.append(RuleResult(rule.rule_id, True, error=str(exc)))
                self.history.record(rule.rule_id, True, None)
        return results

    def rule_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)
