"""
Workflow Engine - Executes and manages complex multi-agent workflows
"""

import ast
import asyncio
import operator
from datetime import datetime
from typing import Any
from uuid import UUID

from enterprise_ai_core.models import (
    Event,
    EventType,
    Task,
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
    WorkflowStep,
)
from enterprise_ai_core.workflows.workflow_builder import WorkflowBuilder
from enterprise_ai_core.workflows.workflow_validator import WorkflowValidator

# Safe condition evaluation — AST allowlist instead of eval() (OWASP A03).
# Blocked: calls, attribute access, imports, collections, dangerous names.
_SAFE_CONDITION_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Not: operator.not_,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Calls and attribute access are fully blocked, so only names that would be
# dangerous if a future change enabled calls need to be blocked here.
_BLOCKED_CONDITION_NAMES = frozenset(
    {
        "__import__", "eval", "exec", "compile", "open", "getattr", "setattr",
        "delattr", "globals", "locals", "vars", "dir", "type", "super",
        "breakpoint",
    }
)


def _safe_eval_condition_node(node: ast.AST, context: dict[str, Any]) -> Any:
    """Evaluate a condition AST node against the operator allowlist."""
    if isinstance(node, ast.Expression):
        return _safe_eval_condition_node(node.body, context)
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _BLOCKED_CONDITION_NAMES:
            raise ValueError(f"access to '{node.id}' is blocked")
        if node.id in context:
            return context[node.id]
        if node.id in ("True", "False", "None"):
            return {"True": True, "False": False, "None": None}[node.id]
        raise NameError(f"name '{node.id}' is not defined")
    if isinstance(node, ast.BinOp):
        if type(node.op) not in _SAFE_CONDITION_OPS:
            raise ValueError("binary operator not allowed")
        return _SAFE_CONDITION_OPS[type(node.op)](
            _safe_eval_condition_node(node.left, context),
            _safe_eval_condition_node(node.right, context),
        )
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _SAFE_CONDITION_OPS:
            raise ValueError("unary operator not allowed")
        return _SAFE_CONDITION_OPS[type(node.op)](_safe_eval_condition_node(node.operand, context))
    if isinstance(node, ast.BoolOp):
        values = [_safe_eval_condition_node(v, context) for v in node.values]
        return all(values) if isinstance(node.op, ast.And) else any(values)
    if isinstance(node, ast.Compare):
        left = _safe_eval_condition_node(node.left, context)
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if type(op) not in _SAFE_CONDITION_OPS:
                raise ValueError("comparison not allowed")
            right = _safe_eval_condition_node(comparator, context)
            if not _SAFE_CONDITION_OPS[type(op)](left, right):
                return False
            left = right
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        # Constant-only collection literals (e.g. ``role in ['admin', 'x']``).
        # Elementos passam pelo mesmo allowlist — calls/attributes seguem bloqueados.
        return [_safe_eval_condition_node(el, context) for el in node.elts]
    if isinstance(node, ast.Dict):
        result: dict[Any, Any] = {}
        for key, value in zip(node.keys, node.values, strict=False):
            if key is None:
                raise ValueError("dict unpacking is not allowed")
            result[_safe_eval_condition_node(key, context)] = _safe_eval_condition_node(value, context)
        return result
    raise ValueError(f"expression type not allowed: {type(node).__name__}")


