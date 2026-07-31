from datetime import timedelta
from typing import Any

from backend.utils.datetime import utc_now
from backend.utils.uuid_utils import generate_uuid
from redis.asyncio import Redis

SESSION_PREFIX = "session:"
SESSION_TTL = timedelta(hours=24)


class SessionManager:
    def __init__(self, ttl: timedelta = SESSION_TTL) -> None:
        self.ttl = ttl

    async def create_session(
        self,
        user_id: str,
        redis_client: Redis,
        ttl: timedelta | None = None,
    ) -> str:
        session_id = generate_uuid()
        session_key = f"{SESSION_PREFIX}{session_id}"
        session_data = {
            "user_id": user_id,
            "created_at": utc_now().isoformat(),
        }
        expiry = ttl or self.ttl
        await redis_client.setex(session_key, int(expiry.total_seconds()), str(session_data))
        return session_id

    async def get_session(
        self,
        session_id: str,
        redis_client: Redis,
    ) -> dict[str, Any] | None:
        session_key = f"{SESSION_PREFIX}{session_id}"
        data = await redis_client.get(session_key)
        if data is None:
            return None
        return {"session_id": session_id, "user_id": data.decode("utf-8")}

    async def delete_session(
        self,
        session_id: str,
        redis_client: Redis,
    ) -> bool:
        session_key = f"{SESSION_PREFIX}{session_id}"
        deleted = await redis_client.delete(session_key)
        return deleted > 0

    async def cleanup_expired(
        self,
        redis_client: Redis,
    ) -> int:
        count = 0
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match=f"{SESSION_PREFIX}*", count=100)
            if keys:
                count += await redis_client.delete(*keys)
            if cursor == 0:
                break
        return count
