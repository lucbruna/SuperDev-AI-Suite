from __future__ import annotations

from typing import Any


class CorrectionMetrics:
    """Metrics collection for correction operations."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, operation: str, duration: float, success: bool) -> None:
        self._records.append(
            {
                "operation": operation,
                "duration": duration,
                "success": success,
            }
        )

    async def average_duration(self) -> float:
        if not self._records:
            return 0.0
        return sum(r.get("duration", 0) for r in self._records) / len(self._records)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "total_operations": len(self._records),
            "avg_duration": await self.average_duration(),
            "success_count": sum(1 for r in self._records if r.get("success")),
        }
