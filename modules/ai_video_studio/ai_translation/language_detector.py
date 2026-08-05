"""Language Detector — stopword-based heuristic identification."""
from __future__ import annotations

import re

# A few high-frequency stopwords per language are enough for detection.
_STOPWORDS: dict[str, set[str]] = {
    "en": {"the", "and", "is", "of", "to", "in", "that", "it", "for", "with"},
    "pt": {"o", "a", "de", "do", "da", "que", "em", "e", "para", "com", "um", "uma"},
    "es": {"el", "la", "de", "que", "y", "en", "un", "una", "por", "con", "para"},
    "fr": {"le", "la", "de", "et", "est", "un", "une", "pour", "avec", "dans"},
    "de": {"der", "die", "das", "und", "ist", "ein", "eine", "für", "mit", "in"},
    "it": {"il", "lo", "la", "di", "che", "e", "un", "una", "per", "con"},
    "ja": {"の", "は", "を", "に", "が", "で", "と", "です", "ます"},
    "zh": {"的", "是", "了", "在", "和", "有", "就", "不", "人", "我"},
    "ko": {"의", "는", "을", "에", "가", "이", "도", "에서", "으로"},
    "ru": {"и", "в", "не", "на", "что", "с", "по", "это", "как", "для"},
    "ar": {"في", "من", "على", "أن", "إلى", "هذا", "هذه", "كان", "مع"},
    "hi": {"और", "का", "है", "में", "की", "से", "यह", "के", "एक"},
    "nl": {"de", "het", "een", "en", "van", "is", "dat", "voor", "met"},
    "pl": {"i", "w", "na", "z", "do", "to", "jest", "się", "nie", "że"},
    "sv": {"och", "är", "i", "att", "det", "som", "på", "en", "den"},
    "tr": {"ve", "bir", "bu", "ile", "için", "de", "da", "mi", "olarak"},
}

_ALPHA_RE = re.compile(r"[a-záàâãéêíóôõúüçñ'-]+")


def detect_language(text: str, *, sample: int = 400) -> str:
    """Return the most likely ISO-639-1 language code ('' when unknown)."""
    if not text or not text.strip():
        return ""
    lowered = text[:sample].lower()
    if _has_cjk(lowered):
        for lang in ("ja", "zh", "ko"):
            if lang == "zh" and any("\u4e00" <= ch <= "\u9fff" for ch in lowered):
                return "zh"
            if lang == "ja" and any("\u3040" <= ch <= "\u30ff" for ch in lowered):
                return "ja"
            if lang == "ko" and any("\uac00" <= ch <= "\ud7af" for ch in lowered):
                return "ko"
    words = _ALPHA_RE.findall(lowered)
    if not words:
        return ""
    scores: dict[str, int] = {}
    for word in words:
        for lang, stops in _STOPWORDS.items():
            if word in stops:
                scores[lang] = scores.get(lang, 0) + 1
    if not scores:
        return ""
    best = max(scores, key=scores.get)
    return best if scores[best] >= 1 else ""


def _has_cjk(text: str) -> bool:
    return any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" or "\uac00" <= ch <= "\ud7af" for ch in text)


def supported_languages() -> list[str]:
    return sorted(_STOPWORDS)
