from __future__ import annotations

import logging
from typing import Any

from .currency_format import CurrencyFormatter
from .date_format import DateFormatter


class LanguageEngine:
    """Resolves locales and translates keys into localized strings."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.localization")
        self._translations: dict[str, dict[str, str]] = {}
        self._fallback = "en_US"
        self._current = "en_US"
        self.date = DateFormatter()
        self.currency = CurrencyFormatter()

    def register(self, locale: str, messages: dict[str, str]) -> None:
        self._translations[locale] = dict(messages)

    def set_locale(self, locale: str) -> bool:
        if locale not in self._translations:
            return False
        self._current = locale
        return True

    def locale(self) -> str:
        return self._current

    def locales(self) -> list[str]:
        return list(self._translations)

    def translate(self, key: str, **params: Any) -> str:
        table = self._translations.get(self._current, {})
        message = table.get(key)
        if message is None:
            fallback = self._translations.get(self._fallback, {}).get(key)
            message = fallback if fallback is not None else key
        return message.format(**params) if "{" in message else message

    def t(self, key: str, **params: Any) -> str:
        return self.translate(key, **params)

    def format_date(self, value: Any) -> str:
        return self.date.format(value, locale=self._current)

    def format_currency(self, value: float, currency: str) -> str:
        return self.currency.format(value, currency, locale=self._current)
