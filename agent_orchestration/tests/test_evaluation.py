"""Tests for the evaluation/ subpackage (Volume 31, Fase 5)."""

from __future__ import annotations

from agent_orchestration.evaluation import (AccuracyScorer, EvaluationEngine,
                                            FeedbackCollector,
                                            PerformanceTracker, QualityScorer)


class TestPerformanceTracker:
    def test_record_and_summary(self):
        tracker = PerformanceTracker()
        tracker.record("a1", 1.0, True)
        tracker.record("a1", 3.0, False)
        summary = tracker.summary("a1")
        assert summary["count"] == 2
        assert summary["successes"] == 1
        assert summary["errors"] == 1
        assert summary["average_time"] == 2.0

    def test_empty_summary(self):
        assert PerformanceTracker().average_time("nobody") == 0.0
        assert PerformanceTracker().count() == 0


class TestAccuracyScorer:
    def test_score_exact_match(self):
        scorer = AccuracyScorer()
        assert scorer.score("a1", 42, 42) == 1.0
        assert scorer.score("a1", 42, 41) == 0.0

    def test_accuracy_and_errors(self):
        scorer = AccuracyScorer()
        scorer.score("a1", "x", "x")
        scorer.score("a1", "y", "z")
        scorer.score("a1", "w", "w")
        assert scorer.accuracy("a1") == 2 / 3
        assert scorer.errors("a1") == 1
        assert scorer.count("a1") == 3

    def test_empty_accuracy(self):
        assert AccuracyScorer().accuracy("nobody") == 0.0


class TestQualityScorer:
    def test_score_weights(self):
        scorer = QualityScorer(max_errors=10, time_baseline=5.0)
        perfect = scorer.score(1.0, 0, 0.0)
        assert perfect > 0.9
        poor = scorer.score(0.0, 10, 5.0)
        assert poor < 0.2

    def test_label_bands(self):
        assert QualityScorer.label(0.95) == "excellent"
        assert QualityScorer.label(0.8) == "good"
        assert QualityScorer.label(0.6) == "acceptable"
        assert QualityScorer.label(0.3) == "poor"


class TestFeedbackCollector:
    def test_add_and_latest(self):
        collector = FeedbackCollector()
        collector.add("a1", "melhorou")
        collector.add("a1", "revisar auth", source="review")
        assert collector.latest("a1") == "revisar auth"
        assert collector.count("a1") == 2

    def test_list_filters(self):
        collector = FeedbackCollector()
        collector.add("a1", "x")
        collector.add("a2", "y")
        assert len(collector.list("a1")) == 1
        assert len(collector.list()) == 2


class TestEvaluationEngine:
    def test_evaluate_produces_report(self):
        engine = EvaluationEngine()
        engine.record("a1", 1.0, True)
        engine.record("a1", 2.0, False)
        engine.score_accuracy("a1", "ok", "ok")
        engine.score_accuracy("a1", "bad", "good")
        engine.add_feedback("a1", "bom")
        report = engine.evaluate("a1")
        assert report.agent_id == "a1"
        assert report.accuracy == 0.5
        assert report.errors == 1
        assert report.avg_time == 1.5
        assert report.feedback == "bom"
        assert report.quality_score > 0
        assert report.evaluation_id.startswith("eval")

    def test_evaluate_empty_agent(self):
        report = EvaluationEngine().evaluate("nobody")
        assert report.quality_score == 0.0

    def test_stats(self):
        engine = EvaluationEngine()
        engine.record("a1", 0.5, True)
        stats = engine.stats()
        assert stats["agents"] == 1
        assert "ao.evaluations_recorded" in stats["metrics"]
