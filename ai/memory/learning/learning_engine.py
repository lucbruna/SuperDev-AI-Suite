from __future__ import annotations

from typing import Any, Dict, List

from .adaptive_learning import AdaptiveLearning
from .evaluation import Evaluation
from .feedback_learning import FeedbackLearning
from .incremental_learning import IncrementalLearning
from .model_updater import ModelUpdater
from .pattern_learning import PatternLearning
from .reinforcement_learning import ReinforcementLearning
from .supervised_learning import SupervisedLearning
from .unsupervised_learning import UnsupervisedLearning


class LearningEngine:
    """Facade for memory learning subsystem."""

    def __init__(self):
        self._feedback = FeedbackLearning()
        self._reinforcement = ReinforcementLearning()
        self._supervised = SupervisedLearning()
        self._unsupervised = UnsupervisedLearning()
        self._pattern = PatternLearning()
        self._adaptive = AdaptiveLearning()
        self._incremental = IncrementalLearning()
        self._updater = ModelUpdater()
        self._evaluation = Evaluation()
        self._learning_count: int = 0

    @property
    def feedback(self) -> FeedbackLearning:
        return self._feedback

    @property
    def reinforcement(self) -> ReinforcementLearning:
        return self._reinforcement

    @property
    def supervised(self) -> SupervisedLearning:
        return self._supervised

    @property
    def unsupervised(self) -> UnsupervisedLearning:
        return self._unsupervised

    @property
    def pattern(self) -> PatternLearning:
        return self._pattern

    @property
    def adaptive(self) -> AdaptiveLearning:
        return self._adaptive

    @property
    def incremental(self) -> IncrementalLearning:
        return self._incremental

    @property
    def updater(self) -> ModelUpdater:
        return self._updater

    @property
    def evaluation(self) -> Evaluation:
        return self._evaluation

    def learn(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        patterns = self._pattern.learn(data)
        self._incremental.update(data)
        self._learning_count += 1
        return {
            "patterns": patterns,
            "learning_id": self._learning_count,
            "sample_count": len(data),
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            "learning_count": self._learning_count,
            "feedback_samples": self._feedback.sample_count,
            "reinforcement_cycles": self._reinforcement.cycle_count,
            "supervised_accuracy": self._evaluation.last_accuracy,
        }
