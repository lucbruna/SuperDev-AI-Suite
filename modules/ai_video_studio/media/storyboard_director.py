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


def _character_identity_prompt(character_ids: list[str]) -> str:
    """Use only user-defined character references; never inject preset identities."""
    return " ".join(
        f"Preservar a identidade visual aprovada e fornecida pelo usuário para {item}."
        for item in character_ids
    )


def analyze_storyboard_continuity(scenes: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate declared per-scene character/object continuity; this is metadata QA, not image recognition."""
    if not isinstance(scenes, list):
        raise ValueError("scenes must be a list")
    warnings: list[dict[str, Any]] = []
    character_sets: list[tuple[int, tuple[str, ...]]] = []
    appearances: dict[str, dict[str, set[str]]] = {}
    for index, scene in enumerate(scenes):
        continuity = scene.get("continuity") if isinstance(scene.get("continuity"), dict) else {}
        raw_characters = continuity.get("characters") or scene.get("character_ids") or scene.get("_darkstudio_characters")
        if raw_characters is not None:
            ids = tuple(sorted(set(str(value) for value in raw_characters)))
            character_sets.append((index, ids))
        raw_appearance = scene.get("character_appearance") or scene.get("character_costumes") or {}
        if isinstance(raw_appearance, dict):
            for character_id, description in raw_appearance.items():
                if isinstance(description, str) and description.strip():
                    appearances.setdefault(str(character_id), {}).setdefault(description.strip().lower(), set()).add(str(index + 1))
    for (left_index, left_ids), (right_index, right_ids) in zip(character_sets, character_sets[1:]):
        if left_ids != right_ids:
            warnings.append({
                "type": "character_presence_change",
                "scene_indices": [left_index, right_index],
                "previous_characters": list(left_ids),
                "current_characters": list(right_ids),
                "severity": "review",
                "message": "A lista de personagens mudou entre cenas consecutivas; confirme se a entrada ou saída é intencional.",
            })
    for character_id, variants in appearances.items():
        if len(variants) > 1:
            scene_groups = [sorted(int(value) - 1 for value in indices) for indices in variants.values()]
            all_indices = sorted({index for group in scene_groups for index in group})
            warnings.append({
                "type": "character_appearance_drift",
                "scene_indices": all_indices,
                "character_id": character_id,
                "variants": [{"description": description, "scene_numbers": sorted(int(value) for value in indices)} for description, indices in variants.items()],
                "severity": "high",
                "message": f"Descrições visuais diferentes foram declaradas para o personagem {character_id}; revise cabelo, roupa e paleta.",
            })
    return {
        "status": "review_required" if warnings else "consistent_metadata",
        "checked_scenes": len(scenes),
        "warnings": warnings,
        "method": "declared_scene_metadata_consistency",
        "limitations": [
            "Esta verificação compara metadados e descrições declaradas, não reconhece personagens dentro dos pixels das imagens.",
            "Mudanças de figurino intencionais devem ser aprovadas pelo roteiro e registradas explicitamente.",
        ],
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
    style_prompt: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Enrich scenes with unique visual prompts and continuity metadata."""
    if studio_id not in {*_STUDIO_STYLE, "custom", "felt_clay"}:
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
        selected_style = (style_prompt or "").strip() or _STUDIO_STYLE.get(
            studio_id, "visual style, materials, palette and art direction defined by the user's prompt"
        )
        prompt = (
            f"{selected_style}. "
            f"Conteúdo desta cena: {visual_core}. "
            f"Direção de composição: {direction or 'composição específica, clara e cinematográfica'}. "
            "Representar somente informações sustentadas pelo texto desta cena; "
            "não inventar eventos, personagens, datas, símbolos ou detalhes históricos."
        )
        identity_prompt = _character_identity_prompt(characters)
        if identity_prompt:
            prompt += " Guia de identidade obrigatório: " + identity_prompt
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

    continuity_report = analyze_storyboard_continuity(storyboard)
    warnings.extend(item["message"] for item in continuity_report["warnings"])
    report = {
        "scene_count": len(storyboard),
        "continuity_report": continuity_report,
        "ready_count": sum(item["storyboard_status"] == "ready" for item in storyboard),
        "needs_review_count": sum(item["storyboard_status"] == "needs_review" for item in storyboard),
        "repeated_visuals": repeated,
        "warnings": warnings,
        "historical_fact_policy": "visuals_must_not_add_unsupported_facts" if studio_id == "historical_documentary" else None,
    }
    return storyboard, report
