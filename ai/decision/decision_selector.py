from __future__ import annotations

from typing import Any


class DecisionSelector:
    """Selects the best option among alternatives."""

    async def select(self, options: list[str], context: Any) -> dict[str, Any]:
        if not options:
            return {"option": "", "confidence": 0.0}
        return {"option": options[0], "confidence": 0.5}

    async def rank(self, options: list[str], criteria: dict[str, Any]) -> list[dict[str, Any]]:
        scored: list[dict[str, Any]] = []
        for i, opt in enumerate(options):
            scored.append({"option": opt, "score": 1.0 / (i + 1), "confidence": 0.5})
        return sorted(scored, key=lambda x: x["score"], reverse=True)
