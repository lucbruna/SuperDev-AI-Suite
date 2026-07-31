"""Central reasoning engine coordinating all reasoning subsystems."""

from __future__ import annotations

from typing import Any

from .decision import DecisionEngine
from .deduction import DeductionEngine
from .evaluation import ReasoningEvaluator
from .hypothesis import HypothesisManager
from .inference import InferenceEngine
from .verification import VerificationEngine


class ReasoningEngine:
    """Central reasoning engine coordinating inference, deduction, evaluation,
    decision making, hypothesis management, and verification."""

    def __init__(self) -> None:
        self._inference = InferenceEngine()
        self._deduction = DeductionEngine()
        self._evaluator = ReasoningEvaluator()
        self._decision = DecisionEngine()
        self._hypothesis = HypothesisManager()
        self._verification = VerificationEngine()
        self._reasoning_count: int = 0

    @property
    def inference(self) -> InferenceEngine:
        return self._inference

    @property
    def deduction(self) -> DeductionEngine:
        return self._deduction

    @property
    def evaluator(self) -> ReasoningEvaluator:
        return self._evaluator

    @property
    def decision(self) -> DecisionEngine:
        return self._decision

    @property
    def hypothesis(self) -> HypothesisManager:
        return self._hypothesis

    def reason(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        self._reasoning_count += 1
        facts = context or {}
        inferred = self._inference.infer(problem, facts)
        deductions = self._deduction.deduce(problem, facts)
        hypotheses = self._hypothesis.generate(problem, context)
        evaluated = []
        for h in hypotheses:
            score = self._evaluator.evaluate(h, facts)
            evaluated.append({"hypothesis": h, "score": score})
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        best = evaluated[0] if evaluated else None
        decision = self._decision.decide(
            {
                "problem": problem,
                "inferences": inferred,
                "deductions": deductions,
                "hypotheses": evaluated,
                "best": best,
            }
        )
        conclusion_str = decision.get("chosen", problem) if isinstance(decision, dict) else str(decision)
        verified_result = self._verification.verify(conclusion_str, facts) if best else {"verified": False}
        verified = verified_result.get("verified", False)
        return {
            "problem": problem,
            "inferences": inferred,
            "deductions": deductions,
            "hypotheses": evaluated,
            "decision": decision,
            "verified": verified,
            "confidence": best["score"] if best else 0.0,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"total_reasoning": self._reasoning_count}
