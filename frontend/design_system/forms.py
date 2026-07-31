from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FieldSpec:
    """Definition of a single form field."""

    name: str
    label: str
    field_type: str = "text"
    required: bool = False
    placeholder: str = ""
    help_text: str = ""
    options: list[str] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)


class Forms:
    """Builds form and field definitions."""

    def __init__(self) -> None:
        self._templates: dict[str, list[FieldSpec]] = {}

    def field(self, name: str, label: str, field_type: str = "text", **kwargs: Any) -> FieldSpec:
        return FieldSpec(name=name, label=label, field_type=field_type, **kwargs)

    def register_template(self, name: str, fields: list[FieldSpec]) -> None:
        self._templates[name] = fields

    def template(self, name: str) -> list[FieldSpec]:
        if name not in self._templates:
            raise KeyError(f"unknown form template: {name}")
        return self._templates[name]

    def build_form(self, name: str, submit_label: str = "Submit", **props: Any) -> dict[str, Any]:
        return {
            "type": "form",
            "name": name,
            "fields": [vars(f) for f in self.template(name)],
            "submit_label": submit_label,
            "props": props,
        }

    def validate(self, name: str, data: dict[str, Any]) -> list[str]:
        errors = []
        for field_spec in self.template(name):
            value = data.get(field_spec.name)
            if field_spec.required and (value is None or value == ""):
                errors.append(f"{field_spec.label} is required")
        return errors
