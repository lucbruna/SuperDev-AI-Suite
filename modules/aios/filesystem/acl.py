"""Filesystem ACL — kernel permission enforcement (Vol 12, Fase 26)."""
from __future__ import annotations

from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


def require_filesystem_action(action: str) -> None:
    """Enforce the ``filesystem:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("filesystem", action):
        raise KernelPermissionDeniedError("filesystem", action)


__all__ = ["require_filesystem_action"]
