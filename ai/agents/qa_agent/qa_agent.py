from __future__ import annotations

from typing import Any

from .acceptance import Acceptance
from .bug_detector import BugDetector
from .coverage import Coverage
from .metrics import Metrics
from .mutation_testing import MutationTesting
from .quality_analyzer import QualityAnalyzer
from .regression import Regression
from .smoke_tests import SmokeTests


class QAAgent:
    """Central orchestrator for quality assurance workflows."""

    def __init__(self) -> None:
        self._quality = QualityAnalyzer()
        self._bugs = BugDetector()
        self._regression = Regression()
        self._smoke = SmokeTests()
        self._acceptance = Acceptance()
        self._coverage = Coverage()
        self._mutation = MutationTesting()
        self._metrics = Metrics()

    @property
    def quality(self) -> QualityAnalyzer:
        return self._quality

    @property
    def bugs(self) -> BugDetector:
        return self._bugs

    @property
    def regression(self) -> Regression:
        return self._regression

    @property
    def smoke(self) -> SmokeTests:
        return self._smoke

    @property
    def acceptance(self) -> Acceptance:
        return self._acceptance

    @property
    def coverage(self) -> Coverage:
        return self._coverage

    @property
    def mutation(self) -> MutationTesting:
        return self._mutation

    @property
    def metrics(self) -> Metrics:
        return self._metrics

    def run_quality_check(self, target: dict[str, Any]) -> dict[str, Any]:
        code = target.get("code", "")
        quality_score = self._quality.calculate_score(code)
        bugs = self._bugs.detect_bugs(code)
        return {
            "status": "checked",
            "quality_score": quality_score,
            "bugs_found": len(bugs),
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "quality_score": 0,
            "bugs": self._bugs.pattern_count,
            "regression_tests": self._regression.test_count,
            "smoke_tests": self._smoke.test_count,
            "mutation_kill_rate": self._mutation.survival_rate,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "qa_agent", "status": self.get_status()}
