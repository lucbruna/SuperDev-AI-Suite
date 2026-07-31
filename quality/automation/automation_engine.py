from __future__ import annotations

from typing import Any

from ..quality_models import TestCase, TestKind, TestSuite


class AutomationEngine:
    """Test automation — generation, execution pipeline, scheduling, parallel runner, retry, notification."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.automation
        self._generated: dict[str, list[TestCase]] = {}
        self._pipeline: list[str] = []
        self._notifications: list[dict[str, Any]] = []
        self._retries: dict[str, int] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- generation ----------------------------------------------------------

    def generate_tests(self, target: str, _source: str | None = None) -> list[TestCase]:
        """Auto-generate test cases for a target."""
        cases = [
            TestCase(name="generated_smoke", kind=TestKind.UNIT, source=target,
                     assertions=["import ok"]),
            TestCase(name="generated_edge", kind=TestKind.UNIT, source=target,
                     assertions=["edge handled"]),
            TestCase(name="generated_negative", kind=TestKind.UNIT, source=target,
                     assertions=["negative handled"]),
        ]
        self._generated[target] = cases
        self.engine.metrics.increment("automation.generated", labels={"target": target})
        return cases

    def generate_suite(self, target: str) -> TestSuite:
        suite = TestSuite(name=f"auto-{target}", kind=TestKind.UNIT, target=target)
        suite.cases = self.generate_tests(target)
        self.engine.registry.register_suite(suite)
        return suite

    # -- pipeline ------------------------------------------------------------

    def build_pipeline(self, stages: list[str]) -> None:
        self._pipeline = list(stages)

    def pipeline_stages(self) -> list[str]:
        return list(self._pipeline)

    # -- parallel runner -----------------------------------------------------

    def partition(self, cases: list[TestCase], workers: int = 4) -> list[list[TestCase]]:
        """Split cases into worker-sized batches (round-robin)."""
        if not cases:
            return []
        workers = max(1, workers)
        batches: list[list[TestCase]] = [[] for _ in range(min(workers, len(cases)))]
        for i, case in enumerate(cases):
            batches[i % len(batches)].append(case)
        return batches

    # -- retry ---------------------------------------------------------------

    def should_retry(self, case_id: str, max_retries: int = 2) -> bool:
        attempts = self._retries.get(case_id, 0)
        if attempts < max_retries:
            self._retries[case_id] = attempts + 1
            return True
        return False

    def reset_retries(self, case_id: str) -> None:
        self._retries.pop(case_id, None)

    # -- notification --------------------------------------------------------

    def notify(self, channel: str, message: str, level: str = "info") -> dict[str, Any]:
        notification = {
            "channel": channel,
            "message": message,
            "level": level,
        }
        self._notifications.append(notification)
        self.engine.metrics.increment(
            "automation.notifications", labels={"channel": channel}
        )
        return notification

    def recent_notifications(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._notifications[-limit:]

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "generated": sum(len(v) for v in self._generated.values()),
            "pipeline_stages": len(self._pipeline),
            "notifications": len(self._notifications),
        }


__all__ = ["AutomationEngine"]
