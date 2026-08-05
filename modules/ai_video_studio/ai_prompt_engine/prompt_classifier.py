"""Prompt classifier — classify prompt intent and type by heuristics."""
from __future__ import annotations

from typing import Any

INTENT_KEYWORDS: dict[str, list[str]] = {
    "advertise": ["propaganda", "anuncio", "ads", "advert", "campanha", "promote", "marketing"],
    "educate": ["explicar", "ensinar", "tutorial", "curso", "educar", "learn", "teach", "explain", "how to"],
    "document": ["documentario", "historia", "story", "documentary", "history"],
    "sell": ["vender", "produto", "oferta", "preco", "sell", "product", "offer", "buy"],
    "entertain": ["entreter", "divertir", "entertain", "fun", "humor"],
    "inform": ["noticia", "resumo", "news", "informar", "report", "inform"],
}

TYPE_KEYWORDS: dict[str, list[str]] = {
    "video": ["video", "clip", "reels", "reel", "short"],
    "advertisement": ["ads", "anuncio", "comercial", "propaganda"],
    "tutorial": ["tutorial", "como", "passo a passo", "step by step", "how to"],
    "presentation": ["apresentacao", "slides", "slideshow", "presentation"],
    "documentary": ["documentario", "documentary"],
    "story": ["historia", "story", "narrativa"],
    "explainer": ["explicar", "explain", "what is"],
}


class PromptClassifier:
    """Deterministic prompt classification into intent and type."""

    def classify(self, prompt: str) -> dict[str, Any]:
        text = (prompt or "").lower()
        intents = sorted(
            (name for name, kws in INTENT_KEYWORDS.items() if any(k in text for k in kws)),
            key=lambda n: sum(1 for k in INTENT_KEYWORDS[n] if k in text),
            reverse=True,
        )
        types = sorted(
            (name for name, kws in TYPE_KEYWORDS.items() if any(k in text for k in kws)),
            key=lambda n: sum(1 for k in TYPE_KEYWORDS[n] if k in text),
            reverse=True,
        )
        return {
            "intent": intents[0] if intents else "generic",
            "intents": intents,
            "type": types[0] if types else "general",
            "types": types,
            "language": self.detect_language(text),
            "word_count": len(text.split()),
        }

    @staticmethod
    def detect_language(text: str) -> str:
        pt = ("para", "você", "como", "uma", "dos", "das", "nao", "não", "sobre", "com")
        en = ("the", "and", "for", "with", "how", "you", "make", "create", "video")
        if sum(1 for w in pt if w in text) > sum(1 for w in en if w in text):
            return "pt"
        if any(w in text for w in en):
            return "en"
        return "unknown"


_prompt_classifier: PromptClassifier | None = None


def get_prompt_classifier() -> PromptClassifier:
    global _prompt_classifier
    if _prompt_classifier is None:
        _prompt_classifier = PromptClassifier()
    return _prompt_classifier
