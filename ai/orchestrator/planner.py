from __future__ import annotations

from typing import Any


class OrchestrationPlanner:
    def __init__(self):
        self._strategies = {
            "parallel": self._plan_parallel,
            "sequential": self._plan_sequential,
            "pipeline": self._plan_pipeline,
        }

    async def plan(self, project: dict[str, Any], agents: list[dict[str, Any]], strategy: str = "pipeline") -> list[dict[str, Any]]:
        planner = self._strategies.get(strategy, self._plan_pipeline)
        return await planner(project, agents)

    async def _plan_pipeline(self, project: dict[str, Any], agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tasks = []
        stages = ["analyze", "design", "implement", "review", "test", "deploy"]
        for i, stage in enumerate(stages):
            agent = agents[i % len(agents)] if agents else {"id": "default", "role": "assistant"}
            tasks.append({
                "stage": stage,
                "agent_id": agent["id"],
                "agent_role": agent.get("role", "assistant"),
                "order": i,
                "description": f"Stage: {stage}",
                "depends_on": [stages[i - 1]] if i > 0 else [],
                "status": "pending",
            })
        return tasks

    async def _plan_parallel(self, project: dict[str, Any], agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tasks = []
        modules = project.get("modules", ["backend", "frontend", "infra"])
        for i, module in enumerate(modules):
            agent = agents[i % len(agents)] if agents else {"id": "default", "role": "assistant"}
            tasks.append({
                "stage": module,
                "agent_id": agent["id"],
                "agent_role": agent.get("role", "assistant"),
                "order": i,
                "description": f"Build {module}",
                "depends_on": [],
                "status": "pending",
            })
        return tasks

    async def _plan_sequential(self, project: dict[str, Any], agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tasks = []
        steps = project.get("steps", ["Step 1", "Step 2", "Step 3"])
        for i, step in enumerate(steps):
            agent = agents[i % len(agents)] if agents else {"id": "default", "role": "assistant"}
            depends = [steps[i - 1]] if i > 0 else []
            tasks.append({
                "stage": step,
                "agent_id": agent["id"],
                "agent_role": agent.get("role", "assistant"),
                "order": i,
                "description": f"Execute {step}",
                "depends_on": depends,
                "status": "pending",
            })
        return tasks

    async def optimize_assignments(self, tasks: list[dict[str, Any]], agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        agent_loads = {a["id"]: 0 for a in agents}
        for task in tasks:
            best_agent = min(agents, key=lambda a: agent_loads[a["id"]])
            task["agent_id"] = best_agent["id"]
            agent_loads[best_agent["id"]] += 1
        return tasks