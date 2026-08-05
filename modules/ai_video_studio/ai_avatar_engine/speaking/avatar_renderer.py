"""Avatar renderer — draws talking-presenter frames for the speaking engine.

Pure PIL drawing, no heavyweight deps: a soft gradient backdrop, shoulders,
neck, ears, hair, brows, blink-aware eyes, nose and a viseme-driven mouth.
The presenter's appearance comes from the digital-human descriptor colors
(skin / hair / eyes / shirt); the mouth and eyes are driven by the per-frame
facial parameters produced by the facial engine (``mouth_open``,
``mouth_round``, ``smile``, ``blink_left``, ``blink_right``).

Landmark positions come from the avatar's face mesh (normalized 0..1 space),
so the mouth geometry already reacts to smile and jaw openness.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from modules.ai_video_studio.ai_avatar_engine.facial_animation.face_mesh import (
    get_face_mesh,
)
from modules.ai_video_studio.editor_common import clamp

_BG_CACHE: dict[tuple[int, int], Image.Image] = {}


def _hex_to_rgb(hex_color: str, default: tuple[int, int, int] = (120, 96, 80)) -> tuple[int, int, int]:
    """Parse ``#rrggbb`` to an RGB tuple; fall back on malformed input."""
    h = str(hex_color).strip().lstrip("#")
    if len(h) != 6:
        return default
    try:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except ValueError:
        return default


def _shade(rgb: tuple[int, int, int], factor: float = 0.72) -> tuple[int, int, int]:
    return tuple(int(c * factor) for c in rgb)


def _background(width: int, height: int) -> Image.Image:
    """Cached vertical gradient + soft glow behind the presenter's head."""
    key = (width, height)
    cached = _BG_CACHE.get(key)
    if cached is not None:
        return cached
    top = np.array([20, 22, 34], dtype=np.float64)
    bottom = np.array([7, 9, 16], dtype=np.float64)
    t = np.linspace(0.0, 1.0, height)[:, None, None]
    grad = (top * (1.0 - t) + bottom * t)  # (height, 1, 3)

    yy, xx = np.mgrid[0:height, 0:width].astype(np.float64)
    glow_cx, glow_cy, glow_r = width / 2, height * 0.42, min(width, height) * 0.42
    glow = np.exp(-(((xx - glow_cx) / glow_r) ** 2 + ((yy - glow_cy) / glow_r) ** 2))
    glow_color = np.array([58, 66, 104], dtype=np.float64)
    arr = grad + glow[:, :, None] * glow_color * 0.45
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    cached = Image.fromarray(arr)
    _BG_CACHE[key] = cached
    return cached


def render_frames(
    params: list[dict[str, Any]],
    *,
    colors: dict[str, str],
    width: int = 640,
    height: int = 480,
) -> list[np.ndarray]:
    """Render one talking-head frame per facial-parameter set (HxWx3 uint8)."""
    if not params:
        return []
    return [_draw_frame(p, colors=colors, width=width, height=height) for p in params]


