from __future__ import annotations

from typing import Any


class Forms:
    """Manages form field definitions and generates form code."""

    def __init__(self) -> None:
        self._fields: dict[str, dict[str, Any]] = {}

    def add_field(
        self,
        name: str,
        field_type: str,
        label: str,
        required: bool = False,
        validation: list[str] | None = None,
    ) -> str:
        self._fields[name] = {
            "name": name,
            "type": field_type,
            "label": label,
            "required": required,
            "validation": validation or [],
        }
        return name

    def get_field(self, name: str) -> dict[str, Any] | None:
        return self._fields.get(name)

    def remove_field(self, name: str) -> bool:
        if name in self._fields:
            del self._fields[name]
            return True
        return False

    def list_fields(self) -> list[dict[str, Any]]:
        return list(self._fields.values())

    @property
    def field_count(self) -> int:
        return len(self._fields)

    def generate_form_code(self) -> str:
        if not self._fields:
            return "// No fields defined"
        field_elems = "\n".join(
            f"        <div className=\"field\">\n"
            f"          <label>{f['label']}</label>\n"
            f"          <input type=\"{f['type']}\" "
            f"name=\"{f['name']}\" "
            f"{'required ' if f['required'] else ''}/>\n"
            f"        </div>"
            for f in self._fields.values()
        )
        return (
            f"import React, {{ useState }} from 'react';\n\n"
            f"const AppForm: React.FC = () => {{\n"
            f"  const handleSubmit = (e: React.FormEvent) => {{\n"
            f"    e.preventDefault();\n"
            f"    // TODO: handle submission\n"
            f"  }};\n\n"
            f"  return (\n"
            f"    <form onSubmit={{handleSubmit}}>\n"
            f"{field_elems}\n"
            f"      <button type=\"submit\">Submit</button>\n"
            f"    </form>\n"
            f"  );\n"
            f"}};\n\n"
            f"export default AppForm;\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "fields": list(self._fields.values()),
            "field_count": self.field_count,
        }
