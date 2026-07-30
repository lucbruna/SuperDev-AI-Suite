from __future__ import annotations

from typing import Any

from .debate_manager import DebateManager
from .debate_agent import DebateAgent
from .debate_judge import DebateJudge
from .debate_consensus import DebateConsensus


class DebateEngine:
    """Core debate engine coordinating multi-agent discussion."""

    def __init__(
        self,
        manager: DebateManager | None = None,
        judge: DebateJudge | None = None,
        consensus: DebateConsensus | None = None,
    ):
        self._manager = manager or DebateManager()
        self._judge = judge or DebateJudge()
        self._consensus = consensus or DebateConsensus()

    async def debate(self, topic: str, agents: list[DebateAgent]) -> dict[str, Any]:
        self._manager.set_topic(topic)
        arguments = []
        for agent in agents:
            arg = await agent.argue(topic)
            arguments.append(arg)
            self._manager.record_argument(agent.name, arg)
        scores = await self._judge.evaluate(arguments)
        consensus = await self._consensus.reach(arguments, scores)
        return {
            "topic": topic,
            "arguments": arguments,
            "scores": scores,
            "consensus": consensus,
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic", "")
        agents_data = context.get("agents", [])
        agents = [DebateAgent(a.get("name", "agent"), a.get("role", "")) for a in agents_data]
        return await self.debate(topic, agents)
