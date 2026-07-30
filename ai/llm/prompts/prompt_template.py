from __future__ import annotations

from pathlib import Path
from typing import Any


class PromptTemplate:
    """A reusable prompt template with variable substitution."""

    def __init__(self, template: str, name: str = "") -> None:
        self._template = template
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def template(self) -> str:
        return self._template

    def render(self, **kwargs: Any) -> str:
        return self._template.format(**kwargs)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self._template, encoding="utf-8")

    @classmethod
    def from_file(cls, path: str | Path, name: str = "") -> PromptTemplate:
        content = Path(path).read_text(encoding="utf-8")
        return cls(template=content, name=name or Path(path).stem)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "template_length": len(self._template),
            "template_preview": self._template[:100],
        }
