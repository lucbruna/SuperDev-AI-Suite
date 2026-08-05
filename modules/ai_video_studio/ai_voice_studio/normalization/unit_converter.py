"""Unit Converter — turns measurements into spoken words (en, pt)."""
from __future__ import annotations

import re

from modules.ai_video_studio.ai_voice_studio.normalization.number_reader import number_to_words

# unit (regex-safe) → {en: singular/plural, pt: singular/plural}
_UNITS = {
    "km": ("kilometer", "kilometers", "quilômetro", "quilômetros"),
    "km/h": ("kilometers per hour", "kilometers per hour", "quilômetros por hora", "quilômetros por hora"),
    "m": ("meter", "meters", "metro", "metros"),
    "cm": ("centimeter", "centimeters", "centímetro", "centímetros"),
    "mm": ("millimeter", "millimeters", "milímetro", "milímetros"),
    "kg": ("kilogram", "kilograms", "quilo", "quilos"),
    "g": ("gram", "grams", "grama", "gramas"),
    "mg": ("milligram", "milligrams", "miligrama", "miligramas"),
    "l": ("liter", "liters", "litro", "litros"),
    "ml": ("milliliter", "milliliters", "mililitro", "mililitros"),
    "m²": ("square meter", "square meters", "metro quadrado", "metros quadrados"),
    "°c": ("degrees Celsius", "degrees Celsius", "graus Celsius", "graus Celsius"),
    "°f": ("degrees Fahrenheit", "degrees Fahrenheit", "graus Fahrenheit", "graus Fahrenheit"),
    "%": ("percent", "percent", "por cento", "por cento"),
    "mb": ("megabyte", "megabytes", "megabyte", "megabytes"),
    "gb": ("gigabyte", "gigabytes", "gigabyte", "gigabytes"),
    "hz": ("hertz", "hertz", "hertz", "hertz"),
    "khz": ("kilohertz", "kilohertz", "quilohertz", "quilohertz"),
    "s": ("second", "seconds", "segundo", "segundos"),
    "min": ("minute", "minutes", "minuto", "minutos"),
    "h": ("hour", "hours", "hora", "horas"),
}

# Longest units first so "km/h" wins over "km" and "m²" over "m".
_ORDERED_UNITS = sorted(_UNITS, key=len, reverse=True)
_UNIT_RE = re.compile(rf"\b(\d+(?:[.,]\d+)?)\s*({'|'.join(re.escape(u) for u in _ORDERED_UNITS)})\b", re.IGNORECASE)


def read_units(text: str, language: str = "en") -> str:
    """Replace measurements like ``10 km`` with spoken words."""
    lang = language.lower().split("-")[0]

    def _replace(match: re.Match[str]) -> str:
        raw_number, raw_unit = match.group(1), match.group(2)
        unit = raw_unit.lower()
        en_s, en_p, pt_s, pt_p = _UNITS.get(unit, (raw_unit, raw_unit, raw_unit, raw_unit))
        try:
            value = float(raw_number.replace(",", "."))
        except ValueError:
            return match.group(0)
        singular = value == 1
        word = (en_s if singular else en_p) if lang == "en" else (pt_s if singular else pt_p)
        return f"{number_to_words(value, language)} {word}"

    return _UNIT_RE.sub(_replace, text)
