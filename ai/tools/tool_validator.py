from __future__ import annotations

from typing import Any

from .tool_interfaces import ITool
from .tool_registry import ToolRegistry


class ToolValidator:
    """Validates tool parameters against tool requirements."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self._registry = registry
        self._errors: list[str] = []

    async def validate(self, tool_name: str, params: dict[str, Any]) -> bool:
        self._errors.clear()
        if self._registry is None:
            return True

        tool = self._registry.get(tool_name)
        if tool is None:
            self._errors.append(f"Tool '{tool_name}' not found")
            return False

        return await tool.validate(params)

    def add_required_param(self, params: dict[str, Any], name: str) -> bool:
        if name not in params:
            self._errors.append(f"Missing required parameter: {name}")
            return False
        return True

    def validate_type(self, value: Any, expected_type: type, name: str) -> bool:
        if not isinstance(value, expected_type):
            self._errors.append(f"Parameter '{name}' must be {expected_type.__name__}, got {type(value).__name__}")
            return False
        return True

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def clear(self) -> None:
        self._errors.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "errors": self._errors,
            "has_errors": self.has_errors,
        }
