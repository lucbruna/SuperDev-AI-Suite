"""Research Engine — Intelligent research and information collection."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .knowledge_models import ResearchQuery, ResearchResult, SourceType, ConfidenceLevel


class ResearchEngine:
    def __init__(self):
        self._queries: Dict[str, ResearchQuery] = {}
        self._results: Dict[str, ResearchResult] = {}
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._plans: Dict[str, Dict[str, Any]] = {}

    def create_query(self, query_text: str, query_type: str = "info", max_results: int = 10) -> ResearchQuery:
        query = ResearchQuery(query_text=query_text, query_type=query_type, max_results=max_results)
        self._queries[query.query_id] = query
        return query

    def add_result(self, result: ResearchResult) -> ResearchResult:
        self._results[result.result_id] = result
        return result

    def get_result(self, result_id: str) -> Optional[ResearchResult]:
        return self._results.get(result_id)

    def get_results_for_query(self, query_id: str) -> List[ResearchResult]:
        return [r for r in self._results.values() if r.query_id == query_id]

    def register_source(self, name: str, source_type: SourceType, config: Dict[str, Any]) -> None:
        self._sources[name] = {"type": source_type, "config": config, "active": True}

    def get_source(self, name: str) -> Optional[Dict[str, Any]]:
        return self._sources.get(name)

    def plan_research(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        plan = {
            "topic": topic,
            "depth": depth,
            "phases": [
                {"phase": "collection", "status": "pending"},
                {"phase": "analysis", "status": "pending"},
                {"phase": "synthesis", "status": "pending"},
            ],
            "estimated_sources": depth * 5,
            "created_at": datetime.now().isoformat(),
        }
        plan_id = f"plan_{topic[:20].replace(' ', '_')}"
        self._plans[plan_id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        return self._plans.get(plan_id)

    def score_relevance(self, result: ResearchResult, query: ResearchQuery) -> float:
        query_words = set(query.query_text.lower().split())
        result_words = set(result.title.lower().split() + result.content.lower().split())
        if not query_words:
            return 0.0
        overlap = len(query_words & result_words)
        return min(overlap / len(query_words), 1.0)

    def deduplicate_results(self, results: List[ResearchResult]) -> List[ResearchResult]:
        seen = set()
        unique = []
        for r in results:
            key = (r.title.lower(), r.source.value)
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_queries": len(self._queries),
            "total_results": len(self._results),
            "total_sources": len(self._sources),
            "total_plans": len(self._plans),
            "active_sources": len([s for s in self._sources.values() if s["active"]]),
        }
