from __future__ import annotations

from typing import Any

from .condition_models import Condition, ConditionOperator


class ConditionParser:
    """Parses condition strings into Condition objects."""

    @staticmethod
    def parse(raw: dict[str, Any]) -> Condition:
        op_str = raw.get("operator", "equals")
        try:
            operator = ConditionOperator(op_str)
        except ValueError:
            operator = ConditionOperator.EQUALS
        return Condition(
            field=raw.get("field", ""),
            operator=operator,
            value=raw.get("value"),
        )
