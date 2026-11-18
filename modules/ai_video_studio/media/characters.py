"""Reusable procedural character assets for DARKSTUDIO.

Characters are assembled from the exact primitives understood by SceneCanvas.
The output remains editable scene data; this is not skeletal rigging.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CharacterPreset:
    """Stable identity palette and proportions for a reusable character."""

    character_id: str
    skin: str
    hair: str
    clothing: str
    trousers: str
    shoes: str
    outline: str = "#18212F"


PRESETS: dict[str, CharacterPreset] = {
    "whymentary_host": CharacterPreset(
        "whymentary_host", "#F2C9A5", "#3B2B24", "#2563EB",
        "#1F2937", "#111827",
    ),
    "historical_narrator": CharacterPreset(
        "historical_narrator", "#D9AE88", "#29231F", "#8B6B43",
        "#343B46", "#171B22",
    ),
}

VALID_POSES = {"neutral", "explain", "point"}
VALID_EXPRESSIONS = {"neutral", "happy", "surprised", "concerned"}


def character_primitives(
    character_id: str,
    *,
    x: float,
    y: float,
    scale: float = 1.0,
    pose: str = "neutral",
    expression: str = "neutral",
) -> dict[str, list[dict[str, Any]]]:
    """Return rect/circle/line primitives around a feet-position anchor."""
    if character_id not in PRESETS:
        raise ValueError(f"Unknown character '{character_id}'")
    if scale <= 0:
        raise ValueError("scale must be greater than zero")
    if pose not in VALID_POSES:
        raise ValueError(f"Unknown pose '{pose}'")
    if expression not in VALID_EXPRESSIONS:
        raise ValueError(f"Unknown expression '{expression}'")

    preset = PRESETS[character_id]
    s = float(scale)

    def px(value: float) -> float:
        return x + value * s

    def py(value: float) -> float:
        return y + value * s

    circles: list[dict[str, Any]] = [
        {"x": px(0), "y": py(-151), "radius": 28*s, "color": preset.hair},
        {"x": px(0), "y": py(-142), "radius": 23*s, "color": preset.skin},
        {"x": px(-8), "y": py(-148), "radius": 2*s, "color": preset.outline},
        {"x": px(8), "y": py(-148), "radius": 2*s, "color": preset.outline},
        {"x": px(-12), "y": py(-162), "radius": 12*s, "color": preset.hair},
    ]
    lines: list[dict[str, Any]] = [
        {"x1": px(-13), "y1": py(-52), "x2": px(-18), "y2": py(-5),
         "color": preset.trousers, "width": max(2, int(9*s))},
        {"x1": px(13), "y1": py(-52), "x2": px(18), "y2": py(-5),
         "color": preset.trousers, "width": max(2, int(9*s))},
        {"x1": px(-18), "y1": py(-5), "x2": px(-29), "y2": py(0),
         "color": preset.shoes, "width": max(2, int(8*s))},
        {"x1": px(18), "y1": py(-5), "x2": px(29), "y2": py(0),
         "color": preset.shoes, "width": max(2, int(8*s))},
    ]

    arms = {
        "neutral": [(-25, -101, -43, -66), (25, -101, 43, -66)],
        "explain": [(-25, -101, -48, -82), (25, -101, 48, -126)],
        "point": [(-25, -101, -48, -82), (25, -101, 55, -145)],
    }[pose]
    for x1, y1, x2, y2 in arms:
        lines.append({
            "x1": px(x1), "y1": py(y1), "x2": px(x2), "y2": py(y2),
            "color": preset.skin, "width": max(2, int(8*s)),
        })

    if expression == "happy":
        lines.append({
            "x1": px(-7), "y1": py(-132), "x2": px(7), "y2": py(-132),
            "color": "#7C2D12", "width": max(1, int(2*s)),
        })
    elif expression == "surprised":
        circles.append({
            "x": px(0), "y": py(-132), "radius": 4*s, "color": "#7C2D12",
        })
    elif expression == "concerned":
        lines.append({
            "x1": px(-6), "y1": py(-128), "x2": px(6), "y2": py(-132),
            "color": "#7C2D12", "width": max(1, int(2*s)),
        })

    rects = [
        {"x": px(-10), "y": py(-120), "w": 20*s, "h": 12*s,
         "color": preset.skin},
        {"x": px(-25), "y": py(-110), "w": 50*s, "h": 58*s,
         "color": preset.clothing},
    ]
    return {"rects": rects, "circles": circles, "lines": lines}


def add_character(
    scene: dict[str, Any],
    character_id: str,
    *,
    x: float,
    y: float,
    scale: float = 1.0,
    pose: str = "neutral",
    expression: str = "neutral",
) -> dict[str, Any]:
    """Copy a scene and append one reusable character to its primitive layers."""
    character = character_primitives(
        character_id, x=x, y=y, scale=scale, pose=pose, expression=expression
    )
    result = dict(scene)
    for layer, primitives in character.items():
        result[layer] = [*scene.get(layer, []), *primitives]
    return result



def add_character_motion(
    scene: dict[str, Any],
    character_id: str,
    *,
    from_x: float,
    from_y: float,
    to_x: float,
    to_y: float,
    duration_frames: int,
    start_frame: int = 0,
    scale: float = 1.0,
    pose: str = "neutral",
    expression: str = "neutral",
) -> dict[str, Any]:
    """Add a character with a smooth, finite position animation.

    Motion uses smoothstep easing and is evaluated by SceneCanvas at render
    time. The character remains at its starting point before start_frame and
    reaches its destination after duration_frames.
    """
    if duration_frames <= 0:
        raise ValueError("duration_frames must be greater than zero")
    if start_frame < 0:
        raise ValueError("start_frame cannot be negative")

    result = add_character(
        scene,
        character_id,
        x=from_x,
        y=from_y,
        scale=scale,
        pose=pose,
        expression=expression,
    )
    displacement = {
        "motion_dx": float(to_x) - float(from_x),
        "motion_dy": float(to_y) - float(from_y),
        "motion_start_frame": int(start_frame),
        "motion_frames": int(duration_frames),
    }
    for layer in ("rects", "circles", "lines"):
        count = len(result[layer]) - len(scene.get(layer, []))
        if count <= 0:
            continue
        for primitive in result[layer][-count:]:
            primitive.update(displacement)
    return result



def build_character_cue_timeline(
    narration_clip: dict[str, Any],
    cues: list[dict[str, Any]],
    *,
    fps: int = 30,
) -> list[dict[str, Any]]:
    """Convert narration-relative gesture cues into absolute video frames.

    Each cue requires offset_seconds and may specify pose and expression.
    The narration clip supplies its absolute start and end timestamps.
    This creates a deterministic cue schedule; a renderer or timeline
    orchestrator must still apply each cue to the character.
    """
    if fps <= 0:
        raise ValueError("fps must be greater than zero")
    start = float(narration_clip["start"])
    end = float(narration_clip["end"])
    if end <= start:
        raise ValueError("narration clip end must be after start")

    timeline: list[dict[str, Any]] = []
    for cue in cues:
        offset = float(cue["offset_seconds"])
        if offset < 0 or start + offset > end:
            raise ValueError("cue offset_seconds must fall within narration clip")
        pose = str(cue.get("pose", "neutral"))
        expression = str(cue.get("expression", "neutral"))
        if pose not in VALID_POSES:
            raise ValueError(f"Unknown pose '{pose}'")
        if expression not in VALID_EXPRESSIONS:
            raise ValueError(f"Unknown expression '{expression}'")
        timestamp = start + offset
        timeline.append({
            "frame": round(timestamp * fps),
            "time_seconds": round(timestamp, 3),
            "pose": pose,
            "expression": expression,
        })
    return sorted(timeline, key=lambda event: event["frame"])
