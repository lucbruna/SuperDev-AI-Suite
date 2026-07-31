"""Document classification into knowledge categories."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize

_CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "code": {"def ", "class ", "import ", "function ", "const ", "var ",
             "return ", "sql"},
    "contract": {"contrato", "cláusula", "partes", "vigência", "clause",
                 "contract", "firmado"},
    "policy": {"política", "policy", "conformidade", "compliance",
               "regulamento", "norma"},
    "finance": {"fatura", "invoice", "imposto", "tax", "receita", "revenue",
                "orçamento", "budget", "fiscal"},
    "meeting": {"ata", "reunião", "minutes", "pauta", "agenda",
                "participantes"},
    "report": {"relatório", "report", "resumo", "conclusão", "summary"},
    "training": {"treinamento", "training", "tutorial", "guia", "guide",
                 "manual"},
}


class DocumentClassifier:
    """Assigns a category and confidence to a document."""

    def __init__(self, categories: dict[str, set[str]] | None = None) -> None:
        self.categories = categories or _CATEGORY_KEYWORDS

    def classify(self, content: str, title: str = "") -> dict[str, Any]:
        text = f"{title}\n{content}".lower()
        scores: dict[str, int] = {}
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] = scores.get(category, 0) + 1
        if not scores:
            return {"category": "general", "confidence": 0.3,
                    "scores": {}}
        total = sum(scores.values())
        category = max(scores, key=lambda item: scores[item])  # type: ignore[arg-type]
        confidence = min(0.95, scores[category] / total)
        return {"category": category, "confidence": confidence,
                "scores": dict(scores)}

    def summarize(self, content: str, limit: int = 3) -> str:
        sentences = [s.strip() for s in
                     (content or "").replace("\n", " ").split(".") if s.strip()]
        if not sentences:
            return ""
        return ". ".join(sentences[:limit]) + "."
