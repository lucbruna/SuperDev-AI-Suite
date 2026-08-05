"""AIOS Kernel Logger — leveled in-memory logging with optional sink.

Deterministic and side-effect free by default: records are kept in
memory and can be drained by a sink callable (e.g. wiring into the
platform's real logger at compose time).
"""

from __future__ import annotations

import time
from typing import Any, Callable

LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}


class KernelLogger:
    """Minimal leveled logger used across the AIOS."""

    def __init__(self, level: str = "info", sink: Callable[[dict[str, Any]], None] | None = None) -> None:
        self.level = LEVELS.get(level, LEVELS["info"])
        self._records: list[dict[str, Any]] = []
        self._sink = sink

    def set_level(self, level: str) -> None:
        self.level = LEVELS.get(level, self.level)

    def _log(self, level: str, message: str, **context: Any) -> None:
        if LEVELS[level] < self.level:
            return
        record = {
            "level": level,
            "message": message,
            "context": context,
            "timestamp": time.time(),
        }
        self._records.append(record)
        if self._sink is not None:
            self._sink(record)

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

    def clear(self) -> None:
        self._records.clear()

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for record in self._records:
            counts[record["level"]] = counts.get(record["level"], 0) + 1
        return counts
