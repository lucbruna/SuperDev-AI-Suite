"""Architecture engine: facade over scanning, building, persistence,
analysis and exports.

This is the entry point used by the REST API, the CLI and the scheduler.
"""
from __future__ import annotations

import logging
import threading
from typing import Any

from modules.architecture_graph.config.graph_settings import get_settings
from modules.architecture_graph.core.discovery_engine import current_snapshot, diff_snapshots
from modules.architecture_graph.core.graph_engine import GraphEngine
from modules.architecture_graph.core.impact_engine import risk_score
from modules.architecture_graph.core.integrity_engine import check as integrity_check
from modules.architecture_graph.core.metrics_engine import graph_metrics, module_metrics
from modules.architecture_graph.core.topology_engine import (
    layer_violations,
    topological_order,
)
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.graph_cache import (
    GraphCache,
    load_snapshot,
    save_snapshot,
)
from modules.architecture_graph.storage.base import GraphStorage, get_storage

logger = logging.getLogger(__name__)


class ArchitectureEngine:
    """Coordinates the full graph lifecycle."""

    def __init__(self, config: Any = None) -> None:
        settings = get_settings()
        self.config = config or settings.config
        self.storage: GraphStorage = get_storage(self.config.storage_backend)
        self.cache = GraphCache()
        self.graph: ArchitectureGraph | None = None
        self._lock = threading.Lock()
        self._last_build: dict[str, Any] = {}

    # ---------------------------------------------------------------- build
    def build(self, *, persist: bool = True) -> ArchitectureGraph:
        """Full scan + parse + build + persist."""
        with self._lock:
            engine = GraphEngine(self.config)
            graph = engine.build()

            self.graph = graph
            self._last_build = {
                "built_at": graph.built_at,
                "stats": graph.stats(),
                "errors": engine.errors,
                "parsed_files": len(engine.parsed_files),
            }
            snapshot = current_snapshot(engine.scan())
            save_snapshot({"files": snapshot, "built_at": graph.built_at})
            if persist:
                self._persist()
            self.cache.invalidate()
            return graph

    def refresh(self) -> dict[str, Any]:
        """Incremental refresh: rebuild only when files changed."""
        with self._lock:
            if self.graph is None:
                graph = self.build()
                return {"full_rebuild": True, "diff": None, "stats": graph.stats()}
            engine = GraphEngine(self.config)
            files = engine.scan()
            old = load_snapshot()
            new = current_snapshot(files)
            diff = diff_snapshots((old or {}).get("files"), new)
            changed = diff["total_added"] + diff["total_removed"] + diff["total_modified"]
            if changed == 0:
                return {"full_rebuild": False, "diff": diff, "stats": self.graph.stats()}
            graph = engine.build()
            save_snapshot({"files": new, "built_at": graph.built_at})
            self.graph = graph
            self._last_build = {
                "built_at": graph.built_at,
                "stats": graph.stats(),
                "errors": engine.errors,
                "parsed_files": len(engine.parsed_files),
            }
            self._persist()
            self.cache.invalidate()
            return {"full_rebuild": True, "diff": diff, "stats": graph.stats()}

    # ---------------------------------------------------------------- load
    def load(self) -> ArchitectureGraph | None:
        """Load the persisted graph (or the last in-memory build)."""
        if self.graph is not None:
            return self.graph
        try:
            self.graph = self.storage.load()
        except Exception as exc:
            logger.warning("Failed to load graph from storage: %s", exc)
            self.graph = None
        return self.graph

    def ensure_graph(self, *, build_if_missing: bool = True) -> ArchitectureGraph | None:
        graph = self.load()
        if graph is None and build_if_missing:
            graph = self.build()
        return graph

    # ------------------------------------------------------------- analysis
    def analyze(self) -> dict[str, Any]:
        """Full analysis report over the current graph."""
        graph = self.ensure_graph()
        if graph is None:
            return {"available": False}

        from modules.architecture_graph.analytics.architecture_score import architecture_score

        ordered, cycles = topological_order(graph, kind="file")
        issues = integrity_check(graph)
        return {
            "available": True,
            "stats": graph.stats(),
            "metrics": graph_metrics(graph),
            "module_metrics": module_metrics(graph)[:20],
            "layer_violations": layer_violations(graph),
            "topological_cycle_ids": cycles,
            "integrity_issues": issues,
            "integrity_summary": {
                k: sum(1 for i in issues if i.get("type") == k)
                for k in sorted({i.get("type", "?") for i in issues})
            },
            "score": architecture_score(graph),
        }

    def impact(self, node_id: str) -> dict[str, Any]:
        from modules.architecture_graph.core.impact_engine import dependents

        graph = self.ensure_graph()
        if graph is None:
            return {"available": False}
        result = dependents(graph, node_id)
        result["risk"] = risk_score(graph, node_id)
        return result

    # ------------------------------------------------------------ persistence
    def _persist(self) -> None:
        if self.graph is None:
            return
        try:
            self.storage.save(self.graph)
        except Exception as exc:
            logger.warning("Graph persistence failed: %s", exc)

    def clear(self) -> None:
        with self._lock:
            self.graph = None
            try:
                self.storage.clear()
            except Exception as exc:
                logger.warning("Graph clear failed: %s", exc)
            self.cache.invalidate()

    @property
    def last_build(self) -> dict[str, Any]:
        return self._last_build


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

_engine: ArchitectureEngine | None = None
_engine_lock = threading.Lock()


def get_engine() -> ArchitectureEngine:
    """Process-wide singleton engine (lazy)."""
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = ArchitectureEngine()
    return _engine


def build_graph(**kwargs: Any) -> ArchitectureGraph:
    return get_engine().build(**kwargs)


def load_graph() -> ArchitectureGraph | None:
    return get_engine().load()
