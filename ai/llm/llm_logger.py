from __future__ import annotations

import logging
from typing import Any


class LLMLogger:
    """Structured logger for LLM operations."""

    def __init__(self, name: str = "llm", level: int = logging.INFO) -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

    def _log(self, level: int, provider: str, message: str, **kwargs: Any) -> None:
        extra = {"provider": provider, **(kwargs if kwargs else {})}
        self._logger.log(level, "[%s] %s - %s", provider, message, extra)

    def info(self, provider: str, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, provider, message, **kwargs)

    def warning(self, provider: str, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, provider, message, **kwargs)

    def error(self, provider: str, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, provider, message, **kwargs)

    def debug(self, provider: str, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, provider, message, **kwargs)
