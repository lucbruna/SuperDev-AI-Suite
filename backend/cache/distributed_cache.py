from typing import Any

import msgpack

from .redis_client import RedisClient


class DistributedCache:
    def __init__(
        self,
        redis_client: RedisClient,
        namespace: str = "superdev",
    ) -> None:
        self._redis = redis_client
        self._namespace = namespace

    def _make_key(self, key: str) -> str:
        return f"{self._namespace}:{key}"

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(self._make_key(key))
        if raw is None:
            return None
        try:
            return msgpack.unpackb(raw)
        except (msgpack.UnpackException, TypeError):
            return raw

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        packed = msgpack.packb(value)
        await self._redis.set(self._make_key(key), packed, ttl=ttl)

    async def delete(self, key: str) -> bool:
        return await self._redis.delete(self._make_key(key))

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(self._make_key(key))
