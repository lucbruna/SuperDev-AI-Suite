"""Deterministic editing director for shot variety and scene transitions."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.media.camera_motion import studio_camera_move


def classify_shot(scene: dict[str, Any], previous: str | None = None) -> str:
    """Infer a visual shot from authored visual and spoken text, not guesses."""
    source = " ".join(
        str(scene.get(key) or "")
        for key in ("visual_prompt", "visualPrompt", "description", "name", "narration", "voiceover_text")
    ).lower()
    rules = (
        ("establishing", ("panorama", "paisagem", "horizonte", "cidade inteira", "mapa geral", "establishing")),
        ("detail", ("detalhe", "close detail", "artefato", "documento", "manuscrito", "objeto em primeiro plano")),
        ("tracking", ("caminha", "atravessa", "cavalg", "navega", "march", "percorre", "viagem")),
        ("close_up", ("rosto", "expressão", "reação", "olhos", "emoção", "close-up", "close up")),
    )
    selected = next((shot for shot, words in rules if any(word in source for word in words)), "medium")
    if selected == previous:
        selected = {"medium": "close_up", "close_up": "tracking", "tracking": "wide", "wide": "detail", "detail": "medium", "establishing": "medium"}[selected]
    return selected


def direct_storyboard(
    scenes: list[dict[str, Any]], *, studio_id: str, fps: int, fallback_duration: float
) -> list[dict[str, Any]]:
    """Apply shot variety, camera movement and style-aware transitions."""
    if not scenes:
        raise ValueError("Cannot direct an empty storyboard")
    directed = [dict(scene) for scene in scenes]
    previous_shot: str | None = None
    for index, scene in enumerate(directed):
        shot = str(scene.get("shot_type") or classify_shot(scene, previous_shot))
        scene["shot_type"] = shot
        previous_shot = shot
        scene_frames = max(2, int(max(0.1, float(scene.get("duration") or fallback_duration)) * fps))
        if not scene.get("camera"):
            scene["camera"] = studio_camera_move(studio_id, index, scene_frames, shot)
        if index < len(directed) - 1 and not scene.get("transition_out"):
            if studio_id == "historical_documentary":
                current_chapter = scene.get("chapter")
                next_chapter = directed[index + 1].get("chapter")
                if current_chapter and next_chapter and current_chapter != next_chapter:
                    scene["transition_out"] = {"type": "fade_through_black", "duration_frames": max(2, fps // 3)}
                else:
                    scene["transition_out"] = {"type": "crossfade", "duration_frames": max(2, fps // 2)}
            elif studio_id == "whymentary":
                scene["transition_out"] = {"type": "cut", "duration_frames": 0}
            else:
                raise ValueError(f"Unknown studio '{studio_id}'")
    return directed
