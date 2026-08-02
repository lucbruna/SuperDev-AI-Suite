"""Go runtime — facade over the go toolchain (Vol 12, Fase 20)."""
from __future__ import annotations

from typing import Any

from modules.aios.go.build import GoBuild
from modules.aios.go.go_client import GoClient, GoUnavailableError
from modules.aios.go.modules import GoModules
from modules.aios.go.test import GoTest


class GoRuntime:
    """Facade over go mod/build/test.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. When go is
    not installed every operation raises GoUnavailableError and ``snapshot``
    degrades gracefully.
    """

    def __init__(self) -> None:
        self.client = GoClient()
        self.modules = GoModules(self.client)
        self.build = GoBuild(self.client)
        self.test = GoTest(self.client)

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; degrades to None when go is missing."""
        version = None
        try:
            version = (await self.client.version())["version"]
        except GoUnavailableError:
            version = None
        return {"go": version}

    async def close(self) -> None:
        """No-op — the go runtime is stateless."""


_go_runtime: GoRuntime | None = None


def get_go_runtime() -> GoRuntime:
    global _go_runtime
    if _go_runtime is None:
        _go_runtime = GoRuntime()
    return _go_runtime


__all__ = ["GoRuntime", "get_go_runtime"]
