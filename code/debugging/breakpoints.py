from __future__ import annotations

import logging
from typing import Any


class BreakpointManager:
    """Manages debugger breakpoints."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.breakpoints")
        self._breakpoints: list[dict[str, Any]] = []

    def set(self, file: str, line: int, condition: str | None = None) -> dict[str, Any]:
        bp = {"file": file, "line": line, "condition": condition, "enabled": True}
        self._breakpoints.append(bp)
        self._log.info("Breakpoint set at %s:%d", file, line)
        return bp

    def clear(self, file: str, line: int) -> bool:
        before = len(self._breakpoints)
        self._breakpoints = [b for b in self._breakpoints if not (b["file"] == file and b["line"] == line)]
        return len(self._breakpoints) < before

    def clear_all(self) -> None:
        self._breakpoints.clear()

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._breakpoints)
