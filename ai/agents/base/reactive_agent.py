from __future__ import annotations

from typing import Any, Dict

from .base_agent import BaseAgent


class ReactiveAgent(BaseAgent):
    """Agent that reacts to stimuli."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        super().__init__(agent_id, name)
        self._stimuli: Dict[str, str] = {}

    def register_stimulus(self, trigger: str, response: str) -> None:
        self._stimuli[trigger] = response

    def react(self, stimulus: str) -> str:
        return self._stimuli.get(stimulus, "unknown")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        stimulus = task.get("stimulus", "")
        response = self.react(stimulus)
        return {"agent_id": self._agent_id, "stimulus": stimulus, "response": response}
