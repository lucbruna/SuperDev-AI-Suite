from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TypeStyle:
    """A single typography style definition."""

    font_size: str
    font_weight: int
    line_height: str


class Typography:
    """Typography scale for the design system."""

    def __init__(self) -> None:
        self._scale: dict[str, TypeStyle] = {
            "display": TypeStyle("3rem", 700, "1.2"),
            "h1": TypeStyle("2.25rem", 700, "1.3"),
            "h2": TypeStyle("1.875rem", 600, "1.35"),
            "h3": TypeStyle("1.5rem", 600, "1.4"),
            "h4": TypeStyle("1.25rem", 600, "1.45"),
            "body": TypeStyle("1rem", 400, "1.6"),
            "body_small": TypeStyle("0.875rem", 400, "1.5"),
            "caption": TypeStyle("0.75rem", 400, "1.4"),
            "code": TypeStyle("0.875rem", 400, "1.6"),
            "label": TypeStyle("0.8125rem", 500, "1.4"),
        }
        self._font_family = (
            "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
        )
        self._mono_family = "'JetBrains Mono', ui-monospace, 'Cascadia Code', Consolas, monospace"

    def get_typography(self) -> dict[str, Any]:
        return {
            "font_family": self._font_family,
            "mono_family": self._mono_family,
            "scale": {name: vars(style) for name, style in self._scale.items()},
        }

    def style(self, token: str) -> TypeStyle:
        if token not in self._scale:
            raise KeyError(f"unknown typography token: {token}")
        return self._scale[token]