def _draw_frame(
    params: dict[str, Any],
    *,
    colors: dict[str, str],
    width: int,
    height: int,
) -> np.ndarray:
    img = _background(width, height).copy()
    draw = ImageDraw.Draw(img)

    skin = _hex_to_rgb(colors.get("skin", "#c68642"))
    hair = _hex_to_rgb(colors.get("hair", "#2b2b2b"))
    iris = _hex_to_rgb(colors.get("eye", "#3a2a1a"))
    shirt = _hex_to_rgb(colors.get("shirt", "#243447"))

    t = float(params.get("frame_time", params.get("time", 0.0)))
    # Subtle constant head bob so the presenter feels alive.
    bob = 2.5 * math.sin(t * 2.1) + 1.2 * math.sin(t * 4.7)

    cx = width / 2.0
    cy = height * 0.44 + bob
    s = min(width, height) * 0.60  # scale: 1.0 normalized unit in pixels

    mesh = get_face_mesh().build(params)

    def px(nx: float) -> float:
        return cx + (nx - 0.5) * s

    def py(ny: float) -> float:
        return cy + (ny - 0.5) * s

    # ── Shoulders ────────────────────────────────────────────────
    shoulder_top = py(0.34)
    draw.rounded_rectangle(
        [cx - 0.55 * s, shoulder_top, cx + 0.55 * s, height + 10],
        radius=0.12 * s, fill=shirt,
    )
    # Collar hint.
    collar = _shade(shirt, 0.8)
    draw.rounded_rectangle(
        [cx - 0.12 * s, shoulder_top - 0.02 * s, cx + 0.12 * s, shoulder_top + 0.10 * s],
        radius=0.05 * s, fill=collar,
    )

    # ── Neck ─────────────────────────────────────────────────────
    neck = _shade(skin, 0.86)
    draw.rectangle(
        [cx - 0.06 * s, py(0.20), cx + 0.06 * s, py(0.34)], fill=neck,
    )

    # ── Ears ─────────────────────────────────────────────────────
    ear_color = _shade(skin, 0.92)
    for side in (-1, 1):
        draw.ellipse(
            [cx + side * 0.235 * s - 0.028 * s, py(0.46) - 0.05 * s,
             cx + side * 0.235 * s + 0.028 * s, py(0.46) + 0.05 * s],
            fill=ear_color,
        )

    # ── Hair (back) ──────────────────────────────────────────────
    draw.ellipse(
        [cx - 0.26 * s, py(0.02) - 0.10 * s, cx + 0.26 * s, py(0.42)],
        fill=hair,
    )

    # ── Face ─────────────────────────────────────────────────────
    face_rect = [cx - 0.23 * s, py(0.22), cx + 0.23 * s, py(0.80)]
    draw.ellipse(face_rect, fill=skin)
    # Cheek shading.
    draw.ellipse(
        [cx - 0.20 * s, py(0.60), cx + 0.20 * s, py(0.86)],
        fill=_shade(skin, 0.94),
    )

    # ── Hair (fringe) ────────────────────────────────────────────
    draw.ellipse(
        [cx - 0.235 * s, py(0.16), cx + 0.235 * s, py(0.42)],
        fill=hair,
    )

    # ── Brows ────────────────────────────────────────────────────
    brow_color = _shade(hair, 0.6)
    brow_w = 0.055 * s
    for key in ("left_brow", "right_brow"):
        bx, by = mesh[key]
        draw.line(
            [px(bx) - brow_w, py(by), px(bx) + brow_w, py(by)],
            fill=brow_color, width=max(2, int(0.018 * s)),
        )

    # ── Eyes (blink-aware) ───────────────────────────────────────
    eye_open = max(
        float(params.get("blink_left", 0.0)),
        float(params.get("blink_right", 0.0)),
    )
    for key in ("left_eye", "right_eye"):
        ex, ey = mesh[key]
        e_cx, e_cy = px(ex), py(ey)
        if eye_open < 0.55:
            # Open eye: white + iris + pupil.
            draw.ellipse(
                [e_cx - 0.036 * s, e_cy - 0.024 * s, e_cx + 0.036 * s, e_cy + 0.024 * s],
                fill=(244, 242, 236),
            )
            draw.ellipse(
                [e_cx - 0.015 * s, e_cy - 0.015 * s, e_cx + 0.015 * s, e_cy + 0.015 * s],
                fill=iris,
            )
            draw.ellipse(
                [e_cx - 0.006 * s, e_cy - 0.006 * s, e_cx + 0.006 * s, e_cy + 0.006 * s],
                fill=(18, 18, 22),
            )
        else:
            # Closed lid.
            draw.line(
                [e_cx - 0.036 * s, e_cy, e_cx + 0.036 * s, e_cy],
                fill=_shade(skin, 0.75), width=max(2, int(0.016 * s)),
            )

    # ── Nose ─────────────────────────────────────────────────────
    bridge = mesh["nose_bridge"]
    tip = mesh["nose_tip"]
    draw.line(
        [px(bridge[0]), py(bridge[1]), px(tip[0]), py(tip[1])],
        fill=_shade(skin, 0.8), width=max(2, int(0.014 * s)),
    )

    # ── Mouth (viseme-driven) ────────────────────────────────────
    left, right = mesh["mouth_left"], mesh["mouth_right"]
    top, bottom = mesh["mouth_top"], mesh["mouth_bottom"]
    mx0, mx1 = px(left[0]), px(right[0])
    my_top = py(top[1])
    my_bot = py(bottom[1])

    open_amt = clamp(float(params.get("mouth_open", 0.0)), 0.0, 1.0)
    mouth_round = clamp(float(params.get("mouth_round", 0.0)), 0.0, 1.0)
    # Base lip thickness + openness-driven height.
    my_bot = max(my_top + 0.02 * s, my_top + (0.035 * s) * (1.0 - open_amt * 0.55) + open_amt * 0.10 * s)

    lip_color = (74, 30, 38)
    inner_color = (40, 16, 22)
    if mouth_round > 0.5:
        # Kiss/rounded mouth → ellipse.
        mh = 0.03 * s + open_amt * 0.07 * s
        draw.ellipse(
            [mx0, my_top - mh, mx1, my_top + mh], fill=lip_color, outline=_shade(lip_color, 0.6),
        )
        if open_amt > 0.08:
            inset = 0.22 * (mx1 - mx0)
            draw.ellipse(
                [mx0 + inset, my_top - mh * 0.6, mx1 - inset, my_top + mh * 0.6],
                fill=inner_color,
            )
    else:
        draw.rounded_rectangle(
            [mx0, my_top, mx1, my_bot], radius=max(1, int(0.012 * s)),
            fill=inner_color if open_amt > 0.08 else lip_color,
            outline=_shade(lip_color, 0.6),
        )

    return np.asarray(img, dtype=np.uint8)
