from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Optional, List, Dict

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import RedisError, ConnectionError, TimeoutError

from backend.config import config

logger = logging.getLogger(__name__)


@dataclass
class RedisNode:
    """Redis node configuration."""
    host: str
    port: int
    is_master: bool = True
    weight: int = 100


class RedisClusterManager:
    """Production-ready Redis manager with Sentinel/Cluster support."""

    def __init__(self):
        self._primary_pool: Optional[ConnectionPool] = None
        self._replica_pools: List[ConnectionPool] = []
        self._primary_client: Optional[Redis] = None
        self._replica_clients: List[Redis] = []
        self._sentinel_client: Optional[Redis] = None
        self._initialized = False

    def _create_pool(
        self,
        host: str,
        port: int,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        socket_keepalive: bool = True,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30,
        **kwargs,
    ) -> ConnectionPool:
        """Create optimized connection pool."""
        return ConnectionPool(
            host=host,
            port=port,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            socket_keepalive=socket_keepalive,
            retry_on_timeout=retry_on_timeout,
            health_check_interval=health_check_interval,
            retry=Retry(ExponentialBackoff(), 3),
            decode_responses=True,
            **kwargs,
        )

    def _create_client(self, pool: ConnectionPool) -> Redis:
        """Create Redis client with optimized settings."""
        return Redis(
            connection_pool=pool,
            auto_close_connection_pool=False,
            single_connection_client=False,
        )

    async def initialize_from_config(self) -> None:
        """Initialize from configuration."""
        redis_config = config.redis

        if redis_config.sentinel_enabled:
            await self._initialize_sentinel(redis_config)
        elif redis_config.cluster_enabled:
            await self._initialize_cluster(redis_config)
        else:
            await self._initialize_standalone(redis_config)

        self._initialized = True
        await self.health_check()

    async def _initialize_standalone(self, redis_config) -> None:
        """Initialize standalone Redis with read replicas."""
        # Primary (write)
        self._primary_pool = self._create_pool(
            host=redis_config.host,
            port=redis_config.port,
            max_connections=redis_config.max_connections,
            password=redis_config.password,
            db=redis_config.db,
        )
        self._primary_client = self._create_client(self._primary_pool)

        # Replicas (read-only) - if configured
        if hasattr(redis_config, 'replica_hosts') and redis_config.replica_hosts:
            for replica in redis_config.replica_hosts:
                pool = self._create_pool(
                    host=replica.host,
                    port=replica.port,
                    max_connections=redis_config.max_connections // 2,
                    password=redis_config.password,
                    db=redis_config.db,
                )
                self._replica_pools.append(pool)
                self._replica_clients.append(self._create_client(pool))

    async def _initialize_sentinel(self, redis_config) -> None:
        """Initialize Redis with Sentinel for HA."""
        from redis.asyncio.sentinel import Sentinel

        sentinel_hosts = [
            (s.host, s.port) for s in redis_config.sentinel_hosts
        ]

        sentinel = Sentinel(
            sentinel_hosts,
            socket_timeout=redis_config.socket_timeout,
            password=redis_config.sentinel_password,
        )

        # Get master
        master = sentinel.master_for(
            redis_config.service_name,
            socket_timeout=redis_config.socket_timeout,
            password=redis_config.password,
            db=redis_config.db,
        )
        self._primary_client = master

        # Get replicas
        slave = sentinel.slave_for(
            redis_config.service_name,
            socket_timeout=redis_config.socket_timeout,
            password=redis_config.password,
            db=redis_config.db,
        )
        self._replica_clients.append(slave)

        self._sentinel_client = sentinel

    async def _initialize_cluster(self, redis_config) -> None:
        """Initialize Redis Cluster."""
        from redis.asyncio.cluster import RedisCluster

        startup_nodes = [
            {"host": n.host, "port": n.port} 
            for n in redis_config.cluster_nodes
        ]

        self._primary_client = RedisCluster(
            startup_nodes=startup_nodes,
            max_connections_per_node=redis_config.max_connections // len(startup_nodes),
            socket_timeout=redis_config.socket_timeout,
            socket_connect_timeout=redis_config.socket_connect_timeout,
            password=redis_config.password,
            decode_responses=True,
            read_from_replicas=True,
        )

    async def health_check(self) -> dict:
        """Comprehensive health check."""
        results = {
            "primary": False,
            "replicas": [],
            "sentinel": False,
        }

        # Check primary
        try:
            await self._primary_client.ping()
            info = await self._primary_client.info("memory")
            results["primary"] = True
            results["primary_memory"] = info.get("used_memory_human", "unknown")
        except Exception as e:
            results["primary_error"] = str(e)

        # Check replicas
        for i, client in enumerate(self._replica_clients):
            try:
                await client.ping()
                info = await client.info("replication")
                results["replicas"].append({
                    "index": i,
                    "healthy": True,
                    "lag": info.get("master_link_status", "unknown"),
                })
            except Exception as e:
                results["replicas"].append({
                    "index": i,
                    "healthy": False,
                    "error": str(e),
                })

        # Check sentinel
        if self._sentinel_client:
            try:
                masters = await self._sentinel_client.sentinel_masters()
                results["sentinel"] = True
                results["sentinel_masters"] = len(masters)
            except Exception as e:
                results["sentinel_error"] = str(e)

        return results

    @asynccontextmanager
    async def get_client(self, readonly: bool = False) -> AsyncGenerator[Redis, None]:
        """Get Redis client with automatic retry."""
        if readonly and self._replica_clients:
            # Round-robin or random selection for replicas
            import random
            client = random.choice(self._replica_clients)
        else:
            client = self._primary_client

        if not client:
            raise RuntimeError("Redis not initialized")

        try:
            yield client
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis connection error, retrying: {e}")
            # Try to reconnect
            await self._reconnect()
            yield self._primary_client

    async def _reconnect(self) -> None:
        """Attempt to reconnect to Redis."""
        for client in [self._primary_client] + self._replica_clients:
            try:
                await client.ping()
            except Exception:
                # Reconnection logic would go here
                pass

    # High-level operations
    async def get(self, key: str, readonly: bool = True) -> Optional[str]:
        async with self.get_client(readonly=readonly) as client:
            return await client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        async with self.get_client(readonly=False) as client:
            return await client.set(key, value, ex=expire, nx=nx, xx=xx)

    async def delete(self, *keys: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        async with self.get_client(readonly=True) as client:
            return await client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        async with self.get_client(readonly=False) as client:
            return await client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        async with self.get_client(readonly=True) as client:
            return await client.ttl(key)

    # Hash operations
    async def hget(self, name: str, key: str, readonly: bool = True) -> Optional[str]:
        async with self.get_client(readonly=readonly) as client:
            return await client.hget(name, key)

    async def hset(self, name: str, mapping: dict) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.hset(name, mapping=mapping)

    async def hgetall(self, name: str, readonly: bool = True) -> dict:
        async with self.get_client(readonly=readonly) as client:
            return await client.hgetall(name)

    async def hdel(self, name: str, *keys: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.hdel(name, *keys)

    # List operations
    async def lpush(self, name: str, *values: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.lpush(name, *values)

    async def rpush(self, name: str, *values: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.rpush(name, *values)

    async def lpop(self, name: str, count: Optional[int] = None) -> Optional[str]:
        async with self.get_client(readonly=False) as client:
            return await client.lpop(name, count=count)

    async def rpop(self, name: str, count: Optional[int] = None) -> Optional[str]:
        async with self.get_client(readonly=False) as client:
            return await client.rpop(name, count=count)

    async def lrange(self, name: str, start: int, end: int, readonly: bool = True) -> list:
        async with self.get_client(readonly=readonly) as client:
            return await client.lrange(name, start, end)

    # Set operations
    async def sadd(self, name: str, *values: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.sadd(name, *values)

    async def srem(self, name: str, *values: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.srem(name, *values)

    async def smembers(self, name: str, readonly: bool = True) -> set:
        async with self.get_client(readonly=readonly) as client:
            return await client.smembers(name)

    # Sorted set operations
    async def zadd(self, name: str, mapping: dict) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.zadd(name, mapping=mapping)

    async def zrem(self, name: str, *values: str) -> int:
        async with self.get_client(readonly=False) as client:
            return await client.zrem(name, *values)

    async def zrange(
        self, name: str, start: int, end: int, desc: bool = False, readonly: bool = True
    ) -> list:
        async with self.get_client(readonly=readonly) as client:
            return await client.zrange(name, start, end, desc=desc)

    # Pub/Sub
    @asynccontextmanager
    async def pubsub(self, *channels: str):
        async with self._primary_client.pubsub() as pubsub:
            await pubsub.subscribe(*channels)
            try:
                yield pubsub
            finally:
                await pubsub.unsubscribe(*channels)

    # Rate limiting
    async def rate_limit_check(
        self,
        key: str,
        limit: int,
        window: int,
        readonly: bool = False,
    ) -> tuple[bool, int, int]:
        """
        Check rate limit using sliding window.
        Returns: (allowed, current_count, remaining)
        """
        import time
        now = int(time.time())
        window_start = now - window

        async with self.get_client(readonly=readonly) as client:
            pipe = client.pipeline()
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            # Count current
            pipe.zcard(key)
            # Add current request
            pipe.zadd(key, {f"{now}:{id(key)}": now})
            # Set expiry
            pipe.expire(key, window)
            results = await pipe.execute()

            current_count = results[1]
            allowed = current_count < limit
            remaining = max(0, limit - current_count)

            if not allowed:
                # Remove the request we just added
                await client.zrem(key, f"{now}:{id(key)}")

            return allowed, current_count, remaining

    # Distributed locking
    @asynccontextmanager
    async def lock(
        self,
        name: str,
        timeout: int = 30,
        blocking: bool = True,
        blocking_timeout: Optional[int] = None,
    ):
        """Distributed lock using Redis."""
        lock = self._primary_client.lock(
            name,
            timeout=timeout,
            blocking=blocking,
            blocking_timeout=blocking_timeout,
        )
        acquired = await lock.acquire()
        try:
            yield acquired
        finally:
            if acquired:
                await lock.release()

    # Cache patterns
    async def get_or_set(
        self,
        key: str,
        factory: callable,
        expire: int = 3600,
        readonly: bool = True,
    ) -> Any:
        """Get cached value or compute and cache."""
        async with self.get_client(readonly=readonly) as client:
            value = await client.get(key)
            if value is not None:
                return json.loads(value)

            # Compute value
            value = await factory() if asyncio.iscoroutinefunction(factory) else factory()
            await client.set(key, json.dumps(value), ex=expire)
            return value

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        async with self.get_client(readonly=False) as client:
            deleted = 0
            async for key in client.scan_iter(match=pattern, count=100):
                deleted += await client.delete(key)
            return deleted

    async def close(self) -> None:
        """Close all connections."""
        if self._primary_client:
            await self._primary_client.close()
        for client in self._replica_clients:
            await client.close()
        for pool in [self._primary_pool] + self._replica_pools:
            if pool:
                await pool.disconnect()
        self._initialized = False


# Global instance
redis_manager = RedisClusterManager()


async def get_redis_client(readonly: bool = False) -> Redis:
    """FastAPI dependency for Redis client."""
    async with redis_manager.get_client(readonly=readonly) as client:
        yield client


async def init_redis() -> None:
    """Initialize Redis on application startup."""
    await redis_manager.initialize_from_config()


async def close_redis() -> None:
    """Close Redis on application shutdown."""
    await redis_manager.close()