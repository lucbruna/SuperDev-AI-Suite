"""Number Reader — converts digits to spoken words (en, pt-BR)."""
from __future__ import annotations

import re

_ONES = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
    12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
}
_TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty",
         70: "seventy", 80: "eighty", 90: "ninety"}
_ORDINALS = {
    1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
    7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh",
    12: "twelfth", 13: "thirteenth", 20: "twentieth", 21: "twenty first",
    30: "thirtieth", 40: "fortieth", 50: "fiftieth", 100: "hundredth",
}

_ONES_PT = {
    0: "zero", 1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco",
    6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez", 11: "onze",
    12: "doze", 13: "treze", 14: "catorze", 15: "quinze", 16: "dezesseis",
    17: "dezessete", 18: "dezoito", 19: "dezenove",
}
_TENS_PT = {20: "vinte", 30: "trinta", 40: "quarenta", 50: "cinquenta",
            60: "sessenta", 70: "setenta", 80: "oitenta", 90: "noventa"}

_NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?")
_ORDINAL_RE = re.compile(r"\d+(?:st|nd|rd|th)\b", re.IGNORECASE)


def number_to_words(value: float | int, language: str = "en") -> str:
    """Convert a number to spoken words (supports en and pt)."""
    lang = language.lower().split("-")[0]
    table = _ONES if lang == "en" else _ONES_PT
    tens_table = _TENS if lang == "en" else _TENS_PT
    scale_hundred = "hundred" if lang == "en" else "centos"
    scale_thousand = "thousand" if lang == "en" else "mil"
    scale_million = "million" if lang == "en" else "milhão"

    integer = int(value)
    fraction = round((float(value) - integer) * 100)

    def _below_100(n: int) -> str:
        if n < 20:
            return table.get(n, str(n))
        t, r = divmod(n, 10)
        word = tens_table.get(t * 10, str(t * 10))
        return f"{word} {table[r]}" if r else word

    def _full(n: int) -> str:
        if n == 0:
            return table[0]
        parts: list[str] = []
        millions, rem = divmod(n, 1_000_000)
        if millions:
            parts.append(f"{_below_100(millions)} {scale_million}")
            n = rem
        thousands, rem = divmod(n, 1000)
        if thousands:
            prefix = _below_100(thousands) if thousands < 100 else f"{table[thousands // 100]} {scale_hundred} " + _below_100(thousands % 100)
            parts.append(f"{prefix} {scale_thousand}".strip())
            n = rem
        hundreds, rem = divmod(n, 100)
        if hundreds:
            parts.append(f"{table[hundreds]} {scale_hundred}")
            n = rem
        if n:
            parts.append(_below_100(n))
        return " ".join(parts)

    result = _full(integer)
    if fraction:
        unit = "point" if lang == "en" else "vírgula"
        frac_words = " ".join(table[int(d)] for d in f"{fraction:02d}")
        result = f"{result} {unit} {frac_words}".strip()
    return result or table[0]


def read_numbers(text: str, language: str = "en") -> str:
    """Replace numeric tokens in text with spoken words (ordinals first)."""
    text = _ORDINAL_RE.sub(
        lambda m: _ORDINALS.get(int(m.group(0)[:-2]), number_to_words(int(m.group(0)[:-2]), language))
        if language.startswith("en") else m.group(0),
        text,
    )

    def _replace(match: re.Match[str]) -> str:
        raw = match.group(0)
        try:
            if "." in raw:
                value = float(raw)
            elif "," in raw and language.startswith("pt"):
                value = float(raw.replace(",", "."))
            else:
                value = int(raw.replace(",", ""))
        except ValueError:
            return raw
        return number_to_words(value, language)

    return _NUMBER_RE.sub(_replace, text)
