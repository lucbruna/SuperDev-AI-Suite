from __future__ import annotations

from typing import Any


class ModelGenerator:
    """Generates and manages data model definitions."""

    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {}

    def add_model(self, name: str, fields: list[dict[str, Any]]) -> str:
        self._models[name] = {
            "name": name,
            "fields": fields,
        }
        return name

    def get_model(self, name: str) -> dict[str, Any] | None:
        return self._models.get(name)

    def remove_model(self, name: str) -> bool:
        if name in self._models:
            del self._models[name]
            return True
        return False

    def list_models(self) -> list[dict[str, Any]]:
        return list(self._models.values())

    @property
    def model_count(self) -> int:
        return len(self._models)

    def generate_model_code(self, name: str) -> str:
        model = self._models.get(name)
        if model is None:
            return f"# Model '{name}' not found"
        field_lines = "\n".join(f"    {f['name']}: {f.get('type', 'str')}" for f in model["fields"])
        return (
            f"from __future__ import annotations\n\nfrom dataclasses import dataclass\n\n\n"
            f"@dataclass\nclass {name}:\n{field_lines}\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "models": list(self._models.values()),
            "model_count": self.model_count,
        }
