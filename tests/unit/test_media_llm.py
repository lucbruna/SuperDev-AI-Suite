"""Unit tests for the media LLM scene planner (Volume 3/4) — fallbacks.

The planner must be fully deterministic when Ollama is unreachable, and the
JSON extraction must tolerate markdown fences and embedded JSON.
"""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from modules.ai_video_studio.media import llm
from modules.ai_video_studio.media.llm import ScenePlanner, _extract_json, generate_text


# ── JSON extraction ──────────────────────────────────────────────────


def test_extract_json_plain() -> None:
    payload = '[{"name": "S1", "duration": 3.0}]'
    assert _extract_json(payload) == [{"name": "S1", "duration": 3.0}]


def test_extract_json_markdown_fence() -> None:
    payload = '```json\n[{"name": "S1", "duration": 3.0}]\n```'
    assert _extract_json(payload) == [{"name": "S1", "duration": 3.0}]


def test_extract_json_embedded_in_prose() -> None:
    # The scanner grabs the first complete JSON value it finds (the object).
    payload = 'Sure! Here is the plan: [{"name": "S1", "duration": 3.0}] Enjoy!'
    extracted = _extract_json(payload)
    assert isinstance(extracted, dict)
    assert extracted.get("name") == "S1"


def test_extract_json_invalid_returns_none() -> None:
    assert _extract_json("no json here at all") is None


# ── Deterministic fallback ───────────────────────────────────────────


def test_fallback_deterministic_same_input() -> None:
    planner = ScenePlanner()
    a = planner.fallback("A robot explores a neon city", num_scenes=3, duration=9.0)
    b = planner.fallback("A robot explores a neon city", num_scenes=3, duration=9.0)
    assert a == b


def test_fallback_different_prompt_differs() -> None:
    planner = ScenePlanner()
    a = planner.fallback("a forest", num_scenes=2)
    b = planner.fallback("the ocean", num_scenes=2)
    assert a["scenes"][0]["description"] != b["scenes"][0]["description"]


def test_fallback_scene_count_and_fields() -> None:
    planner = ScenePlanner()
    result = planner.fallback("cinematic drone shot", num_scenes=3, duration=12.0)
    assert len(result["scenes"]) == 3
    assert result["ai_generated"] is False
    assert result["provider"] is None
    scene = result["scenes"][0]
    assert scene["index"] == 0
    assert scene["duration"] == pytest.approx(4.0)  # 12/3
    assert len(scene["background_colors"]) == 2
    assert scene["background_colors"][0].startswith("#")
    assert isinstance(scene["text"], dict)
    assert scene["camera"] is not None
    assert scene["particles"], "fallback must include renderable particles"


def test_fallback_word_chunks_scene_names() -> None:
    planner = ScenePlanner()
    result = planner.fallback("alpha beta gamma", num_scenes=2)
    assert result["scenes"][0]["name"] == "Scene 1"
    assert result["scenes"][1]["name"] == "Scene 2"


# ── plan() falls back when Ollama is down ────────────────────────────


def test_plan_falls_back_when_ollama_unreachable() -> None:
    planner = ScenePlanner()
    with patch.object(ScenePlanner, "_call_ollama", side_effect=RuntimeError("no ollama")):
        result = planner.plan("a sunrise timelapse", num_scenes=3, duration=9.0)
    assert result["ai_generated"] is False
    assert len(result["scenes"]) == 3


def test_plan_uses_ollama_when_json_valid() -> None:
    scenes = [
        {"name": "Opening", "duration": 2.0, "background_colors": ["#1a1a2e", "#16213e"]},
    ]
    payload = json.dumps(scenes)

    def _fake_ollama(self, prompt, *, num_scenes, duration, timeout):
        return payload

    planner = ScenePlanner()
    with patch.object(ScenePlanner, "_call_ollama", new=_fake_ollama):
        result = planner.plan("test", num_scenes=1, duration=2.0)
    assert result["ai_generated"] is True
    assert result["provider"] == "ollama"
    assert len(result["scenes"]) == 1
    assert result["scenes"][0]["name"] == "Opening"


def test_plan_normalizes_ollama_garbage() -> None:
    """Ollama replies but with unusable content → deterministic fallback."""
    planner = ScenePlanner()
    with patch.object(ScenePlanner, "_call_ollama", return_value="not json at all"):
        result = planner.plan("x", num_scenes=2, duration=6.0)
    assert result["ai_generated"] is False
    assert len(result["scenes"]) == 2


# ── generate_text raises when nothing reachable ──────────────────────


def test_generate_text_raises_when_no_endpoint() -> None:
    # Point at a port nothing listens on; must raise, not hang.
    with patch.object(llm, "_candidate_base_urls", return_value=["http://127.0.0.1:1"]), pytest.raises((RuntimeError, OSError)):
        generate_text("hello", timeout=0.5)


def test_generate_text_candidate_urls_include_localhost() -> None:
    urls = llm._candidate_base_urls()
    assert "http://localhost:11434" in urls
    assert "http://127.0.0.1:11434" in urls


# ── misc helpers ─────────────────────────────────────────────────────


def test_ollama_model_fallback_env(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    # get_settings may fail in test env → env fallback path
    model = llm._ollama_model()
    assert model  # non-empty either from settings or env default
