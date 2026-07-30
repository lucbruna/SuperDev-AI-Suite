from __future__ import annotations

from typing import Any

from .condition_models import Condition
from .condition_evaluator import ConditionEvaluator


class ConditionComposite:
    """Evaluates composite conditions (AND/OR logic)."""

    @staticmethod
    def all(conditions: list[Condition], context: dict[str, Any]) -> bool:
        return all(ConditionEvaluator.evaluate(c, context) for c in conditions)

    @staticmethod
    def any(conditions: list[Condition], context: dict[str, Any]) -> bool:
        return any(ConditionEvaluator.evaluate(c, context) for c in conditions)

    @staticmethod
    def not_all(conditions: list[Condition], context: dict[str, Any]) -> bool:
        return not ConditionComposite.all(conditions, context)
