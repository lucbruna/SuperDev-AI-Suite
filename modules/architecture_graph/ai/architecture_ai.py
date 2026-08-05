"""Architecture AI facade: unified entry point for AI features.

Aggregates reasoning, planning, retrieval (RAG) and explanations over the
architecture graph. The API layer, CLI and Architecture Intelligence module
all consume this facade instead of reaching into individual services.
"""
from __future__ import annotations

import threading
from typing import Any

from modules.architecture_graph.ai.architecture_explainer import (
    ArchitectureExplainer,
)
from modules.architecture_graph.ai.architecture_planner import ArchitecturePlanner
from modules.architecture_graph.ai.architecture_rag import ArchitectureRAG, get_rag
from modules.architecture_graph.ai.architecture_reasoner import (
    ArchitectureReasoner,
)
from modules.architecture_graph.core.architecture_engine import get_engine
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class ArchitectureAI:
    """Facade over the AI capabilities of the Architecture Graph module."""

    def __init__(self) -> None:
        self.reasoner = ArchitectureReasoner()
        self.planner = ArchitecturePlanner()
        self.explainer = ArchitectureExplainer()
        self.rag: ArchitectureRAG | None = None
        self._lock = threading.Lock()

    # ------------------------------------------------------------ graph load
    def _graph(self, build_if_missing: bool = True) -> ArchitectureGraph | None:
        return get_engine().ensure_graph(build_if_missing=build_if_missing)

    # ------------------------------------------------------------ reasoning
    def insights(self, *, build_if_missing: bool = True) -> dict[str, Any]:
        graph = self._graph(build_if_missing)
        if graph is None:
            return {"available": False}
        return self.reasoner.analyze(graph)

    def risk_ranking(self, *, limit: int = 10, build_if_missing: bool = True) -> dict[str, Any]:
        graph = self._graph(build_if_missing)
        if graph is None:
            return {"available": False}
        return {
            "available": True,
            "ranking": self.reasoner.risk_ranking(graph, limit=limit),
        }

    # ------------------------------------------------------------ planning
    def plan(self, *, build_if_missing: bool = True) -> dict[str, Any]:
        graph = self._graph(build_if_missing)
        if graph is None:
            return {"available": False}
        return self.planner.plan(graph)

    def migration_plan(
        self, target_package: str, nodes: list[str] | None = None
    ) -> dict[str, Any]:
        graph = self._graph()
        if graph is None:
            return {"available": False}
        return self.planner.migration_plan(
            graph, target_package=target_package, nodes=nodes
        )

    # ----------------------------------------------------------- explanation
    def explain(self, node_id: str) -> dict[str, Any]:
        graph = self._graph(build_if_missing=False)
        if graph is None:
            return {"available": False, "text": "Graph not built yet."}
        return self.explainer.explain_all(graph, node_id)

    # ------------------------------------------------------------------- RAG
    def _ensure_rag(self, graph: ArchitectureGraph) -> ArchitectureRAG:
        with self._lock:
            if self.rag is None:
                self.rag = get_rag()
                self.rag.index_graph(graph)
            return self.rag

    def search(self, query: str, *, limit: int = 10) -> dict[str, Any]:
        graph = self._graph()
        if graph is None:
            return {"available": False}
        rag = self._ensure_rag(graph)
        return {"available": True, "results": rag.search(query, limit=limit)}

    def related(self, node_id: str, *, limit: int = 5) -> dict[str, Any]:
        graph = self._graph(build_if_missing=False)
        if graph is None:
            return {"available": False}
        rag = self._ensure_rag(graph)
        return {"available": True, "results": rag.suggest_related(node_id, limit=limit)}

    # ------------------------------------------------------------ aggregate
    def full_report(self) -> dict[str, Any]:
        """Everything the dashboard needs in one call."""
        graph = self._graph()
        if graph is None:
            return {"available": False}
        rag = self._ensure_rag(graph)
        return {
            "available": True,
            "insights": self.reasoner.analyze(graph),
            "risk": self.reasoner.risk_ranking(graph, limit=10),
            "plan": self.planner.plan(graph),
            "rag": rag.stats(),
            "graph_stats": graph.stats(),
        }


_ai: ArchitectureAI | None = None
_ai_lock = threading.Lock()


def get_ai() -> ArchitectureAI:
    """Process-wide singleton AI facade."""
    global _ai
    if _ai is None:
        with _ai_lock:
            if _ai is None:
                _ai = ArchitectureAI()
    return _ai
