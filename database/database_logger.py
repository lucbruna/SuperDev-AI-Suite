from __future__ import annotations

import logging
import time
from typing import Any


class DatabaseLogger:
    """Specialized logger for database operations with query tracking."""

    def __init__(self, name: str = "database", level: int = logging.INFO) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._query_log_enabled = False

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def enable_query_logging(self) -> None:
        self._query_log_enabled = True

    def disable_query_logging(self) -> None:
        self._query_log_enabled = False

    def debug(self, message: str, **context: Any) -> None:
        self._logger.debug(self._format(message, **context))

    def info(self, message: str, **context: Any) -> None:
        self._logger.info(self._format(message, **context))

    def warning(self, message: str, **context: Any) -> None:
        self._logger.warning(self._format(message, **context))

    def error(self, message: str, **context: Any) -> None:
        self._logger.error(self._format(message, **context))

    def critical(self, message: str, **context: Any) -> None:
        self._logger.critical(self._format(message, **context))

    def query(self, query: str, duration_ms: float, **context: Any) -> None:
        if not self._query_log_enabled:
            return
        context_str = " | ".join(f"{k}={v}" for k, v in context.items()) if context else ""
        prefix = f"[{context_str}] " if context_str else ""
        self._logger.debug(f"{prefix}Query ({duration_ms:.2f}ms): {query[:200]}")

    def slow_query(self, query: str, duration_ms: float, threshold: float = 1000.0) -> None:
        if duration_ms >= threshold:
            self._logger.warning(f"SLOW QUERY ({duration_ms:.2f}ms, threshold={threshold}ms): {query[:200]}")

    def _format(self, message: str, **context: Any) -> str:
        if not context:
            return message
        ctx = " | ".join(f"{k}={v}" for k, v in context.items())
        return f"[{ctx}] {message}"

    def get_logger(self) -> logging.Logger:
        return self._logger
