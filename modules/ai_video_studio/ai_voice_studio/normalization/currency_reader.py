"""Currency Reader — converts monetary amounts to spoken words (en, pt)."""
from __future__ import annotations

import re

from modules.ai_video_studio.ai_voice_studio.normalization.number_reader import number_to_words

_CURRENCY_RE = re.compile(
    r"(?P<cur>\$\s?|R\$\s?|€\s?|£\s?|US\$\s?)(?P<amount>\d{1,9}(?:[.,]\d{1,2})?)",
    re.IGNORECASE,
)

_CURRENCY_NAMES = {
    "$": ("dollars", "cents", "dólares", "centavos"),
    "us$": ("dollars", "cents", "dólares", "centavos"),
    "r$": ("reais", "centavos", "reais", "centavos"),
    "€": ("euros", "cents", "euros", "centavos"),
    "£": ("pounds", "pence", "libras", "centavos"),
}


def read_currency(text: str, language: str = "en") -> str:
    """Replace currency amounts like ``$12.50`` with spoken words."""

    def _replace(match: re.Match[str]) -> str:
        cur_key = match.group("cur").strip().lower()
        names = _CURRENCY_NAMES.get(cur_key, _CURRENCY_NAMES["$"])
        lang = language.lower().split("-")[0]
        major, minor = (names[0], names[1]) if lang == "en" else (names[2], names[3])

        raw = match.group("amount")
        sep = "," if ("," in raw and lang == "pt") else "."
        if sep in raw:
            whole, frac = raw.split(sep)
            whole_n = int(whole)
            frac_n = int(frac)
        else:
            whole_n = int(raw)
            frac_n = 0

        whole_words = number_to_words(whole_n, language)
        if frac_n:
            frac_words = number_to_words(frac_n, language)
            conjunction = "and" if lang == "en" else "e"
            return f"{whole_words} {major} {conjunction} {frac_words} {minor}"
        return f"{whole_words} {major}"

    return _CURRENCY_RE.sub(_replace, text)
