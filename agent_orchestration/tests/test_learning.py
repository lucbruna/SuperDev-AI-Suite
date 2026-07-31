"""Tests for the learning/ subpackage (Volume 31, Fase 6)."""

from __future__ import annotations

from agent_orchestration.learning import (BehaviorOptimizer, FeedbackProcessor,
                                          ImprovementTracker, LearningEngine)
from agent_orchestration.orchestrator_models import EvaluationReport


class TestFeedbackProcessor:
    def test_kind_detection(self):
        processor = FeedbackProcessor()
        assert processor.process("a1", "corrigir o login")["kind"] == "fix"
        assert processor.process("a1", "otimizar a consulta")[
            "kind"] == "optimize"
        assert processor.process("a1", "documentar a api")[
            "kind"] == "document"
        assert processor.process("a1", "parece ok")["kind"] == "general"

    def test_by_kind_and_count(self):
        processor = FeedbackProcessor()
        processor.process("a1", "testar mais o módulo")
        processor.process("a2", "erro ao salvar")
        processor.process("a1", "tudo certo")
        assert len(processor.by_kind("test")) == 1
        assert len(processor.by_kind("fix")) == 1
        assert processor.count() == 3

    def test_sentences_split(self):
        entry = FeedbackProcessor().process("a1", "Erro A. Corrigir B!")
        assert entry["sentences"][0] == "Erro A"
        assert "Corrigir B" in entry["sentences"][1]


class TestImprovementTracker:
    def test_record_and_list(self):
        tracker = ImprovementTracker()
        entry = tracker.record("a1", "adicionar cache", kind="optimize")
        assert entry["improvement_id"].startswith("improve")
        assert len(tracker.list("a1")) == 1
        assert tracker.list("a2") == []

    def test_mark_applied(self):
        tracker = ImprovementTracker()
        entry = tracker.record("a1", "x")
        assert tracker.mark_applied(entry["improvement_id"]) is True
        assert tracker.applied_count() == 1
        assert tracker.mark_applied("nope") is False


class TestBehaviorOptimizer:
    def test_apply_low_quality_raises_retries(self):
        optimizer = BehaviorOptimizer()
        report = EvaluationReport(evaluation_id="e", agent_id="a1",
                                  quality_score=0.3)
        changes = optimizer.apply(report)
        assert changes.get("max_retries") == 4
        assert optimizer.params["max_retries"] == 4

    def test_apply_high_quality_no_changes(self):
        optimizer = BehaviorOptimizer()
        report = EvaluationReport(evaluation_id="e", agent_id="a1",
                                  quality_score=0.95, avg_time=0.1)
        assert optimizer.apply(report) == {}
        assert optimizer.count() == 0

    def test_timeout_scales(self):
        optimizer = BehaviorOptimizer()
        report = EvaluationReport(evaluation_id="e", agent_id="a1",
                                  quality_score=0.9, avg_time=8.0)
        changes = optimizer.apply(report)
        assert changes.get("timeout") == 15.0

    def test_risk_tolerance_lowers_on_errors(self):
        optimizer = BehaviorOptimizer()
        report = EvaluationReport(evaluation_id="e", agent_id="a1",
                                  quality_score=0.7, errors=3)
        changes = optimizer.apply(report)
        assert changes.get("risk_tolerance") == 0.4


class TestLearningEngine:
    def test_learn_from_feedback(self):
        engine = LearningEngine()
        improvement = engine.learn_from_feedback("a1", "corrigir o bug")
        assert improvement["kind"] == "fix"
        assert engine.metrics.snapshot()["counters"].get(
            "ao.improvements") == 1
        assert engine.metrics.snapshot()["counters"].get(
            "ao.feedback_processed") == 1

    def test_optimize_flow(self):
        engine = LearningEngine()
        report = EvaluationReport(evaluation_id="e", agent_id="a1",
                                  quality_score=0.2)
        changes = engine.optimize(report)
        assert changes["max_retries"] == 4
        assert engine.metrics.snapshot()["counters"].get(
            "ao.behavior_changes") == 1

    def test_record_lesson(self):
        engine = LearningEngine()
        lesson = engine.record_lesson("a1", "auth", "401", "add token")
        assert lesson.topic == "auth"
        assert lesson.lesson_id.startswith("lesson")

    def test_stats(self):
        engine = LearningEngine()
        engine.process_feedback("a1", "otimizar tudo")
        engine.improvements.record("a1", "x")
        stats = engine.stats()
        assert stats["feedback"] == 1
        assert stats["improvements"] == 1
        assert "metrics" in stats
