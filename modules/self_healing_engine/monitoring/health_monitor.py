"""Health monitor: runs checkers, scores health and updates state."""
from __future__ import annotations

from collections.abc import Sequence

from modules.self_healing_engine.diagnostics.checkers import (
    DEFAULT_CHECKERS,
    CheckResult,
    DiagnosticCheck,
)
from modules.self_healing_engine.diagnostics.health import (
    HealthScore,
    compute_health_score,
)
from modules.self_healing_engine.core.healing_context import HealingContext

_MAX_HISTORY = 200


class HealthMonitor:
    """Runs deterministic checkers and publishes health changes."""

    def __init__(
        self, checkers: Sequence[DiagnosticCheck] | None = None
    ) -> None:
        self._checkers: tuple[DiagnosticCheck, ...] = tuple(
            checkers if checkers is not None else DEFAULT_CHECKERS
        )
        self._results: list[CheckResult] = []
        self._last: HealthScore | None = None

    @property
    def checkers(self) -> tuple[DiagnosticCheck, ...]:
        return self._checkers

    def run(self, ctx: HealingContext) -> HealthScore:
        results: list[CheckResult] = []
        for checker in self._checkers:
            results.append(checker.run(ctx))
        score = compute_health_score(results)
        ctx.state.set_health_score(score.score)
        ctx.state.set_health_status(score.status)
        ctx.publish(
            "health.changed",
            {
                "score": score.score,
                "status": score.status,
                "checks_run": score.checks_run,
                "failed": score.failed,
            },
        )
        self._results.extend(results)
        if len(self._results) > _MAX_HISTORY:
            del self._results[: len(self._results) - _MAX_HISTORY]
        self._last = score
        return score

    def results(self) -> list[CheckResult]:
        return list(self._results)

    def last_score(self) -> HealthScore | None:
        return self._last
