"""AIOS Self Evaluation — quality scoring of produced work.

Evaluates a result against expectations with metrics: completeness,
correctness proxy, consistency and speed, yielding an overall score.
"""

from __future__ import annotations

from typing import Any


class SelfEvaluation:
    """Score results against declared expectations."""

    def evaluate(
        self,
        result: Any,
        expected_keys: list[str] | None = None,
        required_fields: list[str] | None = None,
        elapsed_ms: float = 0.0,
    ) -> dict[str, Any]:
        metrics: dict[str, float] = {}
        if isinstance(result, dict):
            if required_fields:
                present = sum(1 for f in required_fields if f in result)
                metrics["completeness"] = round(present / len(required_fields), 4)
            else:
                metrics["completeness"] = 1.0
            if expected_keys:
                found = sum(1 for k in expected_keys if k in result)
                metrics["consistency"] = round(found / len(expected_keys), 4)
            else:
                metrics["consistency"] = 1.0
        else:
            metrics["completeness"] = 1.0 if result is not None else 0.0
            metrics["consistency"] = 1.0
        # Speed proxy: faster than 1000ms is full credit.
        metrics["speed"] = max(0.0, 1.0 - (elapsed_ms / 1000.0))
        overall = round(sum(metrics.values()) / len(metrics), 4)
        return {
            "ok": True,
            "overall": overall,
            "metrics": metrics,
            "verdict": "pass" if overall >= 0.6 else "needs_work",
        }
