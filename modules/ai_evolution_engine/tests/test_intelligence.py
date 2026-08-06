"""Unit tests: optimization, learning, benchmarking, innovation."""
from __future__ import annotations

from modules.ai_evolution_engine.benchmarking.baseline_store import BaselineStore
from modules.ai_evolution_engine.benchmarking.benchmark_runner import (
    BenchmarkRunner,
)
from modules.ai_evolution_engine.benchmarking.benchmark_suite import (
    DEFAULT_SUITE,
)
from modules.ai_evolution_engine.innovation.innovation_engine import InnovationEngine
from modules.ai_evolution_engine.innovation.opportunity_scorer import (
    Opportunity,
    OpportunityScorer,
)
from modules.ai_evolution_engine.learning.feedback_learner import FeedbackLearner
from modules.ai_evolution_engine.learning.incident_learner import (
    IncidentLearner,
    IncidentRecord,
)
from modules.ai_evolution_engine.learning.learning_engine import LearningEngine
from modules.ai_evolution_engine.optimization.optimization_engine import (
    OptimizationEngine,
)
from modules.ai_evolution_engine.tests.helpers import make_context


def test_optimization_suggests_for_bad_cache():
    ctx = make_context(cache_hit_ratio=0.5)
    suggestions = OptimizationEngine().suggest(ctx)
    assert any(s.name == "warm_cache" for s in suggestions)


def test_optimization_no_suggestions_when_healthy():
    ctx = make_context(
        cache_hit_ratio=0.95,
        duplicate_dependencies=0,
        large_files=0,
    )
    assert OptimizationEngine().suggest(ctx) == []


def test_learning_patterns_from_context():
    ctx = make_context(
        duplicated_code=[("src/a.py", 4), ("src/b.py", 2)],
        change_hotspots=[("src/hot.py", 9)],
    )
    patterns = LearningEngine().learn_from_context(ctx)
    assert len(patterns) == 3
    assert patterns[0].name == "duplicated_block"


def test_incident_learner_deduplicates():
    learner = IncidentLearner(max_records=10)
    learner.record(IncidentRecord("i1", "crash", "oom", "increase memory"))
    learner.record(IncidentRecord("i1", "crash", "oom", "increase memory"))
    assert learner.resolve("oom") is not None
    assert learner.resolve("oom").occurrence_count == 2
    assert len(learner.all()) == 1


def test_feedback_learner_dampens_rejected_kind():
    learner = FeedbackLearner()
    for _ in range(4):
        learner.apply("performance", accepted=False)
    factor = learner.dampen_factor("performance")
    assert factor < 1.0
    assert learner.dampen_factor("unknown") == 1.0


def test_benchmark_runner_tracks_baseline():
    runner = BenchmarkRunner()
    ctx = make_context(cache_hit_ratio=0.8)
    first = runner.run(ctx, ["cache_hit_ratio"])
    assert first[0].delta == 0.0

    second_ctx = make_context(cache_hit_ratio=0.85)
    second = runner.run(second_ctx, ["cache_hit_ratio"])
    assert second[0].previous_value == 0.8
    assert second[0].delta == 0.05


def test_default_suite_runs():
    ctx = make_context(
        cache_hit_ratio=0.9,
        test_pass_rate=1.0,
        duplicate_dependencies=0,
        p95_latency_ms=100.0,
        resource_usage_ratio=0.4,
    )
    results = DEFAULT_SUITE.run(ctx, BenchmarkRunner())
    assert len(results) == 5


def test_baseline_store_snapshot_restore():
    store = BaselineStore()
    ctx = make_context(cache_hit_ratio=0.7)
    store.runner.run(ctx, ["cache_hit_ratio"])
    snapshot = store.snapshot()
    store.restore(snapshot)
    assert store.runner.run(ctx, ["cache_hit_ratio"])[0].previous_value == 0.7


def test_opportunity_scorer_ranks_by_score():
    scorer = OpportunityScorer()
    ctx = make_context()
    ranked = scorer.rank(
        ctx,
        [
            Opportunity("a", value=0.9, feasibility=0.9, risk=0.1),
            Opportunity("b", value=0.3, feasibility=0.3, risk=0.5),
        ],
    )
    assert [o.name for o in ranked] == ["a", "b"]
    assert ranked[0].score >= ranked[1].score


def test_innovation_engine_generates_from_context():
    ctx = make_context(
        duplicate_dependencies=5,
        cache_hit_ratio=0.5,
        test_pass_rate=0.5,
    )
    opportunities = InnovationEngine().generate(ctx)
    names = {o.name for o in opportunities}
    assert "harden_test_suite" in names
