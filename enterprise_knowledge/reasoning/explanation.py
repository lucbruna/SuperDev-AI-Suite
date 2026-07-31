"""Natural-language explanations for conclusions."""

from __future__ import annotations

from typing import Any


class ExplanationGenerator:
    """Builds readable explanations linking evidence to conclusions."""

    def explain(self, question: str, conclusion: str,
                evidence: list[str] | None = None,
                confidence: float = 0.0) -> str:
        evidence = evidence or []
        parts = [f"Sobre '{question}', concluímos: {conclusion}."]
        if evidence:
            bullet = "; ".join(evidence)
            parts.append(f"Evidências consideradas: {bullet}.")
        if confidence > 0:
            parts.append(f"Confiança estimada em {confidence:.0%}.")
        return " ".join(parts)

    def bullets(self, evidence: list[str]) -> list[str]:
        return [f"- {item}" for item in evidence]
