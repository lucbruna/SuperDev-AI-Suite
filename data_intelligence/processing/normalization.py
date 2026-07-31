"""Normalization processors (names, emails, UFs)."""

from __future__ import annotations

import re
from typing import Any

from data_intelligence.processing.base import Processor

_UF_MAP = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
    "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}


class NameNormalizer(Processor):
    """Titles a name: ``JOAO SILVA`` -> ``Joao Silva``."""

    name = "name"

    def __init__(self, field: str = "name") -> None:
        self.field = field

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        value = out.get(self.field)
        if isinstance(value, str):
            out[self.field] = value.strip().title()
        return out


class EmailNormalizer(Processor):
    """Normalizes an email: lowercases and strips whitespace."""

    name = "email"

    def __init__(self, field: str = "email") -> None:
        self.field = field

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        value = out.get(self.field)
        if isinstance(value, str):
            out[self.field] = value.strip().lower()
        return out


class UfNormalizer(Processor):
    """Expands a Brazilian UF code to its full state name.

    ``SP`` -> ``São Paulo``. Accepts ``state`` or ``uf`` fields.
    """

    name = "uf"

    def __init__(self, field: str = "uf", output: str | None = None) -> None:
        self.field = field
        self.output = output or field

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        value = out.get(self.field)
        if isinstance(value, str):
            uf = value.strip().upper()
            if uf in _UF_MAP:
                out[self.output] = _UF_MAP[uf]
        return out


class PhoneNormalizer(Processor):
    """Keeps only digits of a phone number."""

    name = "phone"

    def __init__(self, field: str = "phone") -> None:
        self.field = field

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        value = out.get(self.field)
        if isinstance(value, str):
            out[self.field] = re.sub(r"\D", "", value)
        return out
