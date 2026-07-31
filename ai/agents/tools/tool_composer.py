"""Tool composition for multi-tool workflows."""

from __future__ import annotations

from typing import Any


class ToolComposer:
    """Combines multiple tools into composite execution pipelines."""

    def __init__(self) -> None:
        self._pipelines: list[dict[str, Any]] = []

    def compose(self, tool_ids: list[str], task: dict[str, Any], registry: Any) -> dict[str, Any]:
        available: list[dict[str, Any]] = []
        missing: list[str] = []
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

    def get_pipelines(self) -> list[dict[str, Any]]:
        return list(self._pipelines)
