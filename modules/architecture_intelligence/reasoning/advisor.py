"""Architecture advisor: turns insights into prioritized advice.

Optional LLM enrichment: when an LLM provider is configured, the advisor asks
the model to rank and rephrase the deterministic insights; otherwise it serves
the deterministic insights directly.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_intelligence.reasoning.insight_engine import InsightEngine

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class Advisor:
    """Synthesizes advice from raw insights."""

    def __init__(self, insight_engine: InsightEngine | None = None) -> None:
        self.insight_engine = insight_engine or InsightEngine()

    def advise(self, graph: Any, *, limit: int | None = None) -> dict[str, Any]:
        insights = self.insight_engine.run(graph, limit=limit)
        summary: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        categories: dict[str, int] = {}
        for insight in insights:
            summary[insight.get("severity", "low")] = summary.get(
                insight.get("severity", "low"), 0
            ) + 1
            cat = insight.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        enriched = self._enrich(insights)
        return {
            "format": "structured",
            "summary": summary,
            "categories": categories,
            "advice": enriched,
            "generator": "heuristic" if not enriched.get("llm_enriched") else "llm+heuristic",
        }

    def _enrich(self, insights: list[dict[str, Any]]) -> dict[str, Any]:
        # LLM enrichment is best-effort; never block on the provider.
        try:
            from modules.architecture_intelligence.llm.provider import get_provider

            provider = get_provider()
        except Exception:
            provider = None
        if provider is None or not provider.available:
            return {"llm_enriched": False, "insights": insights}
        try:
            text = provider.complete(
                "Summarize these architecture findings in one paragraph for a "
                "technical lead, listing the top 3 priorities: "
                + "; ".join(f"[{i.get('severity')}] {i.get('title')}" for i in insights[:8])
            )
            return {"llm_enriched": True, "insights": insights, "executive_summary": text}
        except Exception:
            return {"llm_enriched": False, "insights": insights}


def advise(graph: Any, *, limit: int | None = None) -> dict[str, Any]:
    return Advisor().advise(graph, limit=limit)
