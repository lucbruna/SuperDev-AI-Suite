from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Callable


class DashboardRefresh:
    """Manages auto-refresh scheduling for dashboards."""

    def __init__(self) -> None:
        self._intervals: dict[str, int] = {}
        self._callbacks: dict[str, Callable[[], None]] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._logger = logging.getLogger("superdev.dashboards.refresh")

    def schedule(
        self,
        dashboard_id: str,
        callback: Callable[[], None],
        interval_seconds: int = 60,
    ) -> None:
        self._intervals[dashboard_id] = interval_seconds
        self._callbacks[dashboard_id] = callback

    async def start(self, dashboard_id: str) -> None:
        if dashboard_id in self._tasks:
            return
        interval = self._intervals.get(dashboard_id, 60)

        async def _loop() -> None:
            while True:
                try:
                    callback = self._callbacks.get(dashboard_id)
                    if callback:
                        callback()
                except Exception as e:
                    self._logger.error("Refresh error for %s: %s", dashboard_id, e)
                await asyncio.sleep(interval)

        self._tasks[dashboard_id] = asyncio.create_task(_loop())

    def stop(self, dashboard_id: str) -> None:
        task = self._tasks.pop(dashboard_id, None)
        if task:
            task.cancel()

    def stop_all(self) -> None:
        for dashboard_id in list(self._tasks.keys()):
            self.stop(dashboard_id)

    def update_interval(self, dashboard_id: str, interval_seconds: int) -> None:
        self._intervals[dashboard_id] = interval_seconds
        self.stop(dashboard_id)

    async def start_all(self) -> None:
        for dashboard_id in list(self._intervals.keys()):
            await self.start(dashboard_id)
