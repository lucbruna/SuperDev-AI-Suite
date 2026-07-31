from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .quality_models import TestCase, TestResult

# A test predicate evaluates a case and returns True when it passes.
TestPredicate = Callable[[TestCase], bool]

# A runner callable receives (case, context) and returns a TestResult-style dict.
RunnerCallable = Callable[[TestCase, dict[str, Any]], dict[str, Any]]

# Quality signals fed into the production gate.
QualitySignals = dict[str, Any]


def result_to_dict(result: TestResult) -> dict[str, Any]:
    """Serialize a TestResult into a plain dict (JSON-safe)."""
    return {
        "result_id": result.result_id,
        "suite_id": result.suite_id,
        "suite_name": result.suite_name,
        "kind": result.kind.value,
        "total": result.total,
        "passed": result.passed,
        "failed": result.failed,
        "skipped": result.skipped,
        "errors": result.errors,
        "duration_ms": result.duration_ms,
        "status": result.status.value,
        "passed_rate": result.passed_rate,
    }


__all__ = ["TestPredicate", "RunnerCallable", "QualitySignals", "result_to_dict"]
