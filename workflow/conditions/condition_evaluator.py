from __future__ import annotations

import re
from typing import Any

from .condition_models import Condition, ConditionOperator


class ConditionEvaluator:
    """Evaluates individual conditions against context data."""

    @staticmethod
    def evaluate(condition: Condition, context: dict[str, Any]) -> bool:
        actual = context.get(condition.field)
        op = condition.operator
        expected = condition.value

        if op == ConditionOperator.EQUALS:
            return actual == expected
        elif op == ConditionOperator.NOT_EQUALS:
            return actual != expected
        elif op == ConditionOperator.GREATER_THAN:
            return (actual or 0) > expected
        elif op == ConditionOperator.LESS_THAN:
            return (actual or 0) < expected
        elif op == ConditionOperator.CONTAINS:
            return expected in (actual or "")
        elif op == ConditionOperator.EXISTS:
            return condition.field in context
        elif op == ConditionOperator.MATCHES:
            return bool(re.match(str(expected), str(actual or "")))
        return False
