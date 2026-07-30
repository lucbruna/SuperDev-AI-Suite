from __future__ import annotations

from typing import Any

from .planner_bridge import PlannerBridge
from .workflow_bridge import WorkflowBridge
from .execution_bridge import ExecutionBridge
from .dependency_analyzer import DependencyAnalyzer
from .strategy_selector import StrategySelector
from .objective_analyzer import ObjectiveAnalyzer
from .goal_optimizer import GoalOptimizer
from .plan_validator import PlanValidator


class PlannerReasoner:
    """Integrates planning and reasoning into a unified pipeline."""

    def __init__(
        self,
        planner: PlannerBridge | None = None,
        workflow: WorkflowBridge | None = None,
        execution: ExecutionBridge | None = None,
        deps: DependencyAnalyzer | None = None,
        strategy: StrategySelector | None = None,
        objective: ObjectiveAnalyzer | None = None,
        optimizer: GoalOptimizer | None = None,
        validator: PlanValidator | None = None,
    ):
        self._planner = planner or PlannerBridge()
        self._workflow = workflow or WorkflowBridge()
        self._execution = execution or ExecutionBridge()
        self._deps = deps or DependencyAnalyzer()
        self._strategy = strategy or StrategySelector()
        self._objective = objective or ObjectiveAnalyzer()
        self._optimizer = optimizer or GoalOptimizer()
        self._validator = validator or PlanValidator()

    async def reason_and_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        objectives = await self._objective.analyze(context)
        strategy = await self._strategy.select(objectives)
        deps = await self._deps.analyze(context)
        plan = await self._planner.create_plan(context, strategy)
        optimized = await self._optimizer.optimize(plan, objectives)
        validated = await self._validator.validate(optimized)
        if not validated.get("valid", False):
            return {"success": False, "errors": validated.get("errors", [])}
        workflow = await self._workflow.create_workflow(optimized)
        execution = await self._execution.prepare(workflow, deps)
        return {
            "success": True,
            "plan": optimized,
            "workflow": workflow,
            "execution": execution,
            "validation": validated,
        }
