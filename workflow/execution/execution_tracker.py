from __future__ import annotations

import time
from typing import Any


class ExecutionTracker:
    """Real-time execution progress tracker."""

    def __init__(self) -> None:
        self._progress: dict[str, dict[str, Any]] = {}

    def update(self, exec_id: str, step_id: str, status: str) -> None:
        if exec_id not in self._progress:
            self._progress[exec_id] = {
                "exec_id": exec_id,
                "steps": {},
                "started_at": time.time(),
            }
        self._progress[exec_id]["steps"][step_id] = {
            "status": status,
            "timestamp": time.time(),
        }
        self._progress[exec_id]["last_update"] = time.time()

    def snapshot(self, exec_id: str) -> dict[str, Any] | None:
        return self._progress.get(exec_id)

    def list_active(self) -> list[str]:
        now = time.time()
        return [
            eid for eid, data in self._progress.items()
            if now - data.get("last_update", 0) < 3600
        ]
