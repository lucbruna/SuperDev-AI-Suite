"""Decision engine: facade for the decisions subsystem."""

from __future__ import annotations

from typing import Any

from automation.decisions.decision_builder import DecisionBuilder
from automation.decisions.decision_history import DecisionHistory
from automation.decisions.decision_models import DecisionResult
from automation.decisions.decision_tree import DecisionTree
from automation.decisions.decision_validator import DecisionValidator
from automation.triggers.trigger_evaluator import TriggerEvaluator


class DecisionEngine:
    """Registers decision trees and evaluates them against data."""

    def __init__(self, validator: DecisionValidator | None = None,
                 history: DecisionHistory | None = None,
                 evaluator: TriggerEvaluator | None = None) -> None:
        self.validator = validator or DecisionValidator()
        self.history = history or DecisionHistory()
        self.evaluator = evaluator or TriggerEvaluator()
        self._trees: dict[str, DecisionTree] = {}

    def build(self) -> DecisionBuilder:
        return DecisionBuilder()

    def register(self, tree: DecisionTree) -> list[str] | None:
        issues = self.validator.validate(tree)
        if issues:
            return issues
        tree.evaluator = self.evaluator
        self._trees[tree.tree_id] = tree
        return None

    def get(self, tree_id: str) -> DecisionTree | None:
        return self._trees.get(tree_id)

    def list(self) -> list[str]:
        return list(self._trees)

    def remove(self, tree_id: str) -> bool:
        return self._trees.pop(tree_id, None) is not None

    def decide(self, tree_id: str,
               data: dict[str, Any]) -> DecisionResult | None:
        tree = self._trees.get(tree_id)
        if tree is None:
            return None
        result = tree.decide(data)
        self.history.record(result)
        return result

    def decision_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)
