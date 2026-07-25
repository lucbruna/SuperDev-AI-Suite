import logging
from typing import Dict, Optional
from .structured_logger import StructuredLogger


class LogManager:
    def __init__(self, global_level: int = logging.INFO) -> None:
        self._global_level = global_level
        self._loggers: Dict[str, StructuredLogger] = {}
        self._handlers: list[logging.Handler] = []

    def get_logger(self, name: str) -> StructuredLogger:
        if name not in self._loggers:
            self._loggers[name] = StructuredLogger(name, self._global_level)
        return self._loggers[name]

    def set_level(self, level: int) -> None:
        self._global_level = level
        for logger in self._loggers.values():
            logger.set_level(level)

    def add_handler(self, handler: logging.Handler) -> None:
        self._handlers.append(handler)
        for logger in self._loggers.values():
            logger.add_handler(handler)

    @property
    def loggers(self) -> Dict[str, StructuredLogger]:
        return dict(self._loggers)

    @property
    def global_level(self) -> int:
        return self._global_level
