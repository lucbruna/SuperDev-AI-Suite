from __future__ import annotations
import hashlib
import json
import time
from typing import Any, Optional
from collections import OrderedDict

from ..providers.base_provider import ChatResponse


class PromptCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: OrderedDict[str, tuple[Any, float, float]] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._redis = None
        self._redis_enabled = False

    async def initialize(self) -> None:
        try:
            import redis.asyncio as redis
            from ..core.configuration import get_platform_config
            config = get_platform_config()
            if config.redis_url:
                self._redis = redis.from_url(config.redis_url, decode_responses=True)
                self._redis_enabled = True
        except Exception:
            self._redis_enabled = False

    def cache_key(self, messages: list[dict], model: str = "", config: Optional[dict] = None) -> str:
        raw = json.dumps({"messages": messages, "model": model, "config": config or {}}, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        if self._redis_enabled and self._redis:
            try:
                data = await self._redis.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass

        if key in self._cache:
            value, expiry, _ = self._cache[key]
            if time.time() < expiry:
                self._cache.move_to_end(key)
                return value
            else:
                del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl

        if self._redis_enabled and self._redis:
            try:
                data = json.dumps(value, default=str)
                await self._redis.setex(key, ttl, data)
            except Exception:
                pass

        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        self._cache[key] = (value, expiry, time.time())

    async def invalidate(self, pattern: str) -> int:
        count = 0
        keys_to_delete = [k for k in self._cache if pattern in k]
        for k in keys_to_delete:
            del self._cache[k]
            count += 1

        if self._redis_enabled and self._redis:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis.scan(cursor=cursor, match=f"*{pattern}*")
                    if keys:
                        await self._redis.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
            except Exception:
                pass
        return count

    def clear(self) -> None:
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)
