"""Pronunciation Engine — spelling rules and overrides for accurate TTS.

The engine rewrites acronyms and tricky words before synthesis so the voice
reads them the intended way (e.g. ``"AI"`` → ``"A I"``, ``"e.g."`` →
``"for example"``).
"""
from __future__ import annotations

import re

# Common words TTS engines mispronounce — mapped to a spelled/simplified form.
PRONUNCIATIONS: dict[str, str] = {
    "ai": "A I",
    "llm": "L L M",
    "api": "A P I",
    "ui": "U I",
    "gpu": "G P U",
    "cpu": "C P U",
    "http": "H T T P",
    "https": "H T T P S",
    "url": "U R L",
    "id": "I D",
    "e.g.": "for example",
    "i.e.": "that is",
    "etc.": "etcetera",
    "vs.": "versus",
    "approx.": "approximately",
    "dept.": "department",
    "apt.": "apartment",
    "est.": "established",
    "min.": "minutes",
    "max.": "maximum",
    "sq.": "square",
    "fig.": "figure",
    "no.": "number",
    "mon.": "Monday",
    "tue.": "Tuesday",
    "wed.": "Wednesday",
    "thu.": "Thursday",
    "fri.": "Friday",
    "sat.": "Saturday",
    "sun.": "Sunday",
}

_ACRONYM_RE = re.compile(r"\b([A-Z]{2,6})\b")


def apply_pronunciations(text: str) -> str:
    """Rewrite known words; spell out 2-6 letter uppercase acronyms."""
    lowered = text
    for key, value in PRONUNCIATIONS.items():
        lowered = re.sub(rf"\b{re.escape(key)}\b", value, lowered, flags=re.IGNORECASE)

    def _spell(match: re.Match[str]) -> str:
        word = match.group(1)
        if word.lower() in {"i", "a"}:
            return word
        return " ".join(word)

    return _ACRONYM_RE.sub(_spell, lowered)


def add_override(word: str, pronunciation: str) -> None:
    PRONUNCIATIONS[word.lower()] = pronunciation
