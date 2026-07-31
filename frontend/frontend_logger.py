from __future__ import annotations

import logging
import sys
from typing import Any


class FrontendLogger:
    """Structured logger for the frontend platform."""

    def __init__(self, name: str = "superdev.frontend", level: int = logging.INFO) -> None:
        self._log = logging.getLogger(name)
        self._log.setLevel(level)
        self._handlers: list[logging.Handler] = []
        self._bound: dict[str, Any] = {}

    def info(self, message: str, **context: Any) -> None:
        self._log.info(message, extra={"context": {**self._bound, **context}})

    def warning(self, message: str, **context: Any) -> None:
        self._log.warning(message, extra={"context": {**self._bound, **context}})

    def error(self, message: str, **context: Any) -> None:
        self._log.error(message, extra={"context": {**self._bound, **context}})

    def debug(self, message: str, **context: Any) -> None:
        self._log.debug(message, extra={"context": {**self._bound, **context}})

    def bind(self, **context: Any) -> "FrontendLogger":
        bound = FrontendLogger(self._log.name, self._log.level)
        bound._bound = {**self._bound, **context}
        for handler in self._handlers:
            bound.add_handler(handler)
        return bound

    def add_handler(self, handler: logging.Handler) -> None:
        self._handlers.append(handler)
        self._log.addHandler(handler)

    def add_default_handler(self) -> None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        self.add_handler(handler)
