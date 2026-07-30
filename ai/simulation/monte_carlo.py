from __future__ import annotations

import random
from typing import Any


class MonteCarlo:
    """Monte Carlo simulation for probabilistic analysis."""

    def __init__(self) -> None:
        self._samples: list[float] = []

    async def run(self, iterations: int, params: dict[str, Any]) -> dict[str, Any]:
        self._samples = []
        mean = params.get("mean", 0.0)
        std = params.get("std", 1.0)
        for _ in range(iterations):
            sample = random.gauss(mean, std)
            self._samples.append(sample)
        return {
            "iterations": iterations,
            "mean": sum(self._samples) / len(self._samples) if self._samples else 0,
            "min": min(self._samples) if self._samples else 0,
            "max": max(self._samples) if self._samples else 0,
        }

    async def probability_of_success(self, threshold: float) -> float:
        if not self._samples:
            return 0.0
        successes = sum(1 for s in self._samples if s >= threshold)
        return successes / len(self._samples)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        iterations = context.get("iterations", 1000)
        params = context.get("params", {})
        return await self.run(iterations, params)
