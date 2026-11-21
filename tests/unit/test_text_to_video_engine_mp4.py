"""Production text-to-video must request strict MP4 encoding."""
from __future__ import annotations

import asyncio

import pytest

from modules.ai_video_studio.ai_video_generator.text_to_video import text_to_video_engine as engine_module


def test_scene_image_seed_is_stable_and_distinct_per_scene():
    scene_a = {"storyboard_scene_id": "opening"}
    scene_b = {"storyboard_scene_id": "turning-point"}

    first = engine_module.derive_scene_image_seed("job-1", scene_a, 0, base_seed=1234)
    repeated = engine_module.derive_scene_image_seed("job-1", scene_a, 0, base_seed=1234)
    other_scene = engine_module.derive_scene_image_seed("job-1", scene_b, 1, base_seed=1234)
    other_job = engine_module.derive_scene_image_seed("job-2", scene_a, 0)

    assert first == repeated
    assert first != other_scene
    assert first != other_job
    assert 0 <= first <= 0x7FFFFFFF
    assert 0 <= other_scene <= 0x7FFFFFFF


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

    def fake_scene_render(scene, output_path, **kwargs):
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
    monkeypatch.setattr(engine_module, "render_single_scene_clip", fake_scene_render)
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
    assert result["edit_timeline"]["fps"] == 24
    assert result["edit_timeline"]["duration_frames"] == 24
    assert result["edit_timeline"]["tracks"][0]["clips"][0]["end_frame"] == 24


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
        {"text": "Esta é a fala.", "duration": 2.0, "start_offset": 0.0},
        {"text": "Segunda fala.", "duration": 1.0, "start_offset": 2.0},
    ]
    assert result["subtitles"]["format"] == "srt"
    assert result["subtitles"]["cue_count"] == 2
    assert result["subtitles"]["file_path"].endswith(".srt")
    subtitle_track = next(track for track in result["edit_timeline"]["tracks"] if track["type"] == "subtitle")
    assert len(subtitle_track["clips"]) == 2
    assert subtitle_track["clips"][1]["start_frame"] == 48


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
                    {"duration": 1.0, "description": "Cena um", "visual_prompt": "A apresentadora aponta para o quadro"},
                    {"duration": 1.0, "description": "Cena dois", "visual_prompt": "O narrador está surpreso"},
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
                "prompt": "Dois apresentadores explicam uma ideia.",
                "params": {
                    "duration": 2.0,
                    "num_scenes": 2,
                    "fps": 24,
                    "width": 640,
                    "height": 360,
                    "studio_id": "whymentary",
                    "character_ids": ["whymentary_host", "historical_narrator"],
                },
            }
        )
    )

    assert result["studio_id"] == "whymentary"
    assert len(captured["scenes"]) == 2
    for scene in captured["scenes"]:
        assert len(scene["rects"]) == 4
        assert len(scene["circles"]) >= 11
        assert scene["_darkstudio_characters"] == ["whymentary_host", "historical_narrator"]
        assert scene["_darkstudio_objects"] == []
    assert captured["scenes"][0]["character_pose"] == "point"
    assert captured["scenes"][1]["character_expression"] == "surprised"


def test_generate_async_composes_selected_objects_into_every_scene(monkeypatch, tmp_path) -> None:
    captured: dict = {}

    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {
                "scenes": [{"duration": 1.0, "description": "Cena com objeto"}],
                "provider": "deterministic",
                "ai_generated": False,
            }

    class Stats:
        def record(self, **kwargs):
            pass

    def fake_render(scenes, output_path, **kwargs):
        captured["scenes"] = scenes
        return {"output_path": str(output_path), "frames": 24, "bytes": 123, "engine": "ffmpeg"}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(engine_module, "unique_filename", lambda *_args: tmp_path / "props.mp4")
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    result = asyncio.run(engine_module.TextToVideoEngine().generate_async({
        "prompt": "Uma cena com copo de água.",
        "params": {
            "duration": 1.0, "num_scenes": 1, "fps": 24,
            "width": 640, "height": 360, "studio_id": "whymentary",
            "object_ids": ["water_glass", "thermometer"],
        },
    }))

    scene = captured["scenes"][0]
    assert result["studio_id"] == "whymentary"
    assert scene["object_ids"] == ["water_glass", "thermometer"]
    assert len(scene["rects"]) == 4
    assert len(scene["circles"]) == 1
    assert scene["rects"][0]["motion_frames"] == 12
    assert scene["rects"][0]["motion_start_frame"] == 0
    assert scene["rects"][2]["motion_start_frame"] == 8


