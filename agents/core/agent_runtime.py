from __future__ import annotations

import asyncio
import time
from enum import StrEnum
from typing import Any

from ..base.base_agent import AgentResult
from ..base.base_tool import BaseTool


class LifecycleStage(StrEnum):
    INIT = "init"
    PLAN = "plan"
    EXECUTE = "execute"
    REVIEW = "review"
    COMPLETE = "complete"


class AgentRuntime:
    def __init__(self) -> None:
        self._agents: dict[str, Any] = {}
        self._tools: dict[str, BaseTool] = {}
        self._stages: dict[str, LifecycleStage] = {}

    def register_agent(self, agent_id: str, agent: Any) -> None:
        self._agents[agent_id] = agent
        self._stages[agent_id] = LifecycleStage.INIT

    def register_tool(self, name: str, tool: BaseTool) -> None:
        self._tools[name] = tool

    async def execute_agent(self, agent_id: str, task: str, config: dict[str, Any]) -> AgentResult:
        agent = self._agents.get(agent_id)
        if agent is None:
            return AgentResult(success=False, output="", error=f"Agent '{agent_id}' not found")

        self._stages[agent_id] = LifecycleStage.PLAN
        start = time.time()

        try:
            self._stages[agent_id] = LifecycleStage.EXECUTE
            result = await agent.execute(task, config)
            self._stages[agent_id] = LifecycleStage.REVIEW
            self._stages[agent_id] = LifecycleStage.COMPLETE
            result.metrics["execution_time"] = time.time() - start
            result.metrics["agent_id"] = agent_id
            return result
        except asyncio.CancelledError:
            self._stages[agent_id] = LifecycleStage.COMPLETE
            return AgentResult(success=False, output="", error="Execution cancelled")
        except Exception as e:
            self._stages[agent_id] = LifecycleStage.COMPLETE
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._stages[agent_id] = LifecycleStage.COMPLETE

    def get_stage(self, agent_id: str) -> LifecycleStage | None:
        return self._stages.get(agent_id)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())
