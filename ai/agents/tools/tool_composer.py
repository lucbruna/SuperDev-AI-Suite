"""Tool composition for multi-tool workflows."""
from __future__ import annotations

from typing import Any, Dict, List


class ToolComposer:
    """Combines multiple tools into composite execution pipelines."""

    def __init__(self) -> None:
        self._pipelines: List[Dict[str, Any]] = []

    def compose(self, tool_ids: List[str], task: Dict[str, Any],
                registry: Any) -> Dict[str, Any]:
        available: List[Dict[str, Any]] = []
        missing: List[str] = []
        for tid in tool_ids:
            tool = registry.get(tid)
            if tool:
                available.append(tool)
            else:
                missing.append(tid)
        pipeline = {
            "tool_ids": tool_ids,
            "available": len(available),
            "missing": missing,
            "task": task.get("type", "unknown"),
        }
        self._pipelines.append(pipeline)
        return pipeline

    def get_pipelines(self) -> List[Dict[str, Any]]:
        return list(self._pipelines)
