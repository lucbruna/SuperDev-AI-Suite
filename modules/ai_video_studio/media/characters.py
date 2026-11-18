"""Reusable procedural character assets for DARKSTUDIO scenes.

This lightweight vector-like library creates editable circles, rectangles and
lines for the current PIL canvas. It is not a skeletal rig.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CharacterDesign:
    character_id: str
    skin: str
    hair: str
    clothing: str
    trousers: str
    shoes: str
    outline: str = "#18212F"


DESIGNS: dict[str, CharacterDesign] = {
    "whymentary_explainer": CharacterDesign(
        "whymentary_explainer", "#F2C9A5", "#3B2B24", "#2563EB",
        "#1F2937", "#111827",
    ),
    "historical_narrator": CharacterDesign(
        "historical_narrator", "#D9AE88", "#29231F", "#8B6B43",
        "#343B46", "#171B22",
    ),
}

POSES = {"neutral", "explain", "point"}
EXPRESSIONS = {"neutral", "happy", "surprised", "concerned"}


def build_character(
    character_id: str,
    *,
    x: float,
    y: float,
    scale: float = 1.0,
    pose: str = "neutral",
    expression: str = "neutral",
) -> dict[str, Any]:
    """Build one character as canvas primitives around a foot-position anchor."""
    if character_id not in DESIGNS:
        raise ValueError(f"Unknown character '{character_id}'")
    if scale <= 0:
        raise ValueError("scale must be greater than zero")
    if pose not in POSES:
        raise ValueError(f"Unknown pose '{pose}'")
    if expression not in EXPRESSIONS:
        raise ValueError(f"Unknown expression '{expression}'")

    d = DESIGNS[character_id]
    s = float(scale)

    def px(v: float) -> float:
        return x + v * s

    def py(v: float) -> float:
        return y + v * s

    head_x, head_y = px(0), py(-142)
    circles = [
        {"x": head_x, "y": py(-151), "radius": 28*s, "color": d.hair},
        {"x": head_x, "y": head_y, "radius": 23*s, "color": d.skin},
        {"x": px(-8), "y": py(-148), "radius": 3*s, "color": d.outline},
        {"x": px(8), "y": py(-148), "radius": 3*s, "color": d.outline},
        {"x": px(-12), "y": py(-162), "radius": 12*s, "color": d.hair},
    ]
    if expression == "surprised":
        circles.append({"x": head_x, "y": py(-132), "radius": 4*s, "color": "#7C2D12"})
    elif expression == "concerned":
        circles.extend([
            {"x": px(-8), "y": py(-155), "radius": 4*s, "color": d.outline},
            {"x": px(8), "y": py(-155), "radius": 4*s, "color": d.outline},
        ])

    rects = [
        {"x": px(-10), "y": py(-120), "w": 20*s, "h": 12*s, "color": d.skin},
        {"x": px(-25), "y": py(-110), "w": 50*s, "h": 58*s, "color": d.clothing},
    ]
    lines = [
        {"x1": px(-13), "y1": py(-52), "x2": px(-18), "y2": py(-5), "color": d.trousers, "width": max(2, int(9*s))},
        {"x1": px(13), "y1": py(-52), "x2": px(18), "y2": py(-5), "color": d.trousers, "width": max(2, int(9*s))},
        {"x1": px(-18), "y1": py(-5), "x2": px(-29), "y2": py(0), "color": d.shoes, "width": max(2, int(8*s))},
        {"x1": px(18), "y1": py(-5), "x2": px(29), "y2": py(0), "color": d.shoes, "width": max(2, int(8*s))},
    ]

    if pose == "neutral":
        arms = [(-25, -101, -43, -66), (25, -101, 43, -66)]
    elif pose == "explain":
        arms = [(-25, -101, -48, -82), (25, -101, 48, -126)]
    else:
        arms = [(-25, -101, -48, -82), (25, -101, 55, -145)]
    for x1, y1, x2, y2 in arms:
        lines.append({
            "x1": px(x1), "y1": py(y1), "x2": px(x2), "y2": py(y2),
            "color": d.skin, "width": max(2, int(8*s)),
        })

    if expression == "happy":
        lines.append({"x1": px(-7), "y1": py(-132), "x2": px(7), "y2": py(-132), "color": "#7C2D12", "width": max(1, int(2*s))})
    elif expression == "concerned":
        lines.append({"x1": px(-6), "y1": py(-128), "x2": px(6), "y2": py(-132), "color": "#7C2D12", "width": max(1, int(2*s))})

    return {
        "character_id": character_id, "x": x, "y": y, "scale": s,
        "pose": pose, "expression": expression,
        "rects": rects, "circles": circles, "lines": lines,
    }


def add_character_to_scene(
    scene: dict[str, Any],
    character_id: str,
    *,
    x: float,
    y: float,
    scale: float = 1.0,
    pose: str = "neutral",
    expression: str = "neutral",
) -> dict[str, Any]:
    """Append a character's primitives to a scene without mutating the input."""
    character = build_character(
        character_id, x=x, y=y, scale=scale, pose=pose, expression=expression
    )
    result = dict(scene)
    for key in ("rects", "circles", "lines"):
        result[key] = [*scene.get(key, []), *character[key]]
    result.setdefault("characters", []).append({
        "character_id": character_id, "x": x, "y": y, "scale": scale,
        "pose": pose, "expression": expression,
    })
    return result
