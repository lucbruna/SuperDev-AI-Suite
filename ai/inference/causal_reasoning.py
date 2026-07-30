from __future__ import annotations

from typing import Any


class CausalReasoning:
    """Causal reasoning with cause-effect relationships."""

    def __init__(self) -> None:
        self._causes: dict[str, list[str]] = {}
        self._effects: dict[str, list[str]] = {}

    def add_causal_link(self, cause: str, effect: str) -> None:
        if cause not in self._causes:
            self._causes[cause] = []
        self._causes[cause].append(effect)
        if effect not in self._effects:
            self._effects[effect] = []
        self._effects[effect].append(cause)

    async def infer_causes(self, effect: str) -> list[str]:
        return self._effects.get(effect, [])

    async def infer_effects(self, cause: str) -> list[str]:
        return self._causes.get(cause, [])

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        event = context.get("event", "")
        mode = context.get("mode", "effects")
        if mode == "causes":
            result = await self.infer_causes(event)
        else:
            result = await self.infer_effects(event)
        return {"event": event, "mode": mode, "related": result}
