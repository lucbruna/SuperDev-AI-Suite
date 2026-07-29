import pytest

from core.ai_knowledge_engine.reasoning.reasoning_engine import (
    ReasoningEngine,
    EngineConfig,
    EngineState,
)
from core.ai_knowledge_engine.reasoning.inference import InferenceEngine
from core.ai_knowledge_engine.reasoning.hypothesis_builder import HypothesisBuilder
from core.ai_knowledge_engine.reasoning.conclusion_engine import ConclusionEngine


@pytest.fixture
async def reasoning_engine():
    engine = ReasoningEngine()
    await engine.initialize()
    yield engine
    await engine.stop()


@pytest.mark.asyncio
async def test_reasoning_engine_initialize_and_stop():
    engine = ReasoningEngine()
    assert engine.state == EngineState.STOPPED
    await engine.initialize()
    assert engine.state == EngineState.RUNNING
    await engine.stop()
    assert engine.state == EngineState.STOPPED


@pytest.mark.asyncio
async def test_reasoning_engine_reason_basic():
    engine = ReasoningEngine()
    await engine.initialize()
    chain = await engine.reason(["revenue_up", "market_expanding"])
    assert chain.completed is True
    assert chain.conclusion is not None
    assert 0.0 <= chain.confidence <= 1.0
    assert len(chain.steps) > 0
    await engine.stop()


@pytest.mark.asyncio
async def test_reasoning_engine_analyze():
    engine = ReasoningEngine()
    await engine.initialize()
    result = await engine.analyze({"premises": ["revenue_up", "costs_down"]})
    assert "chain_id" in result
    assert "analysis" in result
    await engine.stop()


@pytest.mark.asyncio
async def test_reasoning_engine_compare():
    engine = ReasoningEngine()
    await engine.initialize()
    items = [
        {"name": "A", "health": "good", "growth": "high"},
        {"name": "B", "health": "bad", "growth": "low"},
    ]
    results = await engine.compare(items, ["health", "growth"])
    assert len(results) == 2
    assert results[0]["confidence"] >= results[1]["confidence"]
    await engine.stop()


@pytest.mark.asyncio
async def test_reasoning_engine_evaluate():
    engine = ReasoningEngine()
    await engine.initialize()
    result = await engine.evaluate("company_is_healthy", ["revenue_up", "customer_satisfaction_high"])
    assert "verdict" in result
    assert "confidence" in result
    await engine.stop()


@pytest.mark.asyncio
async def test_inference_engine_deductive_reasoning():
    engine = InferenceEngine()
    await engine.initialize()
    result = await engine.deductive_reasoning(["all_premises_true", "revenue_up"])
    assert result["method"] == "deductive"
    assert len(result["conclusions"]) > 0
    await engine.stop()


@pytest.mark.asyncio
async def test_inference_engine_inductive_reasoning():
    engine = InferenceEngine()
    await engine.initialize()
    result = await engine.inductive_reasoning(["sales_increased", "profit_increased", "customers_increased"])
    assert result["method"] == "inductive"
    assert result["confidence"] > 0.0
    await engine.stop()


@pytest.mark.asyncio
async def test_inference_engine_abductive_reasoning():
    engine = InferenceEngine()
    await engine.initialize()
    result = await engine.abductive_reasoning(
        "system_is_slow",
        ["server_overloaded", "network_latency", "database_bottleneck"],
    )
    assert result["method"] == "abductive"
    assert result["best_explanation"] is not None
    await engine.stop()


@pytest.mark.asyncio
async def test_hypothesis_builder_build_and_alternatives():
    builder = HypothesisBuilder()
    await builder.initialize()
    hypothesis = await builder.build_hypothesis(["revenue_up", "market_expanding"])
    assert "id" in hypothesis
    assert "hypothesis" in hypothesis
    alternatives = await builder.generate_alternatives(hypothesis, count=3)
    assert len(alternatives) == 3
    await builder.stop()


@pytest.mark.asyncio
async def test_hypothesis_builder_rank_and_evidence():
    builder = HypothesisBuilder()
    await builder.initialize()
    h1 = await builder.build_hypothesis(["revenue_up"])
    h2 = await builder.build_hypothesis(["costs_down", "competition_increasing"])
    ranked = await builder.rank_hypotheses([h1, h2])
    assert len(ranked) == 2
    supporting = await builder.get_supporting_evidence(h1)
    contradicting = await builder.get_contradicting_evidence(h1)
    assert isinstance(supporting, list)
    assert isinstance(contradicting, list)
    await builder.stop()


@pytest.mark.asyncio
async def test_conclusion_engine_draw_and_evaluate():
    engine = ConclusionEngine()
    await engine.initialize()
    hypothesis = {"hypothesis": "company_is_growing", "confidence": 0.8}
    result = await engine.draw_conclusion(
        ["revenue_up", "market_expanding", "customer_satisfaction_high"],
        hypothesis,
    )
    assert "id" in result
    assert result["confidence"] > 0.0
    evaluation = await engine.evaluate_conclusion(result["id"])
    assert "valid" in evaluation
    await engine.stop()


@pytest.mark.asyncio
async def test_conclusion_engine_compare_and_summarize():
    engine = ConclusionEngine()
    await engine.initialize()
    hypo = {"hypothesis": "test", "confidence": 0.7}
    r1 = await engine.draw_conclusion(["revenue_up"], hypo)
    r2 = await engine.draw_conclusion(["costs_down"], hypo)
    compared = await engine.compare_conclusions([r1["id"], r2["id"]])
    assert len(compared) == 2
    summary = await engine.summarize_findings([r1["id"], r2["id"]])
    assert "overall_confidence" in summary
    await engine.stop()


@pytest.mark.asyncio
async def test_reasoning_engine_get_reasoning_chain():
    engine = ReasoningEngine()
    await engine.initialize()
    chain = await engine.reason(["revenue_up"])
    retrieved = await engine.get_reasoning_chain(chain.chain_id)
    assert retrieved is not None
    assert retrieved.chain_id == chain.chain_id
    await engine.stop()


@pytest.mark.asyncio
async def test_inference_engine_get_confidence():
    engine = InferenceEngine()
    await engine.initialize()
    conf = await engine.get_confidence("company_growing")
    assert conf == 0.85
    unknown_conf = await engine.get_confidence("unknown_conclusion")
    assert unknown_conf == 0.1
    await engine.stop()
