"""Declarative condition evaluation for triggers."""

from __future__ import annotations

from typing import Any

from automation.automation_interfaces import Trigger
from automation.automation_protocols import safe_get
from automation.triggers.trigger_models import TriggerDefinition

_MISSING = object()

_OPS: dict[str, Any] = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gt": lambda a, b: a > b,
    "gte": lambda a, b: a >= b,
    "lt": lambda a, b: a < b,
    "lte": lambda a, b: a <= b,
    "contains": lambda a, b: a is not _MISSING and b in a,
    "in": lambda a, b: a is not _MISSING and a in b,
    "starts_with": lambda a, b: isinstance(a, str) and a.startswith(b),
    "ends_with": lambda a, b: isinstance(a, str) and a.endswith(b),
}


class TriggerEvaluator:
    """Evaluates declarative conditions against event data.

    Leaf: ``{"field": "stock.levels.sku-1", "op": "lt", "value": 10}``
    Combined: ``{"all": [...]}``, ``{"any": [...]}``, ``{"not": {...}}``
    """

    def evaluate_condition(self, condition: dict[str, Any],
                           data: dict[str, Any]) -> bool:
        if "all" in condition:
            return all(self.evaluate_condition(c, data)
                       for c in condition["all"])
        if "any" in condition:
            return any(self.evaluate_condition(c, data)
                       for c in condition["any"])
        if "not" in condition:
            return not self.evaluate_condition(condition["not"], data)

        field = condition.get("field")
        op = condition.get("op")
        value = condition.get("value")
        if not isinstance(field, str) or not field:
            return False
        if op == "exists":
            actual = safe_get(data, field, _MISSING)
            return (actual is not _MISSING) == bool(value)
        actual = safe_get(data, field, _MISSING)
        if actual is _MISSING:
            return False
        handler = _OPS.get(op)
        if handler is None:
            raise ValueError(f"unknown operator: {op}")
        return bool(handler(actual, value))


class TriggerCondition(Trigger):
    """Adapter implementing the core Trigger interface."""

    def __init__(self, definition: TriggerDefinition,
                 evaluator: TriggerEvaluator | None = None) -> None:
        self.definition = definition
        self.evaluator = evaluator or TriggerEvaluator()

    def evaluate(self, event: dict[str, Any] | None = None) -> bool:
        if isinstance(event, dict) and "data" in event:
            data = event["data"]
        else:
            data = event or {}
        if self.definition.condition:
            return self.evaluator.evaluate_condition(self.definition.condition, data)
        if self.definition.predicate:
            return bool(self.definition.predicate(data))
        return False
