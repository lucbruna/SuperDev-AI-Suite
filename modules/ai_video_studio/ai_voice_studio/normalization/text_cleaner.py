"""Text Cleaner — the full normalization pipeline before synthesis.

Order matters: punctuation first, then structured values (dates, currency,
units) that contain numbers, then any remaining plain numbers.
"""
from __future__ import annotations

import re
import unicodedata

from modules.ai_video_studio.ai_voice_studio.normalization.punctuation_engine import normalize_punctuation
from modules.ai_video_studio.ai_voice_studio.normalization.abbreviation_expander import expand_abbreviations
from modules.ai_video_studio.ai_voice_studio.normalization.date_reader import read_dates
from modules.ai_video_studio.ai_voice_studio.normalization.currency_reader import read_currency
from modules.ai_video_studio.ai_voice_studio.normalization.unit_converter import read_units
from modules.ai_video_studio.ai_voice_studio.normalization.number_reader import read_numbers

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_MD_RE = re.compile(r"[*_`~#>|]+")


def normalize_text(text: str, language: str = "en") -> str:
    """Clean and expand text so TTS reads it naturally."""
    out = unicodedata.normalize("NFKC", text)
    out = _URL_RE.sub("link", out)
    out = _EMAIL_RE.sub("email", out)
    out = _MD_RE.sub(" ", out)
    out = normalize_punctuation(out)
    out = expand_abbreviations(out)
    out = read_dates(out, language)
    out = read_currency(out, language)
    out = read_units(out, language)
    out = read_numbers(out, language)
    return re.sub(r"\s+", " ", out).strip()
