"""Terminal history — bounded, filterable command history."""
from __future__ import annotations

from collections import deque


class TerminalHistory:
    """Keeps the last ``maxlen`` executed commands."""

    def __init__(self, maxlen: int = 200) -> None:
        self._entries: deque[str] = deque(maxlen=maxlen)

    def add(self, command: str) -> None:
        if command.strip():
            self._entries.append(command)

    def list(self) -> list[str]:
        return list(self._entries)

    def filter(self, term: str) -> list[str]:
        lowered = term.lower()
        return [c for c in self._entries if lowered in c.lower()]

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


__all__ = ["TerminalHistory"]
