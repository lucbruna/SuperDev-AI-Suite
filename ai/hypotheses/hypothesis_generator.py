from __future__ import annotations

from typing import Any


class HypothesisGenerator:
    """Generates hypotheses from context and evidence."""

    def __init__(self) -> None:
        self._templates: list[str] = []

    def add_template(self, template: str) -> None:
        self._templates.append(template)

    async def generate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        hypotheses: list[dict[str, Any]] = []
        evidence = context.get("evidence", [])
        for i, piece in enumerate(evidence):
            hypotheses.append(
                {
                    "id": f"hyp_{i}",
                    "statement": f"If {piece} then ...",
                    "confidence": 0.5,
                    "source": piece,
                }
            )
        if not hypotheses:
            hypotheses.append(
                {"id": "hyp_0", "statement": "No hypothesis generated", "confidence": 0.0, "source": None}
            )
        return hypotheses

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        hypotheses = await self.generate(context)
        return {"hypotheses": hypotheses, "count": len(hypotheses)}
