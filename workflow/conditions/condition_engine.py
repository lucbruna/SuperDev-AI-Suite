from __future__ import annotations

import logging
from typing import Any

from .condition_models import Condition
from .condition_evaluator import ConditionEvaluator


class ConditionEngine:
    """Evaluates conditions and returns results."""

    def __init__(self) -> None:
        self._evaluator = ConditionEvaluator()
        self._log = logging.getLogger("superdev.workflow.conditions")

    def evaluate(self, condition: Condition, context: dict[str, Any] | None = None) -> bool:
        result = self._evaluator.evaluate(condition, context or {})
        self._log.debug("Condition %s = %s", condition.id, result)
        return result

    def evaluate_all(self, conditions: list[Condition], context: dict[str, Any] | None = None) -> list[bool]:
        return [self.evaluate(c, context) for c in conditions]
