from __future__ import annotations

from typing import Any


class RollbackEngine:
    """Rolls back operations to previous states."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Any] = {}

    def save_checkpoint(self, key: str, state: Any) -> None:
        self._checkpoints[key] = state

    async def rollback(self, context: dict[str, Any]) -> dict[str, Any]:
        key = context.get("checkpoint_key", "")
        if key in self._checkpoints:
            state = self._checkpoints[key]
            return {"rolled_back": True, "state": state, "checkpoint": key}
        return {"rolled_back": False, "error": f"No checkpoint found for '{key}'"}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.rollback(context)
