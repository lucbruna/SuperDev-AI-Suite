from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent
from ..registry.agent_registry import AgentRegistry


class AgentSystem:
    _instance: AgentSystem | None = None

    def __new__(cls) -> AgentSystem:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._agents: dict[str, BaseAgent] = {}
            self._registry: AgentRegistry = AgentRegistry()
            self._config: dict[str, Any] = {}
            self._running: bool = False
            self._lock: asyncio.Lock = asyncio.Lock()
            self._initialized = True

    async def initialize(self, config: dict[str, Any]) -> None:
        self._config = config
        self._running = True
        for name, agent_class in self._registry.list().items():
            agent_config = config.get("agents", {}).get(name, {})
            agent_instance = agent_class(agent_config)
            await agent_instance.initialize()
            self._agents[name] = agent_instance

    async def shutdown(self) -> None:
        async with self._lock:
            for _name, agent in self._agents.items():
                with contextlib.suppress(Exception):
                    await agent.shutdown()
            self._agents.clear()
            self._running = False

    def get_agent(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    async def execute_task(self, agent_name: str, task: str, context: dict[str, Any]) -> AgentResult:
        agent = self.get_agent(agent_name)
        if agent is None:
            return AgentResult(success=False, output="", error=f"Agent '{agent_name}' not found")
        try:
            return await agent.execute(task, context)
        except Exception as e:
            return AgentResult(success=False, output="", error=str(e))

    def get_registry(self) -> AgentRegistry:
        return self._registry
