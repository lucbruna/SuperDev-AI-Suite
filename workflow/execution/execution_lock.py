from __future__ import annotations

import logging
import time
from typing import Any


class ExecutionLock:
    """Prevents concurrent execution of the same workflow."""

    def __init__(self, timeout: float = 300.0) -> None:
        self._locks: dict[str, float] = {}
        self._timeout = timeout
        self._log = logging.getLogger("superdev.workflow.execution.lock")

    def acquire(self, lock_id: str) -> bool:
        now = time.time()
        if lock_id in self._locks:
            if now - self._locks[lock_id] < self._timeout:
                return False
            self._log.warning("Lock expired for %s, reacquiring", lock_id)
        self._locks[lock_id] = now
        return True

    def release(self, lock_id: str) -> None:
        self._locks.pop(lock_id, None)

    def is_locked(self, lock_id: str) -> bool:
        return lock_id in self._locks
