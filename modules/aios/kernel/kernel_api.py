"""Kernel API — service layer an HTTP router can expose for the AIOS."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel import Kernel, get_kernel


class KernelAPI:
    """Async handlers mapping to kernel operations."""

    def __init__(self, kernel: Kernel | None = None) -> None:
        self._kernel = kernel or get_kernel()

    async def status(self) -> dict[str, Any]:
        return self._kernel.status()

    async def info(self) -> dict[str, Any]:
        return self._kernel.info()

    async def health(self) -> dict[str, Any]:
        return self._kernel.manager.health.run()

    async def metrics(self) -> dict[str, Any]:
        return self._kernel.manager.metrics.snapshot()

    async def snapshot(self) -> dict[str, Any]:
        return self._kernel.snapshot()

    async def boot(self) -> dict[str, Any]:
        return self._kernel.boot()


_kernel_api: KernelAPI | None = None


def get_kernel_api() -> KernelAPI:
    global _kernel_api
    if _kernel_api is None:
        _kernel_api = KernelAPI()
    return _kernel_api
