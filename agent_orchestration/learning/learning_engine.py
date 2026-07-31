"""Learning subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.learning.behavior_optimizer import BehaviorOptimizer
from agent_orchestration.learning.feedback_processor import FeedbackProcessor
from agent_orchestration.learning.improvement_tracker import ImprovementTracker
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import EvaluationReport, Lesson
from agent_orchestration.orchestrator_protocols import new_id


class LearningEngine:
    """Facade over feedback processing, improvements and optimization."""

    def __init__(self, feedback: FeedbackProcessor | None = None,
                 improvements: ImprovementTracker | None = None,
                 optimizer: BehaviorOptimizer | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.feedback = feedback or FeedbackProcessor()
        self.improvements = improvements or ImprovementTracker()
        self.optimizer = optimizer or BehaviorOptimizer()
        self.metrics = metrics or OrchestratorMetrics()

    def process_feedback(self, agent_id: str, text: str) -> dict[str, Any]:
        entry = self.feedback.process(agent_id, text)
        self.metrics.increment("ao.feedback_processed")
        return entry

    def learn_from_feedback(self, agent_id: str,
                            text: str) -> dict[str, Any]:
        entry = self.process_feedback(agent_id, text)
        improvement = self.improvements.record(
            agent_id, entry["text"], entry["kind"])
        self.metrics.increment("ao.improvements")
        return improvement

    def optimize(self, report: EvaluationReport) -> dict[str, Any]:
        changes = self.optimizer.apply(report)
        if changes:
            self.metrics.increment("ao.behavior_changes")
        return changes

    def record_lesson(self, agent_id: str, topic: str, error: str,
                      solution: str) -> Lesson:
        lesson = Lesson(lesson_id=new_id("lesson"), agent_id=agent_id,
                        topic=topic, error=error, solution=solution)
        self.metrics.increment("ao.lessons")
        return lesson

    def stats(self) -> dict[str, Any]:
        return {"feedback": self.feedback.count(),
                "improvements": self.improvements.count(),
                "applied": self.improvements.applied_count(),
                "behavior_changes": self.optimizer.count(),
                "metrics": self.metrics.snapshot()["counters"]}
