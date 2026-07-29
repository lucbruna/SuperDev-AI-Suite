from typing import Any

import re


class LanguageProcessor:
    def __init__(self) -> None:
        self._supported_languages: dict[str, str] = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh": "Chinese",
        }

    def analyze_syntax(self, text: str) -> dict[str, Any]:
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        words = text.split()
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "average_word_length": sum(len(w) for w in words) / max(len(words), 1),
            "sentences": sentences,
        }

    def extract_entities(self, text: str) -> list[dict[str, str]]:
        entities: list[dict[str, str]] = []
        patterns: dict[str, str] = {
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "PHONE": r"\+?\d[\d\s\-()]{7,}\d",
            "URL": r"https?://[^\s]+",
            "DATE": r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
            "ORDER_ID": r"ORD-\d{6}",
        }
        for label, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append({"text": match.group(), "label": label})
        return entities

    def detect_language(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()
        lang_signals: dict[str, list[str]] = {
            "en": ["the", "is", "and", "to", "in", "it", "you"],
            "es": ["el", "la", "es", "y", "en", "lo", "de", "un"],
            "fr": ["le", "la", "est", "et", "en", "je", "de", "un"],
            "de": ["der", "die", "ist", "und", "zu", "ich", "das"],
            "zh": ["的", "是", "了", "在", "我", "有", "和"],
        }
        scores: dict[str, int] = {}
        for lang, signals in lang_signals.items():
            scores[lang] = sum(1 for s in signals if s in text_lower)
        detected = max(scores, key=scores.get) if scores else "en"
        return {
            "language": detected,
            "language_name": self._supported_languages.get(detected, "Unknown"),
            "confidence": scores[detected] / max(len(text_lower.split()), 1),
        }

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b\w+\b", text)

    def lemmatize(self, word: str) -> str:
        simple_map: dict[str, str] = {
            "running": "run",
            "ran": "run",
            "runs": "run",
            "better": "good",
            "best": "good",
            "bigger": "big",
            "biggest": "big",
            "went": "go",
            "goes": "go",
            "going": "go",
            "gone": "go",
            "having": "have",
            "has": "have",
            "had": "have",
            "making": "make",
            "made": "make",
            "saying": "say",
            "said": "say",
            "getting": "get",
            "got": "get",
            "gotten": "get",
            "doing": "do",
            "did": "do",
            "done": "do",
            "seeing": "see",
            "saw": "see",
            "seen": "see",
            "knowing": "know",
            "knew": "know",
            "known": "know",
            "taking": "take",
            "took": "take",
            "taken": "take",
            "thinking": "think",
            "thought": "think",
            "coming": "come",
            "came": "come",
            "giving": "give",
            "gave": "give",
            "given": "give",
            "finding": "find",
            "found": "find",
            "telling": "tell",
            "told": "tell",
            "using": "use",
            "used": "use",
            "working": "work",
            "worked": "work",
            "calling": "call",
            "called": "call",
            "trying": "try",
            "tried": "try",
            "asking": "ask",
            "asked": "ask",
        }
        return simple_map.get(word.lower(), word)
