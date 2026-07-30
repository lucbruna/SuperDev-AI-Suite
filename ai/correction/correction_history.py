from __future__ import annotations

from datetime import datetime
from typing import Any


class CorrectionHistory:
    """Tracks correction operations and their outcomes."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    async def record(self, operation: str, error: dict[str, Any], success: bool) -> None:
        self._entries.append({
            "operation": operation,
            "error_type": error.get("type"),
            "success": success,
            "timestamp": datetime.now().isoformat(),
        })

    async def success_rate(self) -> float:
        if not self._entries:
            return 0.0
        successes = sum(1 for e in self._entries if e.get("success"))
        return successes / len(self._entries)

    async def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._entries),
            "success_rate": await self.success_rate(),
            "operations": list({e.get("operation") for e in self._entries}),
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.summary()
