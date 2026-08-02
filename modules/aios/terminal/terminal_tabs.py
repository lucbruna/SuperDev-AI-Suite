"""Terminal tabs — collection of named terminal sessions."""
from __future__ import annotations

from typing import Any

from modules.aios.terminal.terminal_session import (
    TerminalSession,
    TerminalSessionError,
)


class TerminalTabs:
    """Manages named sessions (tabs) in the internal terminal."""

    def __init__(self) -> None:
        self._sessions: dict[str, TerminalSession] = {}
        self._active: str | None = None

    @property
    def active(self) -> str | None:
        return self._active

    def open(self, name: str, **kwargs: Any) -> TerminalSession:
        if name in self._sessions:
            raise TerminalSessionError(f"tab already open: {name}")
        session = TerminalSession(name, **kwargs)
        self._sessions[name] = session
        self._active = name
        return session

    def get(self, name: str | None = None) -> TerminalSession:
        resolved = name or self._active
        if resolved is None or resolved not in self._sessions:
            raise TerminalSessionError(f"no such tab: {resolved}")
        return self._sessions[resolved]

    async def close(self, name: str | None = None) -> None:
        resolved = name or self._active
        if resolved is None or resolved not in self._sessions:
            raise TerminalSessionError(f"no such tab: {resolved}")
        await self._sessions[resolved].close()
        del self._sessions[resolved]
        if self._active == resolved:
            self._active = next(iter(self._sessions), None)

    def list(self) -> list[str]:
        return list(self._sessions)


__all__ = ["TerminalTabs"]
