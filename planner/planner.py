from __future__ import annotations

from .planner_builder import PlannerBuilder
from .planner_context import PlannerContext
from .planner_executor import PlannerExecutor
from .planner_manager import PlannerManager
from .planner_models import Plan, PlannerConfig
from .planner_service import PlannerService


class Planner:
    """Main planner orchestrator for AI task planning."""

    def __init__(self, config: PlannerConfig | None = None):
        self.config = config or PlannerConfig()
        self.service = PlannerService()
        self.manager = PlannerManager()
        self.builder = PlannerBuilder()
        self.executor = PlannerExecutor()
        self.context = PlannerContext()

    async def create_plan(self, goal: str, **kwargs) -> Plan:
        """Create a plan to achieve a goal."""
        context = self.context.create(goal=goal, **kwargs)
        plan = await self.builder.build(context)
        self.manager.register_plan(plan)
        return plan

    async def execute_plan(self, plan_id: str) -> dict:
        """Execute a plan by ID."""
        plan = self.manager.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found")
        return await self.executor.execute(plan)

    async def optimize_plan(self, plan_id: str) -> Plan:
        """Optimize an existing plan."""
        plan = self.manager.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found")
        from .planner_optimizer import PlannerOptimizer
        optimizer = PlannerOptimizer()
        return optimizer.optimize(plan)

    def get_plan(self, plan_id: str):
        return self.manager.get_plan(plan_id)

    def list_plans(self):
        return self.manager.list_plans()
