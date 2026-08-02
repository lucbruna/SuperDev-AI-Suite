"""Terminal stream — line-based output buffer for terminal sessions."""
from __future__ import annotations


class TerminalStream:
    """Accumulates command output as ordered, drainable lines."""

    def __init__(self, max_lines: int = 500) -> None:
        self._lines: list[str] = []
        self._max_lines = max_lines

    def write(self, chunk: str) -> None:
        for line in chunk.splitlines():
            self._lines.append(line)
        if len(self._lines) > self._max_lines:
            del self._lines[: len(self._lines) - self._max_lines]

    def lines(self) -> list[str]:
        return list(self._lines)

    def drain(self) -> list[str]:
        drained, self._lines = self._lines, []
        return drained

    def clear(self) -> None:
        self._lines = []

    def __len__(self) -> int:
        return len(self._lines)


__all__ = ["TerminalStream"]
