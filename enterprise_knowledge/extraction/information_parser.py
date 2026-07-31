"""Information parsing: pulls structured facts from text."""

from __future__ import annotations

import re
from typing import Any

from enterprise_knowledge.knowledge_protocols import coerce_number, tokenize


class InformationParser:
    """Extracts dates, numbers, percentages and currency-like amounts."""

    _DATE_RE = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
    _PERCENT_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*%")
    _MONEY_RE = re.compile(r"\b(R\$\s*)?(\d+(?:[.,]\d+){0,2})\b")
    _NUMBER_RE = re.compile(r"\b\d+(?:[.,]\d+)?\b")

    def parse(self, text: str) -> dict[str, Any]:
        return {
            "dates": self.dates(text),
            "numbers": self.numbers(text),
            "percentages": self.percentages(text),
            "amounts": self.amounts(text),
            "word_count": len(tokenize(text)),
        }

    def dates(self, text: str) -> list[str]:
        return [m.group(1) for m in self._DATE_RE.finditer(text)]

    def percentages(self, text: str) -> list[float]:
        return [coerce_number(m.group(1).replace(",", "."))
                for m in self._PERCENT_RE.finditer(text)]

    def amounts(self, text: str) -> list[float]:
        amounts = []
        for match in self._MONEY_RE.finditer(text):
            value = match.group(2)
            if "," in value and "." in value:
                value = value.replace(".", "").replace(",", ".")
            elif "," in value:
                value = value.replace(",", ".")
            amounts.append(coerce_number(value))
        return amounts

    def numbers(self, text: str) -> list[int]:
        return [int(m.group(0).replace(",", "").split(".")[0])
                for m in self._NUMBER_RE.finditer(text)]
