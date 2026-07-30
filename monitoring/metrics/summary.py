from __future__ import annotations

from typing import Any

from .histogram import Histogram


class Summary:
    """Tracks quantiles over a sliding window (delegates to Histogram)."""

    def __init__(self, name: str, labels: dict[str, str] | None = None, max_age: float = 600.0) -> None:
        self._hist = Histogram(name=name, labels=labels)
        self._max_age = max_age

    def observe(self, value: float) -> None:
        self._hist.observe(value)

    def quantile(self, q: float) -> float:
        return self._hist.percentile(q)

    def stats(self) -> dict[str, float]:
        return self._hist.stats()


__all__ = ["Summary"]
