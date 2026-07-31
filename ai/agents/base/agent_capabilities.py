from __future__ import annotations

from typing import Any


class AgentCapabilities:
    """Declares what an agent can do."""

    def __init__(self) -> None:
        self._capabilities: dict[str, bool] = {}

    def add(self, capability: str) -> None:
        self._capabilities[capability] = True

    def remove(self, capability: str) -> bool:
        return self._capabilities.pop(capability, None) is not None

    def has(self, capability: str) -> bool:
        return self._capabilities.get(capability, False)

    def list_all(self) -> list[str]:
        return [c for c, v in self._capabilities.items() if v]

    def clear(self) -> None:
        self._capabilities.clear()

    def to_dict(self) -> dict[str, Any]:
        return {"capabilities": self.list_all()}
