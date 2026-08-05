"""AIOS Kernel Version — platform version constants.

Single source of truth for the AIOS platform and kernel versions used
by the module compatibility checker.
"""

from __future__ import annotations

from typing import Any

AIOS_NAME = "SuperDev AIOS"
AIOS_VERSION = "1.0.0"
KERNEL_VERSION = "1.0.0"
RUNTIME_VERSION = "1.0.0"
MIN_PYTHON = (3, 10)
SUPPORTED_PYTHON = ">=3.10"

COMPONENT_VERSIONS: dict[str, str] = {
    "kernel": KERNEL_VERSION,
    "runtime": RUNTIME_VERSION,
    "enterprise_memory": "1.0.0",
    "cognition": "1.0.0",
    "reasoning": "1.0.0",
    "planning": "1.0.0",
    "execution": "1.0.0",
    "communications": "1.0.0",
    "services": "1.0.0",
    "agents": "1.0.0",
    "module_registry": "1.0.0",
    "workflows": "1.0.0",
    "extensions": "1.0.0",
    "governance": "1.0.0",
    "self_healing": "1.0.0",
    "digital_twin": "1.0.0",
}


def component_versions() -> dict[str, str]:
    """Return the component version map (defensive copy)."""
    return dict(COMPONENT_VERSIONS)


def platform_info() -> dict[str, Any]:
    import sys

    return {
        "name": AIOS_NAME,
        "version": AIOS_VERSION,
        "kernel": KERNEL_VERSION,
        "python": sys.version.split()[0],
        "python_supported": SUPPORTED_PYTHON,
        "components": component_versions(),
    }
