from __future__ import annotations

import logging
from typing import Any


class LogViewer:
    """Filters and displays debug logs."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.debugging.logs")
        self._entries: list[dict[str, Any]] = []

    def add_entry(self, level: str, source: str, message: str) -> None:
        self._entries.append({"level": level, "source": source, "message": message})

    def filter(self, level: str | None = None, source: str | None = None) -> list[dict[str, Any]]:
        result = list(self._entries)
        if level:
            result = [e for e in result if e["level"] == level]
        if source:
            result = [e for e in result if e["source"] == source]
        return result

    def clear(self) -> None:
        self._entries.clear()
