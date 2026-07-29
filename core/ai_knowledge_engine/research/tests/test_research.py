from __future__ import annotations

import pytest

from ..research_engine import ResearchEngine, EngineConfig, EngineState
from ..source_manager import SourceManager, SourceInfo
from ..information_collector import InformationCollector
from ..query_optimizer import QueryOptimizer
from ..research_planner import ResearchPlanner


@pytest.mark.asyncio
async def test_research_engine_initialize():
    engine = ResearchEngine()
    assert engine.state == EngineState.IDLE
    await engine.initialize()
    assert engine.state == EngineState.READY
    await engine.stop()
    assert engine.state == EngineState.IDLE


@pytest.mark.asyncio
async def test_research_engine_conduct_research():
    engine = ResearchEngine()
    await engine.initialize()
    result = await engine.conduct_research("machine learning")
    assert result["query"] == "machine learning"
    assert "results" in result
    assert "aggregated" in result
    assert engine.metrics.total_researches == 1
    assert engine.metrics.successful_researches == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_research_engine_aggregate_results():
    engine = ResearchEngine()
    results = [
        {"results": [{"title": "A", "relevance": 0.9}]},
        {"results": [{"title": "B", "relevance": 0.8}]},
    ]
    agg = await engine.aggregate_results(results)
    assert agg["total_sources"] == 2
    assert len(agg["findings"]) == 2


@pytest.mark.asyncio
async def test_research_engine_not_ready_raises():
    engine = ResearchEngine()
    with pytest.raises(RuntimeError, match="Engine not ready"):
        await engine.conduct_research("test")


def test_source_manager_list_sources():
    sm = SourceManager()
    sources = sm.list_sources()
    assert len(sources) == 10
    academic = sm.list_sources("academic")
    assert all(s.category == "academic" for s in academic)


def test_source_manager_register_and_validate():
    sm = SourceManager()
    new_source = SourceInfo(id="src_test_001", name="Test Source", category="web", base_url="https://test.com")
    sid = sm.register_source(new_source)
    assert sid == "src_test_001"
    assert sm.validate_source("src_test_001") is True
    assert sm.validate_source("nonexistent") is False


def test_source_manager_get_quality_and_category():
    sm = SourceManager()
    assert sm.get_source_quality("src_web_001") == 0.85
    assert sm.categorize_source("src_web_001") == "academic"
    with pytest.raises(KeyError):
        sm.get_source_quality("invalid")


@pytest.mark.asyncio
async def test_information_collector_collect():
    ic = InformationCollector()
    result = await ic.collect("machine learning")
    assert result["total"] > 0
    assert all("title" in r for r in result["results"])


@pytest.mark.asyncio
async def test_information_collector_filter_and_rank():
    ic = InformationCollector()
    result = await ic.collect("machine learning")
    filtered = ic.filter_results(result["results"], min_relevance=0.8)
    assert all(r["relevance"] >= 0.8 for r in filtered)
    ranked = ic.rank_results(result["results"])
    assert ranked[0]["relevance"] >= ranked[-1]["relevance"]


@pytest.mark.asyncio
async def test_query_optimizer_extract_keywords():
    qo = QueryOptimizer()
    keywords = await qo.extract_keywords("machine learning algorithms for NLP")
    assert "machine" in keywords
    assert "learning" in keywords
    assert "algorithms" in keywords
    assert "nlp" in keywords


@pytest.mark.asyncio
async def test_query_optimizer_expand_and_suggest():
    qo = QueryOptimizer()
    expanded = await qo.expand_query("machine learning basics")
    assert len(expanded) > 1
    suggested = await qo.suggest_related("deep learning")
    assert len(suggested) > 0


@pytest.mark.asyncio
async def test_query_optimizer_calculate_relevance():
    qo = QueryOptimizer()
    score = await qo.calculate_relevance("machine learning", "deep machine learning")
    assert 0.0 < score <= 1.0


@pytest.mark.asyncio
async def test_research_planner_create_and_execute():
    rp = ResearchPlanner()
    plan = await rp.create_plan("machine learning")
    assert "plan_id" in plan
    assert len(plan["steps"]) == 3
    executed = await rp.execute_plan(plan["plan_id"])
    assert executed["status"] == "completed"


@pytest.mark.asyncio
async def test_research_planner_status_and_estimate():
    rp = ResearchPlanner()
    plan = await rp.create_plan("quantum computing")
    status = await rp.get_plan_status(plan["plan_id"])
    assert status["total_steps"] == 3
    assert status["completed_steps"] == 0
    estimate = await rp.estimate_completion(plan["plan_id"])
    assert estimate["remaining_steps"] == 3
    assert estimate["estimated_minutes"] > 0


@pytest.mark.asyncio
async def test_research_planner_add_step():
    rp = ResearchPlanner()
    plan = await rp.create_plan("test topic")
    updated = await rp.add_step(plan["plan_id"], "extra step", 5)
    assert len(updated["steps"]) == 4


@pytest.mark.asyncio
async def test_research_planner_nonexistent_plan():
    rp = ResearchPlanner()
    with pytest.raises(KeyError):
        await rp.execute_plan("nonexistent")


@pytest.mark.asyncio
async def test_information_collector_collect_from_source():
    ic = InformationCollector()
    result = await ic.collect_from_source("machine learning", "ArXiv")
    assert result["source"] == "ArXiv"


@pytest.mark.asyncio
async def test_information_collector_extract_relevant():
    ic = InformationCollector()
    result = await ic.collect("machine learning")
    extracted = ic.extract_relevant(result["results"], top_n=2)
    assert len(extracted) == 2


def test_source_manager_register_duplicate():
    sm = SourceManager()
    with pytest.raises(ValueError, match="already exists"):
        sm.register_source(SourceInfo(id="src_web_001", name="dup", category="web", base_url="x"))


@pytest.mark.asyncio
async def test_research_engine_metrics():
    engine = ResearchEngine()
    await engine.initialize()
    await engine.conduct_research("nlp")
    assert engine.metrics.total_researches == 1
    assert engine.metrics.successful_researches == 1
    assert engine.metrics.total_sources_consulted > 0
    assert engine.metrics.average_research_time_ms >= 0
    await engine.stop()