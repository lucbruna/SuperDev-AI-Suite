from __future__ import annotations

import datetime
from typing import Any

_FORMATS: dict[str, str] = {
    "pt_BR": "%d/%m/%Y",
    "en_US": "%m/%d/%Y",
    "es_ES": "%d/%m/%Y",
}


class DateFormatter:
    """Formats dates per locale."""

    def format(self, value: Any, locale: str = "en_US") -> str:
        if isinstance(value, (int, float)):
            date = datetime.datetime.fromtimestamp(value)
        elif isinstance(value, datetime.datetime):
            date = value
        elif isinstance(value, datetime.date):
            date = datetime.datetime.combine(value, datetime.time())
        else:
            raise TypeError(f"unsupported date value: {type(value)!r}")
        return date.strftime(_FORMATS.get(locale, _FORMATS["en_US"]))
