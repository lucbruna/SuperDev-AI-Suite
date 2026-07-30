from __future__ import annotations

import logging
from typing import Any


class StackTrace:
    """Captures and inspects stack traces."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.stack")

    def capture(self) -> list[dict[str, Any]]:
        frames: list[dict[str, Any]] = []
        self._log.debug("Stack trace captured")
        return frames

    def format(self, frames: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        for i, f in enumerate(frames):
            loc = f"{f.get('file', '?')}:{f.get('line', '?')}"
            lines.append(f"  #{i} {f.get('function', '?')} at {loc}")
        return "\n".join(lines)
