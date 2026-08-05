"""AIOS composition root — wiring the 16 subsystems into a bootable Kernel.

This module is the single integration point of the platform. It attaches
the kernel components (monitor, security, health), registers the named
services expected by the ``KernelAPI`` facade, and provides thin adapters
where a native subsystem API differs from the facade contract:

- ``WorkflowService`` binds named ``WorkflowDefinition`` objects to the
  ``WorkflowEngine`` and exposes ``execute(name, inputs)``.
- ``ModuleService`` maps the manifest dict contract of ``KernelAPI`` onto
  the ``ModuleManager`` API.

Design constraints: pure Python, in-memory, deterministic; no I/O at
import time; everything is created inside :func:`compose_kernel`.
"""

from __future__ import annotations

from typing import Any

from aios.agents.agent_registry import create_default_registry
from aios.communications.event_bus import EventBus
from aios.enterprise_memory.memory_engine import MemoryEngine
from aios.kernel.kernel import Kernel
from aios.kernel.kernel_health import KernelHealth
from aios.kernel.kernel_monitor import KernelMonitor
from aios.kernel.kernel_runtime import KernelRuntime
from aios.kernel.kernel_security import KernelSecurity
from aios.module_registry.module_manager import ModuleManager
from aios.workflows.workflow_definitions import NodeFunc, WorkflowDefinition
from aios.workflows.workflow_engine import WorkflowEngine

__all__ = ["ModuleService", "WorkflowService", "compose_kernel"]


class WorkflowService:
    """Named workflow registry + execution matching the KernelAPI contract.

    ``KernelAPI.run_workflow`` calls ``execute(name, inputs)``; the native
    ``WorkflowEngine`` runs a definition together with a functions table,
    so this adapter binds named definitions to their functions.
    """

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        functions: dict[str, NodeFunc] | None = None,
    ) -> None:
        self.engine = engine if engine is not None else WorkflowEngine()
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._functions: dict[str, NodeFunc] = dict(functions or {})

    def register_definition(
        self,
        name: str,
        definition: WorkflowDefinition,
        functions: dict[str, NodeFunc] | None = None,
    ) -> str:
        """Register a named workflow with its node functions."""
        self._definitions[name] = definition
        self._functions.update(functions or {})
        return name

    def definitions(self) -> dict[str, WorkflowDefinition]:
        return dict(self._definitions)

    def execute(self, name: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run a named workflow, returning the run result as a dict."""
        definition = self._definitions.get(name)
        if definition is None:
            return {"ok": False, "error": f"unknown workflow: {name}"}
        try:
            result = self.engine.run(definition, self._functions, dict(inputs or {}))
        except Exception as exc:  # noqa: BLE001 - facade returns failures as data
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        return result.to_dict()


class ModuleService:
    """Module registry facade matching the KernelAPI manifest contract.

    ``KernelAPI.register_module`` passes a manifest dict; the native
    ``ModuleManager.register`` takes keyword arguments, so this adapter
    translates between the two shapes.
    """

    def __init__(self, manager: ModuleManager | None = None) -> None:
        self.manager = manager if manager is not None else ModuleManager()

    def register(self, manifest: dict[str, Any]) -> dict[str, Any]:
        name = manifest.get("name")
        if not name:
            return {"ok": False, "error": "manifest requires a 'name'"}
        try:
            module = self.manager.register(
                name=name,
                version=manifest.get("version", "1.0.0"),
                entrypoint=manifest.get("entrypoint"),
                capabilities=manifest.get("capabilities"),
                dependencies=manifest.get("dependencies"),
                module_id=manifest.get("module_id"),
                **(manifest.get("metadata") or {}),
            )
        except KeyError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "module": module.to_dict()}

    def list(self) -> list[dict[str, Any]]:
        return [module.to_dict() for module in self.manager.registry.modules()]

    def snapshot(self) -> dict[str, Any]:
        return self.manager.snapshot()


def compose_kernel() -> Kernel:
    """Build the default AIOS kernel with all 16 subsystems wired."""
    kernel = Kernel()

    # -- kernel components ------------------------------------------------
    monitor = KernelMonitor()
    security = KernelSecurity()
    health = KernelHealth(kernel, monitor)

    kernel.attach("kernel_monitor", monitor)
    kernel.attach("kernel_security", security)
    kernel.attach("kernel_health", health)

    # -- named services ----------------------------------------------------
    bus = EventBus()
    memory = MemoryEngine()
    agents = create_default_registry()
    runtime = KernelRuntime()
    workflows = WorkflowService()
    modules = ModuleService()

    kernel.register_service("event_bus", bus)
    kernel.register_service("memory_engine", memory)
    kernel.register_service("agent_registry", agents)
    kernel.register_service("kernel_runtime", runtime)
    kernel.register_service("workflow_engine", workflows)
    kernel.register_service("module_registry", modules)

    # -- monitor probes ----------------------------------------------------
    def _event_bus_check() -> dict[str, Any]:
        return {"status": "ok", "subscriptions": bus.snapshot()["subscription_count"]}

    def _memory_check() -> dict[str, Any]:
        return {"status": "ok", "kinds": memory.kinds()}

    def _agents_check() -> dict[str, Any]:
        return {"status": "ok", "count": len(agents.names())}

    def _modules_check() -> dict[str, Any]:
        return {"status": "ok", "count": len(modules.list())}

    monitor.register("event_bus", _event_bus_check)
    monitor.register("memory", _memory_check)
    monitor.register("agents", _agents_check)
    monitor.register("modules", _modules_check)

    return kernel
