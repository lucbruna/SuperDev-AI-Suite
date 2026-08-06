"""Connectors to the sibling SuperDev modules.

Each connector probes whether the sibling module is installed (``find_spec``,
no import side effects) and exposes the tools it contributes to the
orchestrator's decision surface. Calls are graceful: when the module is not
installed the connector reports ``unavailable`` instead of raising, and when
it is installed the orchestrator delegates the real work to that module's
own API through the ``delegated`` contract.
"""
from __future__ import annotations

from importlib.util import find_spec
from typing import Any

from modules.super_ai_orchestrator.integrations.base import Connector
from modules.super_ai_orchestrator.integrations.handlers import attach_real_handlers

# name -> (module_path, display, tools, note)
_SIBLINGS: dict[str, tuple[str, str, tuple[str, ...], str]] = {
    "architecture_graph": (
        "modules.architecture_graph",
        "Architecture Graph",
        ("architecture_graph",),
        "Module graph and structure analysis",
    ),
    "architecture_intelligence": (
        "modules.architecture_intelligence",
        "Architecture Intelligence",
        ("architecture_intelligence", "architecture_graph"),
        "Architecture intelligence and insights",
    ),
    "ai_code_knowledge_graph": (
        "modules.ai_code_knowledge_graph",
        "AI Code Knowledge Graph",
        ("knowledge_graph",),
        "Code knowledge graph and entity lookups",
    ),
    "autonomous_developer": (
        "modules.autonomous_developer",
        "Autonomous Developer",
        ("autonomous_developer",),
        "Autonomous development and agent loop",
    ),
    "digital_twin": (
        "modules.digital_twin",
        "Digital Twin",
        ("digital_twin",),
        "Project state twin and snapshots",
    ),
    "self_healing_engine": (
        "modules.self_healing_engine",
        "Self-Healing Engine",
        ("self_healing_engine", "checkpoint", "rollback"),
        "Diagnostics, repairs and self-healing",
    ),
    "ai_evolution_engine": (
        "modules.ai_evolution_engine",
        "AI Evolution Engine",
        ("evolution_engine", "ai_evolution_engine", "analytics"),
        "Evolution recommendations and roadmap",
    ),
}


def _installed(module_path: str) -> bool:
    try:
        return find_spec(module_path) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def make_sibling_connectors() -> tuple[Connector, ...]:
    """Build the sibling-module connectors with live availability probes.

    Real in-process handlers are attached to the connectors whose sibling
    modules are installed (see :mod:`handlers`); connectors without a real
    call keep the graceful ``delegated`` contract.
    """
    connectors: list[Connector] = []
    for name, (module_path, display, tools, note) in _SIBLINGS.items():
        connectors.append(
            Connector(
                name=name,
                display=display,
                tools=tools,
                available=_installed(module_path),
                note=f"{note} (module: {module_path})",
            )
        )
    return attach_real_handlers(tuple(connectors))
