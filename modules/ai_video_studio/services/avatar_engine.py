"""AI Avatar Engine — virtual actors, styles, and placeholder avatar cards.

Implements the "avatar" pillar of the studio (blueprint Volume 6). Real
digital-human generation requires heavy model backends that are out of scope
for this repo, so the engine provides:

1. A virtual actor library (``AVATAR_LIBRARY``) with the styles from
   ``AvatarStyle`` (realistic, anime, cartoon, pixel_art, 3d, minimalist).
2. Scene-aware avatar selection (``select_for_scene``).
3. Procedural avatar card generation via Pillow — a real image file that the
   pipeline can overlay onto scenes, giving talking-head videos a visual
   presenter without an external avatar API.

Cards are generated locally with Pillow (installed), so this works offline.
"""
from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.core.constants import AvatarStyle, VoiceGender

logger = logging.getLogger(__name__)

# Style → background gradient seed colors for avatar cards.
STYLE_COLORS: dict[str, tuple[str, str]] = {
    AvatarStyle.REALISTIC.value: ("#2c3e50", "#4ca1af"),
    AvatarStyle.ANIME.value: ("#8e2de2", "#4a00e0"),
    AvatarStyle.CARTOON.value: ("#f7971e", "#ffd200"),
    AvatarStyle.PIXEL_ART.value: ("#0f0c29", "#302b63"),
    AvatarStyle.THREE_D.value: ("#141e30", "#243b55"),
    AvatarStyle.MINIMALIST.value: ("#232526", "#414345"),
}


@dataclass(frozen=True)
class AvatarProfile:
    """A virtual actor."""

    id: str
    name: str
    style: str  # one of AvatarStyle values
    gender: str  # male | female | neutral
    age_group: str  # young | adult | elderly
    description: str = ""
    tags: list[str] = field(default_factory=list)


AVATAR_LIBRARY: list[AvatarProfile] = [
    AvatarProfile("maya", "Maya Chen", AvatarStyle.REALISTIC.value, "female", "adult", "Confident host for corporate and tech content", ["host", "corporate"]),
    AvatarProfile("noah", "Noah Rivers", AvatarStyle.REALISTIC.value, "male", "adult", "Warm narrator for documentary and news", ["narrator", "documentary"]),
    AvatarProfile("luna", "Luna", AvatarStyle.ANIME.value, "female", "young", "Energetic anime presenter for gaming and youth content", ["gaming", "youth"]),
    AvatarProfile("rex", "Rex", AvatarStyle.CARTOON.value, "male", "young", "Playful cartoon character for explainers", ["explainer", "kids"]),
    AvatarProfile("pixel", "Pixel", AvatarStyle.PIXEL_ART.value, "neutral", "adult", "Retro pixel presenter for indie and game content", ["retro", "game"]),
    AvatarProfile("nova", "Nova 3D", AvatarStyle.THREE_D.value, "female", "adult", "Futuristic 3D digital human for product demos", ["product", "futuristic"]),
    AvatarProfile("min", "Min", AvatarStyle.MINIMALIST.value, "neutral", "adult", "Clean minimalist presenter for slides and summaries", ["minimal", "slides"]),
]


def _style_for(style: str | None) -> str:
    valid = {s.value for s in AvatarStyle}
    if style and style in valid:
        return style
    return AvatarStyle.REALISTIC.value


class AvatarEngine:
    """Virtual actor library + procedural avatar card generation."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "avs_avatar")

    def list_avatars(self) -> list[dict[str, Any]]:
        return [
            {
                "id": a.id,
                "name": a.name,
                "style": a.style,
                "gender": a.gender,
                "age_group": a.age_group,
                "description": a.description,
                "tags": a.tags,
            }
            for a in AVATAR_LIBRARY
        ]

    def select_for_scene(
        self,
        scene_type: str = "content",
        style: str | None = None,
        gender: str | None = None,
    ) -> AvatarProfile:
        """Pick the best-matching avatar for a scene."""
        style = _style_for(style)
        gender = (gender or "").lower()

        candidates = [a for a in AVATAR_LIBRARY if a.style == style]
        if not candidates:
            candidates = list(AVATAR_LIBRARY)

        if gender in (VoiceGender.MALE.value, VoiceGender.FEMALE.value):
            gendered = [a for a in candidates if a.gender == gender]
            if gendered:
                candidates = gendered

        # Scene-aware preference.
        preference: dict[str, str] = {
            "intro": "maya",
            "title_card": "nova",
            "outro": "maya",
            "b_roll": "min",
            "content": "noah",
        }
        for aid in (preference.get(scene_type), candidates[0].id):
            match = next((a for a in candidates if a.id == aid), None)
            if match:
                return match
        return candidates[0]

    async def generate_avatar_card(
        self,
        avatar: AvatarProfile,
        *,
        width: int = 640,
        height: int = 640,
        output_path: str | None = None,
    ) -> str:
        """Generate a styled avatar card image (Pillow) and return its path."""
        from PIL import Image, ImageDraw

        os.makedirs(self.output_dir, exist_ok=True)
        path = output_path or os.path.join(self.output_dir, f"avatar_{avatar.id}.png")

        top, bottom = STYLE_COLORS.get(avatar.style, STYLE_COLORS[AvatarStyle.REALISTIC.value])
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # Vertical gradient.
        rgb_top = tuple(int(top.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        rgb_bottom = tuple(int(bottom.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
        for y in range(height):
            t = y / max(height - 1, 1)
            color = tuple(round(a + (b - a) * t) for a, b in zip(rgb_top, rgb_bottom, strict=False))
            draw.line([(0, y), (width, y)], fill=color)

        # Silhouette circle (head) + shoulders.
        cx, cy = width // 2, int(height * 0.38)
        radius = int(width * 0.22)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(240, 240, 240))
        draw.rounded_rectangle(
            [cx - int(width * 0.30), cy + radius - 10, cx + int(width * 0.30), height],
            radius=int(height * 0.08),
            fill=(220, 220, 220),
        )

        # Name + style label.
        font_big = self._font(28)
        font_small = self._font(20)
        name_text = avatar.name
        bbox = draw.textbbox((0, 0), name_text, font=font_big)
        draw.text(
            ((width - (bbox[2] - bbox[0])) / 2, int(height * 0.74)),
            name_text,
            fill=(255, 255, 255),
            font=font_big,
        )
        style_text = f"{avatar.style} • {avatar.gender}"
        bbox = draw.textbbox((0, 0), style_text, font=font_small)
        draw.text(
            ((width - (bbox[2] - bbox[0])) / 2, int(height * 0.84)),
            style_text,
            fill=(230, 230, 230),
            font=font_small,
        )

        img.save(path, "PNG")
        return path

    @staticmethod
    def _font(size: int):
        try:
            from PIL import ImageFont

            return ImageFont.truetype("arial.ttf", size)
        except Exception:  # noqa: BLE001
            from PIL import ImageFont

            return ImageFont.load_default()
