from __future__ import annotations

import asyncio
import time
from typing import Any

from backend.runtime.base_runtime import Language, ResourceLimits, RuntimeConfig
from backend.runtime.runtime_manager import runtime_manager
from backend.websocket.events import EventBuilder
from backend.websocket.manager import manager
from backend.workflow.base_workflow import (
    StepConfig,
    StepResult,
    StepStatus,
    StepType,
    WorkflowDefinition,
    WorkflowStatus,
)


class WorkflowExecutor:
    """Executes workflow definitions step by step."""

    def __init__(self):
        self._running: dict[str, asyncio.Task] = {}

    async def execute(
        self,
        definition: WorkflowDefinition,
        run_id: str,
        variables: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        errors = definition.validate()
        if errors:
            return {
                "run_id": run_id,
                "status": WorkflowStatus.FAILED.value,
                "error": f"Validation errors: {'; '.join(errors)}",
                "steps": {},
            }

        context = {**definition.variables, **(variables or {})}
        step_results: dict[str, StepResult] = {}
        start_time = time.time()

        event = EventBuilder.workflow_start(definition.id, run_id)
        event.user_id = user_id
        await manager.broadcast_all(event.to_dict())

        completed_steps = set()

        while len(completed_steps) < len(definition.steps):
            ready_steps = [
                s for s in definition.steps
                if s.id not in completed_steps
                and all(dep in completed_steps for dep in s.depends_on)
            ]

            if not ready_steps:
                break

            for step in ready_steps:
                step_event = EventBuilder.workflow_step(
                    definition.id, step.id, "running"
                )
                step_event.user_id = user_id
                await manager.broadcast_all(step_event.to_dict())

                result = await self._execute_step(step, context, step_results)
                step_results[step.id] = result
                completed_steps.add(step.id)

                if result.output is not None:
                    context[f"step_{step.id}_output"] = result.output

                step_status = "completed" if result.status == StepStatus.COMPLETED else "failed"
                step_event = EventBuilder.workflow_step(
                    definition.id, step.id, step_status
                )
                step_event.user_id = user_id
                await manager.broadcast_all(step_event.to_dict())

                if result.status == StepStatus.FAILED and not step.continue_on_error:
                    total_time = (time.time() - start_time) * 1000
                    return {
                        "run_id": run_id,
                        "status": WorkflowStatus.FAILED.value,
                        "error": f"Step '{step.id}' failed: {result.error}",
                        "steps": {k: {"status": v.status.value, "output": v.output, "error": v.error} for k, v in step_results.items()},
                        "execution_time_ms": total_time,
                    }

        total_time = (time.time() - start_time) * 1000
        all_completed = all(r.status == StepStatus.COMPLETED for r in step_results.values())

        return {
            "run_id": run_id,
            "status": WorkflowStatus.COMPLETED.value if all_completed else WorkflowStatus.FAILED.value,
            "steps": {k: {"status": v.status.value, "output": v.output, "error": v.error} for k, v in step_results.items()},
            "context": context,
            "execution_time_ms": total_time,
        }

    async def _execute_step(
        self,
        step: StepConfig,
        context: dict[str, Any],
        previous_results: dict[str, StepResult],
    ) -> StepResult:
        start_time = time.time()

        for attempt in range(step.max_retries + 1):
            try:
                if step.step_type == StepType.CODE:
                    result = await self._execute_code_step(step, context)
                elif step.step_type == StepType.CONDITION:
                    result = await self._execute_condition_step(step, context)
                elif step.step_type == StepType.TRANSFORM:
                    result = await self._execute_transform_step(step, context)
                elif step.step_type == StepType.WAIT:
                    result = await self._execute_wait_step(step)
                else:
                    result = StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        error=f"Unsupported step type: {step.step_type}",
                    )

                if result.status == StepStatus.COMPLETED:
                    result.attempts = attempt + 1
                    result.execution_time_ms = (time.time() - start_time) * 1000
                    return result

                if attempt < step.max_retries:
                    await asyncio.sleep(min(2 ** attempt, 30))

            except Exception as e:
                if attempt < step.max_retries:
                    await asyncio.sleep(min(2 ** attempt, 30))
                else:
                    return StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        error=str(e),
                        attempts=attempt + 1,
                        execution_time_ms=(time.time() - start_time) * 1000,
                    )

        return StepResult(
            step_id=step.id,
            status=StepStatus.FAILED,
            error="Max retries exceeded",
            attempts=step.max_retries + 1,
            execution_time_ms=(time.time() - start_time) * 1000,
        )

    async def _execute_code_step(
        self,
        step: StepConfig,
        context: dict[str, Any],
    ) -> StepResult:
        code = step.config.get("code", "")
        language = step.config.get("language", "python")

        try:
            lang = Language(language)
        except ValueError:
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                error=f"Unsupported language: {language}",
            )

        config = RuntimeConfig(
            language=lang,
            code=code,
            resource_limits=ResourceLimits(
                max_execution_time_seconds=step.timeout_seconds,
            ),
        )

        from backend.utils.uuid_utils import generate_uuid
        run_id = generate_uuid()
        result = await runtime_manager.execute(config, run_id)

        return StepResult(
            step_id=step.id,
            status=StepStatus.COMPLETED if result.status.value == "completed" else StepStatus.FAILED,
            output=result.stdout,
            error=result.error or result.stderr,
        )

    async def _execute_condition_step(
        self,
        step: StepConfig,
        context: dict[str, Any],
    ) -> StepResult:
        condition = step.config.get("condition", "True")
        try:
            result = eval(condition, {"__builtins__": {}}, context)
            return StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                output={"condition": condition, "result": bool(result)},
            )
        except Exception as e:
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                error=f"Condition evaluation failed: {e}",
            )

    async def _execute_transform_step(
        self,
        step: StepConfig,
        context: dict[str, Any],
    ) -> StepResult:
        transform_type = step.config.get("transform_type", "extract")
        source_key = step.config.get("source_key", "")

        try:
            if transform_type == "extract":
                output = context.get(source_key)
            elif transform_type == "merge":
                keys = step.config.get("keys", [])
                output = {k: context.get(k) for k in keys}
            elif transform_type == "template":
                template = step.config.get("template", "")
                output = template.format(**context)
            else:
                output = context.get(source_key)

            return StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                output=output,
            )
        except Exception as e:
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                error=str(e),
            )

    async def _execute_wait_step(self, step: StepConfig) -> StepResult:
        duration = step.config.get("duration_seconds", 1)
        await asyncio.sleep(min(duration, 300))
        return StepResult(
            step_id=step.id,
            status=StepStatus.COMPLETED,
            output={"waited_seconds": duration},
        )

    async def cancel(self, run_id: str) -> bool:
        task = self._running.get(run_id)
        if task and not task.done():
            task.cancel()
            return True
        return False


workflow_executor = WorkflowExecutor()
