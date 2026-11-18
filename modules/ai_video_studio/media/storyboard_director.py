"""Narration-aware storyboard planning and visual continuity checks.

This module turns authored scene text into deterministic image-generation
instructions. It does not add narrative facts or rewrite the user's narration.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any


_STUDIO_STYLE = {
    "whymentary": (
        "handcrafted felt-clay stop motion, tactile wool fibers, "
        "bright clean educational composition, soft studio lighting"
    ),
    "historical_documentary": (
        "cinematic historical illustration, layered environmental depth, "
        "period-appropriate materials, atmospheric natural lighting"
    ),
}


def _text(scene: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = scene.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _stable_scene_id(index: int, narration: str, description: str) -> str:
    source = narration or description or f"scene-{index}"
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:10]
    return f"scene-{index + 1:03d}-{digest}"


def _continuity_tokens(scene: dict[str, Any], character_ids: list[str], object_ids: list[str]) -> dict[str, Any]:
    return {
        "characters": sorted(set(str(item) for item in character_ids)),
        "objects": sorted(set(str(item) for item in object_ids)),
        "environment": _text(scene, "environment", "location", "setting", "chapter"),
        "costume": _text(scene, "costume", "wardrobe"),
        "time_of_day": _text(scene, "time_of_day", "lighting_time"),
    }


def _negative_prompt(studio_id: str, character_ids: list[str]) -> str:
    shared = (
        "text, captions, subtitles, watermark, logo, malformed anatomy, "
        "extra limbs, duplicate subjects, blurry, low detail, inconsistent style"
    )
    if character_ids:
        shared += ", unintended people, extra characters, altered character identity"
    if studio_id == "historical_documentary":
        shared += ", modern objects, anachronistic clothing, fantasy elements presented as historical fact"
    return shared


def build_cinematic_storyboard(
    scenes: list[dict[str, Any]],
    *,
    studio_id: str,
    character_ids: list[str] | None = None,
    object_ids: list[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Enrich scenes with unique visual prompts and continuity metadata."""
    if studio_id not in _STUDIO_STYLE:
        raise ValueError(f"Unknown studio '{studio_id}'")
    if not scenes:
        raise ValueError("Cannot build a storyboard without scenes")

    characters = list(character_ids or [])
    objects = list(object_ids or [])
    storyboard: list[dict[str, Any]] = []
    prompt_fingerprints: dict[str, list[int]] = {}
    warnings: list[str] = []

    for index, original in enumerate(scenes):
        scene = dict(original)
        narration = _text(scene, "voiceover_text", "narration", "dialogue")
        description = _text(scene, "description", "name")
        authored_visual = _text(scene, "visual_prompt", "visualPrompt")
        suggested_visual = _text(scene, "visual_prompt_suggestion")
        direction = _text(scene, "visual_direction")
        generic_visuals = {"cena", "uma cena", "ilustração", "imagem", "mostrar", "visual"}
        authored_is_generic = authored_visual.lower().strip(" .,!") in generic_visuals or len(authored_visual) < 28
        visual_core = (
            suggested_visual if authored_is_generic and suggested_visual
            else authored_visual or suggested_visual or description or narration
        )
        if not visual_core:
            visual_core = "Visualizar o conceito principal desta cena sem acrescentar fatos."

        # Keep the authored narration intact and explicitly constrain visual
        # interpretation to what this scene actually says.
        prompt = (
            f"{_STUDIO_STYLE[studio_id]}. "
            f"Conteúdo desta cena: {visual_core}. "
            f"Direção de composição: {direction or 'composição específica, clara e cinematográfica'}. "
            "Representar somente informações sustentadas pelo texto desta cena; "
            "não inventar eventos, personagens, datas, símbolos ou detalhes históricos."
        )
        if characters:
            prompt += (
                " Manter identidade, proporções, cabelo, roupas e paleta dos personagens "
                f"selecionados: {', '.join(characters)}."
            )
        if objects:
            prompt += f" Manter os objetos recorrentes selecionados: {', '.join(objects)}."

        fingerprint = re.sub(r"[^a-z0-9]+", " ", visual_core.lower()).strip()
        if fingerprint:
            prompt_fingerprints.setdefault(fingerprint, []).append(index)

        scene["storyboard_scene_id"] = _stable_scene_id(index, narration, description)
        scene["visual_prompt"] = (authored_visual if authored_visual and not authored_is_generic else prompt)
        scene["visual_prompt_full"] = prompt
        scene["negative_prompt"] = _negative_prompt(studio_id, characters)
        scene["continuity"] = _continuity_tokens(scene, characters, objects)
        scene["storyboard_status"] = "ready" if narration or description or authored_visual else "needs_review"
        storyboard.append(scene)

    repeated = [
        {"scene_indices": indices, "prompt": key}
        for key, indices in prompt_fingerprints.items()
        if len(indices) > 1
    ]
    for group in repeated:
        warnings.append(
            "Repeated visual concept in scenes "
            + ", ".join(str(index + 1) for index in group["scene_indices"])
            + "; review whether the images should differ."
        )
    for index, scene in enumerate(storyboard):
        if scene["storyboard_status"] == "needs_review":
            warnings.append(f"Scene {index + 1}: no narration or visual description; manual storyboard review required.")

    report = {
        "scene_count": len(storyboard),
        "ready_count": sum(item["storyboard_status"] == "ready" for item in storyboard),
        "needs_review_count": sum(item["storyboard_status"] == "needs_review" for item in storyboard),
        "repeated_visuals": repeated,
        "warnings": warnings,
        "historical_fact_policy": "visuals_must_not_add_unsupported_facts" if studio_id == "historical_documentary" else None,
    }
    return storyboard, report
