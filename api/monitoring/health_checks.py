from __future__ import annotations

import time
from typing import Any, Callable


class HealthChecker:
    """Registers and runs health checks for system components."""

    def __init__(self) -> None:
        self._checks: dict[str, Callable] = {}
        self._results: dict[str, dict[str, Any]] = {}

    def register(self, name: str, check_fn: Callable) -> None:
        self._checks[name] = check_fn

    async def run_all(self) -> dict[str, Any]:
        all_healthy = True
        results: dict[str, Any] = {}

        for name, check_fn in self._checks.items():
            try:
                result = check_fn()
                if hasattr(result, "__await__"):
                    result = await result
                healthy = bool(result) if not isinstance(result, dict) else result.get("healthy", False)
                results[name] = {
                    "healthy": healthy,
                    "timestamp": time.time(),
                    "detail": result if isinstance(result, dict) else {},
                }
                if not healthy:
                    all_healthy = False
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "timestamp": time.time(),
                    "error": str(e),
                }
                all_healthy = False

        self._results = results
        return {"healthy": all_healthy, "checks": results, "timestamp": time.time()}

    async def liveness(self) -> dict[str, Any]:
        return {"alive": True, "timestamp": time.time()}

    async def readiness(self) -> dict[str, Any]:
        return await self.run_all()

    def get_result(self, name: str) -> dict[str, Any] | None:
        return self._results.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": list(self._checks.keys()),
            "count": len(self._checks),
            "last_results": self._results,
        }
