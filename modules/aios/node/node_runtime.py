"""Node runtime — facade over node/npm/pnpm/yarn/bun/vitest/jest (Vol 12, Fase 18)."""
from __future__ import annotations

from typing import Any

from modules.aios.node.bun import BunManager, BunUnavailableError
from modules.aios.node.jest import JestRunner, JestUnavailableError
from modules.aios.node.node_client import NodeClient
from modules.aios.node.npm import NpmManager, NpmUnavailableError
from modules.aios.node.package_manager import (
    PackageManager,
    PackageManagerUnavailableError,
)
from modules.aios.node.pnpm import PnpmManager, PnpmUnavailableError
from modules.aios.node.vitest import VitestRunner, VitestUnavailableError
from modules.aios.node.yarn import YarnManager, YarnUnavailableError


class NodeRuntime:
    """Facade over the Node.js toolchain.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. Tools that
    are not installed (yarn) degrade gracefully via their *UnavailableError.
    """

    def __init__(self) -> None:
        self.node = NodeClient()
        self.npm = NpmManager()
        self.pnpm = PnpmManager()
        self.yarn = YarnManager()
        self.bun = BunManager()
        self.packages = PackageManager()
        self.vitest = VitestRunner()
        self.jest = JestRunner()

    async def available(self) -> bool:
        return await self.node.ping()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort tool inventory; each tool degrades to None on error."""
        version = None
        package_manager: str | None = None
        package_manager_version: str | None = None
        yarn: str | None = None
        vitest: str | None = None
        jest: str | None = None
        try:
            version = (await self.node.version())["version"]
        except (NpmUnavailableError, RuntimeError):
            version = None
        try:
            package_manager = self.packages.name
            package_manager_version = (await self.packages.version())["version"]
        except (PackageManagerUnavailableError, RuntimeError):
            package_manager_version = None
        try:
            yarn = (await self.yarn.version())["version"]
        except (YarnUnavailableError, RuntimeError):
            yarn = None
        try:
            vitest = (await self.vitest.version())["version"]
        except (VitestUnavailableError, RuntimeError):
            vitest = None
        try:
            jest = (await self.jest.version())["version"]
        except (JestUnavailableError, RuntimeError):
            jest = None
        return {
            "node": version,
            "package_manager": package_manager,
            "package_manager_version": package_manager_version,
            "npm": await self._manager_version(self.npm, NpmUnavailableError),
            "pnpm": await self._manager_version(self.pnpm, PnpmUnavailableError),
            "yarn": yarn,
            "bun": await self._manager_version(self.bun, BunUnavailableError),
            "vitest": vitest,
            "jest": jest,
        }

    @staticmethod
    async def _manager_version(
        manager: Any, error_type: type[RuntimeError]
    ) -> str | None:
        try:
            return (await manager.version())["version"]
        except error_type:
            return None

    async def close(self) -> None:
        """No-op — the node runtime is stateless."""


_node_runtime: NodeRuntime | None = None


def get_node_runtime() -> NodeRuntime:
    global _node_runtime
    if _node_runtime is None:
        _node_runtime = NodeRuntime()
    return _node_runtime


__all__ = ["NodeRuntime", "get_node_runtime"]