def test_generate_async_rejects_objects_from_another_studio(monkeypatch) -> None:
    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {"scenes": [{"duration": 1.0}], "provider": "deterministic", "ai_generated": False}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    with pytest.raises(Exception, match="do not belong to studio"):
        asyncio.run(engine_module.TextToVideoEngine().generate_async({
            "prompt": "Uma cena histórica.",
            "params": {
                "duration": 1.0, "num_scenes": 1, "fps": 24,
                "width": 640, "height": 360,
                "studio_id": "historical_documentary",
                "object_ids": ["water_glass"],
            },
        }))


def test_generate_async_uses_real_scene_images_and_vidgrid_ten_second_clips(monkeypatch, tmp_path) -> None:
    captured: dict = {}

    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            assert num_scenes == 2
            assert duration == 20.0
            return {
                "scenes": [
                    {"duration": 1.0, "description": "Floresta", "visual_prompt": "A detailed forest at dawn"},
                    {"duration": 1.0, "description": "Rio", "visual_prompt": "A wide river in a valley"},
                ],
                "provider": "ollama", "ai_generated": True,
            }

    class Stats:
        def record(self, **kwargs):
            pass

    def fake_image(prompt, **kwargs):
        from PIL import Image

        captured.setdefault("prompts", []).append(prompt)
        captured.setdefault("image_timeouts", []).append(kwargs.get("timeout"))
        image_dir = tmp_path / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"scene-{len(captured['prompts'])}.png"
        Image.new("RGB", (kwargs["width"], kwargs["height"]), (24, 48, 72)).save(image_path)
        return {
            "image_path": str(image_path),
            "provider": "automatic1111_compatible",
            "image_bytes": image_path.stat().st_size,
        }

    def fake_render(scenes, output_path, **kwargs):
        captured["scenes"] = scenes
        return {"output_path": str(output_path), "frames": 480, "bytes": 100, "engine": "ffmpeg"}

    def fake_scene_render(scene, output_path, **kwargs):
        captured.setdefault("clip_renders", []).append({"scene": scene, "kwargs": kwargs})
        return {"output_path": str(output_path), "frames": 240, "bytes": 50, "engine": "ffmpeg"}

    from modules.ai_video_studio.ai_image_generator.providers import local_diffusion
    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(local_diffusion, "generate_scene_image", fake_image)
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    # SceneCanvas resolves its image root from output_paths directly; keep it
    # aligned with the fake provider output instead of the real downloads dir.
    from modules.ai_video_studio.media import output_paths
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: tmp_path / name)
    monkeypatch.setattr(engine_module, "unique_filename", lambda directory, prefix, extension: tmp_path / f"{prefix}.{extension}")
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    scene_events = []
    result = asyncio.run(engine_module.TextToVideoEngine().generate_async({
        "prompt": "Documentário cinematográfico sobre a natureza.",
        "params": {
            "duration": 6, "num_scenes": 2, "fps": 24,
            "width": 640, "height": 360,
            "studio_id": "historical_documentary",
            "scene_image_mode": "ai",
            "vidgrid_compatible": True,
        },
    }, scene_callback=scene_events.append))

    assert len(captured["prompts"]) == 2
    assert captured["image_timeouts"] == [180.0, 180.0]
    assert "cinematic historical illustration" in captured["prompts"][0]
    assert [scene["duration"] for scene in captured["scenes"]] == [10.0, 10.0]
    assert all(scene["background_image_path"].endswith(".png") for scene in captured["scenes"])
    assert result["vidgrid_compatible"] is True
    assert result["clip_duration_seconds"] == 10.0
    assert result["scene_image_mode"] == "ai_generated"
    assert len(result["scene_assets"]) == 2
    assert len(result["scene_clips"]) == 2
    assert all(clip["duration"] == 10.0 for clip in result["scene_clips"])
    assert all(item["kwargs"]["duration"] == 10.0 for item in captured["clip_renders"])
    assert [event["scene_index"] for event in scene_events if event["stage"] == "storyboard"] == [0, 1]
    assert len([event for event in scene_events if event["stage"] == "image_ready"]) == 2
    assert len([event for event in scene_events if event["stage"] == "clip_ready"]) == 2
    assert all(event["status"] == "completed" for event in scene_events if event["stage"] in {"image_ready", "clip_ready"})
    render_events = [event for event in scene_events if event["stage"] == "scene_render"]
    assert [event["scene_index"] for event in render_events] == [0, 1]
    assert all(event["status"] == "processing" for event in render_events)
    assert all(event.get("scene_snapshot", {}).get("background_image_path") for event in render_events)


