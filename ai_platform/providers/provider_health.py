from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime

from .base_provider import BaseProvider, HealthStatus


class ProviderHealth:
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.last_status: HealthStatus | None = None

    async def check(self) -> HealthStatus:
        start = time.monotonic()
        try:
            status = await self.provider.health()
            elapsed = (time.monotonic() - start) * 1000
            status.latency_ms = elapsed
            status.last_check = datetime.now(UTC)
            self.last_status = status
            return status
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            status = HealthStatus(
                status="unhealthy",
                latency_ms=elapsed,
                last_check=datetime.now(UTC),
                error=str(e),
            )
            self.last_status = status
            return status


class HealthChecker:
    def __init__(self, interval: float = 60.0):
        self.interval = interval
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, HealthStatus] = {}

    async def check(self, provider: BaseProvider) -> bool:
        try:
            status = await provider.health()
            self._results[id(provider)] = status
            return status.status == "healthy"
        except Exception:
            return False

    async def run_periodic(self, name: str, provider: BaseProvider) -> None:
        health = ProviderHealth(provider)
        while True:
            status = await health.check()
            self._results[name] = status
            await asyncio.sleep(self.interval)

    def start_periodic(self, name: str, provider: BaseProvider) -> None:
        task = asyncio.create_task(self.run_periodic(name, provider))
        self._tasks[name] = task

    def stop_all(self) -> None:
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()

    def get_result(self, name: str) -> HealthStatus | None:
        return self._results.get(name)
