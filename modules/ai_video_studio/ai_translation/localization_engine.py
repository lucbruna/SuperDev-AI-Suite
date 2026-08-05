"""Localization Engine — locale-aware formatting for translated content."""
from __future__ import annotations

from datetime import date, datetime

_LOCALES: dict[str, dict] = {
    "pt-BR": {"decimal": ",", "thousands": ".", "date_fmt": "%d/%m/%Y",
              "currency": "R$ {value}", "currency_locale": "pt_BR"},
    "en-US": {"decimal": ".", "thousands": ",", "date_fmt": "%m/%d/%Y",
              "currency": "${value}", "currency_locale": "en_US"},
    "es-ES": {"decimal": ",", "thousands": ".", "date_fmt": "%d/%m/%Y",
              "currency": "{value} €", "currency_locale": "es_ES"},
    "fr-FR": {"decimal": ",", "thousands": " ", "date_fmt": "%d/%m/%Y",
              "currency": "{value} €", "currency_locale": "fr_FR"},
    "de-DE": {"decimal": ",", "thousands": ".", "date_fmt": "%d.%m.%Y",
              "currency": "{value} €", "currency_locale": "de_DE"},
    "ja-JP": {"decimal": ".", "thousands": ",", "date_fmt": "%Y/%m/%d",
              "currency": "¥{value}", "currency_locale": "ja_JP"},
}

_DEFAULTS = _LOCALES["en-US"]


class LocalizationEngine:
    """Formats numbers, dates and currency per locale."""

    def __init__(self, locale: str = "en-US") -> None:
        self.locale = locale
        self.cfg = _LOCALES.get(locale, _DEFAULTS)

    def number(self, value: float, *, decimals: int = 2) -> str:
        formatted = f"{value:.{decimals}f}"
        whole, _, frac = formatted.partition(".")
        whole = self._group(whole)
        return whole if decimals == 0 else f"{whole}{self.cfg['decimal']}{frac}"

    def _group(self, digits: str) -> str:
        out = []
        while digits:
            out.append(digits[-3:])
            digits = digits[:-3]
        return self.cfg["thousands"].join(reversed(out))

    def date(self, value: date | datetime | None = None) -> str:
        value = value or date.today()
        return value.strftime(self.cfg["date_fmt"])

    def currency(self, value: float, *, symbol: str | None = None) -> str:
        formatted = self.number(value)
        template = self.cfg["currency"]
        if symbol:
            template = template.replace("R$", symbol).replace("$", symbol).replace("€", symbol).replace("¥", symbol)
        return template.format(value=formatted)

    def list_locales(self) -> list[str]:
        return sorted(_LOCALES)
