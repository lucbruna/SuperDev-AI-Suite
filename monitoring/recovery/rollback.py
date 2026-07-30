from __future__ import annotations

import logging
import time
from typing import Any, Callable


class RollbackManager:
    """Manages rollback of operations to a known good state."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Any] = {}
        self._rollback_handlers: dict[str, Callable[[], None]] = {}
        self._logger = logging.getLogger("superdev.recovery.rollback")

    def checkpoint(self, name: str, state: Any) -> None:
        import copy
        self._checkpoints[name] = copy.deepcopy(state)
        self._logger.info("Checkpoint saved: %s", name)

    def register_rollback(self, name: str, handler: Callable[[], None]) -> None:
        self._rollback_handlers[name] = handler

    def rollback(self, name: str) -> bool:
        if name not in self._checkpoints:
            self._logger.error("No checkpoint found: %s", name)
            return False

        try:
            handler = self._rollback_handlers.get(name)
            if handler:
                handler()
            del self._checkpoints[name]
            self._logger.info("Rollback completed: %s", name)
            return True
        except Exception as e:
            self._logger.error("Rollback failed for %s: %s", name, e)
            return False

    def rollback_all(self) -> int:
        count = 0
        for name in list(self._checkpoints.keys()):
            if self.rollback(name):
                count += 1
        return count

    def has_checkpoint(self, name: str) -> bool:
        return name in self._checkpoints

    def list_checkpoints(self) -> list[str]:
        return list(self._checkpoints.keys())
