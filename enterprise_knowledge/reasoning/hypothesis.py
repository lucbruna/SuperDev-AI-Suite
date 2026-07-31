"""Hypothesis generation from observed signals."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_protocols import new_id


class HypothesisGenerator:
    """Builds plausible hypotheses from question + evidence hints."""

    def __init__(self) -> None:
        self._signal_patterns: dict[str, str] = {
            "performance": "o desempenho degradou",
            "erro": "ocorreu uma falha de software",
            "seguranca": "há um risco de segurança",
            "cust": "os custos aumentaram",
            "fiscal": "a regra fiscal mudou",
        }

    def generate(self, question: str,
                 evidence: list[str] | None = None) -> list[dict[str, Any]]:
        evidence = evidence or []
        question_lower = question.lower()
        hypotheses = []
        for signal, template in self._signal_patterns.items():
            if signal not in question_lower:
                continue
            hypotheses.append({
                "hypothesis_id": new_id("hypothesis"),
                "statement": f"Pode ser que {template}",
                "signal": signal,
                "evidence": [e for e in evidence
                             if signal in e.lower()],
                "confidence": 0.5,
            })
        if not hypotheses:
            hypotheses.append({
                "hypothesis_id": new_id("hypothesis"),
                "statement": f"Pode ser que o tema '{question}' precise de investigação",
                "signal": "general",
                "evidence": list(evidence),
                "confidence": 0.3,
            })
        return hypotheses

    def refine(self, hypothesis: dict[str, Any],
               confirming: bool) -> dict[str, Any]:
        confidence = hypothesis.get("confidence", 0.5)
        hypothesis["confidence"] = min(
            0.95, confidence + (0.15 if confirming else -0.15))
        return hypothesis
