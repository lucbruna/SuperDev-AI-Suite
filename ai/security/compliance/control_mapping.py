"""Control mapping across standards."""
from __future__ import annotations

from typing import Any


class ControlMapping:
    def __init__(self) -> None:
        self._mappings: dict[str, dict[str, str]] = {}
        self._cross_refs: dict[str, set[str]] = {}
    def map_control(self, source_standard: str, source_control: str, target_standard: str, target_control: str) -> None:
        key = f"{source_standard}:{source_control}"
        self._mappings[key] = {"target_standard": target_standard, "target_control": target_control}
        self._cross_refs.setdefault(source_control, set()).add(target_control)
    def find_equivalent(self, standard: str, control: str) -> list[dict[str, str]]:
        key = f"{standard}:{control}"
        mapping = self._mappings.get(key)
        if mapping:
            return [mapping]
        return []
    def get_cross_references(self, control: str) -> list[str]:
        return sorted(self._cross_refs.get(control, set()))
    def map_batch(self, source_standard: str, target_standard: str, control_pairs: list[list[str]]) -> int:
        count = 0
        for pair in control_pairs:
            if len(pair) == 2:
                self.map_control(source_standard, pair[0], target_standard, pair[1])
                count += 1
        return count
    def list_mappings(self, source_standard: str = "") -> list[dict[str, Any]]:
        results = []
        for key, value in self._mappings.items():
            std, ctrl = key.split(":", 1)
            if not source_standard or std == source_standard:
                results.append({"source_standard": std, "source_control": ctrl, **value})
        return results
    def get_all_controls(self) -> list[str]:
        controls = set()
        for key in self._mappings:
            controls.add(key.split(":", 1)[1])
        return sorted(controls)
