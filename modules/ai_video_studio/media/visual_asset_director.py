"""Deterministic per-scene visual briefs for DARKSTUDIO.

This module prepares image prompts and composition guidance from scene data.
It does not generate images, inspect pixels, or add facts to the narration.
"""
from __future__ import annotations

import re
from typing import Any


_STUDIO_STYLES = {
    "whymentary": (
        "2D educational explainer, clean white background, bold marker-like outlines, "
        "flat bright colors, simple readable visual metaphors"
    ),
    "historical_documentary": (
        "cinematic illustrated historical documentary, layered depth, atmospheric lighting, "
        "period-appropriate materials and architecture"
    ),
    "felt_clay": (
        "handcrafted felt-clay stop motion, tactile wool fibers, soft rounded forms, "
        "consistent handcrafted materials and warm studio lighting"
    ),
}

_SHOT_SEQUENCE = (
    "wide_establishing",
    "medium_action",
    "close_up",
    "detail_insert",
    "over_shoulder",
    "low_angle",
    "environmental_wide",
    "reaction_close_up",
)

_SHOT_GUIDANCE = {
    "wide_establishing": "Plano geral que situa claramente o ambiente e a escala da ação.",
    "medium_action": "Plano médio com ação legível e espaço para linguagem corporal.",
    "close_up": "Close expressivo no elemento principal, sem cortar informação essencial.",
    "detail_insert": "Plano de detalhe de um objeto ou evidência explicitamente citada na cena.",
    "over_shoulder": "Plano sobre o ombro para mostrar a relação entre personagem e elemento observado.",
    "low_angle": "Ângulo baixo moderado para dar presença ao assunto, sem distorção gratuita.",
    "environmental_wide": "Plano aberto com profundidade em primeiro, segundo e terceiro plano.",
    "reaction_close_up": "Close de reação para destacar a resposta emocional descrita no roteiro.",
}

_CHARACTER_VISUAL_LOCKS = {
    "leo": "Leo: menino, cabelo loiro, camisa azul e calça escura; manter rosto, cabelo, roupa, cores e proporções idênticos em todas as cenas.",
    "mia": "Mia: menina, cabelo castanho preso e vestido vermelho; manter rosto, penteado, roupa, cores e proporções idênticos em todas as cenas.",
}

_CONTINUITY_CONSTRAINTS = (
    "Não trocar identidade, idade aparente, cabelo, figurino, paleta ou proporções dos personagens recorrentes.",
    "Não criar cópias do mesmo personagem na mesma cena, salvo quando o roteiro exigir explicitamente.",
    "Preservar o material visual e o acabamento artístico entre cenas consecutivas.",
)

_GENERIC = {"cena", "uma cena", "imagem", "ilustração", "visual", "mostrar"}
_TOKEN_RE = re.compile(r"[a-zà-ÿ0-9]{3,}", re.IGNORECASE)


