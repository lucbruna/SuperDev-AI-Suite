"""AIOS Kernel API — stable public facade over the kernel.

External surfaces (REST gateway, CLI, workflows) should talk to the
platform through this facade instead of reaching into internals,
keeping the public contract stable as subsystems evolve.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Awaitable

from .kernel import Kernel
from .kernel_security import KernelSecurityError


async def _as_coroutine(awaitable: Awaitable[Any]) -> Any:
    """Wrap an awaitable into a coroutine (for typing + reuse)."""
    return await awaitable


def _resolve_awaitable(result: Any) -> Any:
    """Resolve an awaitable synchronously when no event loop is running.

    ``KernelAPI`` keeps a synchronous facade, but some services expose
    async entry points (``EventBus.publish``, ``KernelRuntime.run``).
    When no loop is running we drive the coroutine to completion; inside
    a running loop a sync facade cannot block, so we report that state
    explicitly instead of returning a dangling coroutine.
    """
    if not inspect.isawaitable(result):
        return result
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_as_coroutine(result))
    return {"ok": False, "error": "async service call requires an async caller"}


class KernelAPI:
    """Public operations exposed by the AIOS kernel."""

    def __init__(self, kernel: Kernel) -> None:
        self.kernel = kernel

    # -- lifecycle -----------------------------------------------------
    def boot(self) -> dict[str, Any]:
        return self.kernel.boot()

    def shutdown(self) -> dict[str, Any]:
        return self.kernel.shutdown()

    def health(self) -> dict[str, Any]:
        health = self.kernel.component("kernel_health")
        if health is None:
            return {"overall": "unknown", "kernel_state": self.kernel.state}
        return health.check()

    def snapshot(self) -> dict[str, Any]:
        return self.kernel.snapshot()

    # -- dispatch / events ----------------------------------------------
    def dispatch(self, event_type: str, payload: dict[str, Any] | None = None, source: str = "api") -> dict[str, Any]:
        bus = self.kernel.get_service("event_bus")
        if bus is None:
            return {"ok": False, "error": "event_bus service not registered"}
        from ..kernel.kernel_events import make_event

        return _resolve_awaitable(bus.publish(make_event(event_type, payload, source=source)))

    # -- agents / workflows ----------------------------------------------
    def run_agent(self, agent_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        registry = self.kernel.get_service("agent_registry")
        if registry is None:
            return {"ok": False, "error": "agent_registry service not registered"}
        agent = registry.get(agent_id)
        if agent is None:
            return {"ok": False, "error": f"unknown agent: {agent_id}"}
        runtime = self.kernel.get_service("kernel_runtime")
        if runtime is None:
            return {"ok": False, "error": "kernel_runtime service not registered"}
        return _resolve_awaitable(
            runtime.run(lambda: agent.run(context or {}), metadata={"agent_id": agent_id})
        )

    def run_workflow(self, name: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        engine = self.kernel.get_service("workflow_engine")
        if engine is None:
            return {"ok": False, "error": "workflow_engine service not registered"}
        runtime = self.kernel.get_service("kernel_runtime")
        if runtime is None:
            return {"ok": False, "error": "kernel_runtime service not registered"}
        return _resolve_awaitable(
            runtime.run(lambda: engine.execute(name, inputs or {}), metadata={"workflow": name})
        )

    # -- memory -----------------------------------------------------------
    def store_memory(self, kind: str, content: Any, **meta: Any) -> dict[str, Any]:
        engine = self.kernel.get_service("memory_engine")
        if engine is None:
            return {"ok": False, "error": "memory_engine service not registered"}
        return engine.store(kind=kind, content=content, **meta)

    def recall_memory(self, kind: str, query: Any, limit: int = 5) -> dict[str, Any]:
        engine = self.kernel.get_service("memory_engine")
        if engine is None:
            return {"ok": False, "error": "memory_engine service not registered"}
        return engine.recall(kind=kind, query=query, limit=limit)

    # -- modules -----------------------------------------------------------
    def register_module(self, manifest: dict[str, Any]) -> dict[str, Any]:
        registry = self.kernel.get_service("module_registry")
        if registry is None:
            return {"ok": False, "error": "module_registry service not registered"}
        return registry.register(manifest)

    def list_modules(self) -> list[dict[str, Any]]:
        registry = self.kernel.get_service("module_registry")
        if registry is None:
            return []
        return registry.list()

    # -- security ----------------------------------------------------------
    def check_permission(self, actor: str, action: str, resource: str | None = None) -> bool:
        security = self.kernel.component("kernel_security")
        if security is None:
            return True
        try:
            security.assert_allowed(actor, action, resource)
            return True
        except KernelSecurityError:
            return False
