"""Long-term memory: persistent, searchable facts (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_protocols import now


class LongMemory:
    """Stores durable facts with an importance weight for search."""

    def __init__(self) -> None:
        self._facts: dict[str, list[dict[str, Any]]] = {}

    def remember(self, agent_id: str, key: str, value: Any,
                 importance: float = 0.5) -> dict[str, Any]:
        facts = self._facts.setdefault(agent_id, [])
        for fact in facts:
            if fact["key"] == key:
                fact["value"] = value
                fact["importance"] = importance
                fact["created_at"] = now()
                return fact
        fact = {"key": key, "value": value, "importance": importance,
                "created_at": now()}
        facts.append(fact)
        return fact

    def recall(self, agent_id: str, key: str) -> Any:
        for fact in self._facts.get(agent_id, []):
            if fact["key"] == key:
                return fact["value"]
        return None

    def search(self, agent_id: str, term: str) -> list[dict[str, Any]]:
        lowered = term.lower()
        matches = [fact for fact in self._facts.get(agent_id, [])
                   if lowered in fact["key"].lower()
                   or lowered in str(fact["value"]).lower()]
        return sorted(matches, key=lambda fact: fact["importance"],
                      reverse=True)

    def count(self, agent_id: str | None = None) -> int:
        if agent_id is not None:
            return len(self._facts.get(agent_id, []))
        return sum(len(facts) for facts in self._facts.values())
