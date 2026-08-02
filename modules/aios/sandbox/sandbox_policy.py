"""Sandbox policy — declarative constraints for an isolated environment."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NetworkAccess(StrEnum):
    """Network isolation levels available to a sandbox."""

    OFFLINE = "offline"
    LOOPBACK = "loopback"
    ONLINE = "online"


@dataclass
class SandboxPolicy:
    """Everything a sandbox is allowed (or forbidden) to do.

    Defaults are maximally restrictive: offline, read-only, no time/memory
    budget beyond the OS defaults. Callers opt in per capability.
    """

    name: str
    network: NetworkAccess = NetworkAccess.OFFLINE
    allow_fs_write: bool = False
    allowed_read_paths: list[str] = field(default_factory=list)
    timeout_s: float | None = None
    max_memory_mb: int | None = None
    max_storage_mb: int | None = None
    allowed_commands: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "network": self.network.value,
            "allow_fs_write": self.allow_fs_write,
            "timeout_s": self.timeout_s,
            "max_memory_mb": self.max_memory_mb,
            "max_storage_mb": self.max_storage_mb,
            "allowed_read_paths": list(self.allowed_read_paths),
            "allowed_commands": list(self.allowed_commands),
        }


def restrictive_policy(name: str, **overrides: Any) -> SandboxPolicy:
    """Build a policy from the restrictive default plus explicit overrides."""
    return SandboxPolicy(name=name, **overrides)


__all__ = ["NetworkAccess", "SandboxPolicy", "restrictive_policy"]