class WorkflowEngine:
    """Executes workflows with multiple steps and agents"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.builder = WorkflowBuilder()
        self.validator = WorkflowValidator()
        self._executions: dict[UUID, WorkflowExecution] = {}
        self._running_tasks: dict[UUID, Task] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        for execution in self._executions.values():
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.CANCELLED

    async def execute(
        self,
        workflow: Workflow,
        variables: dict | None = None,
        security_context: dict | None = None,
    ) -> WorkflowExecution:
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            variables=variables or {},
            status=WorkflowStatus.RUNNING,
        )

        self._executions[execution.execution_id] = execution

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()

        await self.orchestrator.publish_event(
            Event(
                type=EventType.WORKFLOW_STARTED,
                source_id=workflow.id,
                source_type="workflow",
                payload={"name": workflow.name, "execution_id": str(execution.execution_id)},
            )
        )

        try:
            await self._execute_steps(workflow, execution, security_context)

            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()

            await self.orchestrator.publish_event(
                Event(
                    type=EventType.WORKFLOW_COMPLETED,
                    source_id=workflow.id,
                    source_type="workflow",
                    payload={"name": workflow.name, "execution_id": str(execution.execution_id)},
                )
            )

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()

            await self.orchestrator.publish_event(
                Event(
                    type=EventType.WORKFLOW_FAILED,
                    source_id=workflow.id,
                    source_type="workflow",
                    payload={"name": workflow.name, "error": str(e)},
                    severity="error",
                )
            )
            raise

        return execution

    async def _execute_steps(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        security_context: dict | None,
    ) -> None:
        steps = workflow.steps

        while execution.current_step < len(steps):
            step_data = steps[execution.current_step]
            step = WorkflowStep(**step_data) if isinstance(step_data, dict) else step_data

            if step.condition and not self._evaluate_condition(step.condition, execution.variables):
                execution.current_step += 1
                continue

            if step.depends_on and not self._check_dependencies(step.depends_on, execution):
                break

            if step.parallel:
                await self._execute_parallel_step(workflow, execution, step, security_context)
            else:
                await self._execute_sequential_step(workflow, execution, step, security_context)

            execution.current_step += 1

    async def _execute_sequential_step(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        security_context: dict | None,
    ) -> None:
        if step.type == "task":
            await self._execute_task_step(workflow, execution, step, security_context)
        elif step.type == "decision":
            await self._execute_decision_step(workflow, execution, step, security_context)
        elif step.type == "approval":
            await self._execute_approval_step(workflow, execution, step, security_context)

    async def _execute_parallel_step(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        security_context: dict | None,
    ) -> None:
        sub_steps = [s for s in workflow.steps if s.get("parallel_group") == step.name]
        tasks = [
            self._execute_task_step(workflow, execution, WorkflowStep(**s), security_context)
            for s in sub_steps
        ]
        await asyncio.gather(*tasks)

    async def _execute_task_step(
        self,
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        _security_context: dict | None,
    ) -> None:
        input_data = self._map_inputs(step.input_mapping, execution.variables)

        task = await self.orchestrator.task_manager.create_task(
            name=step.name,
            payload=input_data,
            workflow_id=workflow.id,
            timeout_seconds=step.timeout_seconds,
        )

        self._running_tasks[task.id] = task

        agents = await self.orchestrator.agent_manager.select_agents(
            {"required_capabilities": step.config.get("required_capabilities", [])},
            execution.variables,
        )

        if agents:
            agent = agents[0]
            task.assigned_agent_id = agent.id
            result = await self.orchestrator.agent_manager.execute_agent(agent, task, execution.variables)
            execution.step_results[step.name] = result
            self._map_outputs(step.output_mapping, result, execution.variables)

        self._running_tasks.pop(task.id, None)

    async def _execute_decision_step(
        self,
        _workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        _security_context: dict | None,
    ) -> None:
        decision = await self.orchestrator.decision_manager.make_decision(
            context=execution.variables,
            options=step.config.get("options", []),
            criteria=step.config.get("criteria", {}),
        )
        execution.step_results[step.name] = decision
        execution.variables[f"{step.name}_decision"] = decision

    async def _execute_approval_step(
        self,
        _workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        _security_context: dict | None,
    ) -> None:
        execution.variables[f"{step.name}_awaiting_approval"] = True

        while execution.variables.get(f"{step.name}_awaiting_approval"):
            await asyncio.sleep(5)

        approval = execution.variables.get(f"{step.name}_approval", {})
        execution.step_results[step.name] = approval

        if not approval.get("approved", False):
            raise Exception(f"Approval denied for step: {step.name}")

    def _evaluate_condition(self, condition: str, variables: dict) -> bool:
        try:
            tree = ast.parse(condition, mode="eval")
            return bool(_safe_eval_condition_node(tree, variables))
        except Exception:
            return False

    def _check_dependencies(self, dependencies: list[UUID], execution: WorkflowExecution) -> bool:
        for dep_id in dependencies:
            dep_step = next((s for s in execution.step_results if s.get("id") == dep_id), None)
            if not dep_step:
                return False
        return True

    def _map_inputs(self, mapping: dict[str, str], variables: dict) -> dict:
        return {k: variables.get(v) for k, v in mapping.items() if v in variables}

    def _map_outputs(self, mapping: dict[str, str], result: dict, variables: dict) -> None:
        for var_name, result_path in mapping.items():
            value = result
            for key in result_path.split("."):
                value = value.get(key) if isinstance(value, dict) else None
                if value is None:
                    break
            if value is not None:
                variables[var_name] = value

    def get_execution(self, execution_id: UUID) -> WorkflowExecution | None:
        return self._executions.get(execution_id)

    def get_workflow_executions(self, workflow_id: UUID) -> list[WorkflowExecution]:
        return [e for e in self._executions.values() if e.workflow_id == workflow_id]

    def pause_execution(self, execution_id: UUID) -> bool:
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.PAUSED
            return True
        return False

    def resume_execution(self, execution_id: UUID) -> bool:
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.PAUSED:
            execution.status = WorkflowStatus.RUNNING
            return True
        return False

    def cancel_execution(self, execution_id: UUID) -> bool:
        execution = self._executions.get(execution_id)
        if execution and execution.status in (WorkflowStatus.RUNNING, WorkflowStatus.PAUSED):
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            return True
        return False
