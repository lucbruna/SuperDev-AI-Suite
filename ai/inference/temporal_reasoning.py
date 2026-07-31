from __future__ import annotations

from typing import Any


class TemporalReasoning:
    """Temporal reasoning over time-ordered events."""

    def __init__(self) -> None:
        self._timeline: list[dict[str, Any]] = []

    def add_event(self, event: dict[str, Any]) -> None:
        self._timeline.append(event)
        self._timeline.sort(key=lambda e: e.get("timestamp", 0))

    async def sequence(self, start: float, end: float) -> list[dict[str, Any]]:
        return [e for e in self._timeline if start <= e.get("timestamp", 0) <= end]

    async def before(self, event_id: str) -> list[dict[str, Any]]:
        idx = next((i for i, e in enumerate(self._timeline) if e.get("id") == event_id), -1)
        return self._timeline[:idx]

    async def after(self, event_id: str) -> list[dict[str, Any]]:
        idx = next((i for i, e in enumerate(self._timeline) if e.get("id") == event_id), -1)
        return self._timeline[idx + 1 :] if idx >= 0 else []

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        mode = context.get("mode", "all")
        if mode == "sequence":
            result = await self.sequence(context.get("start", 0), context.get("end", 0))
        elif mode == "before":
            result = await self.before(context.get("event_id", ""))
        elif mode == "after":
            result = await self.after(context.get("event_id", ""))
        else:
            result = self._timeline
        return {"mode": mode, "events": result, "count": len(result)}
