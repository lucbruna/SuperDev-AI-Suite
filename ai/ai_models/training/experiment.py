"""Experiment tracking."""

from __future__ import annotations

import time
from typing import Any


class ExperimentTracker:
    def __init__(self) -> None:
        self._experiments: dict[str, dict[str, Any]] = {}

    def create(self, name: str, config: dict[str, Any] = None) -> dict[str, Any]:
        exp = {"name": name, "config": config or {}, "runs": [], "created_at": time.time()}
        self._experiments[name] = exp
        return exp

    def add_run(self, name: str, metrics: dict[str, float], tags: dict[str, str] = None) -> dict[str, Any]:
        if name not in self._experiments:
            self.create(name)
        run = {"metrics": metrics, "tags": tags or {}, "timestamp": time.time()}
        self._experiments[name]["runs"].append(run)
        return run

    def get(self, name: str) -> dict[str, Any]:
        return self._experiments.get(name, {"error": "not_found"})

    def compare(self, names: list[str]) -> dict[str, Any]:
        comparison = {}
        for name in names:
            exp = self._experiments.get(name, {})
            runs = exp.get("runs", [])
            if runs:
                comparison[name] = runs[-1].get("metrics", {})
        return comparison

    def best_run(self, name: str, metric: str = "accuracy") -> dict[str, Any]:
        exp = self._experiments.get(name, {})
        runs = exp.get("runs", [])
        if not runs:
            return {"error": "no_runs"}
        return max(runs, key=lambda r: r.get("metrics", {}).get(metric, 0))

    def list_experiments(self) -> list[str]:
        return list(self._experiments.keys())

    def count(self) -> int:
        return len(self._experiments)
