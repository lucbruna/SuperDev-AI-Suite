"""Plan catalog."""
from __future__ import annotations

from typing import Any


class PlanCatalog:
    def __init__(self) -> None:
        self._catalog: list[dict[str, Any]] = []
    def add(self, plan_id: str, name: str, description: str, price: float, features: list[str]) -> dict[str, Any]:
        entry = {"plan_id": plan_id, "name": name, "description": description, "price": price, "features": features, "visible": True}
        self._catalog.append(entry)
        return entry
    def get(self, plan_id: str) -> dict[str, Any]:
        for entry in self._catalog:
            if entry["plan_id"] == plan_id:
                return entry
        return {}
    def list_visible(self) -> list[dict[str, Any]]:
        return [e for e in self._catalog if e.get("visible")]
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._catalog)
    def hide(self, plan_id: str) -> bool:
        for e in self._catalog:
            if e["plan_id"] == plan_id:
                e["visible"] = False
                return True
        return False
    def show(self, plan_id: str) -> bool:
        for e in self._catalog:
            if e["plan_id"] == plan_id:
                e["visible"] = True
                return True
        return False
    def remove(self, plan_id: str) -> bool:
        before = len(self._catalog)
        self._catalog = [e for e in self._catalog if e["plan_id"] != plan_id]
        return len(self._catalog) < before
    def count(self) -> int:
        return len(self._catalog)
