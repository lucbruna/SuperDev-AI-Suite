"""Adaptive replanning engine for plan modification."""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


class Replanner:
    """Handles adaptive replanning when plans encounter failures or changes."""

    def __init__(self) -> None:
        self._replan_count: int = 0
        self._replan_history: List[Dict[str, Any]] = []

    def replan(self, plan: Dict[str, Any], reason: str,
               context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._replan_count += 1
        original_tasks = plan.get("tasks", [])
        completed = [t for t in original_tasks if t.get("status") == "completed"]
        remaining = [t for t in original_tasks if t.get("status") != "completed"]
        new_tasks = list(completed)
        failed = [t for t in remaining if t.get("status") == "failed"]
        pending = [t for t in remaining if t.get("status") == "pending"]
        for task in failed:
            retry = dict(task)
            retry["task_id"] = f"task_{uuid.uuid4().hex[:8]}"
            retry["status"] = "pending"
            retry["retried_from"] = task.get("task_id")
            retry["retry_reason"] = reason
            new_tasks.append(retry)
        new_tasks.extend(pending)
        self._replan_history.append({
            "plan_id": plan.get("plan_id", ""),
            "reason": reason,
            "original_count": len(original_tasks),
            "new_count": len(new_tasks),
            "retried": len(failed),
            "timestamp": time.time(),
        })
        return new_tasks

    def analyze_failure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        error = task.get("result", {}).get("error", "")
        suggestions: List[str] = []
        if "timeout" in error.lower():
            suggestions.append("Increase timeout or split into smaller tasks")
        if "permission" in error.lower():
            suggestions.append("Check agent permissions")
        if "not found" in error.lower():
            suggestions.append("Verify dependencies exist")
        if not suggestions:
            suggestions.append("Retry with different approach")
        return {
            "task_id": task.get("task_id"),
            "error": error,
            "suggestions": suggestions,
        }

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._replan_history)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "total_replans": self._replan_count,
            "history_size": len(self._replan_history),
        }
