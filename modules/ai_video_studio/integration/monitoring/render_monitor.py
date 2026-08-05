"""Render Monitor — tracks render job states in-process."""
from __future__ import annotations

from typing import Any


class RenderMonitor:
    """Records render job lifecycle events."""

    def __init__(self) -> None:
        self._jobs: dict[str, str] = {}

    def track(self, job_id: str, status: str) -> None:
        self._jobs[job_id] = status

    def collect(self) -> dict[str, Any]:
        by_status: dict[str, int] = {}
        for status in self._jobs.values():
            by_status[status] = by_status.get(status, 0) + 1
        return {"jobs": len(self._jobs), "by_status": by_status}


_render_monitor: RenderMonitor | None = None


def get_render_monitor() -> RenderMonitor:
    global _render_monitor
    if _render_monitor is None:
        _render_monitor = RenderMonitor()
    return _render_monitor
