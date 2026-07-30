from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any


_lock_registry: dict[str, str] = {}
_mutex: asyncio.Lock = asyncio.Lock()


class DistributedLock:
    """Simple distributed lock backed by an async-compatible in-process store.

    For production use, back this with Redis or a database advisory lock.
    """

    def __init__(self, resource: str, ttl: float = 30.0) -> None:
        self._resource = resource
        self._ttl = ttl
        self._owner = uuid.uuid4().hex
        self._acquired = False

    async def acquire(self, blocking: bool = True, timeout: float | None = None) -> bool:
        start = time.monotonic()
        while True:
            async with _mutex:
                if self._resource not in _lock_registry:
                    _lock_registry[self._resource] = self._owner
                    self._acquired = True
                    return True
            if not blocking:
                return False
            if timeout is not None and (time.monotonic() - start) > timeout:
                return False
            await asyncio.sleep(0.05)

    async def release(self) -> None:
        async with _mutex:
            if _lock_registry.get(self._resource) == self._owner:
                del _lock_registry[self._resource]
                self._acquired = False

    @property
    def is_acquired(self) -> bool:
        return self._acquired

    async def __aenter__(self) -> DistributedLock:
        await self.acquire(blocking=True)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.release()


__all__ = [
    "DistributedLock",
]
