"""Style selector — pick a visual style configuration."""
from __future__ import annotations

from typing import Any

_STYLES: dict[str, dict[str, Any]] = {
    "anime": {"palette": "vivid", "line_art": "clean", "saturation": 1.3},
    "cinematic": {"palette": "film", "line_art": "soft", "saturation": 0.9, "grain": True},
    "realistic": {"palette": "natural", "line_art": "none", "saturation": 1.0},
    "fantasy": {"palette": "ethereal", "line_art": "detailed", "saturation": 1.2},
    "pixel art": {"palette": "indexed", "line_art": "blocky", "saturation": 1.1},
    "watercolor": {"palette": "pastel", "line_art": "washed", "saturation": 0.8},
    "3d": {"palette": "pbr", "line_art": "none", "saturation": 1.0},
    "cartoon": {"palette": "bold", "line_art": "thick", "saturation": 1.4},
}


class StyleSelector:
    """Selects and customises visual style parameters."""

    def select(self, style: str) -> dict[str, Any]:
        base = _STYLES.get(style, _STYLES["cinematic"])
        return {"name": style, **{k: v for k, v in base.items()}}

    def available_styles(self) -> list[str]:
        return list(_STYLES.keys())

    def register(self, name: str, config: dict[str, Any]) -> None:
        _STYLES[name] = config
