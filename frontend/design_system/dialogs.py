from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DialogSpec:
    """Definition of a modal dialog."""

    title: str
    content: str = ""
    size: str = "md"  # sm | md | lg | xl
    dismissible: bool = True
    actions: list[dict[str, Any]] = field(default_factory=list)


class Dialogs:
    """Builds dialog and modal definitions."""

    SIZES = ("sm", "md", "lg", "xl")

    def __init__(self) -> None:
        self._dialogs: dict[str, DialogSpec] = {}

    def register(self, name: str, spec: DialogSpec) -> None:
        if spec.size not in self.SIZES:
            raise ValueError(f"invalid dialog size: {spec.size}")
        self._dialogs[name] = spec

    def open(self, name: str) -> DialogSpec:
        if name not in self._dialogs:
            raise KeyError(f"unknown dialog: {name}")
        return self._dialogs[name]

    def confirm(self, title: str, message: str = "", **kwargs: Any) -> DialogSpec:
        spec = DialogSpec(
            title=title,
            content=message,
            actions=[
                {"label": "Cancel", "variant": "secondary"},
                {"label": "Confirm", "variant": "primary", "primary": True},
            ],
            **kwargs,
        )
        return spec

    def build(self, name: str, **props: Any) -> dict[str, Any]:
        return {"type": "dialog", "name": name, **vars(self.open(name)), "props": props}
