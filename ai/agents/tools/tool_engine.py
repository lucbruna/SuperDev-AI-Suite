"""Tool engine for agent tool management and execution."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .tool_registry import ToolRegistry
from .tool_executor import ToolExecutor
from .tool_composer import ToolComposer
from .tool_validator import ToolValidator
from .tool_monitor import ToolMonitor
from .tool_security import ToolSecurity


class ToolEngine:
    """Central engine for managing, composing, and executing agent tools."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._registry = ToolRegistry()
        self._executor = ToolExecutor()
        self._composer = ToolComposer()
        self._validator = ToolValidator()
        self._monitor = ToolMonitor()
        self._security = ToolSecurity()
        self._execution_count: int = 0

    def register_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        return self._registry.register(tool)

    def execute_tool(self, tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
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

    def compose_tools(self, tool_ids: List[str], task: Dict[str, Any]) -> Dict[str, Any]:
        return self._composer.compose(tool_ids, task, self._registry)

    def list_tools(self) -> List[Dict[str, Any]]:
        return self._registry.list_all()

    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        return self._registry.get(tool_id)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_executions": self._execution_count,
            "tools_registered": self._registry.count(),
            "monitor": self._monitor.get_summary(),
        }
