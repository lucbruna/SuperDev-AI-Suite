from __future__ import annotations

import time
from typing import Any, Optional


class AgentKernel:
    _instance: Optional["AgentKernel"] = None

    def __new__(cls) -> "AgentKernel":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._services: dict[str, Any] = {}
            self._booted: bool = False
            self._boot_time: Optional[float] = None
            self._initialized = True

    async def boot(self) -> None:
        self._booted = True
        self._boot_time = time.time()

    async def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        return self._services.get(name)

    def health(self) -> dict[str, Any]:
        return {
            "booted": self._booted,
            "boot_time": self._boot_time,
            "uptime": time.time() - self._boot_time if self._boot_time else 0,
            "services": list(self._services.keys()),
            "service_count": len(self._services),
        }
