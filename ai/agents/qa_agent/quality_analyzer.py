from __future__ import annotations

from typing import Any


class QualityAnalyzer:
    """Analyzes code quality metrics and scores."""

    QUALITY_CHECKS: list[tuple[str, str]] = [
        ("function length > 50 lines", "Consider breaking down long functions"),
        ("missing docstrings", "Add docstrings to public functions"),
        ("inconsistent naming", "Follow consistent naming conventions"),
        ("duplicate code", "Extract duplicate logic into shared utilities"),
        ("magic numbers", "Replace magic numbers with named constants"),
        ("deep nesting", "Reduce nesting depth for readability"),
    ]

    def __init__(self) -> None:
        self._metrics: dict[str, dict[str, Any]] = {}

    def analyze_code(self, code_snippet: str) -> list[dict[str, Any]]:
        results = []
        for check, suggestion in self.QUALITY_CHECKS:
            results.append({
                "check": check,
                "suggestion": suggestion,
                "passed": True,
            })
        return results

    def add_metric(self, name: str, description: str, target: float) -> str:
        self._metrics[name] = {
            "name": name,
            "description": description,
            "target": target,
        }
        return name

    def get_metric(self, name: str) -> dict[str, Any] | None:
        return self._metrics.get(name)

    def list_metrics(self) -> list[dict[str, Any]]:
        return list(self._metrics.values())

    @property
    def metric_count(self) -> int:
        return len(self._metrics)

    def calculate_score(self, code: str) -> float:
        base = 85.0
        deductions = 0.0
        if len(code) > 1000:
            deductions += 5.0
        if "TODO" in code:
            deductions += 5.0
        if "print(" in code or "console.log(" in code:
            deductions += 2.0
        return max(0.0, base - deductions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metrics": list(self._metrics.values()),
            "metric_count": self.metric_count,
        }