def test_vidgrid_scene_clips_receive_matching_per_scene_narration(monkeypatch, tmp_path):
    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {"scenes": [
                {"duration": 10, "description": "Cena um", "voiceover_text": "Narração da cena um."},
                {"duration": 10, "description": "Cena dois", "voiceover_text": "Narração da cena dois."},
            ], "provider": "deterministic", "ai_generated": False}

    class Stats:
        def record(self, **kwargs):
            pass

    async def fake_voice(self, prompt, scenes, *, video_path, params):
        return {
            "muxed": True, "narration_style": "per_scene",
            "output_path": video_path, "bytes": 500,
            "clips": [
                {"index": 0, "audio_path": str(tmp_path / "voice-0.wav")},
                {"index": 1, "audio_path": str(tmp_path / "voice-1.wav")},
            ],
        }

    def fake_render(scenes, output_path, **kwargs):
        return {"output_path": str(output_path), "frames": 480, "bytes": 300, "engine": "ffmpeg"}

    def fake_scene_render(scene, output_path, **kwargs):
        return {"output_path": str(output_path), "frames": 240, "bytes": 100, "engine": "ffmpeg"}

    mux_calls = []
    def fake_mux(video_path, audio_path, output_path):
        mux_calls.append((video_path, audio_path))
        return {"muxed": True, "output_path": str(output_path), "bytes": 200}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(engine_module, "unique_filename", lambda directory, prefix, extension: tmp_path / f"{prefix}.{extension}")
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "render_scene_video", fake_scene_render)
    monkeypatch.setattr(engine_module.TextToVideoEngine, "_add_voiceover", fake_voice)
    monkeypatch.setattr("modules.ai_video_studio.media.audio.mux_audio_into_video", fake_mux)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    result = asyncio.run(engine_module.TextToVideoEngine().generate_async({
        "prompt": "Vídeo em blocos de dez segundos.",
        "params": {
            "duration": 6, "num_scenes": 2, "fps": 24,
            "width": 640, "height": 360, "voiceover": True,
            "vidgrid_compatible": True,
        },
    }))
    assert len(mux_calls) == 2
    assert [call[1] for call in mux_calls] == [
        str(tmp_path / "voice-0.wav"), str(tmp_path / "voice-1.wav"),
    ]
    assert all(clip["audio_status"] == "per_scene_narration_muxed" for clip in result["scene_clips"])
    assert all(clip["output_path"].endswith("_voiced.mp4") for clip in result["scene_clips"])

def test_vidgrid_scene_narration_mux_failure_fails_generation(monkeypatch, tmp_path):
    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {"scenes": [{"duration": 10, "description": "Cena", "voiceover_text": "Fala."}],
                    "provider": "deterministic", "ai_generated": False}

    class Stats:
        def record(self, **kwargs):
            pass

    async def fake_voice(self, prompt, scenes, *, video_path, params):
        return {"muxed": True, "narration_style": "per_scene", "output_path": video_path,
                "bytes": 500, "clips": [{"index": 0, "audio_path": str(tmp_path / "voice.wav")}]}

    def fake_render(scenes, output_path, **kwargs):
        return {"output_path": str(output_path), "frames": 240, "bytes": 300, "engine": "ffmpeg"}

    def fake_scene_render(scene, output_path, **kwargs):
        return {"output_path": str(output_path), "frames": 240, "bytes": 100, "engine": "ffmpeg"}

    def failed_mux(*args):
        return {"muxed": False, "reason": "audio input missing or empty"}

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _name: tmp_path)
    monkeypatch.setattr(engine_module, "unique_filename", lambda directory, prefix, extension: tmp_path / (prefix + "." + extension))
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "render_scene_video", fake_scene_render)
    monkeypatch.setattr(engine_module.TextToVideoEngine, "_add_voiceover", fake_voice)
    monkeypatch.setattr("modules.ai_video_studio.media.audio.mux_audio_into_video", failed_mux)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    with pytest.raises(RuntimeError, match="narration could not be embedded"):
        asyncio.run(engine_module.TextToVideoEngine().generate_async({
            "prompt": "Vídeo de teste.",
            "params": {"duration": 6, "num_scenes": 1, "fps": 24, "width": 640,
                       "height": 360, "voiceover": True, "vidgrid_compatible": True},
        }))

