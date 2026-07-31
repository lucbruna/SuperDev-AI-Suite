"""Schema-to-schema mapping with type conversion."""

from __future__ import annotations

from typing import Any

from .normalizer import Normalizer

_TYPE_CONVERTERS = {
    "str": lambda n, v: n.to_str(v),
    "int": lambda n, v: n.to_int(v),
    "float": lambda n, v: n.to_float(v),
    "bool": lambda n, v: n.to_bool(v),
    "date": lambda n, v: n.to_date(v),
}


class SchemaMapper:
    """Converts records from a source schema to a target schema."""

    def __init__(self) -> None:
        self._normalizer = Normalizer()
        self._field_types: dict[str, str] = {}
        self._rename: dict[str, str] = {}
        self._include: list[str] = []
        self._exclude: set[str] = set()

    def field(self, name: str, type_name: str = "str", rename_to: str | None = None,
              include: bool = True) -> None:
        self._field_types[name] = type_name
        self._include.append(name)
        if rename_to:
            self._rename[name] = rename_to

    def exclude(self, name: str) -> None:
        self._exclude.add(name)

    def convert(self, record: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name, type_name in self._field_types.items():
            if name in self._exclude or name not in record:
                continue
            converter = _TYPE_CONVERTERS.get(type_name, _TYPE_CONVERTERS["str"])
            value = converter(self._normalizer, record[name])
            target = self._rename.get(name, name)
            result[target] = value
        return result
