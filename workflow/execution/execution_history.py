from __future__ import annotations

import time
from typing import Any


class ExecutionHistory:
    """Records execution history for workflows."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(
        self, exec_id: str, step_id: str, status: str, duration: float
    ) -> None:
        self._records.append({
            "exec_id": exec_id,
            "step_id": step_id,
            "status": status,
            "duration": duration,
            "timestamp": time.time(),
        })

    def query(self, exec_id: str | None = None) -> list[dict[str, Any]]:
        if exec_id:
            return [r for r in self._records if r["exec_id"] == exec_id]
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()
