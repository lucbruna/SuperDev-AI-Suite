from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .research_planner import ResearchPlanner
from .source_manager import SourceManager
from .information_collector import InformationCollector
from .query_optimizer import QueryOptimizer


class EngineState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class EngineConfig:
    max_concurrent_sources: int = 5
    research_timeout_seconds: int = 300
    default_depth: str = "medium"
    collect_metadata: bool = True
    cache_results: bool = True


@dataclass
class EngineMetrics:
    total_researches: int = 0
    successful_researches: int = 0
    failed_researches: int = 0
    total_sources_consulted: int = 0
    average_research_time_ms: float = 0.0
    active_researches: int = 0


class ResearchEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.IDLE
        self.metrics = EngineMetrics()
        self.planner = ResearchPlanner()
        self.source_manager = SourceManager()
        self.collector = InformationCollector()
        self.query_optimizer = QueryOptimizer()
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await asyncio.sleep(0.01)
        self.state = EngineState.READY

    async def stop(self) -> None:
        self.state = EngineState.STOPPING
        await asyncio.sleep(0.01)
        self.state = EngineState.IDLE

    async def conduct_research(self, query: str, depth: str | None = None) -> dict[str, Any]:
        if self.state != EngineState.READY:
            raise RuntimeError(f"Engine not ready, current state: {self.state.value}")

        async with self._lock:
            self.state = EngineState.RUNNING
            self.metrics.active_researches += 1

        try:
            start = asyncio.get_event_loop().time()

            optimized = await self.query_optimizer.optimize_query(query)
            plan = await self.planner.create_plan(optimized["optimized_query"])
            sources = self.source_manager.list_sources()
            results = []

            for step in plan["steps"]:
                step_result = await self.collector.collect(step["description"])
                results.append(step_result)

            aggregated = await self.aggregate_results(results)

            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            self.metrics.total_researches += 1
            self.metrics.successful_researches += 1
            self.metrics.total_sources_consulted += len(sources)
            prev_avg = self.metrics.average_research_time_ms
            count = self.metrics.total_researches
            self.metrics.average_research_time_ms = prev_avg + (elapsed - prev_avg) / count

            return {
                "query": query,
                "optimized_query": optimized,
                "plan": plan,
                "results": results,
                "aggregated": aggregated,
                "elapsed_ms": elapsed,
            }
        except Exception:
            self.metrics.failed_researches += 1
            raise
        finally:
            async with self._lock:
                self.metrics.active_researches -= 1
                self.state = EngineState.READY

    async def execute_plan(self, plan: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        for step in plan.get("steps", []):
            result = await self.collector.collect(step["description"])
            results.append(result)
        return results

    async def aggregate_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        all_items = []
        for r in results:
            all_items.extend(r.get("results", []))
        return {
            "total_sources": len(all_items),
            "findings": all_items,
            "summary": f"Aggregated {len(all_items)} findings from {len(results)} steps.",
        }