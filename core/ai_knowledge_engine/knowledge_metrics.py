from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .knowledge_context import KnowledgeContext

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeMetrics:
    total_entries: int = 0
    active_knowledge: int = 0
    research_conducted: int = 0
    documents_processed: int = 0
    vectors_indexed: int = 0
    reasoning_performed: int = 0
    learning_iterations: int = 0
    validations_run: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    avg_confidence: float = 0.0
    total_sources: int = 0
    hypotheses_generated: int = 0
    queries_executed: int = 0
    errors: int = 0
    last_updated: Optional[datetime] = None


class MetricsCollector:
    def __init__(self, context: KnowledgeContext):
        self.context = context
        self.metrics = KnowledgeMetrics()
        self._history: Dict[str, List[float]] = {}
        self._confidence_history: List[float] = []

    def increment_entries(self, count: int = 1) -> None:
        self.metrics.total_entries += count
        self._touch()

    def increment_active(self, count: int = 1) -> None:
        self.metrics.active_knowledge += count
        self._touch()

    def increment_research(self) -> None:
        self.metrics.research_conducted += 1
        self._touch()

    def increment_documents(self) -> None:
        self.metrics.documents_processed += 1
        self._touch()

    def increment_vectors(self, count: int = 1) -> None:
        self.metrics.vectors_indexed += count
        self._touch()

    def increment_reasoning(self) -> None:
        self.metrics.reasoning_performed += 1
        self._touch()

    def increment_learning(self) -> None:
        self.metrics.learning_iterations += 1
        self._touch()

    def increment_validations(self) -> None:
        self.metrics.validations_run += 1
        self._touch()

    def set_graph_size(self, nodes: int, edges: int) -> None:
        self.metrics.graph_nodes = nodes
        self.metrics.graph_edges = edges
        self._touch()

    def record_confidence(self, confidence: float) -> None:
        self._confidence_history.append(confidence)
        if len(self._confidence_history) > 10000:
            self._confidence_history.pop(0)
        self.metrics.avg_confidence = sum(self._confidence_history) / max(len(self._confidence_history), 1)
        self._touch()

    def record_error(self) -> None:
        self.metrics.errors += 1
        self._touch()

    def record_metric(self, key: str, value: float) -> None:
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(value)
        if len(self._history[key]) > 1000:
            self._history[key].pop(0)

    def get_average(self, key: str, window: int = 100) -> float:
        values = self._history.get(key, [])
        if not values:
            return 0.0
        recent = values[-window:]
        return sum(recent) / len(recent)

    def get_all_metrics(self) -> Dict[str, Any]:
        return {
            "total_entries": self.metrics.total_entries,
            "active_knowledge": self.metrics.active_knowledge,
            "research_conducted": self.metrics.research_conducted,
            "documents_processed": self.metrics.documents_processed,
            "vectors_indexed": self.metrics.vectors_indexed,
            "reasoning_performed": self.metrics.reasoning_performed,
            "learning_iterations": self.metrics.learning_iterations,
            "validations_run": self.metrics.validations_run,
            "graph_nodes": self.metrics.graph_nodes,
            "graph_edges": self.metrics.graph_edges,
            "avg_confidence": round(self.metrics.avg_confidence, 4),
            "queries_executed": self.metrics.queries_executed,
            "errors": self.metrics.errors,
            "hypotheses_generated": self.metrics.hypotheses_generated,
        }

    def _touch(self) -> None:
        self.metrics.last_updated = datetime.utcnow()