from __future__ import annotations

import time
from typing import Any

from ..data_models import DataSourceType
from .collector import BaseCollector


class AgentCollector(BaseCollector):
    """Collector for AI agent activity.

    Collects agent runs, task results and performance data pushed via
    :meth:`record_activity` or pulled from an external callable (``source``
    in config) that returns an iterable of dicts.
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self._activities: list[dict[str, Any]] = []

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.AGENT

    def record_activity(
        self,
        agent: str,
        action: str,
        status: str = "completed",
        duration_ms: float = 0.0,
        tokens_used: int = 0,
        cost: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        activity = {
            "agent": agent,
            "action": action,
            "status": status,
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "cost": cost,
            "timestamp": time.time(),
        }
        activity.update(metadata or {})
        self._activities.append(activity)
        return activity

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        config = config or {}
        rows: list[dict[str, Any]] = []

        source = config.get("source") or self.config.get("source")
        if callable(source):
            for item in source():
                if isinstance(item, dict):
                    rows.append(item)
        else:
            activities = list(self._activities)
            if config.get("clear", True):
                self._activities.clear()
            rows = list(activities)

        agent_filter = config.get("agent") or self.config.get("agent")
        if agent_filter:
            rows = [row for row in rows if row.get("agent") == agent_filter]

        return self._build_batch(rows, metadata={"collector": "agent"})


__all__ = ["AgentCollector"]
