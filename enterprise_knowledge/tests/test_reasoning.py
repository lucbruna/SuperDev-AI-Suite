"""Tests for the reasoning/ subsystem (Volume 27, Fase 8)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.memory.memory_engine import MemoryEngine
from enterprise_knowledge.reasoning.explanation import ExplanationGenerator
from enterprise_knowledge.reasoning.hypothesis import HypothesisGenerator
from enterprise_knowledge.reasoning.inference import InferenceEngine
from enterprise_knowledge.reasoning.reasoning_engine import ReasoningEngine
from enterprise_knowledge.reasoning.recommendation import RecommendationEngine


@pytest.fixture
def engine():
    engine = build_engine()
    memory = MemoryEngine(events=engine.events, metrics=engine.metrics,
                          config=engine.config, security=engine.security,
                          registry=engine.registry)
    engine.attach_subsystem("memory_engine", memory)
    engine.attach_subsystem(
        "reasoning_engine",
        ReasoningEngine(events=engine.events, metrics=engine.metrics,
                        config=engine.config, security=engine.security,
                        memory=memory))
    return engine


class TestInferenceEngine:
    def test_rule_fires(self):
        inference = InferenceEngine()
        inference.add_rule(["postgresql", "lento"], "criar índice",
                           confidence=0.9)
        results = inference.infer(
            ["o postgresql está lento", "relatório de performance"])
        assert any(r["conclusion"] == "criar índice" for r in results)

    def test_rule_requires_all_antecedents(self):
        inference = InferenceEngine()
        inference.add_rule(["a", "b"], "conclusão")
        assert inference.infer(["apenas a"]) == []

    def test_no_repeat_conclusions(self):
        inference = InferenceEngine()
        inference.add_rule(["x"], "y")
        assert len(inference.infer(["x", "x"])) == 1

    def test_rules_count(self):
        inference = InferenceEngine()
        inference.add_rule(["a"], "b")
        assert inference.rules_count() == 1


class TestHypothesisGenerator:
    def test_generates_signal_hypothesis(self):
        generator = HypothesisGenerator()
        hypotheses = generator.generate("problema de performance")
        assert any(h["signal"] == "performance" for h in hypotheses)

    def test_generates_general_when_no_signal(self):
        generator = HypothesisGenerator()
        hypotheses = generator.generate("tema totalmente novo")
        assert hypotheses[0]["signal"] == "general"

    def test_refine_updates_confidence(self):
        generator = HypothesisGenerator()
        hypothesis = {"confidence": 0.5}
        assert generator.refine(hypothesis, True)["confidence"] == 0.65
        assert generator.refine(hypothesis, False)["confidence"] == 0.5


class TestRecommendationEngine:
    def test_recommends_from_evidence(self):
        recommendations = RecommendationEngine()
        hits = recommendations.recommend(
            ["relatório de performance", "o postgresql está lento"])
        assert any("índice" in h["action"] for h in hits)

    def test_empty_evidence(self):
        assert RecommendationEngine().recommend([]) == []

    def test_always(self):
        recommendations = RecommendationEngine()
        assert recommendations.always("agir")[0]["action"] == "agir"


class TestExplanationGenerator:
    def test_explanation_includes_evidence_and_confidence(self):
        explanation = ExplanationGenerator().explain(
            "por que lento?", "criar índice",
            evidence=["query lenta"], confidence=0.8)
        assert "por que lento?" in explanation
        assert "criar índice" in explanation
        assert "80%" in explanation

    def test_explain_without_evidence(self):
        explanation = ExplanationGenerator().explain("q", "c")
        assert "concluímos: c" in explanation

    def test_bullets(self):
        assert ExplanationGenerator().bullets(["a"]) == ["- a"]


class TestReasoningEngine:
    def test_reason_with_memory_evidence(self, engine):
        engine.memory_engine.remember(
            "performance do postgresql do ERP caiu após o deploy")
        result = engine.reasoning_engine.reason("problema de performance")
        assert result.conclusion
        assert result.evidence
        assert any("postgresql" in e for e in result.evidence)

    def test_reason_falls_back_without_evidence(self, engine):
        result = engine.reasoning_engine.reason("assunto desconhecido")
        assert result.conclusion
        assert result.evidence == ["sem evidências diretas na memória"]
        assert result.confidence <= 0.95

    def test_inference_used_in_reasoning(self, engine):
        engine.reasoning_engine.inference.add_rule(
            ["performance", "deploy"], "reverter o deploy")
        result = engine.reasoning_engine.reason(
            "problema de performance",
            evidence=["performance degradou", "deploy recente"])
        assert result.conclusion == "reverter o deploy"

    def test_recommend(self, engine):
        hits = engine.reasoning_engine.recommend(
            "problema de performance",
            evidence=["performance degradou no ERP"])
        assert hits

    def test_metric_and_event(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.REASONING_COMPLETED,
                         lambda payload: seen.append(payload))
        engine.reasoning_engine.reason("questão qualquer")
        assert engine.metrics.snapshot()["counters"].get(
            "ek.reasonings", 0) == 1
        assert seen and seen[0]["question"] == "questão qualquer"

    def test_stats(self, engine):
        engine.reasoning_engine.reason("x")
        stats = engine.reasoning_engine.stats()
        assert stats["reasonings"] == 1
