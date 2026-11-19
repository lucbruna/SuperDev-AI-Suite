"""Tests for deterministic narrative beat segmentation."""
from modules.ai_video_studio.media.llm import _split_prompt_into_scene_beats


def test_scene_beats_preserve_sentence_order_and_content():
    prompt = (
        "A cidade cresceu perto do rio. "
        "O comércio trouxe novas rotas. "
        "A ferrovia conectou regiões distantes. "
        "A população mudou com a industrialização."
    )
    beats = _split_prompt_into_scene_beats(prompt, 2)

    assert len(beats) == 2
    assert "A cidade cresceu perto do rio." in beats[0]
    assert "O comércio trouxe novas rotas." in beats[0]
    assert "A ferrovia conectou regiões distantes." in beats[1]
    assert "A população mudou com a industrialização." in beats[1]


def test_single_sentence_uses_clause_boundaries_before_word_chunks():
    prompt = "O motor aquece, o líquido circula e o radiador dissipa calor."
    beats = _split_prompt_into_scene_beats(prompt, 3)

    assert len(beats) == 3
    assert "motor aquece" in beats[0]
    assert "líquido circula" in beats[1]
    assert "radiador dissipa calor" in beats[2]


def test_short_brief_uses_contiguous_word_ranges_without_reordering():
    prompt = "A água evapora e forma nuvens"
    beats = _split_prompt_into_scene_beats(prompt, 3)

    assert len(beats) == 3
    assert all(beats)
    assert " ".join(beats).split() == prompt.split()


def test_empty_brief_returns_requested_number_of_reviewable_beats():
    assert _split_prompt_into_scene_beats("   ", 4) == [
        "Parte 1", "Parte 2", "Parte 3", "Parte 4"
    ]
