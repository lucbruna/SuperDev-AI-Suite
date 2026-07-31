"""Enterprise logger."""

from __future__ import annotations

import time
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EnterpriseLogger:
    def __init__(self, max_entries: int = 100000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max = max_entries

    def log(
        self, level: LogLevel, message: str, source: str = "", context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        entry = {
            "level": level.value,
            "message": message,
            "source": source,
            "context": context or {},
            "timestamp": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
        return entry

    def info(self, message: str, source: str = "") -> dict[str, Any]:
        return self.log(LogLevel.INFO, message, source)

    def warning(self, message: str, source: str = "") -> dict[str, Any]:
        return self.log(LogLevel.WARNING, message, source)

    def error(self, message: str, source: str = "") -> dict[str, Any]:
        return self.log(LogLevel.ERROR, message, source)

    def query(self, level: LogLevel | None = None, source: str = "", limit: int = 100) -> list[dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e["level"] == level.value]
        if source:
            entries = [e for e in entries if e["source"] == source]
        return entries[-limit:]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
