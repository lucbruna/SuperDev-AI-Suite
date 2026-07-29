from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .knowledge_config import KnowledgeConfig
from .knowledge_events import KnowledgeEventBus, KnowledgeEvent, EventType
from .knowledge_factory import KnowledgeFactory
from .knowledge_models import (
    KnowledgeEntry, KnowledgeSource, KnowledgeType, KnowledgeState,
    ResearchQuery, ResearchResult, ResearchPlan, Hypothesis,
)
from .knowledge_security import KnowledgeSecurityManager

logger = logging.getLogger(__name__)


class EngineState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EngineConfig:
    config: KnowledgeConfig
    event_bus: KnowledgeEventBus
    security: KnowledgeSecurityManager


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.IDLE
    research_count: int = 0
    sources_collected: int = 0
    reports_generated: int = 0
    total_processing_time_ms: float = 0.0
    errors: int = 0
    last_research_time: Optional[datetime] = None


class ResearchEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._research_history: Dict[str, ResearchResult] = {}

    async def conduct_research(self, query: ResearchQuery) -> ResearchResult:
        start = datetime.utcnow()
        self.metrics.state = EngineState.PLANNING
        await self.config.event_bus.publish(KnowledgeEvent(
            event_type=EventType.RESEARCH_STARTED,
            payload={"query_id": query.id, "query": query.query},
            source="research_engine",
        ))
        plan = await self.plan_research(query)
        self.metrics.state = EngineState.COLLECTING
        findings = await self.collect_information(plan)
        self.metrics.state = EngineState.ANALYZING
        analyzed = await self.analyze_sources(findings, query)
        self.metrics.state = EngineState.REPORTING
        result = await self.generate_report(analyzed, query, plan)
        elapsed = (datetime.utcnow() - start).total_seconds() * 1000
        result.processing_time_ms = elapsed
        self.metrics.research_count += 1
        self.metrics.sources_collected += len(findings)
        self.metrics.reports_generated += 1
        self.metrics.total_processing_time_ms += elapsed
        self.metrics.last_research_time = datetime.utcnow()
        self.metrics.state = EngineState.COMPLETED
        self._research_history[result.id] = result
        await self.config.event_bus.publish(KnowledgeEvent(
            event_type=EventType.RESEARCH_COMPLETED,
            payload={"result_id": result.id, "query": query.query,
                     "sources": len(findings), "duration_ms": elapsed},
            source="research_engine",
        ))
        return result

    async def plan_research(self, query: ResearchQuery) -> ResearchPlan:
        steps = [
            {"step": 1, "action": "search", "description": f"Search for: {query.query}"},
            {"step": 2, "action": "collect", "description": "Collect sources"},
            {"step": 3, "action": "analyze", "description": "Analyze findings"},
            {"step": 4, "action": "synthesize", "description": "Synthesize information"},
            {"step": 5, "action": "report", "description": "Generate report"},
        ]
        return ResearchPlan(
            id=str(uuid.uuid4()),
            query_id=query.id,
            query=query.query,
            steps=steps,
            methodology="systematic_review",
        )

    async def collect_information(self, plan: ResearchPlan) -> List[Dict[str, Any]]:
        findings = []
        for i in range(min(3, plan.steps.count)):
            findings.append({
                "id": f"src-{uuid.uuid4().hex[:8]}",
                "title": f"Source {i + 1} for: {plan.query}",
                "relevance": 0.8 - (i * 0.1),
                "source_type": "web",
            })
        return findings

    async def analyze_sources(self, findings: List[Dict[str, Any]],
                               query: ResearchQuery) -> List[Dict[str, Any]]:
        analyzed = []
        for f in findings:
            analyzed.append({
                **f,
                "summary": f"Analysis of {f.get('title', 'source')}",
                "key_points": [f"Point 1 from {f.get('title', 'source')}"],
                "confidence": f.get("relevance", 0.5),
            })
        return analyzed

    async def generate_report(self, analyzed: List[Dict[str, Any]],
                               query: ResearchQuery,
                               plan: ResearchPlan) -> ResearchResult:
        summary = f"Research completed for query: {query.query}. "
        summary += f"Found {len(analyzed)} relevant sources."
        return ResearchResult(
            id=str(uuid.uuid4()),
            query_id=query.id,
            query=query.query,
            findings=analyzed,
            summary=summary,
            confidence=0.8 if analyzed else 0.0,
        )

    def get_research(self, result_id: str) -> Optional[ResearchResult]:
        return self._research_history.get(result_id)

    def get_recent_research(self, limit: int = 10) -> List[ResearchResult]:
        results = list(self._research_history.values())
        return results[-limit:]