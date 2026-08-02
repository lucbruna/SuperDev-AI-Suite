"""Shell runtime — facade over bash/zsh/fish (Vol 12, Fase 23)."""
from __future__ import annotations

from typing import Any

from modules.aios.shell.bash import Bash
from modules.aios.shell.fish import Fish
from modules.aios.shell.shell_client import ShellUnavailableError
from modules.aios.shell.zsh import Zsh


class ShellRuntime:
    """Facade over POSIX shells.

    Stateless: wrappers are CLI-based. ``close`` is a no-op. Shells that are
    not installed (zsh, fish on Windows) degrade via ShellUnavailableError.
    """

    def __init__(self) -> None:
        self.bash = Bash()
        self.zsh = Zsh()
        self.fish = Fish()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; each shell degrades to None on error."""
        inventory: dict[str, Any] = {}
        for name in ("bash", "zsh", "fish"):
            shell = getattr(self, name)
            try:
                inventory[name] = (await shell.version())["version"]
            except ShellUnavailableError:
                inventory[name] = None
        return inventory

    async def close(self) -> None:
        """No-op — the shell runtime is stateless."""


_shell_runtime: ShellRuntime | None = None


def get_shell_runtime() -> ShellRuntime:
    global _shell_runtime
    if _shell_runtime is None:
        _shell_runtime = ShellRuntime()
    return _shell_runtime


__all__ = ["ShellRuntime", "get_shell_runtime"]
