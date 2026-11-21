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



def classify_narrative_beat(scene: dict[str, Any]) -> str:
    """Classify the role of a scene from its own text; never infer new facts."""
    source = " ".join(
        str(scene.get(key) or "")
        for key in ("narration", "voiceover_text", "dialogue", "description", "visual_prompt")
    ).lower()
    rules = (
        ("hook", ("imagine", "você sabia", "sabia que", "e se ", "mistério", "segredo")),
        ("context", ("naquela época", "contexto", "durante o século", "no início", "era ", "origem")),
        ("cause_effect", ("porque", "por causa", "provocou", "levou a", "resultou", "consequência", "causou")),
        ("comparison", ("compar", "diferente", "enquanto", "ao contrário", "versus", "antes e depois")),
        ("process", ("como funciona", "etapa", "processo", "primeiro", "depois", "em seguida")),
        ("revelation", ("descobriu", "revelou", "evidência", "prova", "documento mostra")),
        ("conclusion", ("portanto", "em resumo", "concluindo", "lição", "hoje sabemos", "conclusão")),
    )
    return next((beat for beat, terms in rules if any(term in source for term in terms)), "development")


def _visual_direction(studio_id: str, shot: str, beat: str) -> str:
    """Return an actionable composition cue while preserving each studio's visual identity."""
    framing = {
        "establishing": "comece com plano geral que situe espaço, época e escala",
        "wide": "mostre a relação espacial entre os elementos importantes",
        "medium": "organize a ação principal em plano médio com leitura imediata",
        "close_up": "aproxime a câmera da expressão ou ação humana decisiva",
        "detail": "isole o objeto, documento ou evidência narrada em primeiro plano",
        "tracking": "use deslocamento lateral ou travelling para acompanhar a ação",
    }.get(shot, "use composição clara e específica para a ação")
    beat_cue = {
        "hook": "crie uma imagem-gancho com silhueta e contraste visual fortes",
        "context": "priorize cenário e pistas visuais de contexto",
        "cause_effect": "torne causa e consequência legíveis no mesmo enquadramento",
        "process": "organize a ação em sequência visual fácil de entender",
        "comparison": "coloque os elementos comparados em áreas distintas e equilibradas",
        "revelation": "dê destaque visual à evidência sem acrescentar informação não narrada",
        "conclusion": "feche com composição limpa que sintetize a ideia narrada",
        "development": "mostre a ação ou conceito específico desta passagem",
    }.get(beat, "mostre a ideia narrada")
    if studio_id == "whymentary":
        style = "fundo branco, formas 2D simples, cores chapadas e legibilidade didática"
    elif studio_id == "historical_documentary":
        style = "ilustração histórica cinematográfica, profundidade em camadas, luz atmosférica e materiais de época"
    elif studio_id == "felt_clay":
        style = "materiais táteis de feltro e argila, iluminação suave e volumes artesanais"
    else:
        # A direção customizada pertence ao usuário; nunca injete uma estética predefinida.
        style = "preserve integralmente o estilo visual, materiais, paleta e direção de arte definidos pelo usuário"
    return f"{framing}; {beat_cue}; {style}."


def _needs_visual_prompt(scene: dict[str, Any]) -> bool:
    prompt = str(scene.get("visual_prompt") or "").strip()
    if len(prompt) < 28:
        return True
    generic = {"cena", "uma cena", "ilustração", "imagem", "mostrar", "visual"}
    return prompt.lower().strip(" .,!") in generic

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
        scene["narrative_beat"] = classify_narrative_beat(scene)
        scene["visual_direction"] = _visual_direction(
            studio_id, shot, scene["narrative_beat"]
        )
        if _needs_visual_prompt(scene):
            source_text = str(
                scene.get("voiceover_text") or scene.get("narration")
                or scene.get("description") or scene.get("name") or ""
            ).strip()
            if source_text:
                scene["visual_prompt_suggestion"] = (
                    f"Representar visualmente, sem acrescentar fatos: {source_text}. "
                    f"{scene['visual_direction']}"
                )
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
            else:
                # Custom and felt-clay profiles use a neutral hard cut unless
                # the user or the scene planner explicitly authored a transition.
                scene["transition_out"] = {"type": "cut", "duration_frames": 0}
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
        beat = str(scene.get("narrative_beat") or classify_narrative_beat(scene))
        visual_prompt = str(scene.get("visual_prompt") or "").strip()
        shot_counts[shot] = shot_counts.get(shot, 0) + 1
        transition = scene.get("transition_out") or {"type": "cut"}
        transition_type = str(transition.get("type", "cut"))
        transition_counts[transition_type] = transition_counts.get(transition_type, 0) + 1
        rows.append({
            "scene_index": index,
            "start_seconds": round(timeline_cursor, 3),
            "duration_seconds": round(duration, 3),
            "shot_type": shot,
            "narrative_beat": beat,
            "visual_prompt_present": bool(visual_prompt),
            "visual_direction": str(scene.get("visual_direction") or ""),
            "visual_prompt_suggestion": str(scene.get("visual_prompt_suggestion") or ""),
            "speech_words": words,
            "speech_wpm": wpm,
            "pacing": "fast" if wpm > target_words_per_minute * 1.25 else "slow" if words and wpm < target_words_per_minute * 0.65 else "balanced",
            "transition_out": transition_type,
        })
        if words and wpm > target_words_per_minute * 1.5:
            warnings.append(f"Scene {index + 1}: narration is dense ({wpm} words/min); consider extending or splitting the scene")
        if duration < 1.0:
            warnings.append(f"Scene {index + 1}: shot is shorter than one second")
        if not visual_prompt and not scene.get("visual_prompt_suggestion"):
            warnings.append(
                f"Scene {index + 1}: no specific visual prompt; add an image that directly illustrates the narration"
            )
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
