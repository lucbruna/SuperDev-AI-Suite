from __future__ import annotations

from typing import Any


class ContradictionDetector:
    """Detects contradictions within responses."""

    def __init__(self) -> None:
        self._patterns: list[dict[str, Any]] = []

    def add_pattern(self, pattern: dict[str, Any]) -> None:
        self._patterns.append(pattern)

    async def detect(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        contradictions: list[str] = []
        for pattern in self._patterns:
            a = pattern.get("statement_a", "")
            b = pattern.get("statement_b", "")
            if a in response and b in response:
                contradictions.append(f"Contradiction between '{a}' and '{b}'")
        return {
            "has_contradiction": len(contradictions) > 0,
            "contradictions": contradictions,
        }
