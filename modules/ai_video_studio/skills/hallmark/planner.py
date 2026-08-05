"""Hallmark planner — decompose a goal into ordered steps."""
from __future__ import annotations
from typing import Any


class TaskPlanner:
    """Break a goal into a numbered plan with dependencies."""

    def __init__(self) -> None:
        pass

    def plan(self, goal: str, steps: int = 3) -> dict[str, Any]:
        """Return a plan of ``steps`` sequential actions toward ``goal``."""
        plan = [
            {
                "step": index,
                "action": f"Prepare step {index} of {goal}.",
                "depends_on": [index - 1] if index > 1 else [],
            }
            for index in range(1, steps + 1)
        ]
        return {
            "goal": goal,
            "step_count": steps,
            "plan": plan,
            "strategy": "sequential, each step unblocks the next",
        }
