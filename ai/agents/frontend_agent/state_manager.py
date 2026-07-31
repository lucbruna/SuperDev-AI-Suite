from __future__ import annotations

from typing import Any


class StateManager:
    """Manages frontend state store definitions."""

    def __init__(self) -> None:
        self._stores: dict[str, dict[str, Any]] = {}

    def add_store(self, name: str, initial_state: dict[str, Any]) -> str:
        self._stores[name] = {
            "name": name,
            "initial_state": initial_state,
        }
        return name

    def get_store(self, name: str) -> dict[str, Any] | None:
        return self._stores.get(name)

    def remove_store(self, name: str) -> bool:
        if name in self._stores:
            del self._stores[name]
            return True
        return False

    def list_stores(self) -> list[dict[str, Any]]:
        return list(self._stores.values())

    @property
    def store_count(self) -> int:
        return len(self._stores)

    def generate_store_code(self, name: str) -> str:
        store = self._stores.get(name)
        if store is None:
            return f"// Store '{name}' not found"
        state_lines = "\n".join(f"  {k}: {repr(v)}," for k, v in store["initial_state"].items())
        capitalized = name[0].upper() + name[1:]
        return (
            f"import {{ create }} from 'zustand';\n\n"
            f"interface {capitalized}State {{\n"
            f"{state_lines}\n"
            f"}}\n\n"
            f"export const use{capitalized}Store = create<{capitalized}State>((set) => ({{\n"
            f"{state_lines}\n"
            f"  // add actions here\n"
            f"}}));\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "stores": list(self._stores.values()),
            "store_count": self.store_count,
        }
