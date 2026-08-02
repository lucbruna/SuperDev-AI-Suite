"""Kernel — root AIOS entry point composing manager + runtime."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel_manager import (
    KernelManager,
    get_kernel_manager,
)
from modules.aios.kernel.kernel_version import KERNEL_NAME, KERNEL_VERSION


class Kernel:
    """Root facade for the SuperDev AIOS kernel."""

    def __init__(self, manager: KernelManager | None = None) -> None:
        self.manager = manager or get_kernel_manager()

    def boot(self) -> dict[str, Any]:
        return self.manager.boot()

    def stop(self) -> dict[str, Any]:
        return self.manager.stop()

    def snapshot(self) -> dict[str, Any]:
        return self.manager.snapshot()

    def status(self) -> dict[str, Any]:
        return self.manager.runtime.status()

    def info(self) -> dict[str, Any]:
        return {**self.manager.info(), "uptime_component": KERNEL_NAME, "version": KERNEL_VERSION}


_kernel: Kernel | None = None


def get_kernel() -> Kernel:
    global _kernel
    if _kernel is None:
        _kernel = Kernel()
    return _kernel
