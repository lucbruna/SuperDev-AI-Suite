from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class DiagnosticResult:
    check: str = ""
    status: str = "passed"  # passed, failed, warning, error
    message: str = ""
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class DiagnosticEngine:
    """Runs diagnostic checks and collects results."""

    def __init__(self) -> None:
        self._checks: list[tuple[str, Callable[[], DiagnosticResult]]] = []
        self._history: list[DiagnosticResult] = []

    def register(self, name: str, check: Callable[[], DiagnosticResult]) -> None:
        self._checks.append((name, check))

    def run_all(self) -> list[DiagnosticResult]:
        results: list[DiagnosticResult] = []
        for name, check in self._checks:
            result = self._run(name, check)
            results.append(result)
            self._history.append(result)
        return results

    def run_one(self, name: str) -> DiagnosticResult | None:
        for check_name, check in self._checks:
            if check_name == name:
                result = self._run(name, check)
                self._history.append(result)
                return result
        return None

    def _run(self, name: str, check: Callable[[], DiagnosticResult]) -> DiagnosticResult:
        start = time.perf_counter()
        try:
            result = check()
        except Exception as e:
            result = DiagnosticResult(
                check=name,
                status="error",
                message=str(e),
            )
        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    def get_history(self, limit: int = 100) -> list[DiagnosticResult]:
        return list(self._history[-limit:])

    def get_passed(self) -> list[DiagnosticResult]:
        return [r for r in self._history if r.status == "passed"]

    def get_failed(self) -> list[DiagnosticResult]:
        return [r for r in self._history if r.status in ("failed", "error")]

    def summary(self) -> dict[str, Any]:
        total = len(self._history)
        passed = len(self.get_passed())
        failed = len(self.get_failed())
        return {
            "total_checks": len(self._checks),
            "total_runs": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total else 0.0,
            "last_run": self._history[-1].timestamp if self._history else 0.0,
        }
