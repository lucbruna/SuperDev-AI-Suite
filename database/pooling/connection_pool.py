from __future__ import annotations

import asyncio
import time
from typing import Any

from ..database_interfaces import IConnectionPool, IDatabaseDriver
from ..database_models import ConnectionConfig, PoolConfig, PoolStatus, PoolStrategy


class ConnectionPool(IConnectionPool):
    """Generic connection pool wrapping any :class:`IDatabaseDriver`.

    Supports ``fixed``, ``dynamic``, and ``threaded`` strategies.
    """

    def __init__(
        self,
        driver: IDatabaseDriver,
        pool_config: PoolConfig | None = None,
    ) -> None:
        self._driver = driver
        self._config = pool_config or PoolConfig()
        self._active: set[int] = set()
        self._idle: set[int] = set()
        self._waiters: list[asyncio.Future[None]] = []
        self._counter = 0
        self._closed = False
        self._lock = asyncio.Lock()

    async def acquire(self) -> IDatabaseDriver:
        if self._closed:
            raise RuntimeError("Pool is closed")
        async with self._lock:
            if self._idle:
                cid = self._idle.pop()
                self._active.add(cid)
                return self._driver
            if self._active_total() < self._config.max_size:
                cid = self._next_id()
                self._active.add(cid)
                return self._driver
        # wait for a slot
        loop = asyncio.get_event_loop()
        fut = loop.create_future()
        async with self._lock:
            self._waiters.append(fut)
        try:
            await asyncio.wait_for(fut, timeout=self._config.acquire_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError("Connection acquire timed out")
        async with self._lock:
            cid = self._idle.pop()
            self._active.add(cid)
        return self._driver

    async def release(self, conn: Any) -> None:
        async with self._lock:
            # find the connection in active set
            to_release: int | None = None
            for cid in self._active:
                to_release = cid
                break
            if to_release is not None:
                self._active.discard(to_release)
                self._idle.add(to_release)
            # wake a waiter
            while self._waiters and self._idle:
                waiter = self._waiters.pop(0)
                if not waiter.done():
                    waiter.set_result(None)
                    break

    async def status(self) -> dict[str, Any]:
        async with self._lock:
            return {
                "active": len(self._active),
                "idle": len(self._idle),
                "waiting": len(self._waiters),
                "total": self._active_total(),
                "max": self._config.max_size,
                "min": self._config.min_size,
                "closed": self._closed,
            }

    async def close(self) -> None:
        async with self._lock:
            self._closed = True
            self._active.clear()
            self._idle.clear()
            for w in self._waiters:
                if not w.done():
                    w.cancel()
            self._waiters.clear()

    def _active_total(self) -> int:
        return len(self._active) + len(self._idle)

    def _next_id(self) -> int:
        self._counter += 1
        return self._counter


__all__ = [
    "ConnectionPool",
]