def _first_text(scene: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = scene.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _tokens(value: str) -> set[str]:
    return {token.casefold() for token in _TOKEN_RE.findall(value)}


def _shot_for_scene(scene: dict[str, Any], index: int) -> tuple[str, str]:
    requested = _first_text(scene, "shot_type", "shot", "camera_shot").casefold().replace("-", "_").replace(" ", "_")
    locked = bool(scene.get("shot_type_locked"))
    if requested in _SHOT_GUIDANCE:
        return requested, _SHOT_GUIDANCE[requested]
    if locked and requested:
        return requested, f"Preservar o enquadramento manual definido: {requested}."
    shot = _SHOT_SEQUENCE[index % len(_SHOT_SEQUENCE)]
    return shot, _SHOT_GUIDANCE[shot]


def build_scene_visual_brief(scene: dict[str, Any], *, scene_index: int = 0, studio_id: str = "whymentary") -> dict[str, Any]:
    """Build one prompt from authored scene content without inventing new facts."""
    if not isinstance(scene, dict):
        raise ValueError("scene must be a dictionary")
    if studio_id not in _STUDIO_STYLES:
        raise ValueError(f"Unknown studio '{studio_id}'")
    if isinstance(scene_index, bool) or not isinstance(scene_index, int) or scene_index < 0:
        raise ValueError("scene_index must be a non-negative integer")

    narration = _first_text(scene, "voiceover_text", "narration", "dialogue", "text")
    description = _first_text(scene, "description", "title", "name")
    authored_prompt = _first_text(scene, "visual_prompt", "visualPrompt")
    suggestion = _first_text(scene, "visual_prompt_suggestion", "visual_direction")
    generic_prompt = authored_prompt.casefold().strip(" .,!?") in _GENERIC or len(authored_prompt) < 24
    visual_core = suggestion if generic_prompt and suggestion else authored_prompt or description or narration
    shot_type, shot_guidance = _shot_for_scene(scene, scene_index)

    if not visual_core:
        status = "needs_storyboard_detail"
        visual_core = "Aguardar descrição visual aprovada; não criar conteúdo por inferência."
    else:
        status = "ready_for_generation"

    prompt = (
        f"{_STUDIO_STYLES[studio_id]}. "
        f"Conteúdo visual sustentado pelo roteiro: {visual_core}. "
        f"Enquadramento: {shot_guidance} "
        "Representar somente fatos, objetos, personagens e ações sustentados pelo texto da cena. "
        "Não acrescentar datas, falas, eventos, símbolos ou personagens não fornecidos."
    )
    character_ids = scene.get("character_ids") or scene.get("continuity", {}).get("characters", [])
    character_visual_locks: dict[str, str] = {}
    if isinstance(character_ids, list) and character_ids:
        prompt += " Preservar as identidades visuais aprovadas de: " + ", ".join(map(str, character_ids)) + "."
        for character_id in character_ids:
            key = str(character_id).casefold()
            if key in _CHARACTER_VISUAL_LOCKS:
                character_visual_locks[key] = _CHARACTER_VISUAL_LOCKS[key]
        if character_visual_locks:
            prompt += " Travas visuais obrigatórias: " + " ".join(character_visual_locks.values())
            prompt += " " + " ".join(_CONTINUITY_CONSTRAINTS)

    negative = (
        "texto ilegível, legendas embutidas, marca d'água, logotipo, anatomia deformada, "
        "personagens duplicados, baixa resolução, composição confusa, estilo inconsistente"
    )
    if studio_id == "historical_documentary":
        negative += ", objetos modernos em época antiga, figurino anacrônico, fantasia apresentada como fato"
    if studio_id == "felt_clay":
        negative += ", aparência fotográfica, plástico brilhante, mudança de material entre cenas"

    return {
        "scene_index": scene_index,
        "status": status,
        "studio_id": studio_id,
        "source_text": narration,
        "visual_core": visual_core,
        "shot_type": shot_type,
        "shot_type_locked": bool(scene.get("shot_type_locked")),
        "image_prompt": prompt,
        "negative_prompt": negative,
        "requires_human_review": status != "ready_for_generation",
        "prompt_source": "authored" if authored_prompt and not generic_prompt else "scene_text_or_suggestion",
        "character_visual_locks": character_visual_locks,
        "continuity_constraints": list(_CONTINUITY_CONSTRAINTS) if character_visual_locks else [],
    }


def plan_scene_visuals(scenes: list[dict[str, Any]], *, studio_id: str = "whymentary") -> dict[str, Any]:
    """Plan visual briefs for a complete storyboard, varying unlocked shot types."""
    if not isinstance(scenes, list):
        raise ValueError("scenes must be a list")
    if not scenes:
        raise ValueError("scenes must not be empty")
    briefs = [
        build_scene_visual_brief(scene, scene_index=index, studio_id=studio_id)
        for index, scene in enumerate(scenes)
    ]
    repeated = []
    seen: dict[str, list[int]] = {}
    for brief in briefs:
        fingerprint = " ".join(sorted(_tokens(brief["visual_core"])))
        if fingerprint:
            seen.setdefault(fingerprint, []).append(brief["scene_index"])
    for indices in seen.values():
        if len(indices) > 1:
            repeated.append(indices)
    return {
        "studio_id": studio_id,
        "scene_count": len(briefs),
        "ready_count": sum(item["status"] == "ready_for_generation" for item in briefs),
        "review_count": sum(item["requires_human_review"] for item in briefs),
        "repeated_visual_groups": repeated,
        "briefs": briefs,
        "limitations": [
            "O planejamento usa texto e metadados declarados; não avalia qualidade visual por pixels.",
            "A variação de enquadramento é uma sugestão determinística, não uma animação de câmera.",
            "A geração efetiva da imagem depende de um provedor configurado e disponível.",
        ],
    }


def rank_visual_candidates(scene: dict[str, Any], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank candidates by metadata token overlap; this is not semantic image scoring."""
    if not isinstance(scene, dict) or not isinstance(candidates, list):
        raise ValueError("scene must be a dictionary and candidates must be a list")
    scene_text = " ".join(
        _first_text(scene, key)
        for key in ("visual_prompt", "visual_prompt_full", "description", "voiceover_text", "narration")
    )
    target = _tokens(scene_text)
    ranked = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            continue
        metadata = " ".join(
            str(candidate.get(key) or "")
            for key in ("prompt", "description", "tags", "provider")
        )
        candidate_tokens = _tokens(metadata)
        overlap = len(target & candidate_tokens)
        score = overlap / max(1, len(target))
        ranked.append({
            **candidate,
            "metadata_match_score": round(score, 4),
            "metadata_match_terms": sorted(target & candidate_tokens),
            "_input_order": index,
        })
    ranked.sort(key=lambda item: (-item["metadata_match_score"], item["_input_order"]))
    for item in ranked:
        item.pop("_input_order", None)
    return ranked
