"""Sandbox network — declared network isolation for a sandbox."""
from __future__ import annotations
from typing import Any

from modules.aios.sandbox.sandbox_policy import NetworkAccess


class SandboxNetwork:
    """Exposes the sandbox's network access level with a permission check."""

    def __init__(self, access: NetworkAccess) -> None:
        self.access = access

    def allows(self, target_access: NetworkAccess) -> bool:
        """Whether this sandbox may reach the given network level."""
        levels = [NetworkAccess.OFFLINE, NetworkAccess.LOOPBACK, NetworkAccess.ONLINE]
        return levels.index(self.access) >= levels.index(target_access)

    def require_online(self) -> None:
        if not self.allows(NetworkAccess.ONLINE):
            raise PermissionError("sandbox is not allowed online network access")

    def snapshot(self) -> dict[str, Any]:
        return {"access": self.access.value}


__all__ = ["SandboxNetwork"]
