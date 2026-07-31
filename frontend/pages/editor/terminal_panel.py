from __future__ import annotations

import logging
from typing import Any


class TerminalPanel:
    """Integrated terminal output for the editor."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.terminal")
        self._lines: list[dict[str, Any]] = []

    def render(self) -> dict[str, Any]:
        return {"history": self.history(), "count": len(self._lines)}

    def execute(self, command: str) -> dict[str, Any]:
        entry = {"command": command, "output": f"$ {command}", "exit": 0}
        self._lines.append(entry)
        return entry

    def clear(self) -> None:
        self._lines.clear()

    def history(self) -> list[str]:
        return [entry["command"] for entry in self._lines]
