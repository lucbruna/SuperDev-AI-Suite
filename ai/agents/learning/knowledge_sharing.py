"""Knowledge sharing between agents."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class KnowledgeSharing:
    """Manages knowledge distribution across agent networks."""

    def __init__(self) -> None:
        self._knowledge_base: List[Dict[str, Any]] = []

    def share(self, agent_id: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        entry = {
            "agent_id": agent_id,
            "knowledge": knowledge,
            "topic": knowledge.get("topic", "general"),
            "shared_at": time.time(),
            "relevance": knowledge.get("relevance", 0.5),
        }
        self._knowledge_base.append(entry)
        return {"status": "shared", "topic": entry["topic"]}

    def retrieve(self, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic:
            return [k for k in self._knowledge_base if k["topic"] == topic]
        return list(self._knowledge_base)

    def count(self) -> int:
        return len(self._knowledge_base)

    def get_topics(self) -> List[str]:
        return list({k["topic"] for k in self._knowledge_base})
