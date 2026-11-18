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


def build_editing_report(
    scenes: list[dict[str, Any]], *, fps: int, fallback_duration: float,
    target_words_per_minute: int = 145,
) -> dict[str, Any]:
    """Summarize pacing, shot variety and transition choices for QA/UI."""
    if fps < 1 or target_words_per_minute < 1:
        raise ValueError("fps and target_words_per_minute must be positive")
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    shot_counts: dict[str, int] = {}
    transition_counts: dict[str, int] = {}
    timeline_cursor = 0.0
    for index, scene in enumerate(scenes):
        duration = max(1, int(max(0.1, float(scene.get("duration") or fallback_duration)) * fps)) / fps
        speech = str(scene.get("voiceover_text") or scene.get("narration") or scene.get("dialogue") or "").strip()
        words = len(speech.split())
        wpm = round(words / duration * 60, 1) if words else 0.0
        shot = str(scene.get("shot_type") or "medium")
        shot_counts[shot] = shot_counts.get(shot, 0) + 1
        transition = scene.get("transition_out") or {"type": "cut"}
        transition_type = str(transition.get("type", "cut"))
        transition_counts[transition_type] = transition_counts.get(transition_type, 0) + 1
        rows.append({
            "scene_index": index,
            "start_seconds": round(timeline_cursor, 3),
            "duration_seconds": round(duration, 3),
            "shot_type": shot,
            "speech_words": words,
            "speech_wpm": wpm,
            "pacing": "fast" if wpm > target_words_per_minute * 1.25 else "slow" if words and wpm < target_words_per_minute * 0.65 else "balanced",
            "transition_out": transition_type,
        })
        if words and wpm > target_words_per_minute * 1.5:
            warnings.append(f"Scene {index + 1}: narration is dense ({wpm} words/min); consider extending or splitting the scene")
        if duration < 1.0:
            warnings.append(f"Scene {index + 1}: shot is shorter than one second")
        timeline_cursor += duration
        if transition_type == "crossfade" and index < len(scenes) - 1:
            overlap = min(int(transition.get("duration_frames", 0)), max(0, int(duration * fps) // 2))
            timeline_cursor -= overlap / fps
    unique_shots = len(shot_counts)
    if len(scenes) >= 4 and unique_shots < 3:
        warnings.append("Low shot variety: use at least three different shot scales or compositions")
    return {
        "scene_count": len(scenes),
        "timeline_duration_seconds": round(max(0.0, timeline_cursor), 3),
        "target_words_per_minute": target_words_per_minute,
        "shot_counts": shot_counts,
        "transition_counts": transition_counts,
        "scenes": rows,
        "warnings": warnings,
    }
