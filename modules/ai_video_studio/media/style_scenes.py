"""Style scenes — build renderable scenes per image style.

Each image generator style maps to a scene descriptor that the canvas can
render into real pixels. The scenes follow the style (anime → vivid
gradients + bold circles, logo → centered shape + text, etc.).
"""
from __future__ import annotations

from typing import Any


def _gradient(a: str, b: str, c: str | None = None) -> list[str]:
    return [a, b, c] if c else [a, b]


STYLE_SCENES: dict[str, Any] = {
    "realistic": {
        "background_type": "gradient",
        "background_colors": ["#2c3e50", "#4a6274", "#1a252f"],
        "rects": [{"x": 120, "y": 420, "w": 1040, "h": 200, "color": "#6b7b8d", "dx": 0.0}],
        "noise": 0.08,
    },
    "anime": {
        "background_type": "radial",
        "background_colors": ["#ff9a9e", "#fecfef", "#a18cd1"],
        "circles": [{"x": 200, "y": 180, "radius": 70, "color": "#ffffff88", "dx": 0.0, "dy": 0.0}],
        "noise": 0.02,
    },
    "cinematic": {
        "background_type": "gradient",
        "background_colors": ["#0f0c29", "#302b63", "#24243e"],
        "lines": [{"x1": 0, "y1": 620, "x2": 1280, "y2": 620, "color": "#e94560", "width": 4}],
        "noise": 0.06,
    },
    "fantasy": {
        "background_type": "radial",
        "background_colors": ["#2e0a4e", "#6a3093", "#a044ff"],
        "circles": [{"x": 900, "y": 200, "radius": 120, "color": "#ffd70066", "dx": 0.0, "dy": 0.0}],
        "noise": 0.04,
    },
    "architecture": {
        "background_type": "gradient",
        "background_colors": ["#0f2027", "#203a43", "#2c5364"],
        "rects": [
            {"x": 150, "y": 300, "w": 160, "h": 300, "color": "#3a6073", "dx": 0.0},
            {"x": 360, "y": 240, "w": 160, "h": 360, "color": "#4b7790", "dx": 0.0},
            {"x": 570, "y": 340, "w": 160, "h": 260, "color": "#3a6073", "dx": 0.0},
        ],
        "noise": 0.03,
    },
    "agriculture": {
        "background_type": "gradient",
        "background_colors": ["#134e5e", "#71b280"],
        "rects": [{"x": 0, "y": 480, "w": 1280, "h": 240, "color": "#2e7d32", "dx": 0.0}],
        "noise": 0.05,
    },
    "medical": {
        "background_type": "solid",
        "background_colors": ["#e8f4f8"],
        "circles": [{"x": 640, "y": 320, "radius": 160, "color": "#5bc0de88", "dx": 0.0, "dy": 0.0}],
        "noise": 0.01,
    },
    "ecommerce": {
        "background_type": "gradient",
        "background_colors": ["#fdfcfb", "#e2d1c3"],
        "rects": [{"x": 440, "y": 260, "w": 400, "h": 300, "color": "#ffffff", "dx": 0.0}],
        "noise": 0.01,
    },
    "product": {
        "background_type": "solid",
        "background_colors": ["#ffffff"],
        "rects": [{"x": 500, "y": 240, "w": 280, "h": 240, "color": "#f1f1f1", "dx": 0.0}],
        "noise": 0.005,
    },
    "logo": {
        "background_type": "solid",
        "background_colors": ["#ffffff"],
        "circles": [{"x": 640, "y": 320, "radius": 160, "color": "#6366f1cc", "dx": 0.0, "dy": 0.0}],
        "noise": 0.0,
    },
    "banner": {
        "background_type": "gradient",
        "background_colors": ["#141e30", "#243b55"],
        "rects": [{"x": 0, "y": 640, "w": 1280, "h": 80, "color": "#e94560", "dx": 0.0}],
        "noise": 0.02,
    },
    "thumbnail": {
        "background_type": "gradient",
        "background_colors": ["#ff512f", "#dd2476"],
        "circles": [{"x": 1040, "y": 200, "radius": 140, "color": "#ffffff55", "dx": 0.0, "dy": 0.0}],
        "noise": 0.03,
    },
    "icon": {
        "background_type": "solid",
        "background_colors": ["#4f46e5"],
        "circles": [{"x": 256, "y": 256, "radius": 180, "color": "#c7d2fe99", "dx": 0.0, "dy": 0.0}],
        "noise": 0.0,
    },
    "infographic": {
        "background_type": "solid",
        "background_colors": ["#0b1e3a"],
        "rects": [
            {"x": 90, "y": 160, "w": 300, "h": 160, "color": "#22d3ee88", "dx": 0.0},
            {"x": 450, "y": 160, "w": 300, "h": 240, "color": "#a78bfa88", "dx": 0.0},
            {"x": 810, "y": 160, "w": 300, "h": 200, "color": "#34d39988", "dx": 0.0},
        ],
        "noise": 0.01,
    },
}


def _luminance(hex_color: str) -> float:
    """Approximate relative luminance of a hex color in [0, 1]."""
    import re

    match = re.fullmatch(r"#([0-9a-fA-F]{6})", hex_color)
    if not match:
        return 0.5
    h = match.group(1)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrasting_text_color(bg_colors: list[str]) -> str:
    """Pick black or white text based on the background luminance."""
    light = sum(_luminance(c) for c in bg_colors[:3]) / max(1, len(bg_colors[:3]))
    return "#1a1a1a" if light > 0.5 else "#FFFFFF"


def scene_for_style(style: str, *, text: str = "") -> dict[str, Any]:
    """Return a renderable scene descriptor for an image style."""
    import copy

    base = copy.deepcopy(STYLE_SCENES.get(style, STYLE_SCENES["realistic"]))
    scene = base
    scene["palette"] = scene.get("background_colors", []) or []
    if text:
        scene["text"] = {
            "content": text[:60],
            "size": 40,
            "color": _contrasting_text_color(scene.get("background_colors", [])),
        }
    return scene


def available_styles() -> list[str]:
    return list(STYLE_SCENES.keys())
