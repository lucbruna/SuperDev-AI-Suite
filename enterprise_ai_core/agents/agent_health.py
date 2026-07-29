"""
Agent Health Monitor - Monitors agent health and performance
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import Agent, AgentHealth, AgentStatus


class AgentHealthMonitor:
    """Monitors health and performance of agents"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self._health: Dict[UUID, AgentHealth] = {}
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self) -> None:
        while self._running:
            await asyncio.sleep(30)
            await self._check_all_agents()

    async def _check_all_agents(self) -> None:
        for agent in self.orchestrator.agent_manager.registry.list():
            await self._check_agent(agent)

    async def _check_agent(self, agent: Agent) -> None:
        health = self._health.get(agent.id, AgentHealth(
            agent_id=agent.id,
            status=agent.status,
            health_score=agent.health_score,
        ))

        health.status = agent.status
        health.health_score = agent.health_score
        health.last_heartbeat = agent.last_heartbeat

        if agent.last_heartbeat:
            elapsed = (datetime.utcnow() - agent.last_heartbeat).total_seconds()
            if elapsed > 300:
                health.health_score = max(0.0, health.health_score - 0.2)
                health.checks["heartbeat"] = "stale"
            else:
                health.checks["heartbeat"] = "ok"

        if agent.status == AgentStatus.ERROR:
            health.health_score = 0.0
        elif agent.status == AgentStatus.RUNNING:
            health.active_tasks = 1

        self._health[agent.id] = health

    def get_health(self, agent_id: UUID) -> Optional[Dict]:
        health = self._health.get(agent_id)
        if health:
            return {
                "agent_id": str(health.agent_id),
                "status": health.status.value,
                "health_score": health.health_score,
                "active_tasks": health.active_tasks,
                "completed_tasks": health.completed_tasks,
                "failed_tasks": health.failed_tasks,
                "avg_response_time": health.avg_response_time,
                "last_error": health.last_error,
                "last_heartbeat": health.last_heartbeat.isoformat() if health.last_heartbeat else None,
                "checks": health.checks,
            }
        return None

    def get_all_health(self) -> Dict[UUID, Dict]:
        return {aid: self.get_health(aid) for aid in self._health}

    def record_task_completion(self, agent_id: UUID, success: bool, response_time: float) -> None:
        health = self._health.get(agent_id)
        if health:
            if success:
                health.completed_tasks += 1
            else:
                health.failed_tasks += 1

            total = health.completed_tasks + health.failed_tasks
            health.avg_response_time = (
                (health.avg_response_time * (total - 1) + response_time) / total
            )

    def record_error(self, agent_id: UUID, error: str) -> None:
        health = self._health.get(agent_id)
        if health:
            health.last_error = error
            health.health_score = max(0.0, health.health_score - 0.1)