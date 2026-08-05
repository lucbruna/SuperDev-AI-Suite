"""AIOS Kernel — composition root and lifecycle owner.

The Kernel is the central object of the SuperDev AIOS. It owns the
lifecycle of the platform, hosts the service registry (named services)
and the component registry (subsystems), and exposes a single entry
point for boot/shutdown/snapshot operations.

Design constraints:
- Pure Python, deterministic, no external I/O at import time.
- Services are lazily wired at ``boot`` time via compose hooks.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Callable

from .kernel_version import AIOS_VERSION, KERNEL_VERSION

BootHook = Callable[["Kernel"], Any]
ShutdownHook = Callable[["Kernel"], Any]


class Kernel:
    """Composition root of the AIOS platform."""

    def __init__(self, name: str = "aios-kernel", version: str = AIOS_VERSION) -> None:
        self.name = name
        self.version = version
        self.kernel_version = KERNEL_VERSION
        self.instance_id = f"{name}-{uuid.uuid4().hex[:12]}"
        self.state = "created"  # created -> booting -> running -> shutting_down -> stopped
        self._services: dict[str, Any] = {}
        self._components: dict[str, Any] = {}
        self._boot_hooks: list[BootHook] = []
        self._shutdown_hooks: list[ShutdownHook] = []
        self.started_at: float | None = None
        self.stopped_at: float | None = None

    # ------------------------------------------------------------------
    # Service registry (generic named services: memory, cache, bus, ...)
    # ------------------------------------------------------------------
    def register_service(self, name: str, instance: Any) -> "Kernel":
        """Register a named service instance."""
        self._services[name] = instance
        return self

    def get_service(self, name: str, default: Any = None) -> Any:
        return self._services.get(name, default)

    def services(self) -> dict[str, Any]:
        return dict(self._services)

    # ------------------------------------------------------------------
    # Component registry (named subsystems: kernel_security, scheduler...)
    # ------------------------------------------------------------------
    def attach(self, name: str, component: Any) -> "Kernel":
        """Attach a subsystem component by name."""
        self._components[name] = component
        return self

    def component(self, name: str, default: Any = None) -> Any:
        return self._components.get(name, default)

    def components(self) -> dict[str, Any]:
        return dict(self._components)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def on_boot(self, hook: BootHook) -> "Kernel":
        self._boot_hooks.append(hook)
        return self

    def on_shutdown(self, hook: ShutdownHook) -> "Kernel":
        self._shutdown_hooks.append(hook)
        return self

    def boot(self) -> dict[str, Any]:
        """Run boot hooks and transition to running."""
        if self.state in ("booting", "running"):
            return self.snapshot()
        self.state = "booting"
        self.started_at = time.time()
        for hook in self._boot_hooks:
            hook(self)
        self.state = "running"
        return self.snapshot()

    def shutdown(self) -> dict[str, Any]:
        if self.state == "stopped":
            return self.snapshot()
        self.state = "shutting_down"
        for hook in reversed(self._shutdown_hooks):
            hook(self)
        self.state = "stopped"
        self.stopped_at = time.time()
        return self.snapshot()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        """Return a deterministic snapshot of the kernel state."""
        return {
            "name": self.name,
            "version": self.version,
            "kernel_version": self.kernel_version,
            "instance_id": self.instance_id,
            "state": self.state,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "component_count": len(self._components),
            "service_count": len(self._services),
            "components": sorted(self._components.keys()),
            "services": sorted(self._services.keys()),
        }

    # ------------------------------------------------------------------
    # Composition
    # ------------------------------------------------------------------
    @staticmethod
    def compose() -> "Kernel":
        """Compose the default AIOS platform into a bootable Kernel.

        The actual wiring lives in ``aios.compose.compose_kernel`` so the
        kernel keeps a single integration point while ``Kernel`` remains
        the composition root API.
        """
        from aios.compose import compose_kernel

        return compose_kernel()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Kernel {self.name} v{self.version} [{self.state}]>"
