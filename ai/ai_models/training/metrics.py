"""Training metrics."""
from __future__ import annotations

import time
from typing import Any


class TrainingMetrics:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
    def log(self, epoch: int, metrics: dict[str, float], phase: str = "train") -> dict[str, Any]:
        entry = {"epoch": epoch, "metrics": metrics, "phase": phase, "timestamp": time.time()}
        self._history.append(entry)
        return entry
    def get_epoch(self, epoch: int) -> list[dict[str, Any]]:
        return [h for h in self._history if h["epoch"] == epoch]
    def get_phase(self, phase: str) -> list[dict[str, Any]]:
        return [h for h in self._history if h["phase"] == phase]
    def latest(self, count: int = 5) -> list[dict[str, Any]]:
        return self._history[-count:]
    def summary(self) -> dict[str, Any]:
        if not self._history:
            return {}
        all_metrics = {}
        for h in self._history:
            for k, v in h["metrics"].items():
                all_metrics.setdefault(k, []).append(v)
        return {k: {"min": min(v), "max": max(v), "avg": sum(v) / len(v)} for k, v in all_metrics.items()}
    def clear(self) -> int:
        n = len(self._history)
        self._history.clear()
        return n
    def count(self) -> int:
        return len(self._history)
