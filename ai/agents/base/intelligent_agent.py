from __future__ import annotations

from typing import Any

from .autonomous_agent import AutonomousAgent
from .cognitive_agent import CognitiveAgent


class IntelligentAgent(CognitiveAgent, AutonomousAgent):
    """Fully intelligent agent with cognition and autonomy."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        CognitiveAgent.__init__(self, agent_id, name)
        AutonomousAgent.__init__(self, agent_id, name)

    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        decision = self.decide(context)
        return {"decision": decision, "context": context}

    def to_dict(self) -> dict[str, Any]:
        d = CognitiveAgent.to_dict(self)
        d["autonomy_level"] = self._autonomy_level
        return d
