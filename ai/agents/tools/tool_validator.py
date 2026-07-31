"""Tool argument validation."""
from __future__ import annotations

from typing import Any


class ToolValidator:
    """Validates tool arguments against parameter schemas."""

    def __init__(self) -> None:
        self._validation_count: int = 0
        self._error_count: int = 0

    def validate(self, tool: dict[str, Any], args: dict[str, Any]) -> bool:
        self._validation_count += 1
        params = tool.get("parameters", {})
        for required_key in params:
            if required_key not in args:
                self._error_count += 1
                return False
        return True

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_validations": self._validation_count,
            "errors": self._error_count,
            "success_rate": round(
                (self._validation_count - self._error_count)
                / max(self._validation_count, 1), 2
            ),
        }
