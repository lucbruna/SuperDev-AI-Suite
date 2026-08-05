"""AIOS Logging Service — structured leveled records.

Records are kept in memory and fanned out to sinks (callables) for
integration with external loggers. Deterministic ordering.
"""

from __future__ import annotations

import time
from typing import Any, Callable

LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}

Sink = Callable[[dict[str, Any]], None]


class LoggingService:
    """Structured logger with fan-out sinks."""

    def __init__(self, level: str = "info") -> None:
        self._level = LEVELS.get(level, 20)
        self._sinks: list[Sink] = []
        self._records: list[dict[str, Any]] = []

    def set_level(self, level: str) -> None:
        self._level = LEVELS.get(level, self._level)

    def add_sink(self, sink: Sink) -> "LoggingService":
        self._sinks.append(sink)
        return self

    def _log(self, level: str, message: str, **context: Any) -> None:
        if LEVELS[level] < self._level:
            return
        record = {
            "level": level,
            "message": message,
            "context": context,
            "timestamp": time.time(),
        }
        self._records.append(record)
        for sink in self._sinks:
            sink(record)

    def debug(self, message: str, **context: Any) -> None:
        self._log("debug", message, **context)

    def info(self, message: str, **context: Any) -> None:
        self._log("info", message, **context)

    def warning(self, message: str, **context: Any) -> None:
        self._log("warning", message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._log("error", message, **context)

    def critical(self, message: str, **context: Any) -> None:
        self._log("critical", message, **context)

    def records(self, level: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        items = self._records
        if level is not None:
            items = [r for r in items if r["level"] == level]
        if limit is not None:
            items = items[-limit:]
        return list(items)

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._records:
            counts[record["level"]] = counts.get(record["level"], 0) + 1
        return counts
