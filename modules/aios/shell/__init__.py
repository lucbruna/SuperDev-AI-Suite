"""Shell package — POSIX shell facade (Vol 12, Fase 23)."""
from __future__ import annotations

from modules.aios.shell.bash import Bash
from modules.aios.shell.fish import Fish
from modules.aios.shell.shell_client import (
    ShellClient,
    ShellUnavailableError,
    require_shell_action,
)
from modules.aios.shell.shell_runtime import ShellRuntime, get_shell_runtime
from modules.aios.shell.zsh import Zsh

__all__ = [
    "Bash",
    "Fish",
    "ShellClient",
    "ShellRuntime",
    "ShellUnavailableError",
    "get_shell_runtime",
    "require_shell_action",
    "Zsh",
]
