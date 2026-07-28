from __future__ import annotations

import json
import os
from typing import Any

import redis.asyncio as aioredis


class AsyncTaskQueue:
    def __init__(self, redis_url: str | None = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis: aioredis.Redis | None = None

    async def connect(self):
        if not self._redis:
            self._redis = aioredis.from_url(self._redis_url, decode_responses=True)

    async def push(self, queue: str, task: dict[str, Any]) -> None:
        await self.connect()
        await self._redis.lpush(queue, json.dumps(task, default=str))

    async def pop(self, queue: str, timeout: int = 5) -> dict[str, Any] | None:
        await self.connect()
        result = await self._redis.brpop(queue, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None

    async def length(self, queue: str) -> int:
        await self.connect()
        return await self._redis.llen(queue)

    async def peek(self, queue: str, index: int = 0) -> dict[str, Any] | None:
        await self.connect()
        result = await self._redis.lindex(queue, index)
        if result:
            return json.loads(result)
        return None

    async def clear(self, queue: str) -> None:
        await self.connect()
        await self._redis.delete(queue)

    async def list_queues(self) -> list[str]:
        await self.connect()
        keys = await self._redis.keys("*")
        return [k for k in keys if k]

    async def close(self):
        if self._redis:
            await self._redis.close()