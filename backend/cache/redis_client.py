from __future__ import annotations

from typing import Any


class RedisClient:
    """Redis client wrapper."""

    def __init__(self, redis_instance=None):
        self._redis = redis_instance

    async def get(self, key: str) -> Any | None:
        if not self._redis:
            return None
        return await self._redis.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self._redis:
            return
        if ttl:
            await self._redis.setex(key, ttl, value)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> bool:
        if not self._redis:
            return False
        return await self._redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        if not self._redis:
            return False
        return await self._redis.exists(key) > 0

    async def clear(self, prefix: str = "") -> int:
        if not self._redis:
            return 0
        if prefix:
            keys = []
            async for key in self._redis.scan_iter(f"{prefix}*"):
                keys.append(key)
            if keys:
                return await self._redis.delete(*keys)
        return 0

    async def incr(self, key: str) -> int:
        if not self._redis:
            return 0
        return await self._redis.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        if self._redis:
            await self._redis.expire(key, ttl)
