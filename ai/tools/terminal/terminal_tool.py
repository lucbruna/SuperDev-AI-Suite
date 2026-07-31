from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .terminal_environment import TerminalEnvironment
from .terminal_executor import TerminalExecutor
from .terminal_history import TerminalHistory
from .terminal_session import TerminalSession


class TerminalTool(BaseTool):
    """Composite terminal tool for command execution and session management."""

    _name = "terminal"
    _description = "Execute commands, manage sessions, history, and environment"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._executor = TerminalExecutor()
        self._session = TerminalSession()
        self._history = TerminalHistory()
        self._env = TerminalEnvironment()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "execute")
        if action == "execute":
            result = await self._executor.execute(params)
            self._history.add_entry(params.get("command", ""), result)
            return result
        elif action in ("create", "delete", "list"):
            return await self._session.execute(params)
        elif action in ("list", "clear", "search"):
            return await self._history.execute(params)
        elif action in ("get", "set", "list"):
            return await self._env.execute(params)
        return {"success": False, "error": f"Unknown action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        await self._executor.cleanup()
        await self._session.cleanup()
        await self._history.cleanup()
        await self._env.cleanup()
