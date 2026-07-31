"""Tool engine for agent tool management and execution."""
from __future__ import annotations

from typing import Any

from .tool_composer import ToolComposer
from .tool_executor import ToolExecutor
from .tool_monitor import ToolMonitor
from .tool_registry import ToolRegistry
from .tool_security import ToolSecurity
from .tool_validator import ToolValidator


class ToolEngine:
    """Central engine for managing, composing, and executing agent tools."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._registry = ToolRegistry()
        self._executor = ToolExecutor()
        self._composer = ToolComposer()
        self._validator = ToolValidator()
        self._monitor = ToolMonitor()
        self._security = ToolSecurity()
        self._execution_count: int = 0

    def register_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        return self._registry.register(tool)

    def execute_tool(self, tool_id: str, args: dict[str, Any]) -> dict[str, Any]:
        tool = self._registry.get(tool_id)
        if not tool:
            return {"error": f"Tool {tool_id} not found"}
        if not self._validator.validate(tool, args):
            return {"error": "Validation failed"}
        self._security.check(tool_id, args)
        self._execution_count += 1
        result = self._executor.execute(tool, args)
        self._monitor.record(tool_id, result)
        return result

    def compose_tools(self, tool_ids: list[str], task: dict[str, Any]) -> dict[str, Any]:
        return self._composer.compose(tool_ids, task, self._registry)

    def list_tools(self) -> list[dict[str, Any]]:
        return self._registry.list_all()

    def get_tool(self, tool_id: str) -> dict[str, Any] | None:
        return self._registry.get(tool_id)

    def get_metrics(self) -> dict[str, Any]:
        return {
            "total_executions": self._execution_count,
            "tools_registered": self._registry.count(),
            "monitor": self._monitor.get_summary(),
        }
