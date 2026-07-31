from __future__ import annotations

from typing import Any

from .tool_interfaces import ITool, IToolRegistry


class ToolRegistry(IToolRegistry):
    """Central registry for tool discovery and lookup."""

    def __init__(self) -> None:
        self._tools: dict[str, ITool] = {}
        self._categories: dict[str, list[str]] = {}

    def register(self, tool: ITool) -> str:
        name = tool.name()
        self._tools[name] = tool
        return name

    def register_with_category(self, tool: ITool, category: str) -> str:
        name = self.register(tool)
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        return name

    def unregister(self, name: str) -> bool:
        if name in self._tools:
            del self._tools[name]
            for cat in self._categories.values():
                if name in cat:
                    cat.remove(name)
            return True
        return False

    def get(self, name: str) -> ITool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ITool]:
        return list(self._tools.values())

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def get_category(self, category: str) -> list[ITool]:
        names = self._categories.get(category, [])
        return [self._tools[n] for n in names if n in self._tools]

    def list_categories(self) -> list[str]:
        return list(self._categories.keys())

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tools": list(self._tools.keys()),
            "categories": {k: list(v) for k, v in self._categories.items()},
            "tool_count": self.tool_count,
        }
