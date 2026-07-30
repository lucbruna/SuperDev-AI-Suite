from __future__ import annotations

from typing import Any

from .trigger_models import Trigger


class TriggerEvaluator:
    """Evaluates trigger conditions before firing."""

    @staticmethod
    def evaluate(trigger: Trigger) -> dict[str, Any]:
        condition = trigger.config.get("condition", {})
        result: dict[str, Any] = {"matched": True, "reason": "trigger fired"}
        if condition:
            result["matched"] = bool(condition.get("value", True))
            result["reason"] = condition.get("reason", "condition evaluated")
        return result
