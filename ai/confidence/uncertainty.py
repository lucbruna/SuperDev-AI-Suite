from __future__ import annotations

import math
from typing import Any


class Uncertainty:
    """Estimates uncertainty in predictions and decisions."""

    def __init__(self) -> None:
        self._methods: dict[str, Any] = {}

    def register_method(self, name: str, method: Any) -> None:
        self._methods[name] = method

    async def estimate(self, context: dict[str, Any]) -> float:
        probabilities = context.get("probabilities", [0.5, 0.5])
        entropy = -sum(p * math.log(p + 1e-10) for p in probabilities)
        normalized = entropy / math.log(len(probabilities) + 1e-10)
        return min(1.0, normalized)

    async def aleatoric(self, context: dict[str, Any]) -> float:
        return context.get("noise_level", 0.1)

    async def epistemic(self, context: dict[str, Any]) -> float:
        return context.get("knowledge_gap", 0.2)
