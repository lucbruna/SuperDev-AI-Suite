"""Network ACL — kernel permission enforcement (Vol 12, Fase 27)."""
from __future__ import annotations

from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    get_kernel_security,
)


def require_network_action(action: str) -> None:
    """Enforce the ``network:<action>`` ACL before any privileged operation."""
    if not get_kernel_security().allow("network", action):
        raise KernelPermissionDeniedError("network", action)


__all__ = ["require_network_action"]
