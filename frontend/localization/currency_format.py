from __future__ import annotations

_SYMBOLS: dict[str, dict[str, str]] = {
    "pt_BR": {"symbol": "R$", "decimal": ",", "thousands": "."},
    "en_US": {"symbol": "$", "decimal": ".", "thousands": ","},
    "es_ES": {"symbol": "€", "decimal": ",", "thousands": "."},
}


class CurrencyFormatter:
    """Formats currency values per locale."""

    def format(self, value: float, currency: str, locale: str = "en_US") -> str:
        style = _SYMBOLS.get(locale, _SYMBOLS["en_US"])
        symbol = style["symbol"] if currency == "locale" else (currency + " ")
        sign = "-" if value < 0 else ""
        amount = abs(value)
        whole = int(amount)
        cents = int(round((amount - whole) * 100))
        whole_str = f"{whole:,}".replace(",", style["thousands"])
        body = f"{whole_str}{style['decimal']}{cents:02d}"
        if locale == "pt_BR":
            return f"{sign}{symbol} {body}"
        return f"{sign}{symbol}{body}"
