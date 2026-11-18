"""Metadata-based visual quality intelligence for DARKSTUDIO storyboards.

The score evaluates authored scene descriptors. It is not computer vision and
does not claim to inspect the final encoded pixels.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


_STUDIO_WEIGHTS = {
    "whymentary": {"motion": 20, "composition": 25, "variety": 25, "clarity": 30},
    "historical_documentary": {"motion": 25, "composition": 25, "variety": 25, "clarity": 25},
}


def _camera_motion(scene: dict[str, Any]) -> tuple[bool, dict[str, float]]:
    camera = scene.get("camera") or {}
    keyframes = camera.get("keyframes") if isinstance(camera, dict) else None
    if isinstance(keyframes, list) and len(keyframes) >= 2:
        first, last = keyframes[0], keyframes[-1]
        delta = {
            "zoom": abs(float(last.get("zoom", 1)) - float(first.get("zoom", 1))),
            "pan": abs(float(last.get("dx", 0)) - float(first.get("dx", 0))) +
                   abs(float(last.get("dy", 0)) - float(first.get("dy", 0))),
            "roll": abs(float(last.get("roll", 0)) - float(first.get("roll", 0))),
        }
        return any(value > 0.001 for value in delta.values()), delta
    if isinstance(camera, dict):
        delta = {
            "zoom": abs(float(camera.get("zoom", 1)) - 1),
            "pan": abs(float(camera.get("dx", 0))) + abs(float(camera.get("dy", 0))),
            "roll": abs(float(camera.get("roll", 0))),
        }
        return any(value > 0.001 for value in delta.values()), delta
    return False, {"zoom": 0.0, "pan": 0.0, "roll": 0.0}


def _primitive_motion(scene: dict[str, Any]) -> int:
    animated = 0
    for layer in ("rects", "circles", "lines"):
        for item in scene.get(layer) or []:
            if not isinstance(item, dict):
                continue
            fields = ("dx", "dy", "dx1", "dy1", "dx2", "dy2", "motion_dx", "motion_dy", "grow_frames")
            if any(abs(float(item.get(field, 0) or 0)) > 0 for field in fields):
                animated += 1
    for particle in scene.get("particles") or []:
        if isinstance(particle, dict) and any(
            abs(float(particle.get(field, 0) or 0)) > 0 for field in ("vx", "vy", "gy")
        ):
            animated += 1
    return animated


def _scene_signature(scene: dict[str, Any]) -> tuple[Any, ...]:
    return (
        scene.get("shot_type", "medium"),
        scene.get("background_type", "gradient"),
        tuple(scene.get("background_colors") or []),
        len(scene.get("rects") or []),
        len(scene.get("circles") or []),
        len(scene.get("lines") or []),
        len(scene.get("particles") or []),
        str((scene.get("text") or {}).get("content", ""))[:32]
        if isinstance(scene.get("text"), dict) else "",
    )


def analyze_visual_quality(
    scenes: list[dict[str, Any]],
    *,
    studio_id: str,
    fps: int,
) -> dict[str, Any]:
    """Score camera motion, primitive animation, shot variety and scene richness."""
    if studio_id not in _STUDIO_WEIGHTS:
        raise ValueError(f"Unknown studio '{studio_id}'")
    if fps < 1:
        raise ValueError("fps must be a positive integer")
    if not scenes:
        raise ValueError("scenes cannot be empty")
    if any(not isinstance(scene, dict) for scene in scenes):
        raise ValueError("every scene must be an object")

    rows: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    shots: list[str] = []
    transition_types: list[str] = []
    signatures: list[tuple[Any, ...]] = []
    camera_moving = 0
    animated_primitives = 0
    composition_scores: list[float] = []
    previous_character_ids: tuple[str, ...] | None = None
    character_changes = 0

    for index, scene in enumerate(scenes):
        moving, camera_delta = _camera_motion(scene)
        primitive_count = sum(len(scene.get(layer) or []) for layer in ("rects", "circles", "lines"))
        particle_count = len(scene.get("particles") or [])
        animated_count = _primitive_motion(scene)
        text = scene.get("text") or {}
        text_present = bool(text.get("content") if isinstance(text, dict) else text)
        shot = str(scene.get("shot_type") or "medium")
        transition = scene.get("transition_out") or {"type": "cut"}
        transition_type = str(transition.get("type") or "cut")
        transition_types.append(transition_type)
        duration = max(1 / fps, float(scene.get("duration") or 0))
        character_ids = tuple(sorted(str(value) for value in (
            scene.get("_darkstudio_characters") or scene.get("character_ids") or []
        )))
        if previous_character_ids is not None and character_ids != previous_character_ids:
            character_changes += 1
            warnings.append({"code": "character_continuity_change", "severity": "warning",
                             "scene_index": index, "previous": list(previous_character_ids),
                             "current": list(character_ids)})
        previous_character_ids = character_ids

        if moving:
            camera_moving += 1
        animated_primitives += animated_count
        shots.append(shot)
        signature = _scene_signature(scene)
        signatures.append(signature)
        richness = min(1.0, (primitive_count + particle_count * 0.5) / 8.0)
        if text_present:
            richness = min(1.0, richness + 0.15)
        composition_scores.append(richness)
        row = {
            "scene_index": index,
            "shot_type": shot,
            "transition_out": transition_type,
            "duration_seconds": round(duration, 3),
            "camera_motion": moving,
            "camera_delta": {key: round(value, 4) for key, value in camera_delta.items()},
            "animated_primitive_count": animated_count,
            "primitive_count": primitive_count,
            "particle_count": particle_count,
            "has_text": text_present,
            "character_ids": list(character_ids),
            "composition_richness": round(richness, 3),
        }
        rows.append(row)
        if not moving and animated_count == 0:
            warnings.append({"code": "static_scene_metadata", "severity": "warning", "scene_index": index})
        if duration > 12:
            warnings.append({"code": "long_unchanged_shot_risk", "severity": "warning",
                             "scene_index": index, "duration_seconds": round(duration, 3)})
        if index and signature == signatures[index - 1]:
            warnings.append({"code": "consecutive_visual_repetition", "severity": "warning",
                             "scene_index": index})

    shot_counts = dict(Counter(shots))
    transition_counts = dict(Counter(transition_types))
    unique_shots = len(shot_counts)
    if len(scenes) >= 4 and unique_shots < 3:
        warnings.append({"code": "low_shot_variety", "severity": "warning", "unique_shots": unique_shots})
    if studio_id == "historical_documentary":
        if len(scenes) >= 4 and len(transition_counts) < 2:
            warnings.append({"code": "low_transition_variety", "severity": "info",
                             "transition_types": list(transition_counts)})
        if camera_moving < max(1, len(scenes) * 0.6):
            warnings.append({"code": "cinematic_camera_coverage_low", "severity": "warning",
                             "moving_scenes": camera_moving, "scene_count": len(scenes)})
    elif studio_id == "whymentary":
        textless = sum(1 for row in rows if not row["has_text"])
        if textless == len(rows):
            warnings.append({"code": "no_explanatory_text_metadata", "severity": "info"})

    n = len(scenes)
    weights = _STUDIO_WEIGHTS[studio_id]
    motion_ratio = camera_moving / n
    if studio_id == "whymentary":
        motion_ratio = min(1.0, (camera_moving + (animated_primitives / max(1, n * 2))) / n)
    variety_ratio = min(1.0, unique_shots / min(4, n))
    composition_ratio = sum(composition_scores) / n
    clarity_ratio = sum(1 for row in rows if row["has_text"] or row["primitive_count"] >= 2) / n
    components = {
        "motion": round(motion_ratio * 100, 1),
        "composition": round(composition_ratio * 100, 1),
        "variety": round(variety_ratio * 100, 1),
        "clarity": round(clarity_ratio * 100, 1),
    }
    score = round(sum(components[key] * weights[key] for key in components) / 100)
    critical = any(item["severity"] == "critical" for item in warnings)
    status = "blocked" if critical else ("needs_review" if warnings else "good")
    return {
        "studio_id": studio_id,
        "status": status,
        "score": score,
        "score_label": "pontuação heurística de metadados",
        "components": components,
        "scene_count": n,
        "moving_camera_scenes": camera_moving,
        "animated_primitives": animated_primitives,
        "unique_shot_types": unique_shots,
        "shot_counts": shot_counts,
        "transition_counts": transition_counts,
        "character_continuity_changes": character_changes,
        "scenes": rows,
        "warnings": warnings,
        "analysis_method": "scene_descriptor_metadata",
        "limitations": [
            "Não inspeciona pixels do MP4 final nem mede qualidade visual por visão computacional.",
            "Não comprova continuidade facial; compara apenas IDs de personagens registrados nos metadados.",
            "A pontuação é heurística e não substitui revisão humana.",
        ],
    }
