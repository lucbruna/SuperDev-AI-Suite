"""Terminology Engine — applies glossaries and protects brand terminology.

Before translation, protected terms are placeheld so the LLM doesn't
translate them; after translation they are restored from the glossary.
"""
from __future__ import annotations

import re

from modules.ai_video_studio.ai_translation.glossary_manager import GlossaryManager

_PLACEHOLDER_RE = re.compile(r"__TERM_(\d+)__")


class TerminologyEngine:
    """Glossary-aware terminology handling around translation."""

    def __init__(self, glossary: GlossaryManager | None = None) -> None:
        self.glossary = glossary or GlossaryManager()

    def protect(self, text: str, source: str, target: str) -> tuple[str, list[str]]:
        """Replace protected terms with placeholders; return them for restore."""
        terms = sorted(self.glossary.terms(source, target), key=len, reverse=True)
        protected: list[str] = []
        out = text
        for i, term in enumerate(terms):
            if not term.strip():
                continue
            pattern = rf"\b{re.escape(term)}\b"
            if re.search(pattern, out, flags=re.IGNORECASE):
                out = re.sub(pattern, f"__TERM_{i}__", out, flags=re.IGNORECASE)
                protected.append(term)
        return out, protected

    def restore(self, translated: str, protected: list[str], source: str, target: str) -> str:
        """Put the glossary translations back into the translated text."""
        for i, term in enumerate(protected):
            value = self.glossary.lookup(source, target, term) or term
            translated = translated.replace(f"__TERM_{i}__", value)
        return translated
