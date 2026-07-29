from __future__ import annotations

from typing import Any, Optional


SUPPORTED_LANGUAGES = {
    "en": "English",
    "pt": "Portuguese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ru": "Russian",
}

LANGUAGE_KEYWORDS: dict[str, list[str]] = {
    "en": ["the", "is", "and", "are", "was", "were", "have", "has", "been", "would", "could", "hello", "goodbye", "please", "thank"],
    "pt": ["o", "a", "os", "as", "um", "uma", "e", "que", "de", "do", "da", "em", "para", "com", "como", "olá", "tchau"],
    "es": ["el", "la", "los", "las", "un", "una", "y", "que", "de", "del", "en", "para", "por", "con", "como", "hola", "adiós"],
    "fr": ["le", "la", "les", "un", "une", "des", "et", "que", "qui", "de", "du", "en", "pour", "avec", "bonjour", "au revoir"],
    "de": ["der", "die", "das", "ein", "eine", "und", "ist", "sind", "war", "werden", "haben", "für", "mit", "hallo", "tschüss"],
    "it": ["il", "la", "le", "gli", "un", "una", "e", "che", "di", "del", "in", "per", "con", "come", "ciao", "arrivederci"],
    "ja": ["です", "ます", "した", "いる", "ある", "こと", "もの", "ため", "とき", "する", "なる", "いう", "できる"],
    "zh": ["的", "是", "了", "在", "有", "和", "不", "就", "这", "那", "也", "都", "要", "会", "着", "没有", "因为"],
    "ru": ["и", "в", "не", "на", "что", "с", "а", "как", "его", "она", "они", "быть", "это", "мы", "вы", "он"],
}


class LanguageDetector:
    def __init__(self) -> None:
        self._languages = dict(SUPPORTED_LANGUAGES)

    def detect_language(self, text: str) -> str:
        return self._score_languages(text)[0][0]

    def detect_multiple(self, text: str, top_n: int = 3) -> list[dict[str, Any]]:
        scores = self._score_languages(text)
        return [
            {"language": lang, "score": score, "name": self._languages[lang]}
            for lang, score in scores[:top_n]
        ]

    def get_confidence(self, text: str) -> float:
        scores = self._score_languages(text)
        if not scores:
            return 0.0
        top_score = scores[0][1]
        total = sum(s for _, s in scores) or 1
        return round(top_score / total, 4)

    def get_supported_languages(self) -> dict[str, str]:
        return dict(self._languages)

    def _score_languages(self, text: str) -> list[tuple[str, int]]:
        if not text.strip():
            return [("en", 0)]
        words = text.lower().split()
        scores: list[tuple[str, int]] = []
        for lang, keywords in LANGUAGE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in words)
            scores.append((lang, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
