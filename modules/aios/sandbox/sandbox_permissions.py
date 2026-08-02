"""Sandbox permissions — ACL over sandbox actions, backed by the kernel."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel_security import get_kernel_security


class SandboxPermissionDeniedError(PermissionError):
    def __init__(self, sandbox_id: str, action: str) -> None:
        self.sandbox_id = sandbox_id
        self.action = action
        super().__init__(f"sandbox permission denied: {sandbox_id}:{action}")


class SandboxPermissions:
    """Per-sandbox grant set layered on the kernel's global ACL."""

    # Sandbox-level actions checked against the kernel ACL component "sandbox".
    ACTIONS = {"run", "fs_write", "network", "command"}

    def __init__(self, sandbox_id: str) -> None:
        self.sandbox_id = sandbox_id
        self._grants: set[str] = set()
        self._kernel = get_kernel_security()

    def grant(self, *actions: str) -> None:
        for action in actions:
            if action not in self.ACTIONS:
                raise ValueError(f"unknown sandbox action: {action}")
        self._grants.update(actions)

    def revoke(self, *actions: str) -> None:
        self._grants.difference_update(actions)

    def allow(self, action: str) -> bool:
        # Global kernel grant always wins; sandbox grants refine it.
        return self._kernel.allow("sandbox", action) or action in self._grants

    def require(self, action: str) -> None:
        if not self.allow(action):
            raise SandboxPermissionDeniedError(self.sandbox_id, action)

    def snapshot(self) -> dict[str, Any]:
        return {"sandbox_id": self.sandbox_id, "grants": sorted(self._grants)}


__all__ = ["SandboxPermissionDeniedError", "SandboxPermissions"]
