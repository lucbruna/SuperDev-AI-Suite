from __future__ import annotations

import logging
from typing import Any


class MetricMonitor:
    """Collects and evaluates scaling metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.scaling.metrics")
        self._metrics: dict[str, list[dict[str, Any]]] = {}

    def record(self, metric: str, value: float, **kwargs: Any) -> None:
        raise NotImplementedError

    def evaluate(self, policy: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def average(self, metric: str, window: int = 300) -> float:
        raise NotImplementedError

    def latest(self, metric: str) -> dict[str, Any]:
        raise NotImplementedError
