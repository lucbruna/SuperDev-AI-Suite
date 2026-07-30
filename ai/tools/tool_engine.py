from __future__ import annotations

from typing import Any

from .tool_manager import ToolManager


class ToolEngine:
    """Main entry point for the Tools Engine layer.

    Provides a unified interface for all agents to discover, validate,
    and execute tools. Composes all tool subsystems.
    """

    def __init__(self) -> None:
        self._manager = ToolManager()

    @property
    def manager(self) -> ToolManager:
        return self._manager

    async def execute(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        return await self._manager.executor.execute(tool_name, params)

    async def validate(self, tool_name: str, params: dict[str, Any]) -> bool:
        return await self._manager.executor.validate(tool_name, params)

    def register_tool(self, tool: Any) -> str:
        return self._manager.registry.register(tool)

    def get_tool(self, name: str) -> Any | None:
        return self._manager.registry.get(name)

    def list_tools(self) -> list[str]:
        return self._manager.registry.list_names()

    def get_status(self) -> dict[str, Any]:
        return self._manager.get_status()

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "tool_engine",
            "status": self.get_status(),
            "registry": self._manager.registry.to_dict(),
            "metrics": self._manager.metrics.to_dict(),
        }
