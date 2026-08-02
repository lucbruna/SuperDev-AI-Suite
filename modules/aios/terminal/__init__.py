"""Terminal package — internal terminal facade (Vol 12, Fase 25)."""
from __future__ import annotations

from modules.aios.terminal.terminal import (
    Terminal,
    get_terminal_runtime,
    require_terminal_action,
)
from modules.aios.terminal.terminal_commands import (
    TerminalCommand,
    TerminalCommands,
)
from modules.aios.terminal.terminal_history import TerminalHistory
from modules.aios.terminal.terminal_session import (
    TerminalSession,
    TerminalSessionError,
)
from modules.aios.terminal.terminal_stream import TerminalStream
from modules.aios.terminal.terminal_tabs import TerminalTabs

__all__ = [
    "Terminal",
    "get_terminal_runtime",
    "require_terminal_action",
    "TerminalCommand",
    "TerminalCommands",
    "TerminalHistory",
    "TerminalSession",
    "TerminalSessionError",
    "TerminalStream",
    "TerminalTabs",
]
