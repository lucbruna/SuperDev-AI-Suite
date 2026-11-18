"""DARKSTUDIO visual profiles for the two independent creative studios.

Profiles provide deterministic scene defaults for the existing SceneCanvas.
They do not claim to generate hand-drawn artwork or documentary footage:
they define the visual contract and scene-level defaults used by render jobs.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class StudioProfile:
    """Immutable visual contract for a DARKSTUDIO production studio."""

    studio_id: str
    display_name: str
    visual_language: str
    background_type: str
    background_colors: tuple[str, ...]
    palette: tuple[str, ...]
    noise: float
    grading_strength: float
    default_text_color: str
    default_text_size: int
    camera_defaults: tuple[tuple[str, float], ...]


WHYMENTARY = StudioProfile(
    studio_id="whymentary",
    display_name="Whymentary",
    visual_language="2D marker explainer; clean white canvas; flat bright colors",
    background_type="solid",
    background_colors=("#FFFFFF",),
    palette=("#FFFFFF", "#111827", "#FACC15", "#2563EB", "#EF4444", "#22C55E"),
    noise=0.0,
    grading_strength=0.0,
    default_text_color="#111827",
    default_text_size=42,
    camera_defaults=(("zoom", 1.0), ("dx", 0.0), ("dy", 0.0), ("roll", 0.0)),
)

HISTORICAL_DOCUMENTARY = StudioProfile(
    studio_id="historical_documentary",
    display_name="Documentário Histórico",
    visual_language="Cinematic illustrated documentary; layered environments; dramatic light and depth",
    background_type="gradient",
    background_colors=("#101827", "#34445B", "#151B2A"),
    palette=("#D7B56D", "#C7D2E0", "#64748B", "#1E293B"),
    noise=0.035,
    grading_strength=0.08,
    default_text_color="#F8FAFC",
    default_text_size=44,
    camera_defaults=(("zoom", 1.025), ("dx", 0.12), ("dy", 0.0), ("roll", 0.0)),
)

PROFILES: dict[str, StudioProfile] = {
    WHYMENTARY.studio_id: WHYMENTARY,
    HISTORICAL_DOCUMENTARY.studio_id: HISTORICAL_DOCUMENTARY,
}


def get_studio_profile(studio_id: str) -> StudioProfile:
    """Return a registered profile; reject unknown studio identifiers."""
    try:
        return PROFILES[studio_id]
    except KeyError as exc:
        choices = ", ".join(sorted(PROFILES))
        raise ValueError(f"Unknown studio '{studio_id}'. Available studios: {choices}") from exc


def apply_studio_profile(
    studio_id: str,
    scene: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a copied, renderable scene with studio-owned visual defaults.

    Studio-owned background, palette, noise and camera defaults are enforced
    so a project cannot accidentally inherit the other studio's look.
    Scene-specific shapes, text content, particles and timing are preserved.
    """
    profile = get_studio_profile(studio_id)
    result = deepcopy(scene or {})
    result["studio_id"] = profile.studio_id
    result["visual_language"] = profile.visual_language
    result["background_type"] = profile.background_type
    result["background_colors"] = list(profile.background_colors)
    result["palette"] = list(profile.palette)
    result["noise"] = profile.noise
    result["grading_strength"] = profile.grading_strength

    text = deepcopy(result.get("text") or {})
    text.setdefault("color", profile.default_text_color)
    text.setdefault("size", profile.default_text_size)
    result["text"] = text

    camera = dict(profile.camera_defaults)
    camera.update(result.get("camera") or {})
    result["camera"] = camera
    return result
