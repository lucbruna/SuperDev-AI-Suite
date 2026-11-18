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
