from __future__ import annotations

import asyncio
import contextlib
import os
import time
from datetime import UTC, datetime
from typing import Any

from ..manager.agent_manager import AgentManager
from ..registry.agent_registry import AgentRegistry
from .hub import OrchestrationHub
from .planner import OrchestrationPlanner
from .routing import RoutingEngine
from .state import OrchestrationState


class OrchestratorEngine:
    """Central orchestrator for the multi-agent system.

    Coordinates task planning, agent routing, execution, health monitoring,
    state persistence, and real-time communication across all 17+ agents.
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        agent_manager: AgentManager | None = None,
        hub: OrchestrationHub | None = None,
        planner: OrchestrationPlanner | None = None,
        router: RoutingEngine | None = None,
        state: OrchestrationState | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.agent_manager = agent_manager or AgentManager(registry=self.registry)
        self.hub = hub or OrchestrationHub()
        self.planner = planner or OrchestrationPlanner()
        self.router = router or RoutingEngine()
        self.state = state or OrchestrationState()

        self._running: bool = False
        self._health_interval: float = 30.0
        self._health_task: asyncio.Task[None] | None = None
        self._metrics: dict[str, Any] = {
            "total_tasks_dispatched": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "total_fallbacks": 0,
            "execution_times": [],
        }

    async def start(self) -> None:
        """Start the orchestrator engine."""
        self._running = True
        # Discover agents from the ai/agents package
        agents_init = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "agents",
            "__init__.py",
        )
        self.registry.discover(agents_init)
        # Start health checker
        self._health_task = asyncio.create_task(self._health_loop())
        await self.hub._bus.publish(
            "orchestrator.started",
            {
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def stop(self) -> None:
        """Stop the orchestrator engine."""
        self._running = False
        if self._health_task:
            self._health_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_task
        await self.hub._bus.publish(
            "orchestrator.stopped",
            {
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def create_orchestration(
        self,
        project_id: str = "",
        name: str = "",
        strategy: str = "pipeline",
    ) -> dict[str, Any]:
        """Create a new orchestration session with planning."""
        session = await self.state.create_session(
            project_id=project_id,
            name=name,
            strategy=strategy,
        )
        hub_session_id = await self.hub.create_session(project_id)
        await self.state.update_session(
            session.session_id,
            context={"hub_session_id": hub_session_id},
        )

        for agent_info in self.agent_manager.list_agents():
            agent_id = agent_info["agent_id"]
            await self.state.assign_agent(
                session.session_id,
                agent_id=agent_id,
                agent_name=agent_info.get("name", agent_id),
            )

        return {
            "session_id": session.session_id,
            "project_id": session.project_id,
            "name": session.name,
            "strategy": session.strategy,
            "status": session.status,
            "agents": len(session.agents),
            "created_at": session.created_at,
        }

    async def run_pipeline(
        self,
        session_id: str,
        tasks: list[dict[str, Any]] | None = None,
        strategy: str = "pipeline",
    ) -> dict[str, Any]:
        """Execute a full orchestration pipeline."""
        session = await self.state.get_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        await self.state.update_session(session_id, status="running")
        start_time = time.time()

        available_agents = [{"id": aid, "role": a.role, "name": a.agent_name} for aid, a in session.agents.items()]

        if tasks is None:
            tasks = await self.planner.plan(
                project={"id": session.project_id, "name": session.name},
                agents=available_agents,
                strategy=strategy,
            )

        optimized = await self.planner.optimize_assignments(tasks, available_agents)

        task_ids = []
        for task in optimized:
            ts = await self.state.add_task(
                session_id,
                description=task.get("description", ""),
                agent_id=task.get("agent_id", ""),
                agent_name=task.get("agent_role", ""),
                task_type=task.get("stage", ""),
                depends_on=task.get("depends_on"),
            )
            if ts:
                task_ids.append(ts.task_id)

        results = []
        failed = False

        while True:
            ready_tasks = []
            for task_state in session.tasks:
                if task_state.status != "pending":
                    continue
                deps_met = all(
                    any(t.task_id == dep_id and t.status == "completed" for t in session.tasks)
                    for dep_id in task_state.depends_on
                )
                if deps_met:
                    ready_tasks.append(task_state)

            if not ready_tasks:
                break

            if failed:
                ready_tasks = [
                    t
                    for t in ready_tasks
                    if not any(
                        any(td.task_id == dep_id and td.status == "failed" for td in session.tasks)
                        for dep_id in t.depends_on
                    )
                ]
                if not ready_tasks:
                    break

            batch_results = await asyncio.gather(
                *[self._execute_task(session_id, t) for t in ready_tasks],
                return_exceptions=True,
            )

            for task_state, result in zip(ready_tasks, batch_results, strict=False):
                if isinstance(result, Exception):
                    await self.state.update_task(
                        session_id,
                        task_state.task_id,
                        status="failed",
                        error=str(result),
                    )
                    self._metrics["total_tasks_failed"] += 1
                    failed = True
                    results.append(
                        {
                            "task_id": task_state.task_id,
                            "description": task_state.description,
                            "success": False,
                            "error": str(result),
                        }
                    )
                else:
                    results.append(result)
                    if not result.get("success", False):
                        failed = True

            session = await self.state.get_session(session_id)
            if not session:
                break

        elapsed = time.time() - start_time
        all_completed = all(t.status == "completed" for t in session.tasks)
        any_failed = any(t.status == "failed" for t in session.tasks)

        if all_completed:
            await self.state.complete_session(session_id)
        elif any_failed:
            await self.state.fail_session(session_id, error="One or more tasks failed")
        else:
            await self.state.update_session(session_id, status="paused")

        self._metrics["execution_times"].append(elapsed)
        if len(self._metrics["execution_times"]) > 100:
            self._metrics["execution_times"] = self._metrics["execution_times"][-100:]

        return {
            "success": all_completed,
            "session_id": session_id,
            "total_tasks": len(session.tasks),
            "completed": sum(1 for t in session.tasks if t.status == "completed"),
            "failed": sum(1 for t in session.tasks if t.status == "failed"),
            "results": results,
            "execution_time_seconds": round(elapsed, 2),
            "strategy": strategy,
        }

    async def _execute_task(
        self,
        session_id: str,
        task_state: Any,
    ) -> dict[str, Any]:
        """Execute a single task with routing and retry logic."""
        await self.state.update_task(session_id, task_state.task_id, status="running")

        try:
            route = await self.router.route(
                task=task_state.description,
                task_type=task_state.task_type,
                preferred_agent=task_state.agent_id if task_state.agent_id else None,
                require_fallback=True,
            )
        except RuntimeError:
            await self.state.update_task(
                session_id,
                task_state.task_id,
                status="failed",
                error="No agent available",
            )
            return {
                "task_id": task_state.task_id,
                "description": task_state.description,
                "success": False,
                "error": "No agent available for routing",
            }

        if route.fallback_used:
            self._metrics["total_fallbacks"] += 1

        agent = self.agent_manager._instances.get(route.agent_id)
        if not agent:
            await self.state.update_task(
                session_id,
                task_state.task_id,
                status="failed",
                error=f"Agent {route.agent_id} not found",
            )
            return {
                "task_id": task_state.task_id,
                "description": task_state.description,
                "success": False,
                "error": f"Agent instance '{route.agent_id}' not found",
            }

        last_error = ""
        for attempt in range(task_state.max_retries + 1):
            try:
                result = await agent.execute(
                    task_state.description,
                    context={"session_id": session_id, "attempt": attempt},
                )

                if result.success:
                    await self.router.complete_task(route.agent_id)
                    await self.state.update_task(
                        session_id,
                        task_state.task_id,
                        status="completed",
                        agent_id=route.agent_id,
                        agent_name=route.agent_name,
                        result=result.model_dump(),
                        retry_count=attempt,
                    )
                    self._metrics["total_tasks_completed"] += 1
                    return {
                        "task_id": task_state.task_id,
                        "description": task_state.description,
                        "success": True,
                        "agent_id": route.agent_id,
                        "agent_name": route.agent_name,
                        "output": result.output,
                        "retry_count": attempt,
                        "execution_time_ms": result.metrics.get("execution_time_ms", 0),
                    }
                else:
                    last_error = result.error
                    if attempt < task_state.max_retries:
                        await asyncio.sleep(2**attempt)
                        continue
            except Exception as e:
                last_error = str(e)
                if attempt < task_state.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue
                break

        await self.router.complete_task(route.agent_id)
        await self.state.update_task(
            session_id,
            task_state.task_id,
            status="failed",
            error=last_error,
            retry_count=task_state.max_retries,
        )
        self._metrics["total_tasks_failed"] += 1
        return {
            "task_id": task_state.task_id,
            "description": task_state.description,
            "success": False,
            "error": last_error,
            "agent_id": route.agent_id,
            "retry_count": task_state.max_retries,
        }

    async def _health_loop(self) -> None:
        """Background health check loop for all agents."""
        while self._running:
            try:
                await asyncio.sleep(self._health_interval)
                for agent_info in self.agent_manager.list_agents():
                    agent_id = agent_info["agent_id"]
                    status = self.agent_manager.get_agent_status(agent_id)
                    health = status.get("health", {})
                    if health.get("error_count", 0) > 5:
                        await self.agent_manager.stop_agent(agent_id)
                        await asyncio.sleep(1)
                        await self.agent_manager.start_agent(agent_id)
                        await self.hub._bus.publish(
                            "orchestrator.agent_restarted",
                            {"agent_id": agent_id, "reason": "too many errors"},
                        )
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def orchestrate_with_prompt(
        self,
        prompt: str,
        project_id: str = "",
        strategy: str = "pipeline",
    ) -> dict[str, Any]:
        """Full orchestration from a natural language prompt."""
        orch = await self.create_orchestration(
            project_id=project_id,
            name=f"Orchestration: {prompt[:50]}",
            strategy=strategy,
        )
        agents_list = [
            {"id": aid, "role": a.role, "name": a.agent_name}
            for aid, a in (await self.state.get_session(orch["session_id"])).agents.items()
        ]
        project = {
            "id": project_id,
            "name": prompt[:100],
            "description": prompt,
            "modules": self._extract_modules(prompt),
            "steps": self._extract_steps(prompt),
        }
        tasks = await self.planner.plan(project, agents_list, strategy)
        result = await self.run_pipeline(orch["session_id"], tasks, strategy)
        return result

    def _extract_modules(self, prompt: str) -> list[str]:
        """Extract module names from a prompt."""
        known_modules = [
            "backend",
            "frontend",
            "mobile",
            "desktop",
            "api",
            "database",
            "auth",
            "cli",
            "docker",
            "kubernetes",
            "infra",
            "config",
            "docs",
            "tests",
        ]
        prompt_lower = prompt.lower()
        return [m for m in known_modules if m in prompt_lower] or ["backend"]

    def _extract_steps(self, prompt: str) -> list[str]:
        """Extract pipeline steps from a prompt."""
        prompt_lower = prompt.lower()
        if "test" in prompt_lower:
            return ["analyze", "design", "implement", "review", "test", "deploy"]
        elif "review" in prompt_lower:
            return ["analyze", "review", "report"]
        elif "deploy" in prompt_lower:
            return ["build", "test", "deploy", "monitor"]
        return ["analyze", "design", "implement", "review", "test", "deploy"]

    def get_metrics(self) -> dict[str, Any]:
        """Get orchestrator performance metrics."""
        times = self._metrics["execution_times"]
        return {
            **self._metrics,
            "avg_execution_time": round(sum(times) / len(times), 2) if times else 0,
            "min_execution_time": round(min(times), 2) if times else 0,
            "max_execution_time": round(max(times), 2) if times else 0,
            "routing_stats": self.router.get_statistics(),
            "session_stats": self.state.get_statistics(),
        }

    async def get_agents_status(self) -> list[dict[str, Any]]:
        """Get status of all registered agents."""
        agents = self.agent_manager.list_agents()
        return [
            {
                **a,
                "health": self.agent_manager.get_agent_status(a["agent_id"]).get("health", {}),
                "load": self.router.get_agent_load(a["agent_id"]),
            }
            for a in agents
        ]
