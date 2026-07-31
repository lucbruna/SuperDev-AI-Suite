from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ReasoningLogger:
    """Structured logger for reasoning operations."""

    def __init__(self, name: str = "reasoning"):
        self._name = name
        self._logs: list[dict[str, Any]] = []

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        self._log("WARN", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "logger": self._name,
            "level": level,
            "message": message,
            **kwargs,
        }
        self._logs.append(entry)

    def get_logs(self, level: str | None = None) -> list[dict[str, Any]]:
        if level:
            return [log for log in self._logs if log["level"] == level]
        return self._logs

    def clear(self) -> None:
        self._logs.clear()
