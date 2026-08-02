"""Sandbox package — isolated execution environments (Vol 12, Fase 13)."""
from __future__ import annotations

from modules.aios.sandbox.sandbox import Sandbox, SandboxFn
from modules.aios.sandbox.sandbox_limits import SandboxLimitError, SandboxLimits
from modules.aios.sandbox.sandbox_manager import SandboxManager, get_sandbox_manager
from modules.aios.sandbox.sandbox_network import SandboxNetwork
from modules.aios.sandbox.sandbox_permissions import (
    SandboxPermissionDeniedError,
    SandboxPermissions,
)
from modules.aios.sandbox.sandbox_policy import NetworkAccess, SandboxPolicy, restrictive_policy
from modules.aios.sandbox.sandbox_storage import SandboxStorage

__all__ = [
    "Sandbox",
    "SandboxFn",
    "SandboxLimitError",
    "SandboxLimits",
    "SandboxManager",
    "get_sandbox_manager",
    "SandboxNetwork",
    "SandboxPermissionDeniedError",
    "SandboxPermissions",
    "NetworkAccess",
    "SandboxPolicy",
    "restrictive_policy",
    "SandboxStorage",
]
