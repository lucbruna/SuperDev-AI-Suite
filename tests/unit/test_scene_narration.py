"""Unit tests for per-scene narration (Volume 4) — separate voice clip per
scene placed at the scene's cumulative offset in the video timeline.
"""
from __future__ import annotations

import pytest

from modules.ai_video_studio.media import dsp, scene_narration


# ── Offset computation ───────────────────────────────────────────────


def test_compute_scene_offsets_cumulative() -> None:
    scenes = [{"duration": 2.0}, {"duration": 3.0}, {"duration": 1.5}]
    assert scene_narration.compute_scene_offsets(scenes) == [0.0, 2.0, 5.0]


def test_compute_scene_offsets_fallback_duration() -> None:
    scenes = [{"duration": 2.0}, {}, {"duration": 4.0}]
    assert scene_narration.compute_scene_offsets(scenes, fallback_duration=3.0) == [0.0, 2.0, 5.0]


def test_compute_scene_offsets_no_scenes() -> None:
    assert scene_narration.compute_scene_offsets([]) == []


def test_scene_narration_text_priority() -> None:
    assert scene_narration.scene_narration_text(
        {"description": "desc", "voiceover_text": "vo", "name": "n"}
    ) == "desc"
    assert scene_narration.scene_narration_text({"voiceover_text": "vo", "name": "n"}) == "vo"
    assert scene_narration.scene_narration_text({"name": "n"}) == "n"
    assert scene_narration.scene_narration_text({}) == ""


# ── Track building (reuses dubbing aligner) ──────────────────────────


def test_build_narration_tracks_places_clips(tmp_path) -> None:
    # Two real audio clips; place_clips must return one track per clip with
    # the correct offsets.
    clip_a = tmp_path / "a.wav"
    clip_b = tmp_path / "b.wav"
    dsp.write_audio(str(clip_a), dsp.sine(330.0, 0.5) * 0.5)
    dsp.write_audio(str(clip_b), dsp.sine(494.0, 0.5) * 0.5)
    clips = [
        {"text": "one", "start": 0.0, "end": 1.0, "audio_path": str(clip_a)},
        {"text": "two", "start": 2.0, "end": 3.0, "audio_path": str(clip_b)},
    ]
    tracks = scene_narration.build_narration_tracks(clips)
    assert len(tracks) == 2
    offsets = sorted(t["offset"] for t in tracks)
    assert offsets == [0.0, 2.0]
    assert all(dsp.peak(t["samples"]) > 0.0 for t in tracks)


def test_build_narration_tracks_empty() -> None:
    assert scene_narration.build_narration_tracks([]) == []


# ── Async synthesis + mux (TTS mocked) ───────────────────────────────


@pytest.fixture
def fake_tts(monkeypatch, tmp_path):
    """Mock VoiceEngine.synthesize_async to return real audio files."""
    from modules.ai_video_studio.ai_voice_studio import voice_engine as ve

    class _FakeEngine:
        async def synthesize_async(self, text, *, voice_id="default", language="en",
                                   speed=1.0, pitch=1.0, output_path=None,
                                   use_cache=True):
            out = str(tmp_path / f"clip_{abs(hash(text)) % 1000}.wav")
            samples = dsp.sine(220.0, max(0.3, len(text) / 15.0)) * 0.5
            dsp.write_audio(out, samples)
            return {
                "output_path": out,
                "duration": round(len(samples) / dsp.SAMPLE_RATE, 3),
                "engine": "formant",
            }

    monkeypatch.setattr(ve.VoiceEngine, "synthesize_async", _FakeEngine.synthesize_async)
    return _FakeEngine


def _scenes() -> list[dict]:
    return [
        {"index": 0, "name": "Opening", "description": "A sunrise over the city.", "duration": 2.0},
        {"index": 1, "name": "Middle", "description": "The hero walks through the market.", "duration": 3.0},
        {"index": 2, "duration": 1.5},  # no text at all → skipped clip
    ]


def test_synthesize_scene_narration_async_offsets(fake_tts, monkeypatch, tmp_path) -> None:
    # No real ffmpeg needed here — we only assert offsets/clips.
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        lambda *a, **k: {"muxed": True, "output_path": "x.mp4", "bytes": 100},
    )
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-video")

    import asyncio

    result = asyncio.run(scene_narration.synthesize_scene_narration_async(
        _scenes(),
        video_path=str(video),
        output_dir=str(tmp_path),
    ))
    # Two scenes have text; the third is skipped with no error.
    clips = result["clips"]
    assert len(clips) == 3
    assert clips[0]["start"] == 0.0
    assert clips[1]["start"] == 2.0  # cumulative offset of scene 2
    assert clips[2]["start"] == 5.0  # scene 3 (no text, no error)
    assert clips[2].get("audio_path") is None
    assert clips[0]["tts_engine"] == "formant"
    assert result["total_duration"] == pytest.approx(6.5)


def test_synthesize_scene_narration_all_no_text(tmp_path) -> None:
    import asyncio

    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-video")
    result = asyncio.run(scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "name": "Only", "duration": 2.0}],  # no description/voiceover
        video_path=str(video),
        output_dir=str(tmp_path),
    ))
    assert result["muxed"] is False
    assert "reason" in result


# ── TextToVideoEngine integration ────────────────────────────────────


def test_engine_add_voiceover_uses_per_scene(fake_tts, monkeypatch, tmp_path) -> None:
    from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import (
        TextToVideoEngine,
    )
    from modules.ai_video_studio.media import scene_narration as sn

    # Mux is a no-op in tests (no real ffmpeg involved) — assert the per-scene
    # path is selected and clips carry offsets.
    engine = TextToVideoEngine()
    captured: dict = {}

    async def _fake_scene_narration(scenes, *, video_path, params):
        captured["scenes"] = scenes
        captured["params"] = params
        return {
            "muxed": True,
            "clips": [{"start": 0.0, "text": "one"}, {"start": 2.0, "text": "two"}],
        }

    monkeypatch.setattr(sn, "synthesize_scene_narration_async", _fake_scene_narration)
    import asyncio

    result = asyncio.run(engine._add_voiceover(
        "prompt",
        _scenes(),
        video_path=str(tmp_path / "v.mp4"),
        params={"voiceover_mode": "per_scene"},
    ))
    assert result["narration_style"] == "per_scene"
    assert len(captured["scenes"]) == 3
    assert captured["params"]["voiceover_mode"] == "per_scene"
    assert result["narration"] == "one two"  # kept as a string, not a list


def test_engine_add_voiceover_single_when_no_scene_text(fake_tts, monkeypatch, tmp_path) -> None:
    from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import (
        TextToVideoEngine,
    )

    engine = TextToVideoEngine()
    called_single = {}

    async def _fake_single(prompt, scenes, *, video_path, params):
        called_single["ok"] = True
        return {"muxed": False, "reason": "test", "narration_style": "single_track"}

    monkeypatch.setattr(engine, "_add_voiceover_single", _fake_single)
    # Scenes with no usable text force the single-track fallback.
    scenes = [{"index": 0, "duration": 2.0}, {"index": 1, "duration": 2.0}]
    import asyncio

    result = asyncio.run(engine._add_voiceover(
        "the prompt",
        scenes,
        video_path=str(tmp_path / "v.mp4"),
        params={"voiceover_mode": "per_scene"},
    ))
    assert called_single["ok"] is True
    assert result["narration_style"] == "single_track"
