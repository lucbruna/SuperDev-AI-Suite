"""Health scoring for the Self-Healing Engine."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from modules.self_healing_engine.config.constants import (
    CHECK_ERROR,
    CHECK_FAILED,
    CHECK_WARNING,
    HEALTH_CRITICAL,
    HEALTH_DEGRADED,
    HEALTH_HEALTHY,
    HEALTH_UNHEALTHY,
)
from modules.self_healing_engine.diagnostics.checkers import CheckResult


@dataclass(slots=True)
class HealthScore:
    """Aggregated health score derived from check results."""

    score: float
    status: str
    checks_run: int = 0
    failed: int = 0
    warnings: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "status": self.status,
            "checks_run": self.checks_run,
            "failed": self.failed,
            "warnings": self.warnings,
        }


def compute_health_score(results: Sequence[CheckResult]) -> HealthScore:
    """Compute a 0-100 health score from check results (deterministic)."""
    score = 100.0
    failed = 0
    warnings = 0
    for result in results:
        if result.status == CHECK_WARNING:
            score -= 10
            warnings += 1
        elif result.status in (CHECK_FAILED, CHECK_ERROR):
            score -= 30
            failed += 1
    score = max(0.0, min(100.0, score))
    if score >= 90:
        status = HEALTH_HEALTHY
    elif score >= 70:
        status = HEALTH_DEGRADED
    elif score >= 40:
        status = HEALTH_UNHEALTHY
    else:
        status = HEALTH_CRITICAL
    return HealthScore(
        score=score,
        status=status,
        checks_run=len(results),
        failed=failed,
        warnings=warnings,
    )
