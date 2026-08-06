"""Typed state store for the Digital Twin module."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config.constants import TWIN_OUT_OF_SYNC, TWIN_SYNCED


@dataclass(slots=True)
class TwinState:
    """Key/value state store with dirty tracking."""

    _values: dict[str, object] = field(default_factory=dict)
    _dirty: set[str] = field(default_factory=set)

    def set(self, key: str, value: object) -> None:
        self._values[key] = value
        self._dirty.add(key)

    def get(self, key: str, default: object = None) -> object:
        return self._values.get(key, default)

    def delete(self, key: str) -> None:
        if key in self._values:
            del self._values[key]
            self._dirty.add(key)

    def has(self, key: str) -> bool:
        return key in self._values

    def dirty_keys(self) -> set[str]:
        return set(self._dirty)

    def mark_clean(self, key: str | None = None) -> None:
        if key is None:
            self._dirty.clear()
        else:
            self._dirty.discard(key)

    def to_dict(self) -> dict[str, object]:
        return dict(self._values)

    def from_dict(self, values: dict[str, object]) -> None:
        self._values = dict(values)
        self._dirty.clear()

    @property
    def twin_status(self) -> str:
        return str(self.get("twin_status", TWIN_SYNCED))

    def set_twin_status(self, status: str) -> None:
        self.set("twin_status", status)

    def mark_out_of_sync(self) -> None:
        self.set_twin_status(TWIN_OUT_OF_SYNC)
