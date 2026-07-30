from __future__ import annotations

from typing import Any


class LogicalValidator:
    """Validates logical structure and reasoning."""

    def __init__(self) -> None:
        self._fallacies: list[str] = []

    def add_fallacy(self, pattern: str) -> None:
        self._fallacies.append(pattern)

    async def validate(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        issues: list[str] = []
        for fallacy in self._fallacies:
            if fallacy.lower() in response.lower():
                issues.append(f"Potential fallacy detected: {fallacy}")
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "has_logical_structure": "if" in response.lower() or "therefore" in response.lower() or "because" in response.lower(),
        }