def test_generate_async_rejects_storyboard_with_wrong_scene_count(monkeypatch) -> None:
    class Planner:
        def plan(self, prompt, *, num_scenes, duration, timeout):
            return {
                "scenes": [{"duration": 1.0, "description": "Somente uma cena."}],
                "provider": "deterministic",
                "ai_generated": False,
            }

    monkeypatch.setattr(engine_module, "get_scene_planner", lambda: Planner())
    with pytest.raises(Exception, match=r"returned 1 scenes; expected 2"):
        asyncio.run(
            engine_module.TextToVideoEngine().generate_async(
                {
                    "prompt": "Vídeo com duas cenas.",
                    "params": {
                        "duration": 20.0,
                        "num_scenes": 2,
                        "fps": 24,
                        "width": 64,
                        "height": 36,
                        "vidgrid_compatible": True,
                    },
                }
            )
        )


def test_generate_async_reuses_complete_saved_storyboard_and_images(monkeypatch, tmp_path):
    from pathlib import Path

    image_root = tmp_path / "images"
    image_root.mkdir()
    saved_image = image_root / "saved-scene.png"
    saved_image.write_bytes(b"saved-image")
    captured = {}

    class Stats:
        def record(self, **kwargs):
            pass

    def unexpected_planner():
        raise AssertionError("planner must not run during checkpoint recovery")

    def fake_render(scenes, output_path, **kwargs):
        captured["scenes"] = scenes
        return {"output_path": str(output_path), "frames": 48, "bytes": 123, "engine": "ffmpeg"}

    monkeypatch.setattr(engine_module, "get_scene_planner", unexpected_planner)
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda name: image_root if name == "images" else tmp_path)
    monkeypatch.setattr(engine_module, "unique_filename", lambda *_args: tmp_path / "recovered.mp4")
    monkeypatch.setattr(engine_module, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())

    clip_dir = tmp_path / "vidgrid_clips"
    clip_dir.mkdir()
    saved_clip = clip_dir / "scene_01.mp4"
    saved_clip.write_bytes(b"saved-clip")
    rendered_scene_indices = []

    def fake_scene_clip(scene, output_path, **kwargs):
        rendered_scene_indices.append(scene.get("description"))
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(b"new-clip")
        return {"output_path": str(output_path), "bytes": 8, "engine": "ffmpeg"}

    monkeypatch.setattr(engine_module, "render_single_scene_clip", fake_scene_clip)
    from types import SimpleNamespace
    monkeypatch.setattr(engine_module.shutil, "which", lambda _name: "ffprobe")
    monkeypatch.setattr(
        engine_module.subprocess, "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, stdout='{"format":{"duration":"10.0"},"streams":[{"codec_type":"video","width":64,"height":36}]}',
            stderr="",
        ),
    )

    saved_scenes = [
        {"duration": 1.0, "description": "Cena salva", "visual_prompt": "Prompt visual preservado",
         "background_image_path": str(saved_image), "rects": [{"x": 10, "y": 20, "w": 30, "h": 40}]},
        {"duration": 1.0, "description": "Segunda cena", "visual_prompt": "Segundo prompt preservado"},
    ]
    result = asyncio.run(engine_module.TextToVideoEngine().generate_async({
        "id": "recovery-job",
        "prompt": "Retomar projeto salvo",
        "params": {
            "duration": 2.0, "num_scenes": 2, "fps": 24, "width": 64, "height": 36,
            "checkpoint_scenes": saved_scenes,
            "scene_image_mode": "procedural",
            "checkpoint_scene_assets": [{"scene_index": 0, "image_path": str(saved_image), "provider": "local", "status": "generated"}],
            "vidgrid_compatible": True,
            "checkpoint_scene_clips": [{
                "scene_index": 0, "duration": 10.0, "fps": 24,
                "width": 64, "height": 36, "output_path": str(saved_clip),
                "bytes": 111, "encode_engine": "ffmpeg",
            }],
        },
    }))

    assert captured["scenes"][0]["rects"] == saved_scenes[0]["rects"]
    assert captured["scenes"][0]["background_image_path"] == str(saved_image)
    assert result["ai_planner"] == "saved_checkpoint"
    assert result["storyboard_report"]["resumed_from_checkpoint"] is True
    assert result["scene_assets"][0]["status"] == "generated"
    assert len(result["scene_clips"]) == 2
    assert result["scene_clips"][0]["reused"] is True
    assert result["scene_clips"][0]["output_path"] == str(saved_clip)
    assert result["scene_clips"][1]["reused"] is False
    assert rendered_scene_indices == ["Segunda cena"]


