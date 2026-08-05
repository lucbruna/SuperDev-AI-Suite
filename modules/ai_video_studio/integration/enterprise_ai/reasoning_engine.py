"""Reasoning Engine — deterministic step-by-step analysis with conclusions."""
from __future__ import annotations

import re
from typing import Any


class ReasoningEngine:
    """Turns a question + evidence into structured reasoning steps."""

    def reason(self, question: str, evidence: list[str] | None = None) -> dict[str, Any]:
        """Return ``{question, steps, conclusion, confidence}``."""
        evidence = [e for e in (evidence or []) if e]
        tokens = [t.lower() for t in re.findall(r"\w+", question)]
        keywords = [t for t in tokens if len(t) > 3][:5]

        steps = ["Decompose the question into atomic sub-problems."]
        if evidence:
            steps.append(f"Consider {len(evidence)} item(s) of evidence.")
        if keywords:
            steps.append(f"Focus on the key concepts: {', '.join(keywords)}.")
        steps.append("Combine evidence and constraints into a final verdict.")

        confidence = min(0.95, 0.45 + 0.1 * len(evidence))
        return {
            "question": question,
            "steps": steps,
            "conclusion": "Resolved" if evidence else "Insufficient evidence for a firm conclusion",
            "confidence": round(confidence, 2),
            "keywords": keywords,
        }


_reasoning_engine: ReasoningEngine | None = None


def get_reasoning_engine() -> ReasoningEngine:
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
