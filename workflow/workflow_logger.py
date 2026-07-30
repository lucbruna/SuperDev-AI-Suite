from __future__ import annotations

import logging
from typing import Any


class WorkflowLogger:
    """Structured logger for workflow events."""

    def __init__(self, name: str = "workflow") -> None:
        self._log = logging.getLogger(f"superdev.{name}")
        self._entries: list[dict[str, Any]] = []

    def info(self, message: str, **kwargs: Any) -> None:
        self._log.info(message, extra=kwargs)
        self._entries.append({"level": "INFO", "message": message, **kwargs})

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log.warning(message, extra=kwargs)
        self._entries.append({"level": "WARNING", "message": message, **kwargs})

    def error(self, message: str, **kwargs: Any) -> None:
        self._log.error(message, extra=kwargs)
        self._entries.append({"level": "ERROR", "message": message, **kwargs})

    def get_entries(self) -> list[dict[str, Any]]:
        return list(self._entries)
