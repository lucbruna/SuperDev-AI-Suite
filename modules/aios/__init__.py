"""AIOS — Artificial Intelligence Operating System (blueprint Volume 12).

Provides a common kernel that modules can boot onto, replacing duplicated
infrastructure with shared lifecycle, health, metrics, security, scheduling,
monitoring and logging primitives. Reuses the Vol 10 integration bus/logger
for events and audit trails.
"""
from __future__ import annotations

from modules.aios.kernel import (
    KERNEL_NAME,
    KERNEL_VERSION,
    Kernel,
    KernelAPI,
    KernelHealth,
    KernelLogger,
    KernelManager,
    KernelMetrics,
    KernelMonitor,
    KernelPermissionDeniedError,
    KernelRuntime,
    KernelScheduler,
    KernelSecurity,
    get_kernel,
    get_kernel_api,
    get_kernel_health,
    get_kernel_logger,
    get_kernel_manager,
    get_kernel_metrics,
    get_kernel_monitor,
    get_kernel_runtime,
    get_kernel_scheduler,
    get_kernel_security,
    version_info,
)

__all__ = [
    "KERNEL_NAME",
    "KERNEL_VERSION",
    "Kernel",
    "KernelAPI",
    "KernelHealth",
    "KernelLogger",
    "KernelManager",
    "KernelMetrics",
    "KernelMonitor",
    "KernelPermissionDeniedError",
    "KernelRuntime",
    "KernelScheduler",
    "KernelSecurity",
    "get_kernel",
    "get_kernel_api",
    "get_kernel_health",
    "get_kernel_logger",
    "get_kernel_manager",
    "get_kernel_metrics",
    "get_kernel_monitor",
    "get_kernel_runtime",
    "get_kernel_scheduler",
    "get_kernel_security",
    "version_info",
]
