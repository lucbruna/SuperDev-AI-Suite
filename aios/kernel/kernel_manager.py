"""AIOS Kernel Manager — process-wide singleton facade.

Provides a single access point for the current kernel instance so that
any module, service or agent can resolve the platform root without
threading references through the call chain.
"""

from __future__ import annotations

from typing import Any

from .kernel import Kernel
from .kernel_version import AIOS_VERSION


class KernelManager:
    """Holds the active :class:`Kernel` and lifecycle helpers."""

    def __init__(self) -> None:
        self._kernel: Kernel | None = None

    def create(self, name: str = "aios-kernel", version: str = AIOS_VERSION) -> Kernel:
        """Create (and remember) a new kernel."""
        self._kernel = Kernel(name=name, version=version)
        return self._kernel

    def get(self) -> Kernel:
        """Return the active kernel or raise if not created yet."""
        if self._kernel is None:
            raise RuntimeError("AIOS kernel not created yet — call create() first.")
        return self._kernel

    def get_or_create(self) -> Kernel:
        if self._kernel is None:
            return self.create()
        return self._kernel

    def reset(self) -> None:
        """Drop the current kernel reference (used by tests)."""
        self._kernel = None

    def is_ready(self) -> bool:
        return self._kernel is not None and self._kernel.state == "running"

    # -- convenience passthrough ----------------------------------------
    def snapshot(self) -> dict[str, Any]:
        return self.get().snapshot()

    def shutdown(self) -> dict[str, Any]:
        return self.get().shutdown()


_manager: KernelManager | None = None


def get_kernel_manager() -> KernelManager:
    """Return the process-wide kernel manager (singleton)."""
    global _manager
    if _manager is None:
        _manager = KernelManager()
    return _manager


def get_kernel() -> Kernel:
    """Return the active kernel (create on demand)."""
    return get_kernel_manager().get_or_create()


def reset_kernel() -> None:
    """Reset the global kernel (testing / hot-reload)."""
    get_kernel_manager().reset()
