"""Glossary Manager — persistent term dictionaries for consistent translation."""
from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_GLOSSARY_FILE = Path(__file__).resolve().parent.parent.parent.parent / "downloads" / "glossary.json"


class GlossaryManager:
    """Stores and applies ``source → target`` term maps per language pair."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else _GLOSSARY_FILE
        self._glossary: dict[str, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                with open(self.path, encoding="utf-8") as f:
                    self._glossary = json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("glossary load failed: %s", e)

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._glossary, f, ensure_ascii=False, indent=2)
        except Exception as e:  # noqa: BLE001
            logger.warning("glossary save failed: %s", e)

    def _pair(self, source: str, target: str) -> str:
        return f"{source.lower()}:{target.lower()}"

    def add_term(self, source: str, target: str, translation: str) -> None:
        pair = self._pair(source, target)
        self._glossary.setdefault(pair, {})[source] = translation
        self._save()

    def add_terms(self, source: str, target: str, terms: dict[str, str]) -> int:
        pair = self._pair(source, target)
        self._glossary.setdefault(pair, {}).update(terms)
        self._save()
        return len(terms)

    def lookup(self, source: str, target: str, term: str) -> str | None:
        return self._glossary.get(self._pair(source, target), {}).get(term)

    def terms(self, source: str, target: str) -> dict[str, str]:
        return dict(self._glossary.get(self._pair(source, target), {}))

    def apply(self, text: str, source: str, target: str, *, case_sensitive: bool = False) -> str:
        """Replace glossary terms in text (longest-first to avoid partial hits)."""
        terms = self.terms(source, target)
        if not terms:
            return text
        import re

        ordered = sorted(terms, key=len, reverse=True)
        flags = 0 if case_sensitive else re.IGNORECASE
        for term in ordered:
            pattern = rf"\b{re.escape(term)}\b"
            text = re.sub(pattern, lambda _m, t=term: terms[t], text, flags=flags)
        return text
