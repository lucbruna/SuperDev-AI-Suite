from __future__ import annotations

import logging
import time
from typing import Any


class CodeLogger:
    """Structured logger for code operations."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.code.logger")

    def log(self, action: str, file_path: str, details: dict[str, Any] | None = None) -> None:
        entry = {
            "action": action,
            "file": file_path,
            "timestamp": time.time(),
            "details": details or {},
        }
        self._entries.append(entry)
        self._log.debug("%s %s", action, file_path)

    def history(self, file_path: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["file"] == file_path]
