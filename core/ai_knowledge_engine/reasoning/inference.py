from __future__ import annotations

import logging
import random
from typing import Any, Optional

logger = logging.getLogger(__name__)


_INFERENCE_RULES: dict[str, list[dict[str, Any]]] = {
    "business": [
        {"pattern": "revenue_up", "conclusion": "company_growing", "confidence": 0.85},
        {"pattern": "costs_down", "conclusion": "profitability_improving", "confidence": 0.80},
        {"pattern": "market_expanding", "conclusion": "growth_opportunity", "confidence": 0.75},
        {"pattern": "customer_satisfaction_high", "conclusion": "strong_retention", "confidence": 0.90},
        {"pattern": "competition_increasing", "conclusion": "margin_pressure", "confidence": 0.70},
    ],
    "technical": [
        {"pattern": "test_coverage_high", "conclusion": "code_quality_good", "confidence": 0.80},
        {"pattern": "response_time_low", "conclusion": "system_performant", "confidence": 0.85},
        {"pattern": "error_rate_high", "conclusion": "stability_risk", "confidence": 0.75},
    ],
    "general": [
        {"pattern": "all_premises_true", "conclusion": "logically_valid", "confidence": 0.95},
        {"pattern": "contradiction_found", "conclusion": "logically_invalid", "confidence": 0.90},
    ],
}


class InferenceEngine:
    def __init__(self) -> None:
        self._rules = _INFERENCE_RULES
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("InferenceEngine initialized")

    async def stop(self) -> None:
        self._initialized = False
        logger.info("InferenceEngine stopped")

    def _match_rules(self, premises: list[str], category: str) -> list[dict[str, Any]]:
        results = []
        rules = self._rules.get(category, [])
        for rule in rules:
            for premise in premises:
                if rule["pattern"] in premise.lower().replace(" ", "_"):
                    results.append({
                        "conclusion": rule["conclusion"],
                        "confidence": rule["confidence"],
                        "rule_category": category,
                    })
                    break
        return results

    async def infer(self, premises: list[str]) -> dict[str, Any]:
        conclusions = []
        for category in self._rules:
            conclusions.extend(self._match_rules(premises, category))

        if not conclusions:
            conclusions.append({
                "conclusion": "no_matching_rule",
                "confidence": 0.1,
                "rule_category": "fallback",
            })

        return {
            "premises": premises,
            "conclusions": [c["conclusion"] for c in conclusions],
            "details": conclusions,
            "method": "rule_based",
        }

    async def deductive_reasoning(self, premises: list[str], rules: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
        used_rules = rules or self._rules.get("general", [])
        conclusions = []
        for rule in used_rules:
            condition = rule.get("pattern", "")
            if any(condition in p.lower().replace(" ", "_") for p in premises):
                conclusions.append({
                    "conclusion": rule["conclusion"],
                    "confidence": rule["confidence"],
                    "type": "deductive",
                })

        if not conclusions:
            conclusions.append({
                "conclusion": "no_deduction_possible",
                "confidence": 0.0,
                "type": "deductive",
            })

        return {"premises": premises, "conclusions": conclusions, "method": "deductive"}

    async def inductive_reasoning(self, observations: list[str]) -> dict[str, Any]:
        if not observations:
            return {"observations": [], "generalization": "no_data", "confidence": 0.0}

        patterns = {}
        for obs in observations:
            for word in obs.lower().split():
                patterns[word] = patterns.get(word, 0) + 1

        common = sorted(patterns.items(), key=lambda x: -x[1])[:3]
        generalization = f"observed_pattern: {'_'.join(w for w, _ in common)}" if common else "no_pattern"

        confidence = min(0.5 + len(observations) * 0.1, 0.95)

        return {
            "observations": observations,
            "generalization": generalization,
            "confidence": confidence,
            "method": "inductive",
        }

    async def abductive_reasoning(self, observation: str, possible_explanations: list[str]) -> dict[str, Any]:
        best_explanation = None
        best_score = -1.0

        for explanation in possible_explanations:
            score = self._calculate_plausibility(observation, explanation)
            if score > best_score:
                best_score = score
                best_explanation = explanation

        return {
            "observation": observation,
            "best_explanation": best_explanation,
            "plausibility": best_score,
            "alternatives": possible_explanations,
            "method": "abductive",
        }

    async def get_confidence(self, conclusion: str) -> float:
        for category, rules in self._rules.items():
            for rule in rules:
                if rule["conclusion"] == conclusion:
                    return rule["confidence"]
        return 0.1

    def _calculate_plausibility(self, observation: str, explanation: str) -> float:
        overlap = len(set(observation.lower().split()) & set(explanation.lower().split()))
        total = max(len(set(observation.lower().split()) | set(explanation.lower().split())), 1)
        return overlap / total * random.uniform(0.8, 1.0)
