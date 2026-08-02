"""Kernel manager — facade over the kernel subsystems."""
from __future__ import annotations
from typing import Any

from modules.aios.kernel.kernel_health import KernelHealth, get_kernel_health
from modules.aios.kernel.kernel_logger import KernelLogger, get_kernel_logger
from modules.aios.kernel.kernel_metrics import KernelMetrics, get_kernel_metrics
from modules.aios.kernel.kernel_monitor import (
    KernelMonitor,
    StatusProbe,
    get_kernel_monitor,
)
from modules.aios.kernel.kernel_runtime import KernelRuntime, get_kernel_runtime
from modules.aios.kernel.kernel_scheduler import KernelScheduler, get_kernel_scheduler
from modules.aios.kernel.kernel_security import (
    KernelPermissionDeniedError,
    KernelSecurity,
    get_kernel_security,
)
from modules.aios.kernel.kernel_version import KERNEL_NAME, KERNEL_VERSION, version_info


class KernelManager:
    """Composes kernel subsystems and exposes a unified snapshot."""

    def __init__(self) -> None:
        self.runtime: KernelRuntime = get_kernel_runtime()
        self.health: KernelHealth = get_kernel_health()
        self.monitor: KernelMonitor = get_kernel_monitor()
        self.metrics: KernelMetrics = get_kernel_metrics()
        self.security: KernelSecurity = get_kernel_security()
        self.scheduler: KernelScheduler = get_kernel_scheduler()
        self.logger: KernelLogger = get_kernel_logger()

    def register_component(self, name: str, probe: StatusProbe | None = None) -> None:
        self.runtime.register_component(name)
        if probe is not None:
            self.monitor.register(name, probe)

    def boot(self) -> dict[str, Any]:
        with self.metrics.timed("kernel.boot"):
            result = self.runtime.boot()
        self.metrics.increment("kernel.boots")
        self.scheduler.start()
        self.monitor.tick()
        return result

    def stop(self) -> dict[str, Any]:
        self.scheduler.stop()
        return self.runtime.stop()

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": KERNEL_NAME,
            "version": KERNEL_VERSION,
            "runtime": self.runtime.status(),
            "health": self.health.run(),
            "monitor": self.monitor.snapshot(),
            "metrics": self.metrics.snapshot(),
            "security": self.security.snapshot(),
            "scheduler": self.scheduler.snapshot(),
        }

    def info(self) -> dict[str, str]:
        return version_info()


_kernel_manager: KernelManager | None = None


def get_kernel_manager() -> KernelManager:
    global _kernel_manager
    if _kernel_manager is None:
        _kernel_manager = KernelManager()
    return _kernel_manager


__all__ = [
    "KernelManager",
    "KernelPermissionDeniedError",
    "get_kernel_manager",
]
