from __future__ import annotations

import logging
from typing import Any


class FrontendMetrics:
    """Collects and reports frontend performance metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.metrics")
        self._metrics: dict[str, list[float]] = {}

    def record(self, name: str, value: float, **kwargs: Any) -> None:
        self._metrics.setdefault(name, []).append(float(value))

    def snapshot(self) -> dict[str, Any]:
        return {name: self._aggregate(name) for name in self._metrics}

    def get(self, name: str) -> Any:
        if name not in self._metrics:
            return None
        return self._aggregate(name)

    def reset(self) -> None:
        self._metrics.clear()

    def _aggregate(self, name: str) -> dict[str, Any]:
        values = self._metrics[name]
        total = sum(values)
        return {
            "count": len(values),
            "sum": total,
            "avg": total / len(values) if values else 0.0,
            "min": min(values) if values else 0.0,
            "max": max(values) if values else 0.0,
            "last": values[-1] if values else 0.0,
        }
