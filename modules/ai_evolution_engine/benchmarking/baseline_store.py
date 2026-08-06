"""Baseline store: in-memory deterministic baseline persistence."""
from __future__ import annotations

from modules.ai_evolution_engine.benchmarking.benchmark_runner import BenchmarkRunner


class BaselineStore:
    """Owns baseline snapshots shared across runs."""

    def __init__(self) -> None:
        self._runner = BenchmarkRunner()

    @property
    def runner(self) -> BenchmarkRunner:
        return self._runner

    def snapshot(self) -> dict[str, float]:
        return dict(self._runner._baseline)

    def restore(self, snapshot: dict[str, float]) -> None:
        self._runner._baseline = dict(snapshot)
