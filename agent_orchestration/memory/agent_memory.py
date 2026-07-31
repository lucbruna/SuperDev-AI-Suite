"""Per-agent working memory (Volume 31)."""

from __future__ import annotations

from typing import Any


class AgentMemory:
    """Stores per-agent facts in a namespaced key-value store."""

    def __init__(self) -> None:
        self._facts: dict[str, dict[str, Any]] = {}

    def remember(self, agent_id: str, key: str, value: Any) -> None:
        self._facts.setdefault(agent_id, {})[key] = value

    def recall(self, agent_id: str, key: str,
               default: Any = None) -> Any:
        return self._facts.get(agent_id, {}).get(key, default)

    def forget(self, agent_id: str, key: str) -> bool:
        return self._facts.get(agent_id, {}).pop(key, None) is not None

    def keys(self, agent_id: str) -> list[str]:
        return list(self._facts.get(agent_id, {}))

    def snapshot(self, agent_id: str) -> dict[str, Any]:
        return dict(self._facts.get(agent_id, {}))

    def count(self, agent_id: str | None = None) -> int:
        if agent_id is not None:
            return len(self._facts.get(agent_id, {}))
        return sum(len(facts) for facts in self._facts.values())
