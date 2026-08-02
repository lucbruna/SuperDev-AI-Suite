"""Kernel package — core of the SuperDev AIOS (Volume 12)."""
from __future__ import annotations

from modules.aios.kernel.kernel import Kernel, get_kernel
from modules.aios.kernel.kernel_api import KernelAPI, get_kernel_api
from modules.aios.kernel.kernel_events import emit
from modules.aios.kernel.kernel_health import KernelHealth, get_kernel_health
from modules.aios.kernel.kernel_logger import KernelLogger, get_kernel_logger
from modules.aios.kernel.kernel_manager import (
    KernelManager,
    KernelPermissionDeniedError,
    get_kernel_manager,
)
from modules.aios.kernel.kernel_metrics import KernelMetrics, get_kernel_metrics
from modules.aios.kernel.kernel_monitor import KernelMonitor, get_kernel_monitor
from modules.aios.kernel.kernel_runtime import KernelRuntime, get_kernel_runtime
from modules.aios.kernel.kernel_scheduler import KernelScheduler, get_kernel_scheduler
from modules.aios.kernel.kernel_security import KernelSecurity, get_kernel_security
from modules.aios.kernel.kernel_version import KERNEL_NAME, KERNEL_VERSION, version_info

__all__ = [
    "KERNEL_NAME",
    "KERNEL_VERSION",
    "Kernel",
    "get_kernel",
    "KernelAPI",
    "get_kernel_api",
    "emit",
    "KernelHealth",
    "get_kernel_health",
    "KernelLogger",
    "get_kernel_logger",
    "KernelManager",
    "KernelPermissionDeniedError",
    "get_kernel_manager",
    "KernelMetrics",
    "get_kernel_metrics",
    "KernelMonitor",
    "get_kernel_monitor",
    "KernelRuntime",
    "get_kernel_runtime",
    "KernelScheduler",
    "get_kernel_scheduler",
    "KernelSecurity",
    "get_kernel_security",
    "version_info",
]
