from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from backend.config import config
from pydantic import BaseModel, Field

logger = logging.getLogger("superdev")


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckResult(BaseModel):
    status: HealthStatus
    component: str
    message: str = ""
    latency_ms: float = Field(default=0.0, ge=0.0)
    checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    details: dict[str, Any] = Field(default_factory=dict)


class HealthChecker:
    def __init__(self) -> None:
        self._checks: dict[str, Any] = {
            "database": self._check_database,
            "redis": self._check_redis,
            "cache": self._check_cache,
            "providers": self._check_providers,
            "disk": self._check_disk_space,
            "memory": self._check_memory,
            "uptime": self._check_uptime,
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
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import create_async_engine

            engine = create_async_engine(config.database.url, pool_size=1, echo=False)
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
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
            from redis.asyncio import Redis

            redis = Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password or None,
                db=config.redis.db,
                decode_responses=config.redis.decode_responses,
                socket_connect_timeout=5,
            )
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
            from redis.asyncio import Redis

            redis = Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password or None,
                db=config.redis.db,
                decode_responses=config.redis.decode_responses,
                socket_connect_timeout=5,
            )
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

    async def _check_disk_space(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            import shutil
            usage = shutil.disk_usage("/")
            free_pct = (usage.free / usage.total) * 100
            latency = (time.monotonic() - start) * 1000
            if free_pct < 10:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    component="disk",
                    message=f"Low disk space: {free_pct:.1f}% free",
                    latency_ms=round(latency, 2),
                    details={
                        "total_gb": round(usage.total / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "free_percent": round(free_pct, 1),
                    },
                )
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="disk",
                message=f"Disk OK: {free_pct:.1f}% free",
                latency_ms=round(latency, 2),
                details={
                    "total_gb": round(usage.total / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "free_percent": round(free_pct, 1),
                },
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                component="disk",
                message=str(e),
                latency_ms=round(latency, 2),
            )

    async def _check_memory(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            import psutil
            mem = psutil.virtual_memory()
            latency = (time.monotonic() - start) * 1000
            if mem.percent > 90:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    component="memory",
                    message=f"High memory usage: {mem.percent}%",
                    latency_ms=round(latency, 2),
                    details={
                        "total_gb": round(mem.total / (1024**3), 2),
                        "available_gb": round(mem.available / (1024**3), 2),
                        "used_percent": mem.percent,
                    },
                )
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="memory",
                message=f"Memory OK: {mem.percent}% used",
                latency_ms=round(latency, 2),
                details={
                    "total_gb": round(mem.total / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "used_percent": mem.percent,
                },
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                component="memory",
                message=str(e),
                latency_ms=round(latency, 2),
            )

    async def _check_uptime(self) -> HealthCheckResult:
        start = time.monotonic()
        try:
            from backend.registry import service_registry
            started_at = service_registry.get("started_at")
            if not started_at:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    component="uptime",
                    message="Start time not recorded",
                    latency_ms=round((time.monotonic() - start) * 1000, 2),
                )
            from datetime import UTC, datetime
            start_dt = datetime.fromisoformat(started_at)
            now = datetime.now(UTC)
            uptime_secs = (now - start_dt).total_seconds()
            hours = int(uptime_secs // 3600)
            minutes = int((uptime_secs % 3600) // 60)
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                component="uptime",
                message=f"Uptime: {hours}h {minutes}m",
                latency_ms=round((time.monotonic() - start) * 1000, 2),
                details={"seconds": int(uptime_secs), "started_at": started_at},
            )
        except Exception as e:
            latency = (time.monotonic() - start) * 1000
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                component="uptime",
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