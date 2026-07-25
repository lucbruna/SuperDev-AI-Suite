from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import BaseModel, Field

from ..planner.execution_plan import ExecutionPlan
from ..planner.planner import Step


class ExecutionResult(BaseModel):
    success: bool = True
    step_results: list[dict[str, Any]] = Field(default_factory=list)
    error: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)


class Executor:
    def __init__(self) -> None:
        self._executors: dict[str, Any] = {}

    def register_agent_executor(self, agent_name: str, executor: Any) -> None:
        self._executors[agent_name] = executor

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        context: dict[str, Any],
    ) -> ExecutionResult:
        if not plan.validate():
            return ExecutionResult(success=False, error="Invalid execution plan")

        start = time.time()
        step_results = []
        failed = False

        while not plan.is_complete() and not failed:
            next_steps = plan.get_next_steps()
            if not next_steps:
                break

            tasks = [self._execute_step(step, context) for step in next_steps]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, result in zip(next_steps, results, strict=False):
                if isinstance(result, Exception):
                    plan.mark_failed(step.id)
                    step_results.append({
                        "step_id": step.id,
                        "description": step.description,
                        "success": False,
                        "error": str(result),
                    })
                    failed = True
                elif not result.get("success", False):
                    plan.mark_failed(step.id)
                    step_results.append(result)
                    failed = True
                else:
                    plan.mark_complete(step.id)
                    step_results.append(result)

        execution_time = time.time() - start
        return ExecutionResult(
            success=not failed and plan.is_complete(),
            step_results=step_results,
            error="" if not failed else "Plan execution failed",
            metrics={
                "execution_time": execution_time,
                "total_steps": len(step_results),
                "completed": plan.progress()["completed"],
            },
        )

    async def _execute_step(self, step: Step, context: dict[str, Any]) -> dict[str, Any]:
        agent_executor = self._executors.get(step.assigned_agent)
        if agent_executor is None:
            return {
                "step_id": step.id,
                "description": step.description,
                "success": False,
                "error": f"No executor for agent '{step.assigned_agent}'",
            }
        try:
            result = await agent_executor(step.description, context)
            return {
                "step_id": step.id,
                "description": step.description,
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }
        except Exception as e:
            return {
                "step_id": step.id,
                "description": step.description,
                "success": False,
                "error": str(e),
            }
