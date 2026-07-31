from __future__ import annotations

from typing import Any

from ..base.base_agent import AgentResult, BaseAgent
from ..planner.planner import Planner


class PlannerAgent(BaseAgent):
    async def initialize(self) -> None:
        self._planner = Planner()
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"
            steps = await self._planner.plan(task, context)

            plan_output = "\n".join(f"[{s.id[:8]}] {s.description} (agent: {s.assigned_agent})" for s in steps)

            return AgentResult(
                success=True,
                output=plan_output,
                metrics={"step_count": len(steps)},
                artifacts={"steps": [s.model_dump() for s in steps]},
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def capabilities(self) -> list[str]:
        return ["planning", "task_decomposition", "goal_analysis"]
