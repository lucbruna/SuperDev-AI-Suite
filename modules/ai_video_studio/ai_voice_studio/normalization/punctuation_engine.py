"""Punctuation Engine — normalizes punctuation so voices read naturally."""
from __future__ import annotations

import re
import unicodedata

_SMART_QUOTES = {
    "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
    "\u201a": "'", "\u201b": "'", "\u00ab": '"', "\u00bb": '"',
}

_MULTI_SPACES = re.compile(r"\s+")


def normalize_punctuation(text: str) -> str:
    """Normalize smart quotes, dashes, spacing and duplicate punctuation."""
    text = unicodedata.normalize("NFKC", text)
    for smart, plain in _SMART_QUOTES.items():
        text = text.replace(smart, plain)
    text = text.replace("\u2013", "-").replace("\u2014", " - ")
    # "Hello!!" → "Hello!" and "???" → "?"
    text = re.sub(r"[!]{2,}", "!", text)
    text = re.sub(r"[?]{2,}", "?", text)
    text = re.sub(r"[.]{3,}", "\u2026", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)          # no space before punctuation
    text = re.sub(r"([,.;:!?])(?=[A-Za-z])", r"\1 ", text)  # space after punctuation
    return _MULTI_SPACES.sub(" ", text).strip()
