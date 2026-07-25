from __future__ import annotations

from datetime import datetime
from typing import Any


class HistoryRecord:
    def __init__(self, event_type: str, data: dict[str, Any]):
        self.timestamp = datetime.now()
        self.event_type = event_type
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "data": self.data,
        }


class ExecutionHistory:
    def __init__(self):
        self._records: dict[str, list[HistoryRecord]] = {}

    def record(self, event: Any) -> None:
        event_type = type(event).__name__
        data = event.model_dump() if hasattr(event, "model_dump") else event.__dict__
        workflow_id = data.get("workflow_id", "_global")
        rec = HistoryRecord(event_type, data)
        self._records.setdefault(workflow_id, []).append(rec)

    def get_history(self, workflow_id: str) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._records.get(workflow_id, [])]

    def get_timeline(self, workflow_id: str) -> list[dict[str, Any]]:
        records = sorted(self._records.get(workflow_id, []), key=lambda r: r.timestamp)
        return [r.to_dict() for r in records]
