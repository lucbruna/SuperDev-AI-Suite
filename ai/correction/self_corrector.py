from __future__ import annotations

from typing import Any


class SelfCorrector:
    """Self-correction of responses based on error feedback."""

    def __init__(self) -> None:
        self._patterns: dict[str, str] = {}

    def add_pattern(self, error_type: str, fix: str) -> None:
        self._patterns[error_type] = fix

    async def correct(self, response: str, error: dict[str, Any]) -> dict[str, Any]:
        error_type = error.get("type", "")
        if error_type in self._patterns:
            fix = self._patterns[error_type]
            corrected = response.replace(error.get("segment", ""), fix)
            return {"success": True, "corrected": corrected, "changes": 1}
        return {"success": False, "corrected": response, "changes": 0}
