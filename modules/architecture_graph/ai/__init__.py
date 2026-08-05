"""AI layer for the Architecture Graph module.

Reasoning (insights), planning (improvement plans), retrieval (RAG over the
graph) and explanation (why does this node matter) — all offline and
dependency-free, exposed through the :class:`ArchitectureAI` facade.
"""
from __future__ import annotations

from modules.architecture_graph.ai.architecture_ai import (
    ArchitectureAI,
    get_ai,
)
from modules.architecture_graph.ai.architecture_explainer import (
    ArchitectureExplainer,
    explain,
)
from modules.architecture_graph.ai.architecture_planner import (
    ArchitecturePlanner,
    plan,
)
from modules.architecture_graph.ai.architecture_rag import (
    ArchitectureRAG,
    get_rag,
)
from modules.architecture_graph.ai.architecture_reasoner import (
    ArchitectureReasoner,
    reason,
)

__all__ = [
    "ArchitectureAI",
    "ArchitectureExplainer",
    "ArchitecturePlanner",
    "ArchitectureRAG",
    "ArchitectureReasoner",
    "explain",
    "get_ai",
    "get_rag",
    "plan",
    "reason",
]
