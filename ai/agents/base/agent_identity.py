from __future__ import annotations

from typing import Any, Dict


class AgentIdentity:
    """Identity information for an agent."""

    def __init__(self, agent_id: str, agent_type: str) -> None:
        self._agent_id = agent_id
        self._agent_type = agent_type
        self._version: str = "1.0.0"

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def agent_type(self) -> str:
        return self._agent_type

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "agent_type": self._agent_type,
            "version": self._version,
        }
