from __future__ import annotations

from typing import Any


class ChainMetrics:
    """Metrics collection for chain execution."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    async def record(self, chain_id: str, steps: int, duration: float, success: bool) -> None:
        self._records.append(
            {
                "chain_id": chain_id,
                "steps": steps,
                "duration": duration,
                "success": success,
            }
        )

    async def average_steps(self) -> float:
        if not self._records:
            return 0.0
        return sum(r.get("steps", 0) for r in self._records) / len(self._records)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "total_chains": len(self._records),
            "avg_steps": await self.average_steps(),
            "success_rate": sum(1 for r in self._records if r.get("success")) / len(self._records)
            if self._records
            else 0,
        }
