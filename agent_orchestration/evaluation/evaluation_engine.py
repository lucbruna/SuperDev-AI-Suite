"""Evaluation subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.evaluation.accuracy import AccuracyScorer
from agent_orchestration.evaluation.feedback import FeedbackCollector
from agent_orchestration.evaluation.performance import PerformanceTracker
from agent_orchestration.evaluation.quality_score import QualityScorer
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import EvaluationReport
from agent_orchestration.orchestrator_protocols import new_id, now


class EvaluationEngine:
    """Facade that produces EvaluationReports from performance signals."""

    def __init__(self, performance: PerformanceTracker | None = None,
                 accuracy: AccuracyScorer | None = None,
                 quality: QualityScorer | None = None,
                 feedback: FeedbackCollector | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.performance = performance or PerformanceTracker()
        self.accuracy = accuracy or AccuracyScorer()
        self.quality = quality or QualityScorer()
        self.feedback = feedback or FeedbackCollector()
        self.metrics = metrics or OrchestratorMetrics()

    def record(self, agent_id: str, duration: float,
               success: bool) -> None:
        self.performance.record(agent_id, duration, success)
        self.metrics.increment("ao.evaluations_recorded")

    def score_accuracy(self, agent_id: str, output: Any,
                       expected: Any) -> float:
        value = self.accuracy.score(agent_id, output, expected)
        self.metrics.increment("ao.accuracy_scores")
        return value

    def add_feedback(self, agent_id: str, text: str,
                     source: str = "human") -> None:
        self.feedback.add(agent_id, text, source)

    def evaluate(self, agent_id: str) -> EvaluationReport:
        accuracy = self.accuracy.accuracy(agent_id)
        errors = self.accuracy.errors(agent_id)
        avg_time = self.performance.average_time(agent_id)
        has_data = (self.performance.count(agent_id) > 0
                    or self.accuracy.count(agent_id) > 0)
        quality_score = (self.quality.score(accuracy, errors, avg_time)
                         if has_data else 0.0)
        report = EvaluationReport(
            evaluation_id=new_id("eval"), agent_id=agent_id,
            accuracy=accuracy, errors=errors, avg_time=avg_time,
            quality_score=quality_score,
            feedback=self.feedback.latest(agent_id), created_at=now())
        self.metrics.increment("ao.evaluations")
        return report

    def stats(self) -> dict[str, Any]:
        counters = self.metrics.snapshot()["counters"]
        return {"agents": self.performance.count(),
                "feedback_total": self.feedback.count(),
                "metrics": counters}
