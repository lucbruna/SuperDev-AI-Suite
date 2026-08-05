"""Canvas — real procedural rendering with PIL and numpy.

The ``SceneCanvas`` renders a structured scene descriptor into actual pixel
data (numpy array / PIL image). It supports:

* gradient and solid backgrounds with vignette
* deterministic noise (film grain / star fields) seeded per frame
* particles (circles, glowing) with motion
* shapes: rects, circles, lines, polygons
* text overlays
* camera transforms: pan (dx/dy), zoom and rotation
* style colour grading through a palette mapping

Rendering is deterministic: the same scene + frame index produces the same
pixels, which keeps tests stable and videos temporally consistent.
"""
from __future__ import annotations

import random
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

try:
    from PIL import ImageFont
except Exception:  # pragma: no cover  # very old Pillow
    ImageFont = None


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Invalid hex color '{hex_color}'")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _font(size: int) -> Any:
    """Best-effort TTF font lookup, falling back to the default bitmap font."""
    if ImageFont is None:
        return None
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:  # noqa: BLE001 — try next font
            continue
    return None


class SceneCanvas:
    """Renders scene descriptors into real image arrays."""

    def __init__(
        self,
        *,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        seed: int = 42,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width/height must be positive")
        self.width = width
        self.height = height
        self.fps = fps
        self.seed = seed

    # ── Public API ────────────────────────────────────────────────
    def render_scene(self, scene: dict[str, Any], frame_index: int) -> np.ndarray:
        """Render one frame for a scene descriptor at ``frame_index``."""
        rng = random.Random(self.seed * 1000003 + frame_index)
        bg = self._background(scene, rng)
        img = Image.fromarray(bg)

        draw = ImageDraw.Draw(img)
        for particle in scene.get("particles", []):
            self._draw_particle(draw, particle, frame_index, rng)
        for rect in scene.get("rects", []):
            self._draw_rect(draw, rect, frame_index)
        for circle in scene.get("circles", []):
            self._draw_circle(draw, circle, frame_index)
        for line in scene.get("lines", []):
            self._draw_line(draw, line, frame_index)

        text = scene.get("text")
        if text:
            self._draw_text(draw, text)

        img = self._apply_camera(img, scene.get("camera") or {}, frame_index)
        img = self._apply_grading(img, scene.get("palette") or [])

        return np.asarray(img, dtype=np.uint8)

    def render_frame(self, job: dict[str, Any], frame_index: int) -> np.ndarray:
        """Render API compatible with the render controller."""
        return self.render_scene(job.get("scene") or job.get("params", {}), frame_index)

    # ── Background ────────────────────────────────────────────────
    def _background(self, scene: dict[str, Any], rng: random.Random) -> np.ndarray:
        bg_type = scene.get("background_type", "gradient")
        colors = [c for c in scene.get("background_colors", []) if c]
        if len(colors) < 2:
            colors = ["#1a1a2e", "#16213e"]

        h, w = self.height, self.width
        if bg_type == "solid":
            rgb = _hex_to_rgb(colors[0])
            return np.zeros((h, w, 3), dtype=np.uint8) + np.array(rgb, dtype=np.uint8)

        c0 = np.array(_hex_to_rgb(colors[0]), dtype=np.float32)
        c1 = np.array(_hex_to_rgb(colors[1]), dtype=np.float32)
        c2 = np.array(_hex_to_rgb(colors[2]), dtype=np.float32) if len(colors) > 2 else c1

        y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
        if bg_type == "radial":
            dist = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) / 0.7071
            t = np.clip(dist, 0, 1)[..., None]
        else:  # linear vertical gradient
            t = y[..., None]
        img = c0 * (1 - t) + c1 * t
        # Optional third-color influence near the bottom for depth.
        mask = np.clip((y - 0.7) / 0.3, 0, 1)[..., None]
        img = img * (1 - mask * 0.4) + c2 * mask * 0.4

        # Deterministic stars/noise for cinematic feel.
        noise_strength = scene.get("noise", 0.05)
        grain = np.asarray(
            [rng.random() for _ in range(h * w)], dtype=np.float32
        ).reshape(h, w, 1) * 255.0 * noise_strength
        img = np.clip(img + grain, 0, 255)
        return img.astype(np.uint8)

    # ── Primitive drawing ─────────────────────────────────────────
    def _draw_particle(self, draw: ImageDraw.ImageDraw, p: dict[str, Any], frame_index: int, rng: random.Random) -> None:
        x = float(p.get("x", 0)) + float(p.get("vx", 0)) * frame_index
        y = float(p.get("y", 0)) + float(p.get("vy", 0)) * frame_index + 0.5 * float(p.get("gy", 0)) * frame_index**2
        r = max(1, int(p.get("radius", 3)))
        color = p.get("color", "#FFFFFF")
        alpha = p.get("alpha", 0.8)
        # Particles wrap around horizontally.
        x = x % (self.width + 2 * r) - r
        if y > self.height + r:
            return
        try:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
            if alpha < 1.0 and r > 2:
                glow_r = int(r * 1.8)
                draw.ellipse([x - glow_r, y - glow_r, x + glow_r, y + glow_r], outline=color, width=1)
        except Exception:  # noqa: BLE001 — never break a frame
            return

    def _draw_rect(self, draw: ImageDraw.ImageDraw, r: dict[str, Any], frame_index: int) -> None:
        dx = float(r.get("dx", 0)) * frame_index
        x0 = float(r.get("x", 0)) + dx
        y0 = float(r.get("y", 0))
        x1 = x0 + float(r.get("w", 50))
        y1 = y0 + float(r.get("h", 50))
        draw.rectangle([x0, y0, x1, y1], fill=r.get("color", "#888888"), outline=r.get("outline"))

    def _draw_circle(self, draw: ImageDraw.ImageDraw, c: dict[str, Any], frame_index: int) -> None:
        cx = float(c.get("x", 0)) + float(c.get("dx", 0)) * frame_index
        cy = float(c.get("y", 0)) + float(c.get("dy", 0)) * frame_index
        r = max(1, float(c.get("radius", 20)))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c.get("color", "#FFFFFF"))

    def _draw_line(self, draw: ImageDraw.ImageDraw, line: dict[str, Any], frame_index: int) -> None:
        growth = min(1.0, max(0.0, (frame_index - float(line.get("start_frame", 0))) / max(1, float(line.get("grow_frames", 10)))))
        x1 = float(line.get("x1", 0)) + float(line.get("dx1", 0)) * frame_index
        y1 = float(line.get("y1", 0)) + float(line.get("dy1", 0)) * frame_index
        x2 = float(line.get("x2", 0)) + float(line.get("dx2", 0)) * frame_index
        y2 = float(line.get("y2", 0)) + float(line.get("dy2", 0)) * frame_index
        if growth < 1.0:
            x2 = x1 + (x2 - x1) * growth
            y2 = y1 + (y2 - y1) * growth
        draw.line([x1, y1, x2, y2], fill=line.get("color", "#FFFFFF"), width=int(line.get("width", 3)))

    def _draw_text(self, draw: ImageDraw.ImageDraw, text: dict[str, Any]) -> None:
        content = text.get("content", "")
        if not content:
            return
        font = _font(int(text.get("size", 48)))
        xy = (float(text.get("x", self.width / 2)), float(text.get("y", self.height / 2)))
        anchor = text.get("anchor", "mm")
        try:
            draw.text(xy, content, fill=text.get("color", "#FFFFFF"), font=font, anchor=anchor)
        except Exception:  # noqa: BLE001 — bitmap font fallback
            draw.text(xy, content, fill=text.get("color", "#FFFFFF"))

    # ── Camera & grading ──────────────────────────────────────────
    def _apply_camera(self, img: Image.Image, camera: dict[str, Any], frame_index: int) -> Image.Image:
        dx = float(camera.get("dx", 0)) * frame_index
        dy = float(camera.get("dy", 0)) * frame_index
        zoom = float(camera.get("zoom", 1.0))
        roll = float(camera.get("roll", 0)) * frame_index
        if zoom != 1.0:
            # Zoom-in: scale UP then crop the centre back to canvas size so the
            # output frame always keeps the exact canvas dimensions.
            nw = max(self.width + 1, int(self.width * zoom))
            nh = max(self.height + 1, int(self.height * zoom))
            img = img.resize((nw, nh), Image.BILINEAR).crop(
                ((nw - self.width) // 2, (nh - self.height) // 2,
                 (nw - self.width) // 2 + self.width, (nh - self.height) // 2 + self.height)
            )
        if roll:
            img = img.rotate(roll, resample=Image.BILINEAR, expand=False)
        if dx or dy:
            img = img.transform(
                img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR, fillcolor=0,
            )
        return img

    def _apply_grading(self, img: Image.Image, palette: list[str]) -> Image.Image:
        """Simple cinematic grade: tint shadows toward the first palette color."""
        if not palette:
            return img
        rgb = _hex_to_rgb(palette[0])
        img = img.filter(ImageFilter.GaussianBlur(radius=0.2))
        arr = np.asarray(img, dtype=np.float32)
        tint = np.array(rgb, dtype=np.float32)
        arr = arr * 0.92 + tint * 0.08
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    # ── Convenience ───────────────────────────────────────────────
    def scene_placeholder(
        self,
        *,
        text: str = "",
        colors: list[str] | None = None,
        camera: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a simple, fully renderable scene descriptor."""
        return {
            "background_type": "gradient",
            "background_colors": colors or ["#1a1a2e", "#0f3460"],
            "particles": [{"x": x * self.width / 8, "y": 0.0, "vx": -0.4, "vy": 0.8, "radius": 2, "color": "#FFFFFF"} for x in range(8)],
            "text": {"content": text, "color": "#FFFFFF", "size": 48, "anchor": "mm"},
            "camera": camera or {},
            "palette": colors or [],
        }
