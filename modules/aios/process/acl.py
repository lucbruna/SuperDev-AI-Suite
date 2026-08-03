"""Process ACL — kernel permission enforcement for process operations."""
from __future__ import annotations

from modules.aios.kernel import get_kernel_security, KernelPermissionDeniedError


def require_process_action(action: str) -> None:
    """Enforce the ``process:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("process", action):
        raise KernelPermissionDeniedError("process", action)


__all__ = ["require_process_action"]
