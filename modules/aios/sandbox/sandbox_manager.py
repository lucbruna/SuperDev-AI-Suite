"""Sandbox manager — registry and lifecycle for sandboxes in this process."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.sandbox.sandbox import Sandbox
from modules.aios.sandbox.sandbox_policy import SandboxPolicy


class SandboxManager:
    """Creates, tracks and closes sandboxes; reports aggregate state."""

    def __init__(self) -> None:
        self._sandboxes: dict[str, Sandbox] = {}
        self._metrics = get_kernel_metrics()

    def create(self, policy: SandboxPolicy) -> Sandbox:
        sandbox = Sandbox(policy)
        self._sandboxes[sandbox.id] = sandbox
        self._metrics.increment("sandbox.created")
        self._metrics.set_gauge("sandbox.active", len(self._sandboxes))
        return sandbox

    def get(self, sandbox_id: str) -> Sandbox | None:
        return self._sandboxes.get(sandbox_id)

    async def close(self, sandbox_id: str) -> bool:
        sandbox = self._sandboxes.pop(sandbox_id, None)
        if sandbox is None:
            return False
        await sandbox.close()
        self._metrics.increment("sandbox.closed")
        self._metrics.set_gauge("sandbox.active", len(self._sandboxes))
        return True

    async def close_all(self) -> int:
        count = 0
        for sandbox_id in list(self._sandboxes):
            if await self.close(sandbox_id):
                count += 1
        return count

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": len(self._sandboxes),
            "sandboxes": {
                sid: {"name": s.policy.name, "closed": s.closed}
                for sid, s in self._sandboxes.items()
            },
            "created": self._metrics.counter("sandbox.created"),
            "closed": self._metrics.counter("sandbox.closed"),
        }


_sandbox_manager: SandboxManager | None = None


def get_sandbox_manager() -> SandboxManager:
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager


__all__ = ["SandboxManager", "get_sandbox_manager"]
