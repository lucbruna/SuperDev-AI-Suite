"""Kernel version — AIOS identity and versioning constants."""
from __future__ import annotations

KERNEL_NAME = "SuperDev AIOS"
KERNEL_VERSION = "0.1.0"
KERNEL_API_VERSION = "v1"
KERNEL_DESCRIPTION = (
    "Artificial Intelligence Operating System for the SuperDev AI Suite"
)


def version_info() -> dict[str, str]:
    return {
        "name": KERNEL_NAME,
        "version": KERNEL_VERSION,
        "api_version": KERNEL_API_VERSION,
        "description": KERNEL_DESCRIPTION,
    }
