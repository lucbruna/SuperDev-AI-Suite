import pytest

from core.ai_knowledge_engine.learning.learning_engine import (
    LearningEngine,
    EngineConfig,
    EngineState,
)
from core.ai_knowledge_engine.learning.feedback_manager import FeedbackManager
from core.ai_knowledge_engine.learning.experience_analyzer import ExperienceAnalyzer
from core.ai_knowledge_engine.learning.improvement_engine import ImprovementEngine


@pytest.fixture
async def learning_engine():
    engine = LearningEngine()
    await engine.initialize()
    yield engine
    await engine.stop()


@pytest.mark.asyncio
async def test_learning_engine_initialize_and_stop():
    engine = LearningEngine()
    assert engine.state == EngineState.STOPPED
    await engine.initialize()
    assert engine.state == EngineState.RUNNING
    await engine.stop()
    assert engine.state == EngineState.STOPPED


@pytest.mark.asyncio
async def test_learning_engine_learn_basic(learning_engine):
    result = await learning_engine.learn(
        {"source": "user_feedback"},
        {"rating": 5, "sentiment": "positive"},
    )
    assert "session_id" in result
    assert "feedback" in result
    assert "experience" in result
    assert "improvements" in result
    assert len(result["improvements"]) > 0


@pytest.mark.asyncio
async def test_learning_engine_apply_feedback(learning_engine):
    result = await learning_engine.apply_feedback({
        "source": "test",
        "rating": 2,
        "sentiment": "negative",
    })
    assert "feedback_id" in result
    assert "analysis" in result


@pytest.mark.asyncio
async def test_learning_engine_analyze_experience(learning_engine):
    result = await learning_engine.analyze_experience({
        "data": {"outcome": "success", "metrics": {"accuracy": 0.95}},
        "context": {"task": "classification"},
    })
    assert "id" in result
    assert result["outcome"] == "success"


@pytest.mark.asyncio
async def test_learning_engine_improve(learning_engine):
    result = await learning_engine.improve("accuracy", {"impact_score": 0.8})
    assert "id" in result
    assert result["status"] == "applied"


@pytest.mark.asyncio
async def test_learning_engine_get_learning_stats(learning_engine):
    await learning_engine.learn({"source": "test"}, {"rating": 4})
    await learning_engine.improve("speed", {"impact_score": 0.6})
    stats = await learning_engine.get_learning_stats()
    assert "metrics" in stats
    assert stats["metrics"]["total_learning_cycles"] >= 1
    assert stats["metrics"]["improvements_applied"] >= 1


@pytest.mark.asyncio
async def test_feedback_manager_register_and_analyze():
    mgr = FeedbackManager()
    await mgr.initialize()
    fid = await mgr.register_feedback({"source": "api", "rating": 1, "sentiment": "negative"})
    assert fid is not None
    analysis = await mgr.analyze_feedback(fid)
    assert analysis["is_negative"] is True
    assert analysis["requires_action"] is True
    await mgr.stop()


@pytest.mark.asyncio
async def test_feedback_manager_collect_and_summary():
    mgr = FeedbackManager()
    await mgr.initialize()
    await mgr.collect_feedback("system", {"rating": 5, "sentiment": "positive"})
    await mgr.collect_feedback("user", {"rating": 2, "sentiment": "negative"})
    summary = await mgr.get_feedback_summary()
    assert summary["total_feedback"] == 2
    assert summary["sentiment_breakdown"]["positive"] == 1
    assert summary["sentiment_breakdown"]["negative"] == 1
    await mgr.stop()


@pytest.mark.asyncio
async def test_experience_analyzer_analyze_and_extract():
    analyzer = ExperienceAnalyzer()
    await analyzer.initialize()
    exp = await analyzer.analyze_experience({"outcome": "failure"}, {"env": "prod"})
    lessons = await analyzer.extract_lessons(exp["id"])
    assert len(lessons) >= 1
    assert lessons[0]["outcome"] == "failure"
    await analyzer.stop()


@pytest.mark.asyncio
async def test_experience_analyzer_patterns_and_recommendations():
    analyzer = ExperienceAnalyzer()
    await analyzer.initialize()
    e1 = await analyzer.analyze_experience({"outcome": "success"}, {"env": "test"})
    e2 = await analyzer.analyze_experience({"outcome": "success"}, {"env": "prod"})
    e3 = await analyzer.analyze_experience({"outcome": "failure"}, {"env": "prod"})
    patterns = await analyzer.identify_patterns([e1, e2, e3])
    assert len(patterns) >= 1
    recs = await analyzer.generate_recommendations(e3)
    assert len(recs) >= 1
    assert recs[0]["type"] == "corrective"
    await analyzer.stop()


@pytest.mark.asyncio
async def test_improvement_engine_identify_and_apply():
    engine = ImprovementEngine()
    await engine.initialize()
    feedback = {"sentiment": "negative"}
    experience = {"outcome": "failure"}
    improvements = await engine.identify_improvements(feedback, experience)
    assert len(improvements) > 0
    assert improvements[0]["priority"] == "high"
    applied = await engine.apply_improvement("process", {"impact_score": 0.9})
    assert applied["status"] == "applied"
    await engine.stop()


@pytest.mark.asyncio
async def test_improvement_engine_measure_and_rollback():
    engine = ImprovementEngine()
    await engine.initialize()
    applied = await engine.apply_improvement("latency", {"impact_score": 0.7})
    impact = await engine.measure_impact(applied["id"])
    assert "measured_impact" in impact
    rollback = await engine.rollback_improvement(applied["id"])
    assert rollback["status"] == "rolled_back"
    history = await engine.get_improvement_history()
    assert len(history) == 1
    await engine.stop()
