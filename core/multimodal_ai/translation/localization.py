from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


LOCALE_SETTINGS: dict[str, dict[str, Any]] = {
    "en-US": {"date_format": "%m/%d/%Y", "currency": "USD", "currency_symbol": "$", "decimal_sep": ".", "thousands_sep": ","},
    "en-GB": {"date_format": "%d/%m/%Y", "currency": "GBP", "currency_symbol": "£", "decimal_sep": ".", "thousands_sep": ","},
    "pt-BR": {"date_format": "%d/%m/%Y", "currency": "BRL", "currency_symbol": "R$", "decimal_sep": ",", "thousands_sep": "."},
    "es-ES": {"date_format": "%d/%m/%Y", "currency": "EUR", "currency_symbol": "€", "decimal_sep": ",", "thousands_sep": "."},
    "fr-FR": {"date_format": "%d/%m/%Y", "currency": "EUR", "currency_symbol": "€", "decimal_sep": ",", "thousands_sep": " "},
    "de-DE": {"date_format": "%d.%m.%Y", "currency": "EUR", "currency_symbol": "€", "decimal_sep": ",", "thousands_sep": "."},
    "ja-JP": {"date_format": "%Y/%m/%d", "currency": "JPY", "currency_symbol": "¥", "decimal_sep": ".", "thousands_sep": ","},
}

LOCALIZED_STRINGS: dict[str, dict[str, str]] = {
    "en-US": {"greeting": "Hello", "farewell": "Goodbye", "yes": "Yes", "no": "No", "submit": "Submit"},
    "pt-BR": {"greeting": "Olá", "farewell": "Tchau", "yes": "Sim", "no": "Não", "submit": "Enviar"},
    "es-ES": {"greeting": "Hola", "farewell": "Adiós", "yes": "Sí", "no": "No", "submit": "Enviar"},
    "fr-FR": {"greeting": "Bonjour", "farewell": "Au revoir", "yes": "Oui", "no": "Non", "submit": "Soumettre"},
    "de-DE": {"greeting": "Hallo", "farewell": "Tschüss", "yes": "Ja", "no": "Nein", "submit": "Einreichen"},
    "ja-JP": {"greeting": "こんにちは", "farewell": "さようなら", "yes": "はい", "no": "いいえ", "submit": "送信"},
}


class Localizer:
    def __init__(self) -> None:
        self._locale_settings = LOCALE_SETTINGS
        self._strings = LOCALIZED_STRINGS

    def localize_content(self, content: str, locale: str) -> str:
        locale_strings = self._strings.get(locale, self._strings.get("en-US", {}))
        localized = content
        for key, value in locale_strings.items():
            localized = localized.replace(f"{{{{{key}}}}}", value)
        return localized

    def format_date(self, date: datetime, locale: str = "en-US") -> str:
        settings = self._locale_settings.get(locale, self._locale_settings["en-US"])
        return date.strftime(settings["date_format"])

    def format_currency(self, amount: float, locale: str = "en-US") -> str:
        settings = self._locale_settings.get(locale, self._locale_settings["en-US"])
        symbol = settings["currency_symbol"]
        if locale == "ja-JP":
            return f"{symbol}{int(amount):,}"
        formatted = f"{amount:,.2f}"
        return f"{symbol}{formatted}"

    def format_number(self, number: float, locale: str = "en-US") -> str:
        settings = self._locale_settings.get(locale, self._locale_settings["en-US"])
        dec = settings["decimal_sep"]
        th = settings["thousands_sep"]
        parts = f"{number:,.2f}".replace(",", "␟").replace(".", "␞")
        parts = parts.replace("␟", th).replace("␞", dec)
        return parts

    def get_locale_settings(self, locale: str) -> Optional[dict[str, Any]]:
        return self._locale_settings.get(locale)

    def get_localized_string(self, key: str, locale: str = "en-US") -> Optional[str]:
        locale_strings = self._strings.get(locale, {})
        return locale_strings.get(key)
