"""Real in-process handlers for the sibling-module connectors.

Each handler conforms to the ``Connector.execute`` contract::

    handler(action: str, **kwargs) -> dict

Handlers import their sibling module lazily (so the orchestrator imports
cleanly even when a sibling is missing or broken), run the real sibling
engine, and never raise: failures are returned as structured
``{"status": "error", ...}`` dicts. When a sibling is unavailable the
connector keeps its graceful ``unavailable`` degradation because the
handler is only attached to connectors whose module is installed.

Only connectors with a real, deterministic sibling call receive a handler;
the rest keep the ``delegated`` contract (status returned by
:meth:`Connector.execute` when ``handler is None``).
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------- #
# Handler factories
# ---------------------------------------------------------------------- #


def make_self_healing_handler() -> Any:
    """Real handler for the Self-Healing Engine connector."""

    def handler(action: str = "run", **kwargs: Any) -> dict[str, Any]:
        from modules.self_healing_engine.core.healing_context import HealingContext
        from modules.self_healing_engine.core.healing_engine import HealingEngine

        engine = HealingEngine()
        if action == "status":
            return {"status": "ok", "engine": "self_healing_engine", "cycles": engine.cycles}
        incident = kwargs.get("incident")
        result = engine.run(HealingContext(), incident)
        return {"status": "ok", "engine": "self_healing_engine", "result": result.to_dict()}

    return handler


def make_digital_twin_handler() -> Any:
    """Real handler for the Digital Twin connector."""

    def handler(action: str = "run", **kwargs: Any) -> dict[str, Any]:
        from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
        from modules.digital_twin.core.digital_twin_engine import DigitalTwinEngine

        engine = DigitalTwinEngine()
        if action == "status":
            return {"status": "ok", "engine": "digital_twin", "cycles": engine.cycles}
        result = engine.run(DigitalTwinContext())
        return {"status": "ok", "engine": "digital_twin", "result": result.to_dict()}

    return handler


def make_knowledge_graph_handler() -> Any:
    """Real handler for the AI Code Knowledge Graph connector."""

    def handler(action: str = "status", **kwargs: Any) -> dict[str, Any]:
        from modules.ai_code_knowledge_graph.core.knowledge_engine import get_engine

        engine = get_engine()
        if action == "scan":
            return {
                "status": "ok",
                "engine": "ai_code_knowledge_graph",
                "result": engine.scan(project_root=kwargs.get("project_root")),
            }
        if action == "snapshot":
            return {
                "status": "ok",
                "engine": "ai_code_knowledge_graph",
                "result": engine.snapshot(),
            }
        if action == "files":
            return {
                "status": "ok",
                "engine": "ai_code_knowledge_graph",
                "result": engine.files(language=kwargs.get("language")),
            }
        return {"status": "ok", "engine": "ai_code_knowledge_graph", "result": engine.status()}

    return handler


def make_autonomous_developer_handler() -> Any:
    """Real handler for the Autonomous Developer connector."""

    def handler(action: str = "status", **kwargs: Any) -> dict[str, Any]:
        from modules.autonomous_developer.core.runtime import build_runtime

        runtime = build_runtime()
        if action == "run_phase":
            phase = kwargs.get("phase", "plan")
            return {
                "status": "ok",
                "engine": "autonomous_developer",
                "result": runtime.run_phase(phase, **kwargs.get("phase_kwargs", {})),
            }
        return {"status": "ok", "engine": "autonomous_developer", "result": runtime.status()}

    return handler


# ---------------------------------------------------------------------- #
# Wiring
# ---------------------------------------------------------------------- #

# connector name -> real handler factory. Connectors absent from this map
# keep the graceful ``delegated`` contract (handler stays None).
_REAL_HANDLERS: dict[str, Any] = {
    "self_healing_engine": make_self_healing_handler,
    "digital_twin": make_digital_twin_handler,
    "ai_code_knowledge_graph": make_knowledge_graph_handler,
    "autonomous_developer": make_autonomous_developer_handler,
}


def attach_real_handlers(connectors: tuple[Any, ...]) -> tuple[Any, ...]:
    """Attach real handlers to sibling connectors that have one.

    Only connectors whose module is installed (``available=True``) receive
    a handler, preserving graceful degradation for missing siblings.
    """
    from modules.super_ai_orchestrator.integrations.base import Connector

    wired: list[Connector] = []
    for connector in connectors:
        factory = _REAL_HANDLERS.get(connector.name)
        if factory is not None and connector.available:
            connector.handler = factory()
        wired.append(connector)
    return tuple(wired)
