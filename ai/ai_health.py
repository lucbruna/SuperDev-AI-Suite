from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any


class AIHealth:
    """Health monitoring for AI engines and providers."""

    def __init__(self):
        self._check_results: dict[str, dict[str, Any]] = {}
        self._thresholds = {
            "latency_warning_ms": 5000,
            "latency_critical_ms": 15000,
            "timeout_seconds": 10,
        }

    async def check_provider(self, provider_name: str, provider: Any) -> dict[str, Any]:
        """Check health of a specific provider."""
        start = time.time()
        result: dict[str, Any] = {
            "provider": provider_name,
            "status": "unknown",
            "latency_ms": 0,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        try:
            if hasattr(provider, "health"):
                health = provider.health() if callable(provider.health) else provider.health
                if isinstance(health, dict):
                    result.update(health)
                result["status"] = "healthy"
            else:
                result["status"] = "unknown"

            elapsed = (time.time() - start) * 1000
            result["latency_ms"] = round(elapsed, 2)

            if elapsed > self._thresholds["latency_critical_ms"]:
                result["status"] = "critical"
            elif elapsed > self._thresholds["latency_warning_ms"]:
                result["status"] = "degraded"

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            result["status"] = "unhealthy"
            result["latency_ms"] = round(elapsed, 2)
            result["error"] = str(e)

        self._check_results[provider_name] = result
        return result

    async def check_all(self, providers: dict[str, Any]) -> dict[str, Any]:
        """Check health of all providers."""
        results: dict[str, Any] = {}
        for name, provider in providers.items():
            results[name] = await self.check_provider(name, provider)
        return results

    def check_engine(self, engine: Any) -> dict[str, Any]:
        """Check health of the AI engine."""
        result: dict[str, Any] = {
            "status": "healthy",
            "initialized": getattr(engine, "is_initialized", False),
            "version": "2.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if hasattr(engine, "uptime"):
            result["uptime"] = getattr(engine, "uptime", 0)

        if hasattr(engine, "manager") and hasattr(engine.manager, "health"):
            result["modules"] = engine.manager.health()

        return result

    def get_last_check(self, provider_name: str) -> dict[str, Any] | None:
        """Get the last health check result for a provider."""
        return self._check_results.get(provider_name)

    def set_thresholds(self, **kwargs: Any) -> None:
        """Update health check thresholds."""
        for key, value in kwargs.items():
            if key in self._thresholds:
                self._thresholds[key] = value

    def health(self) -> dict[str, Any]:
        """Get health subsystem status."""
        return {
            "status": "healthy",
            "providers_checked": len(self._check_results),
            "thresholds": dict(self._thresholds),
            "timestamp": datetime.now(UTC).isoformat(),
        }
