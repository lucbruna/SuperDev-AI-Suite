"""Lifecycle manager and public API for the AI Evolution Engine."""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.config.constants import (
    EVENT_RECOMMENDATION_CREATED,
    EVENT_RECOMMENDATION_APPROVED,
    EVENT_RECOMMENDATION_REJECTED,
    EVENT_ROADMAP_PLANNED,
    REC_APPROVED,
    REC_DRAFT,
    REC_PENDING,
    REC_REJECTED,
)
from modules.ai_evolution_engine.config.evolution_config import EvolutionConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_engine import (
    EngineResult,
    EvolutionEngine,
)
from modules.ai_evolution_engine.core.evolution_kernel import EvolutionKernel
from modules.ai_evolution_engine.core.evolution_pipeline import EvolutionPipeline


@dataclass(slots=True)
class ManagerState:
    """Public state snapshot reported by the manager."""

    running: bool
    cycles: int
    last_analysis_score: float
    open_recommendations: int
    open_decisions: int
    ticks: int

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "cycles": self.cycles,
            "last_analysis_score": self.last_analysis_score,
            "open_recommendations": self.open_recommendations,
            "open_decisions": self.open_decisions,
            "ticks": self.ticks,
        }


class EvolutionManager:
    """High-level operations for an AI Evolution Engine instance."""

    def __init__(
        self,
        context: EvolutionContext | None = None,
        config: EvolutionConfig | None = None,
        pipeline: EvolutionPipeline | None = None,
        engine: EvolutionEngine | None = None,
        kernel: EvolutionKernel | None = None,
    ) -> None:
        self._config = config or EvolutionConfig()
        self._ctx = context or EvolutionContext(config=self._config)
        self._pipeline = pipeline or EvolutionPipeline()
        self._engine = engine or EvolutionEngine(self._pipeline)
        self._kernel = kernel or EvolutionKernel(self._ctx, self._engine)
        self._recommendations: list = []
        self._decisions: list = []

    @property
    def context(self) -> EvolutionContext:
        return self._ctx

    @property
    def pipeline(self) -> EvolutionPipeline:
        return self._pipeline

    @property
    def engine(self) -> EvolutionEngine:
        return self._engine

    @property
    def recommendations(self) -> list:
        return list(self._recommendations)

    @property
    def decisions(self) -> list:
        return list(self._decisions)

    def resolve(self, project_root: str | None = None) -> None:
        self._config.resolve(project_root)

    def start(self) -> None:
        self._kernel.start()

    def stop(self) -> None:
        self._kernel.stop()

    def tick(self, steps: int = 1) -> int:
        return self._kernel.tick(steps)

    def analyze(self) -> EngineResult:
        return self._engine.run(self._ctx)

    def recommend(self, item) -> None:
        """Register a recommendation (draft) and publish creation event."""
        item.status = REC_DRAFT
        self._recommendations.append(item)
        self._ctx.publish(EVENT_RECOMMENDATION_CREATED, item.to_dict())

    def submit_for_approval(self, item) -> None:
        item.status = REC_PENDING
        self._ctx.state.set_open_recommendations(len(self._recommendations))

    def approve(self, item) -> None:
        item.status = REC_APPROVED
        self._ctx.publish(EVENT_RECOMMENDATION_APPROVED, item.to_dict())

    def reject(self, item) -> None:
        item.status = REC_REJECTED
        self._ctx.publish(EVENT_RECOMMENDATION_REJECTED, item.to_dict())

    def plan_roadmap(self, approved: list) -> object:
        self._ctx.publish(EVENT_ROADMAP_PLANNED, {"items": len(approved)})
        return {"planned": len(approved), "items": [i.to_dict() for i in approved]}

    def state(self) -> ManagerState:
        return ManagerState(
            running=self._ctx.state.running,
            cycles=self._ctx.state.cycles,
            last_analysis_score=self._ctx.state.last_analysis_score,
            open_recommendations=self._ctx.state.open_recommendations,
            open_decisions=self._ctx.state.open_decisions,
            ticks=self._kernel.ticks,
        )
