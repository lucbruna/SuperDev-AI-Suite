"""Metrics subsystem engine."""
from __future__ import annotations

from typing import Any


class MetricsEngine:
    def __init__(self) -> None:
        self._collectors: list[str] = []
        self._aggregators: list[str] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def add_collector(self, name: str) -> None:
        self._collectors.append(name)
    def add_aggregator(self, name: str) -> None:
        self._aggregators.append(name)
    def get_status(self) -> dict[str, Any]:
        return {"running": self._started, "collectors": len(self._collectors), "aggregators": len(self._aggregators)}
