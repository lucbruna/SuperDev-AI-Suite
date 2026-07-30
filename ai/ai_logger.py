from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from .ai_context import AIContext


class AILogger:
    """Structured logger for the AI engine."""

    def __init__(self, name: str = "ai_engine", level: str = "INFO"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()

        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(getattr(logging, level.upper(), logging.INFO))
        console.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        self._logger.addHandler(console)

        self._enable_json: bool = False
        self._handlers: list[logging.Handler] = [console]

    def set_level(self, level: str) -> None:
        """Set the logging level."""
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def enable_json(self, enabled: bool = True) -> None:
        """Enable or disable JSON structured logging."""
        self._enable_json = enabled

    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom log handler."""
        self._logger.addHandler(handler)
        self._handlers.append(handler)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal log method with structured context."""
        extra = kwargs.pop("extra", {})
        record = {
            "message": message,
            "level": logging.getLevelName(level),
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": AIContext.get_request_id(),
            "session_id": AIContext.get_session_id(),
            "user_id": AIContext.get_user_id(),
            **extra,
        }

        if self._enable_json:
            self._logger.log(level, json.dumps(record))
        else:
            context_parts = []
            if record["request_id"]:
                context_parts.append(f"req={record['request_id']}")
            if record["session_id"]:
                context_parts.append(f"ses={record['session_id']}")
            context_str = f" [{', '.join(context_parts)}]" if context_parts else ""
            extra_str = f" | {json.dumps(extra)}" if extra else ""
            self._logger.log(level, f"{message}{context_str}{extra_str}")

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self._log(logging.ERROR, message, **kwargs)

    def warn(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback."""
        self._logger.exception(message)

    def health(self) -> dict[str, Any]:
        """Get logger health status."""
        return {
            "status": "healthy",
            "level": logging.getLevelName(self._logger.level),
            "json_mode": self._enable_json,
            "handlers": len(self._handlers),
            "timestamp": datetime.now(UTC).isoformat(),
        }
