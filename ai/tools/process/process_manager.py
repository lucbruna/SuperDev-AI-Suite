from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .process_executor import ProcessExecutor
from .process_monitor import ProcessMonitor


class ProcessManager(BaseTool):
    """Composite process management tool."""

    _name = "process"
    _description = "Manage system processes: execute, monitor, list, kill"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._executor = ProcessExecutor()
        self._monitor = ProcessMonitor()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        if action == "execute":
            return await self._executor.execute(params)
        elif action in ("list", "status", "kill"):
            return await self._monitor.execute(params)
        return {"success": False, "error": f"Unknown action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        await self._executor.cleanup()
        await self._monitor.cleanup()
