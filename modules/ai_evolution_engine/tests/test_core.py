"""Unit tests: core components."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    EVENT_TICK,
    REC_APPROVED,
    REC_DRAFT,
    REC_PENDING,
    REC_REJECTED,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_engine import EvolutionEngine
from modules.ai_evolution_engine.core.evolution_kernel import EvolutionKernel
from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager
from modules.ai_evolution_engine.core.evolution_memory import EvolutionMemory
from modules.ai_evolution_engine.core.evolution_pipeline import (
    AnalysisResult,
    EvolutionPipeline,
    EvolutionReport,
)
from modules.ai_evolution_engine.core.evolution_state import EvolutionState
from modules.ai_evolution_engine.tests.helpers import make_context, make_recommendation


class _DummyAnalyzer:
    def analyze(self, ctx: EvolutionContext) -> AnalysisResult:
        return AnalysisResult(
            dimension="dummy",
            score=0.75,
            status="ok",
            metrics={"health": 0.75},
            findings=[{"message": "no-op"}],
        )


def test_pipeline_runs_analyzers_and_aggregates():
    ctx = make_context()
    pipeline = EvolutionPipeline(analyzers=[_DummyAnalyzer()])
    report = pipeline.run(ctx)

    assert isinstance(report, EvolutionReport)
    assert report.status == "completed"
    assert report.scores["dummy"] == 0.75
    assert ctx.state.cycles == 1
    assert ctx.state.last_analysis_score == 0.75


def test_pipeline_empty_report_when_no_analyzers():
    ctx = make_context()
    report = EvolutionPipeline().run(ctx)
    assert report.status == "empty"
    assert report.scores == {}


def test_engine_cycle_returns_engine_result():
    ctx = make_context()
    engine = EvolutionEngine(EvolutionPipeline(analyzers=[_DummyAnalyzer()]))
    result = engine.run(ctx)
    payload = result.to_dict()
    assert payload["status"] == "ok"
    assert payload["report"]["status"] == "completed"


def test_kernel_tick_driven_and_deterministic():
    ctx = make_context()
    kernel = EvolutionKernel(ctx, EvolutionEngine(), interval=2)
    kernel.start()
    assert kernel.tick(1) == 0
    assert kernel.ticks == 1
    # second tick triggers one analysis cycle
    assert kernel.tick(1) == 1
    assert ctx.state.cycles == 1


def test_kernel_ignores_ticks_when_stopped():
    ctx = make_context()
    kernel = EvolutionKernel(ctx, EvolutionEngine(), interval=2)
    assert kernel.tick(5) == 0
    assert ctx.state.cycles == 0


def test_memory_set_get_delete():
    memory = EvolutionMemory()
    memory.remember("key", {"a": 1})
    assert memory.recall("key") == {"a": 1}
    memory.forget("key")
    assert memory.recall("key") is None


def test_manager_lifecycle_and_recommendations():
    manager = EvolutionManager(EvolutionContext())
    manager.start()
    assert manager.state().running is True

    item = make_recommendation()
    manager.recommend(item)
    assert item.status == REC_DRAFT
    assert len(manager.recommendations) == 1

    manager.submit_for_approval(item)
    assert item.status == REC_PENDING

    manager.approve(item)
    assert item.status == REC_APPROVED

    other = make_recommendation(title="rejected one")
    manager.recommend(other)
    manager.submit_for_approval(other)
    manager.reject(other)
    assert other.status == REC_REJECTED

    state = manager.state()
    assert state.cycles == 0
    assert state.last_analysis_score == 0.0


def test_manager_analyze_publishes_analysis_event():
    ctx = EvolutionContext()
    manager = EvolutionManager(ctx, pipeline=EvolutionPipeline(analyzers=[_DummyAnalyzer()]))
    result = manager.analyze()
    assert result.to_dict()["report"]["scores"]["dummy"] == 0.75
    assert ctx.state.cycles == 1


def test_events_bus_publishes_tick():
    ctx = make_context()
    seen: list[str] = []
    ctx.events.subscribe(lambda event: seen.append(event.type))
    ctx.publish(EVENT_TICK, {"tick": 1})
    assert seen == [EVENT_TICK]
    assert ctx.state.last_event == EVENT_TICK


def test_context_reset_clears_state_and_events():
    ctx = make_context(foo=1)
    ctx.publish(EVENT_TICK)
    ctx.state.increment_cycles(3)
    ctx.reset()
    assert ctx.get_artifact("foo") is None
    assert ctx.state.cycles == 0
    assert ctx.state.last_event == ""


def test_state_defaults():
    state = EvolutionState()
    assert state.running is False
    assert state.cycles == 0
    assert state.open_recommendations == 0
    assert state.open_decisions == 0
