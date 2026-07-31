"""Central planning engine for goal decomposition and task management."""
from __future__ import annotations

import time
import uuid
from typing import Any

from .goal_manager import GoalManager
from .optimization import PlanningOptimizer
from .replanning import Replanner
from .scheduling import Scheduler
from .strategy import StrategyEngine
from .task_decomposition import TaskDecomposer


class PlanningEngine:
    """Central planning engine coordinating goal management, task decomposition,
    strategy selection, scheduling, and adaptive replanning."""

    def __init__(self) -> None:
        self._goal_manager = GoalManager()
        self._decomposer = TaskDecomposer()
        self._strategy = StrategyEngine()
        self._scheduler = Scheduler()
        self._optimizer = PlanningOptimizer()
        self._replanner = Replanner()
        self._plans: dict[str, dict[str, Any]] = {}
        self._plan_count: int = 0

    @property
    def goal_manager(self) -> GoalManager:
        return self._goal_manager

    @property
    def decomposer(self) -> TaskDecomposer:
        return self._decomposer

    @property
    def strategy(self) -> StrategyEngine:
        return self._strategy

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    def create_plan(self, goal: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        self._goal_manager.add_goal(goal, context)
        tasks = self._decomposer.decompose(goal, context)
        strategy = self._strategy.select_strategy(goal, tasks)
        scheduled = self._scheduler.schedule(tasks)
        plan = {
            "plan_id": plan_id,
            "goal": goal,
            "context": context or {},
            "tasks": tasks,
            "strategy": strategy,
            "schedule": scheduled,
            "status": "created",
            "created_at": time.time(),
            "task_count": len(tasks),
        }
        self._plans[plan_id] = plan
        self._plan_count += 1
        return plan

    def execute_plan(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"error": f"Plan {plan_id} not found"}
        plan["status"] = "executing"
        plan["started_at"] = time.time()
        return {"plan_id": plan_id, "status": "executing", "tasks": plan["tasks"]}

    def complete_task(self, plan_id: str, task_id: str,
                      result: dict[str, Any] | None = None) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"error": "Plan not found"}
        for task in plan["tasks"]:
            if task.get("task_id") == task_id:
                task["status"] = "completed"
                task["result"] = result
                break
        completed = sum(1 for t in plan["tasks"] if t.get("status") == "completed")
        total = len(plan["tasks"])
        if completed == total:
            plan["status"] = "completed"
            plan["completed_at"] = time.time()
        return {"plan_id": plan_id, "completed": completed, "total": total}

    def replan(self, plan_id: str, reason: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"error": "Plan not found"}
        new_tasks = self._replanner.replan(plan, reason)
        plan["tasks"] = new_tasks
        plan["status"] = "replanned"
        plan["replan_reason"] = reason
        return {"plan_id": plan_id, "new_task_count": len(new_tasks)}

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        return self._plans.get(plan_id)

    def list_plans(self) -> list[dict[str, Any]]:
        return [
            {"plan_id": p["plan_id"], "goal": p["goal"], "status": p["status"]}
            for p in self._plans.values()
        ]

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_plans": self._plan_count,
            "active_plans": len(self._plans),
            "goals": self._goal_manager.snapshot(),
        }
