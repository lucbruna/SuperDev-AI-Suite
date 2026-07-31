from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ButtonStyle:
    """Style definition for a button variant."""

    variant: str
    background: str
    text_color: str
    border: str = "none"
    radius: str = "8px"
    padding: str = "8px 16px"
    font_weight: int = 500
    hover: dict[str, str] = field(default_factory=dict)
    disabled: dict[str, str] = field(default_factory=dict)


class Buttons:
    """Registry of button variants and style builder."""

    def __init__(self, colors: Any) -> None:
        self._colors = colors
        self._variants: dict[str, ButtonStyle] = {}

    def register(self, name: str, style: ButtonStyle) -> None:
        self._variants[name] = style

    def variant(self, name: str) -> ButtonStyle:
        if name not in self._variants:
            raise KeyError(f"unknown button variant: {name}")
        return self._variants[name]

    def default_variants(self) -> None:
        c = self._colors
        self._variants = {
            "primary": ButtonStyle(
                "primary",
                c.color("primary"),
                "#ffffff",
                hover={"background": c.color("primary") + "cc"},
                disabled={"background": c.color("border")},
            ),
            "secondary": ButtonStyle(
                "secondary",
                c.color("surface"),
                c.color("text"),
                border=f"1px solid {c.color('border')}",
            ),
            "danger": ButtonStyle("danger", c.color("danger"), "#ffffff"),
            "ghost": ButtonStyle(
                "ghost", "transparent", c.color("text"), disabled={"opacity": "0.5"}
            ),
        }

    def list(self) -> list[str]:
        return list(self._variants)

    def build(self, variant: str, label: str, **props: Any) -> dict[str, Any]:
        style = self.variant(variant)
        return {"type": "button", "label": label, "variant": variant, "style": vars(style), "props": props}
