from __future__ import annotations

import contextlib
import uuid
from typing import Any

from ..base.base_agent import BaseAgent
from ..core.agent_configuration import AgentConfig
from ..registry.agent_registry import AgentRegistry


class AgentManager:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self._instances: dict[str, BaseAgent] = {}
        self._configs: dict[str, AgentConfig] = {}
        self._statuses: dict[str, str] = {}
        self._registry = registry or AgentRegistry()

    async def create_agent(self, config: AgentConfig) -> str:
        agent_class = self._registry.get(config.name)
        if agent_class is None:
            raise ValueError(f"Agent class '{config.name}' not found in registry")

        agent_id = config.agent_id or str(uuid.uuid4())
        agent_instance = agent_class(config.model_dump())
        await agent_instance.initialize()
        self._instances[agent_id] = agent_instance
        self._configs[agent_id] = config
        self._statuses[agent_id] = "idle"
        return agent_id

    async def destroy_agent(self, agent_id: str) -> None:
        agent = self._instances.pop(agent_id, None)
        if agent:
            with contextlib.suppress(Exception):
                await agent.shutdown()
        self._configs.pop(agent_id, None)
        self._statuses.pop(agent_id, None)

    async def start_agent(self, agent_id: str) -> None:
        agent = self._instances.get(agent_id)
        if agent is None:
            raise ValueError(f"Agent '{agent_id}' not found")
        await agent.resume()
        self._statuses[agent_id] = "running"

    async def stop_agent(self, agent_id: str) -> None:
        agent = self._instances.get(agent_id)
        if agent is None:
            raise ValueError(f"Agent '{agent_id}' not found")
        await agent.pause()
        self._statuses[agent_id] = "paused"

    def list_agents(self) -> list[dict[str, Any]]:
        result = []
        for agent_id in self._instances:
            config = self._configs.get(agent_id)
            result.append({
                "agent_id": agent_id,
                "name": config.name if config else "unknown",
                "status": self._statuses.get(agent_id, "unknown"),
                "description": config.description if config else "",
            })
        return result

    def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        agent = self._instances.get(agent_id)
        if agent is None:
            return {"agent_id": agent_id, "status": "not_found"}
        return {
            "agent_id": agent_id,
            "status": self._statuses.get(agent_id, agent.status()),
            "health": agent.health(),
            "capabilities": agent.capabilities(),
        }
