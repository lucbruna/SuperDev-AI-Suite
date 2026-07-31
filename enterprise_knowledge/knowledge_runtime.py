"""Runtime lifecycle for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

import threading
import time
from typing import Any

from enterprise_knowledge.knowledge_logger import get_logger


class EnterpriseKnowledgeRuntime:
    """Idempotent start/stop with state tracking."""

    def __init__(self) -> None:
        self._log = get_logger("runtime")
        self._lock = threading.Lock()
        self._running = False
        self._started_at = 0.0

    def start(self) -> bool:
        with self._lock:
            if self._running:
                return True
            self._running = True
            self._started_at = time.time()
            self._log.info("enterprise knowledge runtime started")
            return True

    def stop(self) -> bool:
        with self._lock:
            if not self._running:
                return True
            self._running = False
            self._log.info("enterprise knowledge runtime stopped")
            return True

    def is_running(self) -> bool:
        return self._running

    def state(self) -> dict[str, Any]:
        return {"running": self._running,
                "started_at": self._started_at,
                "uptime": (time.time() - self._started_at)
                if self._running else 0.0}
