"""SuperDev AIOS — Artificial Intelligence Operating System.

Pure-Python, deterministic, in-memory platform composed of 16 subsystems.
:func:`compose_kernel` wires them into a bootable
:class:`~aios.kernel.kernel.Kernel`; :class:`~aios.kernel.kernel_api.KernelAPI`
is the stable public facade.
"""

from __future__ import annotations

from . import (
    agents,
    cognition,
    communications,
    digital_twin,
    enterprise_memory,
    execution,
    extensions,
    governance,
    kernel,
    module_registry,
    planning,
    reasoning,
    runtime,
    self_healing,
    services,
    workflows,
)
from .compose import ModuleService, WorkflowService, compose_kernel
from .kernel import Kernel
from .kernel.kernel_api import KernelAPI
from .kernel.kernel_manager import (
    KernelManager,
    get_kernel,
    get_kernel_manager,
    reset_kernel,
)
from .kernel.kernel_version import (
    AIOS_NAME,
    AIOS_VERSION,
    COMPONENT_VERSIONS,
    component_versions,
    platform_info,
)

__all__ = [
    # composition
    "Kernel",
    "KernelAPI",
    "KernelManager",
    "get_kernel",
    "get_kernel_manager",
    "reset_kernel",
    "compose_kernel",
    "WorkflowService",
    "ModuleService",
    # version
    "AIOS_NAME",
    "AIOS_VERSION",
    "COMPONENT_VERSIONS",
    "component_versions",
    "platform_info",
    # subsystems
    "agents",
    "cognition",
    "communications",
    "digital_twin",
    "enterprise_memory",
    "execution",
    "extensions",
    "governance",
    "kernel",
    "module_registry",
    "planning",
    "reasoning",
    "runtime",
    "self_healing",
    "services",
    "workflows",
]
