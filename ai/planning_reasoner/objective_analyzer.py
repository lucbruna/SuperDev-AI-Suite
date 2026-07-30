from __future__ import annotations

from typing import Any


class ObjectiveAnalyzer:
    """Analyzes objectives to determine complexity and scope."""

    def __init__(self) -> None:
        self._keywords: dict[str, int] = {}

    def add_keyword(self, keyword: str, weight: int) -> None:
        self._keywords[keyword.lower()] = weight

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        description = context.get("description", "")
        keyword_matches = [k for k in self._keywords if k in description.lower()]
        complexity = sum(self._keywords[k] for k in keyword_matches)
        if complexity > 10:
            level = "high"
        elif complexity > 5:
            level = "medium"
        else:
            level = "low"
        return {
            "complexity": level,
            "complexity_score": complexity,
            "keywords_found": keyword_matches,
            "scope": context.get("scope", "unknown"),
        }
