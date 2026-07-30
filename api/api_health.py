from __future__ import annotations

import time
from typing import Any


class APIHealth:
    """Health check for the API engine and its dependencies."""

    def __init__(self) -> None:
        self._start_time = time.time()
        self._dependencies: dict[str, dict[str, Any]] = {}

    def register_dependency(self, name: str, check_fn: Any) -> None:
        self._dependencies[name] = {"check": check_fn, "healthy": True, "last_check": 0.0}

    async def check(self) -> dict[str, Any]:
        deps: dict[str, Any] = {}
        all_healthy = True

        for name, dep in self._dependencies.items():
            try:
                fn = dep["check"]
                result = fn() if not hasattr(fn, "__call__") else fn()
                if hasattr(result, "__await__"):
                    result = await result
                healthy = result is True or (isinstance(result, dict) and result.get("healthy", False))
                dep["healthy"] = healthy
                dep["last_check"] = time.time()
                deps[name] = {"healthy": healthy}
                if not healthy:
                    all_healthy = False
            except Exception as e:
                dep["healthy"] = False
                dep["last_check"] = time.time()
                deps[name] = {"healthy": False, "error": str(e)}
                all_healthy = False

        return {
            "healthy": all_healthy,
            "uptime_seconds": round(time.time() - self._start_time, 2),
            "dependencies": deps,
            "timestamp": time.time(),
        }

    async def liveness(self) -> dict[str, Any]:
        return {"alive": True, "uptime_seconds": round(time.time() - self._start_time, 2)}

    async def readiness(self) -> dict[str, Any]:
        return await self.check()

    def to_dict(self) -> dict[str, Any]:
        return {
            "uptime_seconds": round(time.time() - self._start_time, 2),
            "dependency_count": len(self._dependencies),
        }
