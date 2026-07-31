from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .reasoning_models import ReasoningResult


class ReasoningSnapshot:
    """Full snapshot of a reasoning session."""

    def __init__(self):
        self._snapshots: dict[str, dict[str, Any]] = {}

    def create(self, result: ReasoningResult, state: dict[str, Any] | None = None) -> str:
        snapshot_id = f"snap_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        self._snapshots[snapshot_id] = {
            "id": snapshot_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "result": {
                "decision": result.decision,
                "confidence": result.confidence,
                "context_id": result.context_id,
            },
            "state": state or {},
        }
        return snapshot_id

    def get(self, snapshot_id: str) -> dict[str, Any] | None:
        return self._snapshots.get(snapshot_id)

    def list(self) -> list[str]:
        return list(self._snapshots.keys())

    def delete(self, snapshot_id: str) -> bool:
        return self._snapshots.pop(snapshot_id, None) is not None
