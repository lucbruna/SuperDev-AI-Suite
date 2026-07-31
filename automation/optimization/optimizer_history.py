"""History of optimization suggestions."""

from __future__ import annotations

from typing import Any

from automation.optimization.optimizer_models import OptimizationReport


class OptimizerHistory:
    """Append-only log of optimization suggestions."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record_suggestions(self, report: OptimizationReport) -> None:
        for suggestion in report.suggestions:
            self._records.append(suggestion.to_dict())

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._records[-limit:])

    def mark_applied(self, suggestion_id: str) -> bool:
        for record in self._records:
            if record["suggestion_id"] == suggestion_id:
                record["applied"] = True
                return True
        return False

    def applied_count(self) -> int:
        return sum(1 for r in self._records if r["applied"])

    def clear(self) -> None:
        self._records.clear()
