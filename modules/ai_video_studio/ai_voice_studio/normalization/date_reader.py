"""Date Reader — converts dates/times to spoken words (en, pt)."""
from __future__ import annotations

import re

from modules.ai_video_studio.ai_voice_studio.normalization.number_reader import number_to_words

_MONTHS_EN = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
              7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
_MONTHS_PT = {1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
              7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"}
_ORDINAL_SUFFIX = {1: "st", 2: "nd", 3: "rd", 21: "st", 22: "nd", 23: "rd", 31: "st"}

_DATE_RE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")
_TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\b")


def _ordinal(day: int) -> str:
    suffix = _ORDINAL_SUFFIX.get(day, "th")
    return f"{day}{suffix}"


def read_dates(text: str, language: str = "en") -> str:
    """Replace dates and times with spoken forms."""
    lang = language.lower().split("-")[0]

    def _date(match: re.Match[str]) -> str:
        a, b, year = int(match.group(1)), int(match.group(2)), match.group(3)
        if lang == "pt" or a > 12:  # day/month order (pt-BR) or ambiguous
            day, month = a, b
        else:                       # month/day order (en-US)
            month, day = a, b
        month_name = (_MONTHS_PT if lang == "pt" else _MONTHS_EN).get(month, str(month))
        year_words = number_to_words(int(year), language) if lang == "en" and int(year) < 2100 else year
        if lang == "pt":
            return f"dia {number_to_words(day, language)} de {month_name} de {year_words}"
        return f"{month_name} {_ordinal(day)}, {year_words}"

    def _time(match: re.Match[str]) -> str:
        h, m = int(match.group(1)), int(match.group(2))
        if lang == "pt":
            return f"{number_to_words(h, 'pt')} e {number_to_words(m, 'pt')} minutos" if m else number_to_words(h, "pt")
        if m == 0:
            return f"{number_to_words(h)} o'clock"
        return f"{number_to_words(h)} {number_to_words(m)}"

    text = _DATE_RE.sub(_date, text)
    return _TIME_RE.sub(_time, text)
