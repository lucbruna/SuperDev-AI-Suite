from __future__ import annotations

import pytest

from core.ai_knowledge_engine.validation.source_checker import SourceChecker
from core.ai_knowledge_engine.validation.confidence_score import ConfidenceScorer
from core.ai_knowledge_engine.validation.fact_checker import FactChecker
from core.ai_knowledge_engine.validation.validation_engine import (
    ValidationEngine,
    EngineConfig,
    EngineState,
)


@pytest.fixture
def source_checker() -> SourceChecker:
    return SourceChecker()


@pytest.fixture
def confidence_scorer() -> ConfidenceScorer:
    return ConfidenceScorer()


@pytest.fixture
def fact_checker() -> FactChecker:
    return FactChecker()


@pytest.fixture
async def engine() -> ValidationEngine:
    eng = ValidationEngine()
    await eng.initialize()
    yield eng
    await eng.stop()


@pytest.mark.asyncio
async def test_source_checker_verify_valid_url(source_checker: SourceChecker) -> None:
    result = await source_checker.verify_url("https://wikipedia.org/wiki/Python")
    assert result["verified"] is True
    assert result["has_scheme"] is True
    assert result["has_domain"] is True


@pytest.mark.asyncio
async def test_source_checker_verify_invalid_url(source_checker: SourceChecker) -> None:
    result = await source_checker.verify_url("not-a-url")
    assert result["verified"] is False
    assert result["has_scheme"] is False


@pytest.mark.asyncio
async def test_source_checker_reliability_known_domain(source_checker: SourceChecker) -> None:
    result = await source_checker.check_reliability("https://arxiv.org/paper")
    assert result["score"] == 0.95
    assert result["source"] == "known"


@pytest.mark.asyncio
async def test_source_checker_reliability_unknown_domain(source_checker: SourceChecker) -> None:
    result = await source_checker.check_reliability("https://example-unknown.com/page")
    assert result["score"] == 0.40
    assert result["source"] == "unknown"


@pytest.mark.asyncio
async def test_confidence_scorer_high_confidence(confidence_scorer: ConfidenceScorer) -> None:
    content = "A " * 300
    score = await confidence_scorer.calculate_confidence("test_id", content, 0.95, "verified")
    assert score >= 0.7


@pytest.mark.asyncio
async def test_confidence_scorer_breakdown(confidence_scorer: ConfidenceScorer) -> None:
    content = "Short."
    await confidence_scorer.calculate_confidence("breakdown_id", content, 0.5, "unverified")
    breakdown = await confidence_scorer.get_confidence_breakdown("breakdown_id")
    assert "source_quality" in breakdown
    assert "evidence" in breakdown
    assert "consistency" in breakdown
    assert "final_confidence" in breakdown


@pytest.mark.asyncio
async def test_fact_checker_verified_claim(fact_checker: FactChecker) -> None:
    result = await fact_checker.verify_claim("The Earth is round")
    assert result["status"] == "verified"
    assert result["is_true"] is True


@pytest.mark.asyncio
async def test_fact_checker_contradicted_claim(fact_checker: FactChecker) -> None:
    result = await fact_checker.verify_claim("The Sun orbits the Earth")
    assert result["status"] == "contradicted"
    assert result["is_true"] is False


@pytest.mark.asyncio
async def test_fact_checker_unverified_claim(fact_checker: FactChecker) -> None:
    result = await fact_checker.verify_claim("Some random unknown claim")
    assert result["status"] == "unverified"


@pytest.mark.asyncio
async def test_fact_checker_supporting_evidence(fact_checker: FactChecker) -> None:
    evidence = await fact_checker.find_supporting_evidence("Water boils at 100 degrees Celsius at sea level")
    assert len(evidence) >= 1
    assert evidence[0]["type"] == "supporting"


@pytest.mark.asyncio
async def test_fact_checker_contradicting_evidence(fact_checker: FactChecker) -> None:
    evidence = await fact_checker.find_contradicting_evidence("The Sun orbits the Earth")
    assert len(evidence) >= 1
    assert evidence[0]["type"] == "contradicting"


@pytest.mark.asyncio
async def test_validation_engine_initialize_and_stop(engine: ValidationEngine) -> None:
    assert engine.state == EngineState.READY


@pytest.mark.asyncio
async def test_validation_engine_full_validation(engine: ValidationEngine) -> None:
    result = await engine.validate(
        "knowledge_1",
        "The Earth is round and water boils at 100 degrees Celsius.",
        "https://wikipedia.org/wiki/Python",
    )
    assert result.is_valid is True
    assert result.confidence_score >= 0.5


@pytest.mark.asyncio
async def test_validation_engine_low_confidence(engine: ValidationEngine) -> None:
    engine.config.min_confidence_threshold = 0.9
    result = await engine.validate(
        "knowledge_2",
        "Short",
        "https://reddit.com/r/unknown",
    )
    assert result.is_valid is False


@pytest.mark.asyncio
async def test_validation_engine_history(engine: ValidationEngine) -> None:
    await engine.validate("hist_1", "Content A", "https://arxiv.org/a")
    await engine.validate("hist_2", "Content B", "https://arxiv.org/b")
    history = await engine.get_validation_history(5)
    assert len(history) == 2
    assert history[0].knowledge_id == "hist_1"
    assert history[1].knowledge_id == "hist_2"


@pytest.mark.asyncio
async def test_validation_engine_metrics(engine: ValidationEngine) -> None:
    await engine.validate("m1", "Test content here", "https://arxiv.org/x")
    await engine.validate("m2", "More test content here", "https://arxiv.org/y")
    assert engine.metrics.total_validations == 2
    assert engine.metrics.sources_checked == 2


@pytest.mark.asyncio
async def test_validation_engine_validate_source(engine: ValidationEngine) -> None:
    result = await engine.validate_source("https://github.com/user/repo")
    assert result["verified"] is True
    assert "score" in result


@pytest.mark.asyncio
async def test_source_checker_cache(source_checker: SourceChecker) -> None:
    result1 = await source_checker.check_source("https://nature.com/article")
    result2 = await source_checker.check_source("https://nature.com/article")
    assert result1["url"] == result2["url"]
    assert result1["score"] == result2["score"]


@pytest.mark.asyncio
async def test_confidence_scorer_contradiction_penalty(confidence_scorer: ConfidenceScorer) -> None:
    score_fact = await confidence_scorer.calculate_confidence("cp1", "Content", 0.8, "verified")
    score_no_fact = await confidence_scorer.calculate_confidence("cp2", "Content", 0.8, "unverified")
    assert score_fact >= score_no_fact


@pytest.mark.asyncio
async def test_fact_checker_check_fact(fact_checker: FactChecker) -> None:
    result = await fact_checker.check_fact("kid1", "Python is a compiled language")
    assert result["status"] == "contradicted"
    assert result["is_true"] is False


@pytest.mark.asyncio
async def test_fact_checker_get_verification_status(fact_checker: FactChecker) -> None:
    await fact_checker.check_fact("vs1", "The Earth is round")
    status = await fact_checker.get_verification_status("vs1")
    assert status["status"] == "verified"