"""Text classification for extraction routing."""

from __future__ import annotations

from typing import Any

_CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "code": {"def ", "class ", "import ", "function ", "const ", "return ",
             "sql", "select "},
    "finance": {"fatura", "imposto", "receita", "orçamento", "fiscal",
                "invoice", "tax", "budget"},
    "contract": {"contrato", "cláusula", "vigência", "partes", "contract"},
    "meeting": {"ata", "reunião", "pauta", "participantes", "minutes"},
    "support": {"erro", "bug", "problema", "incidente", "falha", "error"},
}


class TextClassifier:
    """Assigns a coarse category used to route extraction strategies."""

    def __init__(self) -> None:
        self.categories = {k: set(v)
                           for k, v in _CATEGORY_KEYWORDS.items()}

    def classify(self, text: str) -> dict[str, Any]:
        text_lower = (text or "").lower()
        scores: dict[str, int] = {}
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[category] = scores.get(category, 0) + 1
        if not scores:
            return {"category": "general", "confidence": 0.3,
                    "scores": {}}
        total = sum(scores.values())
        category = max(scores, key=lambda item: scores[item])  # type: ignore[arg-type]
        return {"category": category,
                "confidence": min(0.95, scores[category] / total),
                "scores": dict(scores)}
