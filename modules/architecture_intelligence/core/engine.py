"""Architecture Intelligence engine: the module facade.

Coordinates graph access (via the Architecture Graph module), metric history,
reasoning, planning, prediction, optimization, graph Q&A, diagnostics and
agent runs into one coherent API used by the REST API, CLI and scheduler.

Every method degrades gracefully: when the underlying graph is unavailable it
returns ``{"available": False}``; when no LLM provider is configured the
analysis packages fall back to deterministic heuristics.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

from modules.architecture_intelligence.config.intelligence_settings import get_settings
from modules.architecture_intelligence.core.history import MetricHistory, get_history

logger = logging.getLogger(__name__)


class ArchitectureIntelligenceEngine:
    """Facade over graph access + analysis + history."""

    def __init__(self, history: MetricHistory | None = None) -> None:
        self.settings = get_settings()
        self.history = history or get_history()
        self._lock = threading.Lock()
        self._graph_engine: Any | None = None

    # ------------------------------------------------------------ graph access
    @property
    def graph_engine(self) -> Any:
        """Lazy handle to the Architecture Graph engine (may be absent)."""
        if self._graph_engine is None:
            try:
                from modules.architecture_graph.core.architecture_engine import (
                    get_engine,
                )

                self._graph_engine = get_engine()
            except Exception as exc:  # module not installed / import error
                logger.debug("Architecture Graph module unavailable: %s", exc)
                self._graph_engine = None
        return self._graph_engine

    @property
    def available(self) -> bool:
        return self.graph_engine is not None

    def graph(self, *, build_if_missing: bool = True) -> Any | None:
        if self.graph_engine is None:
            return None
        try:
            return self.graph_engine.ensure_graph(build_if_missing=build_if_missing)
        except Exception as exc:
            logger.warning("Graph unavailable: %s", exc)
            return None

    # ------------------------------------------------------------------ history
    def snapshot(self) -> dict[str, Any]:
        """Capture the current state (metrics + analysis) into history."""
        analysis = self._core_metrics()
        if not analysis.get("available", True):
            return {"available": False, "appended": False}
        snapshot = {
            "ts": time.time(),
            "nodes": analysis.get("stats", {}).get("nodes", 0),
            "edges": analysis.get("stats", {}).get("edges", 0),
            "score": _nested(analysis, "score.score", 0.0),
            "integrity_issues": _nested(analysis, "integrity_summary", {}).get("total", 0),
        }
        appended = self.history.append(
            snapshot, min_interval_seconds=self.settings.config.history_min_interval_seconds
        )
        return {"available": True, "snapshot": snapshot, "appended": appended}

    def history_recent(self, limit: int = 20) -> dict[str, Any]:
        series = self.history.recent(limit)
        return {"available": True, "count": len(series), "snapshots": series}

    # --------------------------------------------------------------- analysis
    def analyze(self) -> dict[str, Any]:
        """Full intelligence report: metrics + trends + insights + plan + forecast."""
        metrics = self._core_metrics()
        if not metrics.get("available", True):
            return {"available": False, "reason": "graph unavailable"}
        trends = self.trends()
        forecast = self.forecast()
        return {
            "available": True,
            "generated_at": time.time(),
            "metrics": metrics,
            "trends": trends,
            "forecast": forecast,
        }

    def insights(self, *, limit: int | None = None) -> dict[str, Any]:
        from modules.architecture_intelligence.reasoning.insight_engine import get_insight_engine

        graph = self.graph()
        if graph is None:
            return {"available": False}
        return {"available": True, "insights": get_insight_engine().run(graph, limit=limit)}

    def plan(self) -> dict[str, Any]:
        from modules.architecture_intelligence.planning.roadmap import RoadmapGenerator

        graph = self.graph()
        if graph is None:
            return {"available": False}
        return {"available": True, **RoadmapGenerator().generate(graph)}

    def forecast(self) -> dict[str, Any]:
        from modules.architecture_intelligence.prediction.forecast import ForecastEngine

        return ForecastEngine(self.history, self.settings.config.forecast_horizon).run()

    def trends(self) -> dict[str, Any]:
        from modules.architecture_intelligence.prediction.trends import TrendAnalyzer

        return TrendAnalyzer(self.history).analyze()

    def optimize(self) -> dict[str, Any]:
        from modules.architecture_intelligence.optimization.recommendations import (
            Optimizer,
        )

        graph = self.graph()
        if graph is None:
            return {"available": False}
        return {"available": True, **Optimizer().recommend(graph)}

    def ask(self, question: str) -> dict[str, Any]:
        """Graph-aware Q&A (LLM-backed, heuristic fallback)."""
        from modules.architecture_intelligence.graph_ai.assistant import GraphAssistant

        graph = self.graph()
        if graph is None:
            return {"available": False, "answer": "The architecture graph is not available yet."}
        return {"available": True, **GraphAssistant().ask(question, graph)}

    def diagnose(self) -> dict[str, Any]:
        from modules.architecture_intelligence.diagnostics.health import HealthChecker

        return HealthChecker(self).run()

    def agents(self) -> dict[str, Any]:
        from modules.architecture_intelligence.agents.manager import AgentManager

        return AgentManager(self).run_all()

    def report(self) -> dict[str, Any]:
        """One-shot aggregate payload for dashboards."""
        result: dict[str, Any] = {
            "available": self.available,
            "generated_at": time.time(),
        }
        if not self.available:
            return result
        result.update(self.analyze())
        result["insights"] = self.insights()
        result["optimizations"] = self.optimize()
        result["diagnostics"] = self.diagnose()
        result["history"] = self.history_recent(limit=10)
        return result

    # -------------------------------------------------------------- internals
    def _core_metrics(self) -> dict[str, Any]:
        graph = self.graph(build_if_missing=False)
        if graph is None:
            return {"available": False}
        try:
            return self.graph_engine.analyze()
        except Exception as exc:
            logger.warning("Graph analysis failed: %s", exc)
            return {"available": False, "error": str(exc)}


def _nested(payload: dict[str, Any], dotted: str, default: Any = None) -> Any:
    node: Any = payload
    for part in dotted.split("."):
        if not isinstance(node, dict):
            return default
        node = node.get(part)
    return node if node is not None else default


_engine: ArchitectureIntelligenceEngine | None = None
_engine_lock = threading.Lock()


def get_intelligence() -> ArchitectureIntelligenceEngine:
    """Process-wide singleton intelligence engine (lazy)."""
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = ArchitectureIntelligenceEngine()
    return _engine
