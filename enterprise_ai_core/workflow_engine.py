"""
Workflow Engine - Executes and manages complex multi-agent workflows
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from enterprise_ai_core.models import (
    Workflow,
    WorkflowExecution,
    WorkflowStatus,
    WorkflowStep,
    Task,
    TaskStatus,
    Event,
    EventType,
    AgentType,
)
from enterprise_ai_core.workflows.workflow_builder import WorkflowBuilder
from enterprise_ai_core.workflows.workflow_validator import WorkflowValidator


class WorkflowEngine:
    """Executes workflows with multiple steps and agents"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.builder = WorkflowBuilder()
        self.validator = WorkflowValidator()
        self._executions: Dict[UUID, WorkflowExecution] = {}
        self._running_tasks: Dict[UUID, Task] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        for execution in self._executions.values():
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.CANCELLED

    async def execute(
        self,
        workflow: Workflow,
        variables: Optional[Dict] = None,
        security_context: Optional[Dict] = None,
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
        security_context: Optional[Dict],
    ) -> None:
        steps = workflow.steps

        while execution.current_step < len(steps):
            step_data = steps[execution.current_step]
            step = WorkflowStep(**step_data) if isinstance(step_data, dict) else step_data

            if step.condition and not self._evaluate_condition(step.condition, execution.variables):
                execution.current_step += 1
                continue

            if step.depends_on:
                if not self._check_dependencies(step.depends_on, execution):
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
        security_context: Optional[Dict],
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
        security_context: Optional[Dict],
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
        security_context: Optional[Dict],
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
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        security_context: Optional[Dict],
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
        workflow: Workflow,
        execution: WorkflowExecution,
        step: WorkflowStep,
        security_context: Optional[Dict],
    ) -> None:
        execution.variables[f"{step.name}_awaiting_approval"] = True

        while execution.variables.get(f"{step.name}_awaiting_approval"):
            await asyncio.sleep(5)

        approval = execution.variables.get(f"{step.name}_approval", {})
        execution.step_results[step.name] = approval

        if not approval.get("approved", False):
            raise Exception(f"Approval denied for step: {step.name}")

    def _evaluate_condition(self, condition: str, variables: Dict) -> bool:
        try:
            return eval(condition, {"__builtins__": {}}, variables)
        except Exception:
            return False

    def _check_dependencies(self, dependencies: List[UUID], execution: WorkflowExecution) -> bool:
        for dep_id in dependencies:
            dep_step = next((s for s in execution.step_results if s.get("id") == dep_id), None)
            if not dep_step:
                return False
        return True

    def _map_inputs(self, mapping: Dict[str, str], variables: Dict) -> Dict:
        return {k: variables.get(v) for k, v in mapping.items() if v in variables}

    def _map_outputs(self, mapping: Dict[str, str], result: Dict, variables: Dict) -> None:
        for var_name, result_path in mapping.items():
            value = result
            for key in result_path.split("."):
                value = value.get(key) if isinstance(value, dict) else None
                if value is None:
                    break
            if value is not None:
                variables[var_name] = value

    def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        return self._executions.get(execution_id)

    def get_workflow_executions(self, workflow_id: UUID) -> List[WorkflowExecution]:
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