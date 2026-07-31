"""Knowledge sharing between agents."""

from __future__ import annotations

import time
from typing import Any


class KnowledgeSharing:
    """Manages knowledge distribution across agent networks."""

    def __init__(self) -> None:
        self._knowledge_base: list[dict[str, Any]] = []

    def share(self, agent_id: str, knowledge: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "agent_id": agent_id,
            "knowledge": knowledge,
            "topic": knowledge.get("topic", "general"),
            "shared_at": time.time(),
            "relevance": knowledge.get("relevance", 0.5),
        }
        self._knowledge_base.append(entry)
        return {"status": "shared", "topic": entry["topic"]}

    def retrieve(self, topic: str | None = None) -> list[dict[str, Any]]:
        if topic:
            return [k for k in self._knowledge_base if k["topic"] == topic]
        return list(self._knowledge_base)

    def count(self) -> int:
        return len(self._knowledge_base)

    def get_topics(self) -> list[str]:
        return list({k["topic"] for k in self._knowledge_base})
