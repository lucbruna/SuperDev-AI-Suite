"""Production text-to-video must request strict MP4 encoding."""
from __future__ import annotations

import asyncio

from modules.ai_video_studio.ai_video_generator.text_to_video import text_to_video_engine as engine_module


def test_generate_async_requires_mp4_output(monkeypatch, tmp_path) -> None:
    captured: dict = {}

    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {
                "scenes": [{"duration": 1.0, "description": "Uma cena de teste."}],
                "provider": "deterministic",
                "ai_generated": False,
            }

    class Stats:
        def record(self, **kwargs):
            captured["stats"] = kwargs

    def fake_render(scenes, output_path, **kwargs):
        captured["render"] = kwargs
        return {
            "output_path": str(output_path),
            "frames": 24,
            "bytes": 123,
            "engine": "ffmpeg",
        }

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(
        engine_module, "unique_filename", lambda *_args: tmp_path / "strict.mp4"
    )
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    result = asyncio.run(
        engine_module.TextToVideoEngine().generate_async(
            {
                "prompt": "Crie uma cena simples.",
                "params": {
                    "duration": 1.0,
                    "num_scenes": 1,
                    "fps": 24,
                    "width": 64,
                    "height": 36,
                },
            }
        )
    )

    assert captured["render"]["require_mp4"] is True
    assert result["encode_engine"] == "ffmpeg"
    assert result["output_path"].endswith(".mp4")


def test_generate_async_can_write_timed_srt_sidecar(monkeypatch, tmp_path) -> None:
    captured: dict = {}

    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {
                "scenes": [
                    {"duration": 2.0, "description": "Direção visual", "voiceover_text": "Esta é a fala."},
                    {"duration": 1.0, "narration": "Segunda fala."},
                ],
                "provider": "deterministic",
                "ai_generated": False,
            }

    class Stats:
        def record(self, **kwargs):
            pass

    class SubtitleService:
        def generate_srt(self, scenes, *, output_path):
            captured["scenes"] = scenes
            captured["output_path"] = output_path
            return {"file_path": output_path, "cue_count": 2, "duration": 3.0}

    def fake_render(scenes, output_path, **kwargs):
        return {"output_path": str(output_path), "frames": 72, "bytes": 123, "engine": "ffmpeg"}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(
        engine_module, "unique_filename",
        lambda directory, prefix, extension: tmp_path / f"test.{extension}",
    )
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())
    monkeypatch.setattr(
        "modules.ai_video_studio.services.subtitle_studio.SubtitleStudioService",
        SubtitleService,
    )

    result = asyncio.run(
        engine_module.TextToVideoEngine().generate_async(
            {
                "prompt": "Vídeo com legendas.",
                "params": {
                    "duration": 3.0,
                    "num_scenes": 2,
                    "fps": 24,
                    "width": 64,
                    "height": 36,
                    "generate_subtitles": True,
                },
            }
        )
    )

    assert captured["scenes"] == [
        {"text": "Esta é a fala.", "duration": 2.0},
        {"text": "Segunda fala.", "duration": 1.0},
    ]
    assert result["subtitles"]["format"] == "srt"
    assert result["subtitles"]["cue_count"] == 2
    assert result["subtitles"]["file_path"].endswith(".srt")


def test_narration_builder_prefers_authored_speech_to_visual_description() -> None:
    narration = engine_module.TextToVideoEngine._build_narration(
        "Prompt fallback.",
        [
            {
                "description": "Wide shot of a medieval castle at sunrise.",
                "voiceover_text": "A cidade despertou antes do amanhecer.",
            },
            {
                "description": "A map moves across the screen.",
                "narration": "As rotas comerciais ligavam os reinos.",
            },
        ],
    )
    assert narration == (
        "A cidade despertou antes do amanhecer. "
        "As rotas comerciais ligavam os reinos."
    )


def test_generate_async_composes_selected_characters_into_every_scene(monkeypatch, tmp_path) -> None:
    captured: dict = {}

    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {
                "scenes": [
                    {"duration": 1.0, "description": "Cena um"},
                    {"duration": 1.0, "description": "Cena dois"},
                ],
                "provider": "deterministic",
                "ai_generated": False,
            }

    class Stats:
        def record(self, **kwargs):
            pass

    def fake_render(scenes, output_path, **kwargs):
        captured["scenes"] = scenes
        return {"output_path": str(output_path), "frames": 48, "bytes": 123, "engine": "ffmpeg"}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(
        engine_module, "unique_filename", lambda *_args: tmp_path / "characters.mp4"
    )
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    result = asyncio.run(
        engine_module.TextToVideoEngine().generate_async(
            {
                "prompt": "Mia e Leo explicam uma ideia.",
                "params": {
                    "duration": 2.0,
                    "num_scenes": 2,
                    "fps": 24,
                    "width": 640,
                    "height": 360,
                    "studio_id": "whymentary",
                    "character_ids": ["mia", "leo"],
                },
            }
        )
    )

    assert result["studio_id"] == "whymentary"
    assert len(captured["scenes"]) == 2
    for scene in captured["scenes"]:
        assert len(scene["rects"]) == 5
        assert len(scene["circles"]) >= 11
