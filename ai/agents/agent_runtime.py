from __future__ import annotations

import time
from typing import Any


class AgentRuntime:
    """Runtime context for agent execution."""

    def __init__(self, agent_id: str) -> None:
        self._agent_id = agent_id
        self._started_at: float | None = None
        self._status: str = "idle"
        self._metadata: dict[str, Any] = {}

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def started_at(self) -> float | None:
        return self._started_at

    @property
    def status(self) -> str:
        return self._status

    @property
    def uptime(self) -> float:
        if self._started_at is None:
            return 0.0
        return time.time() - self._started_at

    def start(self) -> None:
        self._started_at = time.time()
        self._status = "running"

    def stop(self) -> None:
        self._status = "stopped"

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str) -> Any | None:
        return self._metadata.get(key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "status": self._status,
            "uptime": self.uptime,
            "started_at": self._started_at,
        }
