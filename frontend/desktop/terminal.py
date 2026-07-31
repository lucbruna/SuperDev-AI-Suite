from __future__ import annotations

import logging
from typing import Any


class DesktopTerminal:
    """Embedded terminal emulator for the desktop surface."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop.terminal")
        self._lines: list[dict[str, str]] = []
        self._cwd = "/workspace"
        self._open = False

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def is_open(self) -> bool:
        return self._open

    def execute(self, command: str, output: str = "") -> str:
        line_id = f"l{len(self._lines) + 1}"
        self._lines.append({"id": line_id, "command": command, "output": output})
        return line_id

    def set_cwd(self, path: str) -> None:
        self._cwd = path

    def cwd(self) -> str:
        return self._cwd

    def clear(self) -> None:
        self._lines.clear()

    def history(self) -> list[dict[str, str]]:
        return list(self._lines)

    def status(self) -> dict[str, Any]:
        return {"open": self._open, "cwd": self._cwd, "commands": len(self._lines)}
