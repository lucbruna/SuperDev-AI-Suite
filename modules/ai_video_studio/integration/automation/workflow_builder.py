"""Workflow Builder — produces suite-compatible workflow definitions."""
from __future__ import annotations

from typing import Any


class WorkflowBuilder:
    """Builds JSON workflow definitions from action steps."""

    def build(self, name: str = "video_pipeline", steps: list[str] | None = None) -> dict[str, Any]:
        steps = [s for s in (steps or ["plan", "generate", "render", "export"]) if s]
        return {
            "type": "workflow",
            "name": name,
            "version": "1.0",
            "steps": [
                {"id": f"step_{i}", "action": step, "order": i}
                for i, step in enumerate(steps)
            ],
            "step_count": len(steps),
        }


_workflow_builder: WorkflowBuilder | None = None


def get_workflow_builder() -> WorkflowBuilder:
    global _workflow_builder
    if _workflow_builder is None:
        _workflow_builder = WorkflowBuilder()
    return _workflow_builder
