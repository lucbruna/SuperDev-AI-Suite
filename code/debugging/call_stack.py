from __future__ import annotations

import logging
from typing import Any


class CallStack:
    """Represents the current call stack in a debug session."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.callstack")
        self._frames: list[dict[str, Any]] = []

    def push(self, frame: dict[str, Any]) -> None:
        self._frames.append(frame)

    def pop(self) -> dict[str, Any] | None:
        return self._frames.pop() if self._frames else None

    def top(self) -> dict[str, Any] | None:
        return self._frames[-1] if self._frames else None

    def depth(self) -> int:
        return len(self._frames)
