from __future__ import annotations

from typing import Any


class ThemeManager:
    """Manages theme configuration for frontend applications."""

    def __init__(self) -> None:
        self._primary_color: str = "#1976d2"
        self._secondary_color: str = "#dc004e"
        self._font: str = "Inter, sans-serif"
        self._spacing: str = "8px"
        self._saved_themes: dict[str, dict[str, str]] = {}

    def set_primary_color(self, color: str) -> None:
        self._primary_color = color

    def set_secondary_color(self, color: str) -> None:
        self._secondary_color = color

    def set_font(self, font: str) -> None:
        self._font = font

    def set_spacing(self, unit: str) -> None:
        self._spacing = unit

    def get_theme(self) -> dict[str, str]:
        return {
            "primary_color": self._primary_color,
            "secondary_color": self._secondary_color,
            "font": self._font,
            "spacing": self._spacing,
        }

    def generate_css_variables(self) -> str:
        return (
            f":root {{\n"
            f"  --color-primary: {self._primary_color};\n"
            f"  --color-secondary: {self._secondary_color};\n"
            f"  --font-family: {self._font};\n"
            f"  --spacing-unit: {self._spacing};\n"
            f"}}\n"
        )

    def save_theme(self, name: str) -> str:
        self._saved_themes[name] = self.get_theme()
        return name

    def load_theme(self, name: str) -> bool:
        theme = self._saved_themes.get(name)
        if theme is None:
            return False
        self._primary_color = theme["primary_color"]
        self._secondary_color = theme["secondary_color"]
        self._font = theme["font"]
        self._spacing = theme["spacing"]
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.get_theme(),
            "saved_themes": self._saved_themes,
        }
