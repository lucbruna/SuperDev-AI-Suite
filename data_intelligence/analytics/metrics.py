"""Analytics metric helpers."""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_protocols import numeric_values


def total(values: Iterable[Any]) -> float:
    numbers: list[float] = []
    for value in values:
        if isinstance(value, dict):
            numbers.extend(numeric_values([value], "__value__"))
        else:
            try:
                numbers.append(float(value))
            except (TypeError, ValueError):
                continue
    return round(sum(numbers), 4)


def average(values: Iterable[Any]) -> float:
    numbers = list(values)
    if not numbers:
        return 0.0
    return round(sum(numbers) / len(numbers), 4)


def growth_rate(current: float, previous: float) -> float:
    """Returns the percentage growth (``+18`` = 18% growth)."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / abs(previous) * 100, 2)


def percentage(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 2)
