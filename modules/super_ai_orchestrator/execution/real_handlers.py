"""Real kind handlers for the orchestrator pipeline.

The default executor handlers are deterministic stubs (``delegated`` results)
so the full pipeline runs end-to-end with zero integrations installed. These
real handlers override that default per task kind by dispatching the task to
the corresponding sibling connector (Self-Healing Engine, Digital Twin, AI
Code Knowledge Graph, Autonomous Developer).

Installation is opt-in (:meth:`TaskExecutor.install_real_handlers`) so the
deterministic default behaviour and its tests are preserved: callers that want
the full end-to-end chain enable it explicitly.

Every real handler receives an ``OrchestrationContext`` and returns a dict.
It degrades to a stub-like ``delegated`` result when the sibling connector is
unavailable or raises, so the pipeline never breaks.
"""
from __future__ import annotations

from typing import Any, Callable

from modules.super_ai_orchestrator.core.context import OrchestrationContext
from modules.super_ai_orchestrator.integrations.registry import ConnectorRegistry

Handler = Callable[[OrchestrationContext], dict[str, Any]]

# kind -> sibling connector name (from integrations/sibling.py)
_KIND_CONNECTOR: dict[str, str] = {
    "repair": "self_healing_engine",
    "recover": "self_healing_engine",
    "monitor": "digital_twin",
    "analyze": "ai_code_knowledge_graph",
    "develop": "autonomous_developer",
}


def _stub(context: OrchestrationContext, kind: str, note: str) -> dict[str, Any]:
    """Deterministic stub-shaped result used when the real call is unavailable."""
    task = context.task
    return {
        "status": "delegated",
        "kind": kind,
        "title": task.title,
        "handler": "real",
        "owner": task.owner,
        "llm": task.llm,
        "plan": [step["action"] for step in context.plan],
        "note": note,
    }


def _make_real_handler(kind: str, connector_name: str) -> Handler:
    def handler(context: OrchestrationContext) -> dict[str, Any]:
        registry = ConnectorRegistry()
        connector = registry.get(connector_name)
        if connector is None or not connector.available:
            return _stub(context, kind, f"{connector_name} unavailable; delegated")
        action = "run" if kind in ("repair", "recover", "monitor") else "status"
        try:
            result = connector.execute(action, task=context.task.to_dict())
        except Exception as exc:  # never break the pipeline
            return _stub(context, kind, f"real handler error: {exc}")
        if result.get("status") == "error":
            return _stub(context, kind, result.get("error", "real handler error"))
        return {
            "status": "ok",
            "kind": kind,
            "title": context.task.title,
            "handler": "real",
            "connector": connector_name,
            "owner": context.task.owner,
            "llm": context.task.llm,
            "plan": [step["action"] for step in context.plan],
            "result": result,
        }

    return handler


def real_handlers() -> dict[str, Handler]:
    """Build the real kind handlers for the wired sibling connectors."""
    return {kind: _make_real_handler(kind, conn) for kind, conn in _KIND_CONNECTOR.items()}
