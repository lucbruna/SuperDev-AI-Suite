from __future__ import annotations

import logging
from typing import Any


class DataLogger:
    """Structured logger bridging to Python's logging module."""

    def __init__(self, name: str = "data") -> None:
        self._logger = logging.getLogger(name)
        self._entries: list[dict[str, Any]] = []

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("info", message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        self._log("warn", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("critical", message, **kwargs)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        entry = {
            "level": level,
            "message": message,
            "labels": kwargs.pop("labels", {}),
            "extra": kwargs,
        }
        self._entries.append(entry)
        log_fn = getattr(self._logger, level, self._logger.info)
        log_fn(message, extra=kwargs)

    def get_entries(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._entries[-limit:]

    def clear(self) -> None:
        self._entries.clear()


__all__ = ["DataLogger"]
