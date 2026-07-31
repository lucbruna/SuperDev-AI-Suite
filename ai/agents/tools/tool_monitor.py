"""Tool execution monitoring."""
from __future__ import annotations

import time
from typing import Any, Dict, List


class ToolMonitor:
    """Monitors tool execution performance and health."""

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []

    def record(self, tool_id: str, result: Dict[str, Any]) -> None:
        self._records.append({
            "tool_id": tool_id,
            "status": result.get("status", "unknown"),
            "duration_ms": result.get("duration_ms", 0),
            "timestamp": time.time(),
        })

    def get_summary(self) -> Dict[str, Any]:
        if not self._records:
            return {"total": 0, "success": 0, "failure": 0, "avg_duration_ms": 0}
        success = sum(1 for r in self._records if r["status"] == "completed")
        failure = len(self._records) - success
        avg_dur = sum(r["duration_ms"] for r in self._records) / len(self._records)
        return {
            "total": len(self._records),
            "success": success,
            "failure": failure,
            "success_rate": round(success / max(len(self._records), 1), 2),
            "avg_duration_ms": round(avg_dur, 2),
        }

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._records[-limit:]
