from __future__ import annotations

from typing import Any

from .tool_interfaces import ITool, IToolFactory


class ToolFactory(IToolFactory):
    """Creates tool instances by type name."""

    def __init__(self) -> None:
        self._tool_classes: dict[str, type[ITool]] = {}

    def register_class(self, tool_type: str, cls: type[ITool]) -> str:
        self._tool_classes[tool_type] = cls
        return tool_type

    def create(self, tool_type: str, **kwargs: Any) -> ITool:
        cls = self._tool_classes.get(tool_type)
        if cls is None:
            raise ValueError(f"Unknown tool type: {tool_type}")
        return cls(**kwargs)

    def list_types(self) -> list[str]:
        return list(self._tool_classes.keys())

    @property
    def type_count(self) -> int:
        return len(self._tool_classes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "types": list(self._tool_classes.keys()),
            "type_count": self.type_count,
        }
