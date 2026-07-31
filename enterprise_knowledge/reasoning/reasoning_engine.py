"""Reasoning engine: draws evidence-backed conclusions and recommendations."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_config import EnterpriseKnowledgeConfig
from enterprise_knowledge.knowledge_events import (EnterpriseKnowledgeEvents,
                                                   EnterpriseKnowledgeEventType)
from enterprise_knowledge.knowledge_logger import get_logger
from enterprise_knowledge.knowledge_metrics import EnterpriseKnowledgeMetrics
from enterprise_knowledge.knowledge_models import ReasoningResult
from enterprise_knowledge.knowledge_security import EnterpriseKnowledgeSecurity
from enterprise_knowledge.memory.memory_engine import MemoryEngine
from enterprise_knowledge.reasoning.explanation import ExplanationGenerator
from enterprise_knowledge.reasoning.hypothesis import HypothesisGenerator
from enterprise_knowledge.reasoning.inference import InferenceEngine
from enterprise_knowledge.reasoning.recommendation import RecommendationEngine


class ReasoningEngine:
    """Orquestrador de raciocínio (Fase 8 do Volume 27)."""

    def __init__(self, events: EnterpriseKnowledgeEvents | None = None,
                 metrics: EnterpriseKnowledgeMetrics | None = None,
                 config: EnterpriseKnowledgeConfig | None = None,
                 security: EnterpriseKnowledgeSecurity | None = None,
                 memory: MemoryEngine | None = None) -> None:
        self._log = get_logger("reasoning")
        self.events = events or EnterpriseKnowledgeEvents()
        self.metrics = metrics or EnterpriseKnowledgeMetrics()
        self.config = config or EnterpriseKnowledgeConfig()
        self.security = security or EnterpriseKnowledgeSecurity()
        self.memory = memory
        self.inference = InferenceEngine()
        self.hypotheses = HypothesisGenerator()
        self.recommendations = RecommendationEngine()
        self.explainer = ExplanationGenerator()

    def reason(self, question: str,
               evidence: list[str] | None = None) -> ReasoningResult:
        evidence = self._gather_evidence(question, evidence)
        derived = self.inference.infer(evidence)
        conclusions = [item["conclusion"] for item in derived]
        conclusion = self._conclude(question, evidence, conclusions)
        hypotheses = self.hypotheses.generate(question, evidence)
        explanation = self.explainer.explain(
            question, conclusion, evidence=evidence,
            confidence=self._confidence(evidence, derived))
        result = ReasoningResult(
            conclusion=conclusion,
            confidence=self._confidence(evidence, derived),
            evidence=list(evidence),
            explanation=explanation,
            hypotheses=hypotheses)
        self.metrics.increment("ek.reasonings")
        self.events.publish(EnterpriseKnowledgeEventType.REASONING_COMPLETED,
                            {"question": question,
                             "confidence": result.confidence})
        return result

    def _gather_evidence(self, question: str,
                         evidence: list[str] | None) -> list[str]:
        evidence = list(evidence or [])
        if self.memory is not None:
            for record in self.memory.recall(question, limit=5):
                evidence.append(record.content)
        if not evidence:
            evidence.append("sem evidências diretas na memória")
        return evidence

    @staticmethod
    def _conclude(question: str, evidence: list[str],
                  derived: list[str]) -> str:
        if derived:
            return derived[0]
        return f"não há conclusão suficiente sobre '{question}'"

    @staticmethod
    def _confidence(evidence: list[str], derived: list[dict[str, Any]]) -> float:
        base = 0.3 if len(evidence) >= 1 else 0.1
        boost = max([item["confidence"] for item in derived], default=0.0) * 0.5
        return min(0.95, base + boost + min(0.2, len(evidence) * 0.05))

    def recommend(self, question: str,
                  evidence: list[str] | None = None) -> list[dict[str, Any]]:
        evidence = self._gather_evidence(question, evidence)
        return self.recommendations.recommend(evidence)

    def stats(self) -> dict[str, Any]:
        return {"reasonings": self.metrics.snapshot()["counters"].get(
            "ek.reasonings", 0),
            "rules": self.inference.rules_count()}
