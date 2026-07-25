from __future__ import annotations

from typing import Any

from backend.cache.memory_cache import MemoryCache
from backend.cache.redis_client import RedisClient


class CacheManager:
    """Unified cache manager with memory and Redis backends."""

    def __init__(self):
        self._memory = MemoryCache()
        self._redis: RedisClient | None = None

    def set_redis(self, redis: RedisClient) -> None:
        self._redis = redis

    async def get(self, key: str) -> Any | None:
        result = self._memory.get(key)
        if result is not None:
            return result
        if self._redis:
            return await self._redis.get(key)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._memory.set(key, value, ttl)
        if self._redis:
            await self._redis.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        self._memory.delete(key)
        if self._redis:
            await self._redis.delete(key)
        return True

    async def exists(self, key: str) -> bool:
        if self._memory.get(key) is not None:
            return True
        if self._redis:
            return await self._redis.exists(key)
        return False

    async def clear(self, prefix: str = "") -> int:
        self._memory.clear()
        if self._redis:
            return await self._redis.clear(prefix)
        return 0


cache_manager = CacheManager()
