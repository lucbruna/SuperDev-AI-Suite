"""Unified package manager — auto-selects npm/pnpm/yarn/bun for the node runtime."""
from __future__ import annotations

import shutil
from typing import Any

from modules.aios.node.bun import BunManager
from modules.aios.node.npm import NpmManager
from modules.aios.node.pnpm import PnpmManager
from modules.aios.node.yarn import YarnManager


class PackageManagerUnavailableError(RuntimeError):
    """Raised when no supported package manager is installed."""


_BACKENDS: dict[str, Any] = {
    "npm": NpmManager,
    "pnpm": PnpmManager,
    "yarn": YarnManager,
    "bun": BunManager,
}


class PackageManager:
    """Delegates package operations to the first available CLI (npm first)."""

    def __init__(self, manager: str | None = None) -> None:
        self.name = manager or self._detect()
        if self.name not in _BACKENDS:
            raise PackageManagerUnavailableError(f"unsupported manager: {self.name}")
        self._backend = _BACKENDS[self.name]()

    @staticmethod
    def _detect() -> str:
        for name in _BACKENDS:
            if shutil.which(name):
                return name
        raise PackageManagerUnavailableError(
            "no package manager found (tried npm, pnpm, yarn, bun)"
        )

    async def version(self) -> dict[str, Any]:
        return await self._backend.version()

    async def install(
        self,
        package: str | None = None,
        *,
        cwd: str | None = None,
        dev: bool = False,
        global_: bool = False,
    ) -> dict[str, Any]:
        if isinstance(self._backend, NpmManager):
            return await self._backend.install(
                package, cwd=cwd, dev=dev, global_=global_
            )
        return await self._backend.install(package, cwd=cwd, dev=dev)

    async def run_script(self, name: str, *, cwd: str | None = None) -> dict[str, Any]:
        return await self._backend.run_script(name, cwd=cwd)

    async def list(self, *, cwd: str | None = None) -> list[dict[str, Any]]:
        if isinstance(self._backend, NpmManager):
            return await self._backend.list(cwd=cwd)
        return []


__all__ = ["PackageManager", "PackageManagerUnavailableError"]
