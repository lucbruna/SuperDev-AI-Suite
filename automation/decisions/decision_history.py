"""History of decision tree evaluations."""

from __future__ import annotations

import time
from typing import Any


class DecisionHistory:
    """Append-only log of decision results."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(self, result: Any) -> None:
        self._records.append({
            "tree_id": result.tree_id,
            "decision": result.decision,
            "action": result.action,
            "timestamp": time.time(),
        })

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._records[-limit:])

    def count(self, tree_id: str | None = None) -> int:
        if tree_id is None:
            return len(self._records)
        return sum(1 for r in self._records if r["tree_id"] == tree_id)

    def clear(self) -> None:
        self._records.clear()
