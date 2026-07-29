"""
Agent Manager - Manages AI agent lifecycle, registration, and execution
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import (
    Agent,
    AgentStatus,
    AgentType,
    Event,
    EventType,
    Task,
    TaskStatus,
)
from enterprise_ai_core.agents.agent_registry import AgentRegistry
from enterprise_ai_core.agents.agent_executor import AgentExecutor
from enterprise_ai_core.agents.agent_health import AgentHealthMonitor


class AgentManager:
    """Manages agent lifecycle, selection, and execution"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.registry = AgentRegistry()
        self.executor = AgentExecutor(orchestrator)
        self.health_monitor = AgentHealthMonitor(orchestrator)
        self._agent_tasks: Dict[UUID, Task] = {}

    async def initialize(self) -> None:
        await self.registry.initialize()
        await self.health_monitor.start()
        await self._load_configured_agents()

    async def shutdown(self) -> None:
        await self.health_monitor.stop()
        await self.registry.shutdown()

    async def _load_configured_agents(self) -> None:
        for name, agent_config in self.config.agents.items():
            agent = Agent(
                name=name,
                type=AgentType(agent_config.config.get("type", "reactive")),
                capabilities=agent_config.capabilities,
                permissions=agent_config.permissions,
                config=agent_config.config,
                status=AgentStatus.IDLE if agent_config.enabled else AgentStatus.STOPPED,
            )
            await self.register(agent)

    async def register(self, agent: Agent) -> None:
        await self.registry.register(agent)
        await self.orchestrator.publish_event(
            Event(
                type=EventType.AGENT_STARTED,
                source_id=agent.id,
                source_type="agent",
                payload={"name": agent.name, "type": agent.type.value},
            )
        )

    async def unregister(self, agent_id: UUID) -> None:
        agent = self.registry.get(agent_id)
        if agent:
            await self.registry.unregister(agent_id)
            await self.orchestrator.publish_event(
                Event(
                    type=EventType.AGENT_STOPPED,
                    source_id=agent_id,
                    source_type="agent",
                    payload={"name": agent.name},
                )
            )

    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        return self.registry.get(agent_id)

    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        return self.registry.get_by_name(name)

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[Agent]:
        return self.registry.list(status)

    async def select_agents(self, intent: Dict, context: Dict) -> List[Agent]:
        required_caps = intent.get("required_capabilities", [])
        domain = intent.get("domain", "general")

        candidates = self.registry.list(AgentStatus.IDLE)
        candidates = [a for a in candidates if a.status in (AgentStatus.IDLE, AgentStatus.RUNNING)]

        scored = []
        for agent in candidates:
            score = self._score_agent(agent, required_caps, domain, context)
            if score > 0:
                scored.append((score, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [agent for _, agent in scored[:5]]

    def _score_agent(
        self,
        agent: Agent,
        required_caps: List[str],
        domain: str,
        context: Dict,
    ) -> float:
        score = 0.0

        cap_match = len(set(agent.capabilities) & set(required_caps))
        score += cap_match * 10

        if domain in agent.capabilities or domain in agent.config.get("domains", []):
            score += 20

        score += agent.health_score * 10

        if agent.status == AgentStatus.IDLE:
            score += 5
        elif agent.status == AgentStatus.RUNNING:
            score += 2

        return score

    async def execute_agent(
        self,
        agent: Agent,
        task: Task,
        context: Dict,
    ) -> Dict[str, Any]:
        agent.status = AgentStatus.RUNNING
        agent.current_task_id = task.id
        agent.last_heartbeat = datetime.utcnow()
        self._agent_tasks[task.id] = task

        await self.orchestrator.publish_event(
            Event(
                type=EventType.TASK_STARTED,
                source_id=agent.id,
                source_type="agent",
                payload={"task_id": str(task.id), "agent": agent.name},
            )
        )

        try:
            result = await self.executor.execute(agent, task, context)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = result

            await self.orchestrator.publish_event(
                Event(
                    type=EventType.TASK_COMPLETED,
                    source_id=agent.id,
                    source_type="agent",
                    payload={"task_id": str(task.id), "agent": agent.name},
                )
            )

            agent.status = AgentStatus.IDLE
            agent.current_task_id = None
            self._agent_tasks.pop(task.id, None)

            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()

            await self.orchestrator.publish_event(
                Event(
                    type=EventType.TASK_FAILED,
                    source_id=agent.id,
                    source_type="agent",
                    payload={"task_id": str(task.id), "agent": agent.name, "error": str(e)},
                    severity="error",
                )
            )

            agent.status = AgentStatus.ERROR
            agent.current_task_id = None
            self._agent_tasks.pop(task.id, None)

            raise

    async def pause_agent(self, agent_id: UUID) -> bool:
        agent = self.get_agent(agent_id)
        if agent and agent.status == AgentStatus.RUNNING:
            agent.status = AgentStatus.PAUSED
            return True
        return False

    async def resume_agent(self, agent_id: UUID) -> bool:
        agent = self.get_agent(agent_id)
        if agent and agent.status == AgentStatus.PAUSED:
            agent.status = AgentStatus.IDLE
            return True
        return False

    async def stop_agent(self, agent_id: UUID) -> bool:
        agent = self.get_agent(agent_id)
        if agent:
            agent.status = AgentStatus.STOPPED
            return True
        return False

    def get_agent_health(self, agent_id: UUID) -> Optional[Dict]:
        return self.health_monitor.get_health(agent_id)

    def get_all_health(self) -> Dict[UUID, Dict]:
        return self.health_monitor.get_all_health()

    def get_agent_metrics(self, agent_id: UUID) -> Dict:
        agent = self.get_agent(agent_id)
        if not agent:
            return {}

        health = self.health_monitor.get_health(agent_id) or {}

        return {
            "agent_id": str(agent_id),
            "name": agent.name,
            "status": agent.status.value,
            "health_score": agent.health_score,
            "active_task": str(agent.current_task_id) if agent.current_task_id else None,
            "metrics": health,
        }