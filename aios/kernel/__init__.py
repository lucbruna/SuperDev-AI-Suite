"""AIOS Kernel — core subsystem.

Exports the kernel root, singleton manager, runtime, scheduler, event
model, security, monitor, logger, health, metrics, API facade and
version info.
"""

from __future__ import annotations

from .kernel import Kernel
from .kernel_api import KernelAPI
from .kernel_events import (
    AGENT_FINISHED,
    AGENT_STARTED,
    FAILURE_DETECTED,
    HEALTH_DEGRADED,
    KERNEL_BOOTED,
    KERNEL_SHUTDOWN,
    MEMORY_RECALLED,
    MEMORY_STORED,
    MODULE_REGISTERED,
    MODULE_UNREGISTERED,
    POLICY_VIOLATION,
    RECOVERY_COMPLETED,
    WORKFLOW_FINISHED,
    WORKFLOW_STARTED,
    ALL_EVENTS,
    KernelEvent,
    make_event,
)
from .kernel_health import DEGRADED, HEALTHY, UNHEALTHY, KernelHealth
from .kernel_logger import LEVELS, KernelLogger
from .kernel_manager import (
    KernelManager,
    get_kernel,
    get_kernel_manager,
    reset_kernel,
)
from .kernel_metrics import KernelMetrics
from .kernel_monitor import KernelMonitor
from .kernel_runtime import KernelRuntime
from .kernel_scheduler import KernelScheduler
from .kernel_security import (
    ACTOR_ADMIN,
    ACTOR_AGENT,
    ACTOR_SERVICE,
    ACTOR_SYSTEM,
    ACTOR_USER,
    KernelSecurity,
    KernelSecurityError,
)
from .kernel_version import (
    AIOS_NAME,
    AIOS_VERSION,
    COMPONENT_VERSIONS,
    KERNEL_VERSION,
    MIN_PYTHON,
    RUNTIME_VERSION,
    SUPPORTED_PYTHON,
    component_versions,
    platform_info,
)

__all__ = [
    "Kernel",
    "KernelAPI",
    "KernelEvent",
    "KernelHealth",
    "KernelLogger",
    "KernelManager",
    "KernelMetrics",
    "KernelMonitor",
    "KernelRuntime",
    "KernelScheduler",
    "KernelSecurity",
    "KernelSecurityError",
    "LEVELS",
    "DEGRADED",
    "HEALTHY",
    "UNHEALTHY",
    "ALL_EVENTS",
    "KERNEL_BOOTED",
    "KERNEL_SHUTDOWN",
    "AGENT_STARTED",
    "AGENT_FINISHED",
    "WORKFLOW_STARTED",
    "WORKFLOW_FINISHED",
    "MODULE_REGISTERED",
    "MODULE_UNREGISTERED",
    "MEMORY_STORED",
    "MEMORY_RECALLED",
    "POLICY_VIOLATION",
    "HEALTH_DEGRADED",
    "FAILURE_DETECTED",
    "RECOVERY_COMPLETED",
    "ACTOR_ADMIN",
    "ACTOR_AGENT",
    "ACTOR_SERVICE",
    "ACTOR_SYSTEM",
    "ACTOR_USER",
    "AIOS_NAME",
    "AIOS_VERSION",
    "KERNEL_VERSION",
    "RUNTIME_VERSION",
    "MIN_PYTHON",
    "SUPPORTED_PYTHON",
    "COMPONENT_VERSIONS",
    "component_versions",
    "platform_info",
    "get_kernel",
    "get_kernel_manager",
    "reset_kernel",
    "make_event",
]
