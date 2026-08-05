"""ResearchAgent: deterministic information retrieval over a knowledge store."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    def __init__(self, name: str = "research", knowledge: dict[str, list[str]] | None = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="researcher",
            capabilities=["research", "information_retrieval", "summarization"],
            description="Retrieves and summarizes knowledge",
            **kwargs,
        )
        self.knowledge = knowledge or {}

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        if isinstance(input_data, dict):
            query = str(input_data.get("query", ""))
        else:
            query = str(input_data)
        knowledge = self.knowledge or dict(context.get("knowledge", {}))
        top_k = int(context.get("top_k", 3))

        query_lower = query.lower()
        matches = []
        for topic, items in sorted(knowledge.items()):
            score = 1.0 if query_lower in topic.lower() else 0.0
            for item in items:
                if query_lower in str(item).lower():
                    score = max(score, 0.5)
            if score > 0:
                matches.append({"topic": topic, "score": round(score, 3), "items": list(items)})
        matches.sort(key=lambda m: (-m["score"], m["topic"]))
        findings = matches[:top_k]
        return {
            "query": query,
            "findings": findings,
            "count": len(findings),
            "summary": f"found {len(findings)} relevant topic(s) for {query!r}",
        }
