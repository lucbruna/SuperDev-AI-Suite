"""Coding score evaluation."""

from __future__ import annotations

from typing import Any


class CodingEvaluator:
    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []

    def evaluate(self, code: str, language: str = "python") -> dict[str, Any]:
        scores = {
            "syntax": 1.0 if code.strip() else 0.0,
            "length": min(len(code) / 100, 1.0),
            "has_functions": 1.0 if "def " in code or "function " in code else 0.5,
            "has_classes": 1.0 if "class " in code else 0.3,
        }
        avg = sum(scores.values()) / len(scores)
        result = {"language": language, "scores": scores, "avg_score": avg}
        self._results.append(result)
        return result

    def evaluate_solution(self, code: str, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
        passed = 0
        for _tc in test_cases:
            try:
                # Guarded execution: AST-allowlist + restricted builtins.
                # Lazy import keeps this module importable in constrained
                # environments (e.g. the standalone ai_models smoke script).
                from core.safe_exec import safe_exec

                safe_exec(code, {})
                passed += 1
            except Exception:
                pass
        total = len(test_cases)
        score = (passed / total * 100) if total > 0 else 0
        return {"score": score, "passed": passed, "total": total}

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._results[-limit:]

    def average_score(self) -> float:
        if not self._results:
            return 0.0
        return sum(r["avg_score"] for r in self._results) / len(self._results)

    def count(self) -> int:
        return len(self._results)
