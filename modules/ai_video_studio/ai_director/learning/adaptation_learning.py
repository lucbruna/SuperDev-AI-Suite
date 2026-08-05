"""Adaptation learning — adapts direction to changing constraints."""
from __future__ import annotations

from typing import Any


class AdaptationLearning:
    """Adjusts plans when constraints change."""

    def adapt(self, plan: dict[str, Any], constraint: str, value: Any) -> dict[str, Any]:
        adapted = dict(plan)
        if constraint == "budget":
            adapted["budget_scale"] = value
        elif constraint == "time":
            adapted["time_scale"] = value
        else:
            adapted[constraint] = value
        return adapted


_adaptation_learning: AdaptationLearning | None = None


def get_adaptation_learning() -> AdaptationLearning:
    global _adaptation_learning
    if _adaptation_learning is None:
        _adaptation_learning = AdaptationLearning()
    return _adaptation_learning