def test_generate_async_rejects_incomplete_saved_storyboard(monkeypatch):
    class Stats:
        def record(self, **kwargs):
            pass

    monkeypatch.setattr(engine_module, "get_generation_statistics", lambda: Stats())
    with pytest.raises(Exception, match="complete saved storyboard"):
        asyncio.run(engine_module.TextToVideoEngine().generate_async({
            "prompt": "Retomar projeto salvo",
            "params": {
                "duration": 2.0, "num_scenes": 2, "fps": 24, "width": 64, "height": 36,
                "checkpoint_scenes": [{"duration": 1.0, "description": "Só uma cena"}],
            },
        }))



def test_reusable_vidgrid_clip_requires_valid_ffprobe_metadata(monkeypatch, tmp_path):
    from types import SimpleNamespace

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"not-empty")
    monkeypatch.setattr(engine_module.shutil, "which", lambda _name: "ffprobe")
    monkeypatch.setattr(
        engine_module.subprocess, "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout='{"format":{"duration":"10.0"},"streams":[{"codec_type":"video","width":64,"height":36}]}',
            stderr="",
        ),
    )
    saved = {
        "scene_index": 2, "output_path": str(clip), "duration": 10.0,
        "fps": 24, "width": 64, "height": 36,
    }
    assert engine_module._is_reusable_vidgrid_clip(
        saved, scene_index=2, video_root=tmp_path, fps=24, width=64, height=36,
    )


def test_reusable_vidgrid_clip_rejects_wrong_measured_duration(monkeypatch, tmp_path):
    from types import SimpleNamespace

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"not-empty")
    monkeypatch.setattr(engine_module.shutil, "which", lambda _name: "ffprobe")
    monkeypatch.setattr(
        engine_module.subprocess, "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout='{"format":{"duration":"9.5"},"streams":[{"codec_type":"video","width":64,"height":36}]}',
            stderr="",
        ),
    )
    saved = {
        "scene_index": 2, "output_path": str(clip), "duration": 10.0,
        "fps": 24, "width": 64, "height": 36,
    }
    assert not engine_module._is_reusable_vidgrid_clip(
        saved, scene_index=2, video_root=tmp_path, fps=24, width=64, height=36,
    )


def test_reusable_vidgrid_clip_rejects_old_narration_when_voiceover_disabled(monkeypatch, tmp_path):
    from types import SimpleNamespace

    clip = tmp_path / "voiced_clip.mp4"
    clip.write_bytes(b"non-empty-mp4-placeholder")
    monkeypatch.setattr(engine_module.shutil, "which", lambda _name: "ffprobe")
    monkeypatch.setattr(
        engine_module.subprocess, "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout='{"format":{"duration":"10.0"},"streams":[{"codec_type":"video","width":64,"height":36}]}',
            stderr="",
        ),
    )
    saved = {
        "scene_index": 0, "output_path": str(clip), "duration": 10.0,
        "fps": 24, "width": 64, "height": 36,
        "audio_status": "per_scene_narration_muxed",
    }

    assert not engine_module._is_reusable_vidgrid_clip(
        saved, scene_index=0, video_root=tmp_path, fps=24, width=64, height=36,
        voiceover_requested=False,
    )
    assert engine_module._is_reusable_vidgrid_clip(
        saved, scene_index=0, video_root=tmp_path, fps=24, width=64, height=36,
        voiceover_requested=True,
    )



def test_add_voiceover_forwards_narration_checkpoints_and_callback(monkeypatch):
    from modules.ai_video_studio.media import scene_narration

    captured = {}
    expected_checkpoints = [
        {"index": 0, "text": "Texto salvo", "audio_path": "/voice/scene-0.wav"}
    ]
    callback = lambda clip: None

    async def fake_synthesize(scenes, **kwargs):
        captured.update(kwargs)
        return {
            "muxed": True,
            "clips": [{"index": 0, "text": "Texto salvo", "audio_path": "/voice/scene-0.wav"}],
        }

    monkeypatch.setattr(scene_narration, "synthesize_scene_narration_async", fake_synthesize)
    result = asyncio.run(engine_module.TextToVideoEngine()._add_voiceover(
        "Prompt", [{"duration": 10, "voiceover_text": "Texto salvo"}],
        video_path="/videos/source.mp4",
        params={
            "voiceover_mode": "per_scene",
            "checkpoint_narration_clips": expected_checkpoints,
            "narration_clip_callback": callback,
        },
    ))

    assert captured["checkpoint_clips"] == expected_checkpoints
    assert captured["clip_callback"] is callback
    assert result["narration_style"] == "per_scene"
