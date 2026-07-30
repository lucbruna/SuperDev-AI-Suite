from __future__ import annotations

import logging
from typing import Any

from .monitoring_models import LogEntry, LogLevel


class MonitoringLogger:
    """Structured logger bridging to Python's logging module."""

    def __init__(self, name: str = "monitoring") -> None:
        self._logger = logging.getLogger(name)
        self._entries: list[LogEntry] = []

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log(LogLevel.INFO, message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        self._log(LogLevel.WARN, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def _log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        entry = LogEntry(
            message=message,
            level=level,
            logger=self._logger.name,
            labels=kwargs.pop("labels", {}),
            extra=kwargs,
        )
        self._entries.append(entry)
        log_fn = getattr(self._logger, level.value, self._logger.info)
        log_fn(message, extra=kwargs)

    def get_entries(self, limit: int = 100) -> list[LogEntry]:
        return self._entries[-limit:]

    def clear(self) -> None:
        self._entries.clear()


__all__ = ["MonitoringLogger"]
