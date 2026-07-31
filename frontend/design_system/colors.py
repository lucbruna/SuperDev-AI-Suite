from __future__ import annotations

from typing import Any


class ColorPalette:
    """Design system color tokens with light/dark variants."""

    def __init__(self, mode: str = "light") -> None:
        self._mode = mode
        self._semantic: dict[str, dict[str, str]] = {
            "primary": {"light": "#4f46e5", "dark": "#818cf8"},
            "secondary": {"light": "#64748b", "dark": "#94a3b8"},
            "success": {"light": "#16a34a", "dark": "#4ade80"},
            "warning": {"light": "#d97706", "dark": "#fbbf24"},
            "danger": {"light": "#dc2626", "dark": "#f87171"},
            "info": {"light": "#0284c7", "dark": "#38bdf8"},
            "background": {"light": "#f8fafc", "dark": "#0f172a"},
            "surface": {"light": "#ffffff", "dark": "#1e293b"},
            "border": {"light": "#e2e8f0", "dark": "#334155"},
            "text": {"light": "#0f172a", "dark": "#f1f5f9"},
            "text_muted": {"light": "#64748b", "dark": "#94a3b8"},
        }

    @property
    def mode(self) -> str:
        return self._mode

    def set_mode(self, mode: str) -> None:
        self._mode = mode

    def color(self, token: str) -> str:
        if token not in self._semantic:
            raise KeyError(f"unknown color token: {token}")
        return self._semantic[token][self._mode]

    def get_colors(self) -> dict[str, str]:
        return {name: values[self._mode] for name, values in self._semantic.items()}
