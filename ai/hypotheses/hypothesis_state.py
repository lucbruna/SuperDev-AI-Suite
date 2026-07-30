from __future__ import annotations

from typing import Any


class HypothesisState:
    """Manages state transitions for hypotheses."""

    def __init__(self) -> None:
        self._states: dict[str, str] = {}

    async def set_state(self, hypothesis_id: str, state: str) -> None:
        self._states[hypothesis_id] = state

    async def get_state(self, hypothesis_id: str) -> str | None:
        return self._states.get(hypothesis_id)

    async def transition(self, hypothesis_id: str, new_state: str) -> bool:
        valid_transitions = {
            "draft": ["review", "discarded"],
            "review": ["accepted", "rejected"],
            "accepted": ["tested", "discarded"],
            "tested": ["confirmed", "rejected"],
        }
        current = self._states.get(hypothesis_id, "draft")
        if new_state in valid_transitions.get(current, []):
            self._states[hypothesis_id] = new_state
            return True
        return False

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        hypothesis_id = context.get("hypothesis_id", "")
        target = context.get("state", "")
        success = await self.transition(hypothesis_id, target)
        return {"hypothesis_id": hypothesis_id, "state": self._states.get(hypothesis_id), "success": success}
