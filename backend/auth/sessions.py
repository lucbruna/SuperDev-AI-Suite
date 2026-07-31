"""Session manager with lazy Redis import.

Redis is only imported when actually needed, preventing import failures
when Redis is not installed or configured.
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Any

from backend.utils.datetime import utc_now
from backend.utils.uuid_utils import generate_uuid

SESSION_PREFIX = "session:"
SESSION_TTL = timedelta(hours=24)


def _get_redis_url() -> str:
    return os.environ.get("REDIS_URL", "redis://localhost:6379/0")


class SessionManager:
    def __init__(self, ttl: timedelta = SESSION_TTL) -> None:
        self.ttl = ttl

    async def create_session(
        self,
        user_id: str,
        redis_client: Any | None = None,
        ttl: timedelta | None = None,
    ) -> str:
        session_id = generate_uuid()
        session_key = f"{SESSION_PREFIX}{session_id}"
        session_data = {
            "user_id": user_id,
            "created_at": utc_now().isoformat(),
        }
        expiry = ttl or self.ttl

        if redis_client is None:
            redis_client = await self._get_redis()

        if redis_client is None:
            # Fallback: return session ID without persistence
            return session_id

        await redis_client.setex(session_key, int(expiry.total_seconds()), str(session_data))
        return session_id

    async def get_session(
        self,
        session_id: str,
        redis_client: Any | None = None,
    ) -> dict[str, Any] | None:
        if redis_client is None:
            redis_client = await self._get_redis()
        if redis_client is None:
            return None

        session_key = f"{SESSION_PREFIX}{session_id}"
        data = await redis_client.get(session_key)
        if data is None:
            return None
        return {"session_id": session_id, "user_id": data.decode("utf-8")}

    async def delete_session(
        self,
        session_id: str,
        redis_client: Any | None = None,
    ) -> bool:
        if redis_client is None:
            redis_client = await self._get_redis()
        if redis_client is None:
            return False

        session_key = f"{SESSION_PREFIX}{session_id}"
        deleted = await redis_client.delete(session_key)
        return deleted > 0

    async def cleanup_expired(
        self,
        redis_client: Any | None = None,
    ) -> int:
        if redis_client is None:
            redis_client = await self._get_redis()
        if redis_client is None:
            return 0

        count = 0
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match=f"{SESSION_PREFIX}*", count=100)
            if keys:
                count += await redis_client.delete(*keys)
            if cursor == 0:
                break
        return count

    async def _get_redis(self) -> Any:
        """Lazily create and return a Redis client, or None if unavailable."""
        try:
            import redis.asyncio as aioredis

            return aioredis.from_url(_get_redis_url(), decode_responses=True, socket_connect_timeout=2)
        except Exception:
            return None
