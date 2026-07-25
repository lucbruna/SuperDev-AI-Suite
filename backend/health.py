from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from backend.config import config

logger = logging.getLogger("superdev")


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckResult(BaseModel):
    status: HealthStatus
    component: str
    message: str = ""
    latency_ms: float = Field(default=0.0, ge=0.0)
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: dict[str, Any] = Field(default_factory=dict)


class HealthChecker:
    def __init__(self) -> None:
        self._checks: dict[str, Any] = {
            "database": self._check_database,
            "redis": self._check_redis,
            "cache": self._check_cache,
            "providers": self._check_providers,
        }

    async def check_all(self) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        for name, check_fn in self._checks.items():
            try:
                result = await check_fn()
                results[name] = result
            except Exception as e:
                results[name] = HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    component=name,
                    message=str(e),
                )
        return results

    async def check_component(self, component: str) -> HealthCheckResult:
        check_fn = self._checks.get(component)
        if check_fn is None:
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component=component,
                message=f"Unknown component: {component}",
            )
        return await check_fn()

    async def _check_database(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(config.database.url, pool_size=1, echo=False)
            async with engine.begin() as conn:
                await conn.execute("SELECT 1")
            await engine.dispose()
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="database",
                message="Database is reachable",
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component="database",
                message=str(e),
                latency_ms=round(latency, 2),
            )

    async def _check_redis(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            from redis.asyncio import from_url

            redis = await from_url(config.redis.url, socket_connect_timeout=5)
            await redis.ping()
            await redis.aclose()
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="redis",
                message="Redis is reachable",
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component="redis",
                message=str(e),
                latency_ms=round(latency, 2),
            )

    async def _check_cache(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            from redis.asyncio import from_url

            redis = await from_url(config.redis.url, socket_connect_timeout=5)
            await redis.set("health:test", "1", ex=5)
            val = await redis.get("health:test")
            await redis.aclose()
            latency = (time.monotonic() - start) * 1000
            if val == "1":
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    component="cache",
                    message="Cache read/write working",
                    latency_ms=round(latency, 2),
                )
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                component="cache",
                message="Cache read/write mismatch",
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                component="cache",
                message=str(e),
                latency_ms=round(latency, 2),
            )

    async def _check_providers(self) -> HealthCheckResult:
        start = time.monotonic()
        missing_keys = []
        if config.providers.openai_api_key:
            try:
                import httpx

                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {config.providers.openai_api_key}"},
                    )
                    if resp.status_code == 200:
                        pass
                    elif resp.status_code == 401:
                        missing_keys.append("openai: invalid API key")
                    else:
                        missing_keys.append(f"openai: HTTP {resp.status_code}")
            except Exception as e:
                missing_keys.append(f"openai: {e}")
        else:
            missing_keys.append("openai: no API key configured")

        latency = (time.monotonic() - start) * 1000
        if not missing_keys:
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="providers",
                message="All configured providers are reachable",
                latency_ms=round(latency, 2),
            )
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            component="providers",
            message="; ".join(missing_keys),
            latency_ms=round(latency, 2),
            details={"issues": missing_keys},
        )