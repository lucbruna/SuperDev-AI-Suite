from __future__ import annotations

from typing import Any


class AgentConfig:
    """Configuration for an agent."""

    def __init__(self, agent_id: str, config: dict[str, Any] | None = None) -> None:
        self._agent_id = agent_id
        self._config: dict[str, Any] = config or {}

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def update(self, config: dict[str, Any]) -> None:
        self._config.update(config)

    def to_dict(self) -> dict[str, Any]:
        return {"agent_id": self._agent_id, "config": dict(self._config)}
