"""History of monitoring reports."""

from __future__ import annotations

import time
from typing import Any


class MonitorHistory:
    """Append-only log of monitoring snapshots."""

    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []

    def snapshot(self, report: dict[str, Any]) -> None:
        self._snapshots.append({**report, "captured_at": time.time()})

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._snapshots[-limit:])

    def count(self) -> int:
        return len(self._snapshots)

    def clear(self) -> None:
        self._snapshots.clear()
