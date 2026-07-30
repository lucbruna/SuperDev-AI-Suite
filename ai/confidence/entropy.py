from __future__ import annotations

import math
from typing import Any


class Entropy:
    """Entropy-based uncertainty measurement."""

    @staticmethod
    async def shannon(probabilities: list[float]) -> float:
        if not probabilities:
            return 0.0
        return -sum(p * math.log(p + 1e-10) for p in probabilities)

    @staticmethod
    async def normalized(probabilities: list[float]) -> float:
        if not probabilities or len(probabilities) < 2:
            return 0.0
        raw = await Entropy.shannon(probabilities)
        max_entropy = math.log(len(probabilities))
        return raw / max_entropy if max_entropy > 0 else 0.0

    @staticmethod
    async def information_gain(prior_entropy: float, posterior_entropy: float) -> float:
        return prior_entropy - posterior_entropy

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        probabilities = context.get("probabilities", [])
        raw = await self.shannon(probabilities)
        norm = await self.normalized(probabilities)
        return {"shannon_entropy": raw, "normalized_entropy": norm}
