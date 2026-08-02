"""Terminal — the internal terminal facade (Vol 12, Fase 25)."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)
from modules.aios.terminal.terminal_commands import (
    TerminalCommand,
    TerminalCommands,
)
from modules.aios.terminal.terminal_history import TerminalHistory
from modules.aios.terminal.terminal_tabs import TerminalTabs


def require_terminal_action(action: str) -> None:
    """Enforce the ``terminal:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("terminal", action):
        raise KernelPermissionDeniedError("terminal", action)


class Terminal:
    """Internal terminal: tabs (sessions), history and command registry.

    Stateless by design — sessions keep their own state; ``close`` closes all
    open tabs. Backed by the host shell (powershell.exe on Windows).
    """

    def __init__(self) -> None:
        self.tabs = TerminalTabs()
        self.history = TerminalHistory()
        self.commands = TerminalCommands()
        self._logger = get_kernel_logger()
        self._register_builtins()

    def _register_builtins(self) -> None:
        self.commands.register(TerminalCommand("help", "list builtin commands", handler=lambda: ", ".join(self.commands.names())))
        self.commands.register(TerminalCommand("clear", "clear the active tab output"))
        self.commands.register(TerminalCommand("history", "show executed commands"))
        self.commands.register(TerminalCommand("exit", "close the active tab"))

    async def open_tab(self, name: str, **kwargs: Any) -> dict[str, Any]:
        require_terminal_action("session")
        session = self.tabs.open(name, **kwargs)
        await session.start()
        return {"tab": name, "shell": session.shell, "cwd": session.cwd}

    async def close_tab(self, name: str | None = None) -> dict[str, Any]:
        require_terminal_action("session")
        resolved = name or self.tabs.active
        await self.tabs.close(resolved)
        return {"closed": resolved}

    async def run(
        self, command: str, *, tab: str | None = None
    ) -> dict[str, Any]:
        require_terminal_action("run")
        session = self.tabs.get(tab)
        result = await session.run(command)
        self.history.add(command)
        return {"tab": session.name, **result}

    async def snapshot(self) -> dict[str, Any]:
        """Inventory: tabs, shell of active tab, command count."""
        return {
            "tabs": self.tabs.list(),
            "active": self.tabs.active,
            "commands": self.commands.names(),
            "history_entries": len(self.history),
        }

    async def close(self) -> None:
        for name in list(self.tabs.list()):
            await self.tabs.close(name)


_terminal: Terminal | None = None


def get_terminal_runtime() -> Terminal:
    global _terminal
    if _terminal is None:
        _terminal = Terminal()
    return _terminal


__all__ = ["Terminal", "get_terminal_runtime", "require_terminal_action"]
