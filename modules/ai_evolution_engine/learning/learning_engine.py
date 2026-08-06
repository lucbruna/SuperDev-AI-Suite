"""Learning engine: coordinates pattern/incident/feedback learners."""
from __future__ import annotations

from modules.ai_evolution_engine.config.learning_config import LearningConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.learning.feedback_learner import (
    FeedbackLearner,
)
from modules.ai_evolution_engine.learning.incident_learner import (
    IncidentLearner,
    IncidentRecord,
)
from modules.ai_evolution_engine.learning.pattern_learner import (
    CodePattern,
    learn as learn_patterns,
)


class LearningEngine:
    """Deterministic learning entry point."""

    def __init__(self, config: LearningConfig | None = None) -> None:
        self._config = config or LearningConfig()
        self.incidents = IncidentLearner(max_records=self._config.max_incidents)
        self.feedback = FeedbackLearner(max_kinds=self._config.max_feedback)

    def learn_from_context(self, ctx: EvolutionContext) -> list[CodePattern]:
        if not self._config.pattern_enabled:
            return []
        patterns = learn_patterns(ctx)
        return patterns[: self._config.max_patterns]

    def record_incident(self, record: IncidentRecord) -> None:
        if self._config.incident_enabled:
            self.incidents.record(record)

    def apply_feedback(self, kind: str, accepted: bool) -> None:
        if self._config.feedback_enabled:
            self.feedback.apply(kind, accepted)
