from __future__ import annotations

from typing import Any, Optional

from ..base.base_tool import BaseTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, type[BaseTool]] = {}
        self._categories: dict[str, list[str]] = {}

    def register(self, name: str, tool_class: type[BaseTool], category: str = "general") -> None:
        if not issubclass(tool_class, BaseTool):
            raise TypeError(f"{tool_class.__name__} must be a subclass of BaseTool")
        self._tools[name] = tool_class
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

    def get(self, name: str) -> Optional[type[BaseTool]]:
        return self._tools.get(name)

    def list_by_category(self, category: str) -> list[dict[str, Any]]:
        tool_names = self._categories.get(category, [])
        result = []
        for name in tool_names:
            tool_cls = self._tools.get(name)
            if tool_cls:
                instance = tool_cls()
                result.append({
                    "name": name,
                    "description": instance.description(),
                    "permissions": instance.permissions(),
                    "category": category,
                })
        return result

    def list_all(self) -> list[dict[str, Any]]:
        result = []
        for name, tool_cls in self._tools.items():
            instance = tool_cls()
            category = next(
                (cat for cat, names in self._categories.items() if name in names),
                "general",
            )
            result.append({
                "name": name,
                "description": instance.description(),
                "permissions": instance.permissions(),
                "category": category,
            })
        return result
