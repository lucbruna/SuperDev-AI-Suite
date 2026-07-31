from __future__ import annotations

import logging
import sys
from typing import Any


class KnowledgeLogger:
    """Provides a structured logger bound to the knowledge namespace."""

    def __init__(self, name: str = "superdev.knowledge", level: int = logging.INFO) -> None:
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
            )
            self._logger.addHandler(handler)
        self._logger.setLevel(level)
        self._logger.propagate = False

    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(self._format(message, kwargs))

    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(self._format(message, kwargs))

    def warning(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(self._format(message, kwargs))

    def error(self, message: str, **kwargs: Any) -> None:
        self._logger.error(self._format(message, kwargs))

    def child(self, suffix: str) -> "KnowledgeLogger":
        return KnowledgeLogger(f"{self._logger.name}.{suffix}", self._logger.level)

    @staticmethod
    def _format(message: str, kwargs: dict[str, Any]) -> str:
        if not kwargs:
            return message
        try:
            return message % kwargs
        except (TypeError, ValueError):
            return f"{message} {kwargs}"
