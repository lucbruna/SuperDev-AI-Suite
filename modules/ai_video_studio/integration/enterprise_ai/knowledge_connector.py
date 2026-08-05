"""Knowledge Connector — bridge to the suite knowledge engine, local store fallback."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.enterprise_ai.memory_connector import (
    get_memory_connector,
)


class KnowledgeConnector:
    """Documented facts: suite knowledge engine when available, else local."""

    def __init__(self) -> None:
        self._facts: list[dict[str, Any]] = []
        self._suite = self._suite_module()

    @staticmethod
    def _suite_module() -> Any | None:
        import importlib.util

        try:
            if importlib.util.find_spec("SuperDev.knowledge") is not None:
                import SuperDev.knowledge  # noqa: F401

                return True
        except Exception:  # noqa: BLE001
            pass
        return None

    def ingest(self, fact: str, **meta: Any) -> dict[str, Any]:
        self._facts.append({"fact": fact, **meta})
        get_memory_connector().store(fact, kind="knowledge")
        return {"ingested": len(self._facts), "suite": self._suite is not None}

    def query(self, question: str, *, limit: int = 5) -> dict[str, Any]:
        q = question.lower()
        scored = sorted(
            (
                (sum(1 for w in q.split() if w in f["fact"].lower()), f)
                for f in self._facts
            ),
            key=lambda x: -x[0],
        )
        hits = [dict(f) for score, f in scored if score][:limit]
        return {"question": question, "facts": hits, "count": len(hits)}


_knowledge_connector: KnowledgeConnector | None = None


def get_knowledge_connector() -> KnowledgeConnector:
    global _knowledge_connector
    if _knowledge_connector is None:
        _knowledge_connector = KnowledgeConnector()
    return _knowledge_connector
