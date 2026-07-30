from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DecisionLogger:
    """Structured logging for decision operations."""

    def __init__(self):
        self._logs: list[dict[str, Any]] = []

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        self._log("WARN", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        self._logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **kwargs,
        })

    def get_logs(self, level: str | None = None) -> list[dict[str, Any]]:
        if level:
            return [log for log in self._logs if log["level"] == level]
        return list(self._logs)

    def clear(self) -> None:
        self._logs.clear()
