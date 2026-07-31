"""Structured logging for the Security Engine (Volume 16)."""

from __future__ import annotations

import json
import logging
from typing import Any


class SecurityLogger:
    """Thin structured-logging wrapper emitting JSON lines."""

    def __init__(self, name: str = "security-engine") -> None:
        self._log = logging.getLogger(f"superdev.{name}")

    def _emit(self, level: str, message: str, **context: Any) -> None:
        record = {"event": "security." + level, "message": message, **context}
        line = json.dumps(record, default=str)
        getattr(self._log, level if level != "warn" else "warning")(line)

    def info(self, message: str, **context: Any) -> None:
        self._emit("info", message, **context)

    def warning(self, message: str, **context: Any) -> None:
        self._emit("warn", message, **context)

    def error(self, message: str, **context: Any) -> None:
        self._emit("error", message, **context)

    def critical(self, message: str, **context: Any) -> None:
        self._emit("critical", message, **context)
