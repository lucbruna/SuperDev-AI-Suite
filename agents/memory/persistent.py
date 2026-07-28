from __future__ import annotations

import json
from typing import Any

from ..base.base_memory import BaseMemory


class PersistentMemory(BaseMemory):
    def __init__(self, connection_string: str | None = None, redis_url: str | None = None):
        self._connection_string = connection_string
        self._redis_url = redis_url
        self._pg_pool: Any = None
        self._redis_client: Any = None
        self._initialized = False

    async def _ensure_pg(self):
        if self._pg_pool is None and self._connection_string:
            try:
                import asyncpg
                self._pg_pool = await asyncpg.create_pool(self._connection_string, min_size=1, max_size=5)
            except ImportError:
                pass

    async def _ensure_redis(self):
        if self._redis_client is None and self._redis_url:
            try:
                import redis.asyncio as aioredis
                self._redis_client = aioredis.from_url(self._redis_url, decode_responses=True)
            except ImportError:
                pass

    async def _initialize(self):
        if not self._initialized:
            await self._ensure_pg()
            await self._ensure_redis()
            if self._pg_pool:
                async with self._pg_pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS agent_memory (
                            key TEXT PRIMARY KEY,
                            value JSONB NOT NULL,
                            namespace TEXT NOT NULL DEFAULT 'default',
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            updated_at TIMESTAMPTZ DEFAULT NOW()
                        )
                    """)
                    await conn.execute("""
                        CREATE INDEX IF NOT EXISTS idx_memory_namespace ON agent_memory(namespace)
                    """)
            self._initialized = True

    async def store(self, key: str, value: Any, namespace: str = "default") -> None:
        await self._initialize()
        serialized = json.dumps(value, default=str)
        if self._pg_pool:
            async with self._pg_pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO agent_memory (key, value, namespace, updated_at)
                       VALUES ($1, $2::jsonb, $3, NOW())
                       ON CONFLICT (key) DO UPDATE SET value = $2::jsonb, updated_at = NOW()""",
                    key, serialized, namespace,
                )
        if self._redis_client:
            await self._redis_client.setex(f"memory:{namespace}:{key}", 86400, serialized)

    async def retrieve(self, key: str, namespace: str = "default") -> Any | None:
        await self._initialize()
        if self._redis_client:
            cached = await self._redis_client.get(f"memory:{namespace}:{key}")
            if cached:
                return json.loads(cached)
        if self._pg_pool:
            async with self._pg_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT value FROM agent_memory WHERE key = $1 AND namespace = $2",
                    key, namespace,
                )
                if row:
                    value = json.loads(row["value"])
                    if self._redis_client:
                        await self._redis_client.setex(f"memory:{namespace}:{key}", 86400, row["value"])
                    return value
        return None

    async def search(self, query: str, namespace: str = "default") -> list[Any]:
        await self._initialize()
        if not self._pg_pool:
            return []
        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT value FROM agent_memory
                   WHERE namespace = $1
                   AND (key ILIKE $2 OR value::text ILIKE $2)
                   LIMIT 50""",
                namespace, f"%{query}%",
            )
            return [json.loads(r["value"]) for r in rows]

    async def search_similar(self, embedding: list[float], namespace: str = "default", limit: int = 10) -> list[tuple[Any, float]]:
        await self._initialize()
        if not self._pg_pool:
            return []
        try:
            from pgvector.asyncpg import register_vector
            async with self._pg_pool.acquire() as conn:
                await register_vector(conn)
                rows = await conn.fetch(
                    """SELECT value, embedding <-> $1::vector AS distance
                       FROM agent_memory
                       WHERE namespace = $2 AND embedding IS NOT NULL
                       ORDER BY distance LIMIT $3""",
                    embedding, namespace, limit,
                )
                return [(json.loads(r["value"]), float(r["distance"])) for r in rows]
        except ImportError:
            return []

    async def delete(self, key: str, namespace: str = "default") -> None:
        await self._initialize()
        if self._pg_pool:
            async with self._pg_pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM agent_memory WHERE key = $1 AND namespace = $2",
                    key, namespace,
                )
        if self._redis_client:
            await self._redis_client.delete(f"memory:{namespace}:{key}")

    async def clear(self, namespace: str | None = None) -> None:
        await self._initialize()
        if self._pg_pool:
            async with self._pg_pool.acquire() as conn:
                if namespace:
                    await conn.execute("DELETE FROM agent_memory WHERE namespace = $1", namespace)
                else:
                    await conn.execute("DELETE FROM agent_memory")
        if self._redis_client:
            pattern = f"memory:{namespace or '*'}:*"
            keys = await self._redis_client.keys(pattern)
            if keys:
                await self._redis_client.delete(*keys)

    async def list_namespaces(self) -> list[str]:
        await self._initialize()
        if not self._pg_pool:
            return []
        async with self._pg_pool.acquire() as conn:
            rows = await conn.fetch("SELECT DISTINCT namespace FROM agent_memory ORDER BY namespace")
            return [r["namespace"] for r in rows]

    async def count(self, namespace: str | None = None) -> int:
        await self._initialize()
        if not self._pg_pool:
            return 0
        async with self._pg_pool.acquire() as conn:
            if namespace:
                row = await conn.fetchval("SELECT COUNT(*) FROM agent_memory WHERE namespace = $1", namespace)
            else:
                row = await conn.fetchval("SELECT COUNT(*) FROM agent_memory")
            return row or 0

    async def close(self):
        if self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
        self._initialized = False