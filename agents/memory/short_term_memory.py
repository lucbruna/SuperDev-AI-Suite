from __future__ import annotations

import asyncio
import time
from typing import Any

from ..base.base_memory import BaseMemory


class ShortTermMemory(BaseMemory):
    def __init__(self, ttl: int = 300) -> None:
        self._data: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl
        self._lock = asyncio.Lock()

    async def store(self, key: str, value: Any) -> None:
        async with self._lock:
            self._data[key] = (value, time.time())
        await self._cleanup()

    async def retrieve(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            value, timestamp = entry
            if time.time() - timestamp > self._ttl:
                del self._data[key]
                return None
            return value

    async def search(self, query: str) -> list[Any]:
        await self._cleanup()
        results = []
        q = query.lower()
        async with self._lock:
            for key, (value, _) in self._data.items():
                if q in key.lower():
                    results.append(value)
        return results

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()

    async def _cleanup(self) -> None:
        now = time.time()
        async with self._lock:
            expired = [k for k, (_, t) in self._data.items() if now - t > self._ttl]
            for k in expired:
                del self._data[k]

    def size(self) -> int:
        return len(self._data)
