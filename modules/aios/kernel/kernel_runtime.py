"""Kernel runtime — lifecycle of the AIOS kernel (boot/stop/status)."""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any

from modules.aios.kernel.kernel_events import emit
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_version import KERNEL_VERSION


class KernelRuntime:
    """Tracks kernel state and emits lifecycle events."""

    def __init__(self) -> None:
        self._state = "stopped"
        self._booted_at: str | None = None
        self._logger = get_kernel_logger()
        self._components: list[str] = []

    @property
    def state(self) -> str:
        return self._state

    def register_component(self, name: str) -> None:
        if name not in self._components:
            self._components.append(name)

    def boot(self) -> dict[str, Any]:
        if self._state == "running":
            return {"state": self._state, "booted": False}
        self._state = "running"
        self._booted_at = datetime.now(UTC).isoformat()
        self._logger.log("runtime", f"kernel booted (v{KERNEL_VERSION})")
        try:
            import asyncio

            asyncio.get_running_loop().create_task(
                emit("booted", version=KERNEL_VERSION, components=list(self._components))
            )
        except RuntimeError:
            pass
        return {"state": self._state, "booted": True, "booted_at": self._booted_at}

    def stop(self) -> dict[str, Any]:
        if self._state != "running":
            return {"state": self._state, "stopped": False}
        self._state = "stopped"
        self._logger.log("runtime", "kernel stopped")
        return {"state": self._state, "stopped": True}

    def status(self) -> dict[str, Any]:
        return {
            "state": self._state,
            "version": KERNEL_VERSION,
            "booted_at": self._booted_at,
            "components": list(self._components),
        }


_kernel_runtime: KernelRuntime | None = None


def get_kernel_runtime() -> KernelRuntime:
    global _kernel_runtime
    if _kernel_runtime is None:
        _kernel_runtime = KernelRuntime()
    return _kernel_runtime
