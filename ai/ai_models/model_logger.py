"""AI Model logger."""

from __future__ import annotations

import time
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ModelLogger:
    def __init__(self, max_entries: int = 100000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max = max_entries

    def log(self, level: LogLevel, message: str, source: str = "", model_id: str = "") -> dict[str, Any]:
        entry = {
            "level": level.value,
            "message": message,
            "source": source,
            "model_id": model_id,
            "timestamp": time.time(),
        }
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
        return entry

    def info(self, message: str, source: str = "", model_id: str = "") -> dict[str, Any]:
        return self.log(LogLevel.INFO, message, source, model_id)

    def warning(self, message: str, source: str = "", model_id: str = "") -> dict[str, Any]:
        return self.log(LogLevel.WARNING, message, source, model_id)

    def error(self, message: str, source: str = "", model_id: str = "") -> dict[str, Any]:
        return self.log(LogLevel.ERROR, message, source, model_id)

    def query(self, level: LogLevel | None = None, model_id: str = "", limit: int = 100) -> list[dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e["level"] == level.value]
        if model_id:
            entries = [e for e in entries if e.get("model_id") == model_id]
        return entries[-limit:]

    def count(self) -> int:
        return len(self._entries)
