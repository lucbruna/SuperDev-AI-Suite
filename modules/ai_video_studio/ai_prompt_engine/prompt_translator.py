"""Prompt translator — translate prompts between languages."""
from __future__ import annotations

from typing import Any

# Minimal phrase dictionary for common video-brief tokens (pt <-> en).
PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "video": "video", "sobre": "about", "energia solar": "solar energy",
        "explicar": "explain", "como funciona": "how it works", "vender": "sell",
        "produto": "product", "criar": "create", "fazer": "make", "um": "a",
        "uma": "a", "para": "for", "com": "with", "e": "and", "de": "of",
        "marketing": "marketing", "agricultura": "agriculture", "imovel": "property",
        "curso": "course", "empresa": "company",
    },
    "pt": {
        "video": "vídeo", "about": "sobre", "solar energy": "energia solar",
        "explain": "explicar", "how it works": "como funciona", "sell": "vender",
        "product": "produto", "create": "criar", "make": "fazer", "a": "um",
        "an": "um", "for": "para", "with": "com", "and": "e", "of": "de",
        "marketing": "marketing", "agriculture": "agricultura", "property": "imóvel",
        "course": "curso", "company": "empresa",
    },
}


class PromptTranslator:
    """Word/phrase-level prompt translation (deterministic, offline)."""

    SUPPORTED = ("en", "pt", "es", "fr", "de", "it", "ja", "zh")

    def translate(self, prompt: str, target_lang: str) -> dict[str, Any]:
        target_lang = target_lang.lower()
        if target_lang not in self.SUPPORTED:
            return {
                "translated": prompt,
                "target_lang": target_lang,
                "mode": "passthrough",
                "reason": f"unsupported language (supported: {', '.join(self.SUPPORTED)})",
            }
        if target_lang not in PHRASES:
            return {"translated": prompt, "target_lang": target_lang, "mode": "passthrough", "reason": "offline dictionary limited"}

        text = prompt or ""
        table = PHRASES[target_lang]
        translated = text
        for src, dst in table.items():
            translated = translated.replace(src, dst)
        return {
            "translated": translated,
            "target_lang": target_lang,
            "mode": "dictionary",
            "matched_terms": sum(1 for src in table if src in (prompt or "").lower()),
        }


_prompt_translator: PromptTranslator | None = None


def get_prompt_translator() -> PromptTranslator:
    global _prompt_translator
    if _prompt_translator is None:
        _prompt_translator = PromptTranslator()
    return _prompt_translator
