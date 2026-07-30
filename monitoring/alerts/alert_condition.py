from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

ConditionFn = Callable[[], tuple[bool, float]]


@dataclass
class AlertCondition:
    """A named condition that can be evaluated to produce alerts."""

    name: str
    evaluator: ConditionFn
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)

    def evaluate(self) -> tuple[bool, float]:
        return self.evaluator()

    @staticmethod
    def gt(value_fn: Callable[[], float], threshold: float) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (val > threshold, val)
        return _eval

    @staticmethod
    def lt(value_fn: Callable[[], float], threshold: float) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (val < threshold, val)
        return _eval

    @staticmethod
    def gte(value_fn: Callable[[], float], threshold: float) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (val >= threshold, val)
        return _eval

    @staticmethod
    def lte(value_fn: Callable[[], float], threshold: float) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (val <= threshold, val)
        return _eval

    @staticmethod
    def between(
        value_fn: Callable[[], float],
        low: float,
        high: float,
    ) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (low <= val <= high, val)
        return _eval

    @staticmethod
    def change(
        value_fn: Callable[[], list[float]] | Callable[[], float],
        threshold_pct: float,
    ) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            result = value_fn()
            if isinstance(result, (int, float)):
                return (False, float(result))
            values = list(result)
            if len(values) < 2:
                return (False, 0.0)
            pct = ((values[-1] - values[0]) / abs(values[0] or 1)) * 100
            return (abs(pct) > threshold_pct, pct)
        return _eval

    @staticmethod
    def boolean(value_fn: Callable[[], bool]) -> ConditionFn:
        def _eval() -> tuple[bool, float]:
            val = value_fn()
            return (val, 1.0 if val else 0.0)
        return _eval
