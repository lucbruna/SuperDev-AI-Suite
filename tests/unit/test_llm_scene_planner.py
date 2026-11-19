"""Tests for deterministic scene planning without a local LLM."""
from modules.ai_video_studio.media.llm import ScenePlanner


def test_fallback_creates_scene_specific_composition_guidance() -> None:
    plan = ScenePlanner().fallback(
        "Uma cidade emerge do nevoeiro. Um trem atravessa a ponte. A locomotiva chega à estação.",
        num_scenes=3,
        duration=30.0,
    )
    scenes = plan["scenes"]
    assert len(scenes) == 3
    assert [scene["shot_type"] for scene in scenes] == ["establishing", "wide", "medium"]
    assert "very wide establishing view" in scenes[0]["visual_prompt"]
    assert "wide environmental composition" in scenes[1]["visual_prompt"]
    assert "medium shot" in scenes[2]["visual_prompt"]
    assert len({scene["visual_prompt"] for scene in scenes}) == 3
    assert all("Keep the user's requested art style" in scene["visual_prompt"] for scene in scenes)


def test_normalize_replaces_unsupported_shot_type_with_valid_fallback() -> None:
    scenes = ScenePlanner()._normalize(
        [{"name": "Cena", "description": "Ação", "shot_type": "drone_360"}],
        num_scenes=1,
        duration=10.0,
    )
    assert scenes[0]["shot_type"] == "establishing"


def test_fallback_assigns_coherent_narrative_progression() -> None:
    scenes = ScenePlanner().fallback(
        "Uma expedição parte ao amanhecer. A equipe atravessa a floresta. "
        "Encontra ruínas antigas. Registra a descoberta e retorna.",
        num_scenes=4,
        duration=40.0,
    )["scenes"]
    assert [scene["narrative_role"] for scene in scenes] == [
        "hook", "context", "development", "payoff"
    ]


def test_single_scene_combines_hook_and_payoff() -> None:
    scenes = ScenePlanner().fallback(
        "Uma máquina transforma água salgada em água potável.",
        num_scenes=1,
        duration=10.0,
    )["scenes"]
    assert scenes[0]["narrative_role"] == "hook_payoff"


def test_ollama_normalization_assigns_roles_by_scene_position() -> None:
    scenes = ScenePlanner()._normalize(
        [{"name": "A"}, {"name": "B"}, {"name": "C"}],
        num_scenes=3,
        duration=30.0,
    )
    assert [scene["narrative_role"] for scene in scenes] == [
        "hook", "context", "payoff"
    ]
