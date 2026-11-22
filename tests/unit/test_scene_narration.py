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


def test_compute_scene_offsets_accounts_for_crossfade_overlap() -> None:
    scenes = [
        {"duration": 2.0, "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"duration": 3.0},
    ]
    assert scene_narration.compute_scene_offsets(scenes, fps=24) == [0.0, 1.5]


def test_compute_scene_offsets_does_not_shorten_fade_through_black() -> None:
    scenes = [
        {"duration": 2.0, "transition_out": {"type": "fade_through_black", "duration_frames": 8}},
        {"duration": 3.0},
    ]
    assert scene_narration.compute_scene_offsets(scenes, fps=24) == [0.0, 2.0]


def test_compute_scene_offsets_clamps_crossfade_like_renderer() -> None:
    scenes = [
        {"duration": 0.5, "transition_out": {"type": "crossfade", "duration_frames": 20}},
        {"duration": 0.5},
    ]
    assert scene_narration.compute_scene_offsets(scenes, fps=24) == [0.0, 0.25]


def test_scene_narration_text_prefers_authored_speech_over_visual_description() -> None:
    assert scene_narration.scene_narration_text(
        {"description": "visual direction", "voiceover_text": "spoken line", "name": "scene"}
    ) == "spoken line"
    assert scene_narration.scene_narration_text({"narration": "narrated line", "description": "visual"}) == "narrated line"
    assert scene_narration.scene_narration_text({"description": "desc", "name": "n"}) == "desc"
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


def test_synthesize_scene_narration_defaults_to_portuguese_brazil(monkeypatch, tmp_path) -> None:
    import asyncio
    from modules.ai_video_studio.ai_voice_studio import voice_engine as ve

    seen_languages: list[str] = []

    async def _fake_synthesize(self, text, *, voice_id="default", language="en",
                               speed=1.0, pitch=1.0, output_path=None, use_cache=True):
        seen_languages.append(language)
        out = str(tmp_path / "pt_br.wav")
        samples = dsp.sine(220.0, 0.5) * 0.5
        dsp.write_audio(out, samples)
        return {"output_path": out, "duration": 0.5, "engine": "formant"}

    monkeypatch.setattr(ve.VoiceEngine, "synthesize_async", _fake_synthesize)
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        lambda *a, **k: {"muxed": True, "output_path": "pt_br.mp4", "bytes": 100},
    )
    video = tmp_path / "video.mp4"
    video.write_bytes(b"fake-video")

    result = asyncio.run(scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "voiceover_text": "Esta é uma narração de teste.", "duration": 2.0}],
        video_path=str(video),
        output_dir=str(tmp_path),
    ))

    assert result["language"] == "pt-BR"
    assert seen_languages == ["pt-BR"]


def test_synthesize_scene_narration_respects_explicit_language(fake_tts, monkeypatch, tmp_path) -> None:
    import asyncio

    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        lambda *a, **k: {"muxed": True, "output_path": "explicit.mp4", "bytes": 100},
    )
    video = tmp_path / "video-explicit.mp4"
    video.write_bytes(b"fake-video")
    result = asyncio.run(scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "voiceover_text": "Testing explicit language.", "duration": 1.0}],
        video_path=str(video),
        params={"voice_language": "en"},
        output_dir=str(tmp_path),
    ))
    assert result["language"] == "en"


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

    async def _fake_scene_narration(
        scenes, *, video_path, params, checkpoint_clips=None, clip_callback=None
    ):
        captured["scenes"] = scenes
        captured["params"] = params
        captured["checkpoint_clips"] = checkpoint_clips
        captured["clip_callback"] = clip_callback
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
        params={
            "voiceover_mode": "per_scene",
            "checkpoint_narration_clips": [{"index": 0, "text": "one"}],
            "narration_clip_callback": lambda clip: None,
        },
    ))
    assert result["narration_style"] == "per_scene"
    assert captured["checkpoint_clips"] == [{"index": 0, "text": "one"}]
    assert callable(captured["clip_callback"])
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



@pytest.mark.asyncio(loop_scope="function")
async def test_scene_narration_uses_frame_rounded_duration_for_audio_slots(monkeypatch, tmp_path):
    from modules.ai_video_studio.media import scene_narration

    class FakeVoiceEngine:
        async def synthesize_async(self, text, **kwargs):
            output = tmp_path / "voice.wav"
            dsp.write_audio(str(output), dsp.sine(220.0, 0.8) * 0.5)
            return {"output_path": str(output), "engine": "fake", "duration": 0.8}

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_voice_studio.get_voice_engine",
        lambda: FakeVoiceEngine(),
    )
    captured = {}

    def fake_export(tracks, output_path, *, total_duration):
        captured["tracks"] = tracks
        captured["total_duration"] = total_duration
        return {"duration": total_duration}

    def fake_mux(video_path, audio_path, output_path):
        return {"muxed": True, "output_path": output_path, "bytes": 1}

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_dubbing.export_dubbing.export_audio_track",
        fake_export,
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        fake_mux,
    )
    result = await scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "voiceover_text": "line", "duration": 1.03}],
        video_path=str(tmp_path / "video.mp4"),
        params={"fps": 24},
        output_dir=str(tmp_path),
    )
    assert result["clips"][0]["end"] == pytest.approx(25 / 24, abs=0.001)  # duration metadata is rounded to milliseconds
    assert captured["total_duration"] == pytest.approx(25 / 24, abs=0.001)  # duration metadata is rounded to milliseconds

def test_remap_narration_clips_for_reordered_and_resized_scenes() -> None:
    original = [
        {"text": "first", "audio_path": "first.wav"},
        {"text": "second", "audio_path": "second.wav"},
        {"text": "third", "audio_path": "third.wav"},
    ]
    edited_scenes = [
        {"_source_scene_index": 2, "voiceover_text": "third", "duration": 1.5},
        {"_source_scene_index": 0, "voiceover_text": "first", "duration": 2.0,
         "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"_source_scene_index": 1, "voiceover_text": "second", "duration": 3.0},
    ]

    clips = scene_narration.remap_narration_clips_for_edits(
        edited_scenes, original, fps=24
    )

    assert [clip["audio_path"] for clip in clips] == [
        "third.wav", "first.wav", "second.wav"
    ]
    assert [(clip["start"], clip["end"]) for clip in clips] == [
        (0.0, 1.5), (1.5, 3.0), (3.0, 6.0)
    ]


def test_remap_narration_omits_scenes_without_audio_and_rejects_bad_source_index() -> None:
    original = [{"text": "silent scene"}, {"text": "spoken", "audio_path": "voice.wav"}]
    scenes = [
        {"_source_scene_index": 0, "duration": 1.0},
        {"_source_scene_index": 1, "voiceover_text": "spoken", "duration": 2.0},
    ]
    clips = scene_narration.remap_narration_clips_for_edits(scenes, original, fps=30)
    assert len(clips) == 1
    assert clips[0]["start"] == 1.0
    assert clips[0]["end"] == 3.0

    with pytest.raises(ValueError, match="source index"):
        scene_narration.remap_narration_clips_for_edits(
            [{"_source_scene_index": "bad", "duration": 1.0}], original
        )


def test_scene_offsets_round_duration_to_the_same_frame_grid_as_video_rendering():
    from modules.ai_video_studio.media.scene_narration import compute_scene_offsets

    offsets = compute_scene_offsets(
        [{"duration": 1.03}, {"duration": 1.0}],
        fps=24,
    )
    assert offsets[1] == pytest.approx(25 / 24, abs=0.000001)  # offsets are rounded to six decimal places


def test_remap_narration_does_not_reuse_audio_after_speech_text_changes() -> None:
    original = [
        {"text": "old narration", "audio_path": "old.wav"},
        {"text": "unchanged narration", "audio_path": "same.wav"},
    ]
    edited = [
        {"_source_scene_index": 0, "voiceover_text": "new narration", "duration": 2.0},
        {"_source_scene_index": 1, "voiceover_text": "unchanged narration", "duration": 2.0},
    ]

    assert scene_narration.narration_text_changes_for_edits(edited, original) == [0]
    clips = scene_narration.remap_narration_clips_for_edits(edited, original)
    assert [clip["audio_path"] for clip in clips] == ["same.wav"]
    assert clips[0]["index"] == 1


def test_remap_narration_keeps_audio_for_visual_only_edits() -> None:
    original = [{"text": "same narration", "audio_path": "voice.wav"}]
    edited = [{"_source_scene_index": 0, "voiceover_text": "same narration",
               "description": "new visual", "duration": 2.0}]

    assert scene_narration.narration_text_changes_for_edits(edited, original) == []
    clips = scene_narration.remap_narration_clips_for_edits(edited, original)
    assert [clip["audio_path"] for clip in clips] == ["voice.wav"]


@pytest.mark.asyncio(loop_scope="function")
async def test_regenerate_changed_narration_only_synthesizes_edited_scene(monkeypatch):
    from modules.ai_video_studio.media import scene_narration

    calls = []

    class FakeVoiceEngine:
        async def synthesize_async(self, text, **kwargs):
            calls.append(text)
            return {"output_path": f"{text}.wav", "engine": "fake", "duration": 1.2}

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_voice_studio.get_voice_engine",
        lambda: FakeVoiceEngine(),
    )
    original = [
        {"text": "old first", "audio_path": "first-old.wav"},
        {"text": "keep second", "audio_path": "second.wav"},
    ]
    edited = [
        {"_source_scene_index": 0, "voiceover_text": "new first", "duration": 2.0},
        {"_source_scene_index": 1, "voiceover_text": "keep second", "duration": 2.0},
    ]

    result = await scene_narration.regenerate_changed_scene_narration_async(
        edited, original, params={"voice_language": "pt-BR"}, fps=24,
    )

    assert calls == ["new first"]
    assert result["regenerated_scene_indices"] == [0]
    assert result["failed_scene_indices"] == []
    assert [clip["audio_path"] for clip in result["clips"]] == [
        "new first.wav", "second.wav",
    ]
    assert [clip["start"] for clip in result["clips"]] == [0.0, 2.0]



@pytest.mark.asyncio(loop_scope="function")
async def test_regenerate_changed_narration_when_original_tts_failed(monkeypatch):
    from modules.ai_video_studio.media import scene_narration

    calls = []

    class FakeVoiceEngine:
        async def synthesize_async(self, text, **kwargs):
            calls.append(text)
            return {"output_path": "recovered.wav", "engine": "fake", "duration": 1.0}

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_voice_studio.get_voice_engine",
        lambda: FakeVoiceEngine(),
    )
    original = [{"index": 0, "text": "old line", "error": "TTS unavailable"}]
    edited = [{"_source_scene_index": 0, "voiceover_text": "new line", "duration": 2.0}]

    result = await scene_narration.regenerate_changed_scene_narration_async(
        edited, original, params={"voice_language": "pt-BR"}, fps=24,
    )

    assert calls == ["new line"]
    assert result["regenerated_scene_indices"] == [0]
    assert result["failed_scene_indices"] == []
    assert result["clips"][0]["audio_path"] == "recovered.wav"


def test_narration_change_detection_uses_explicit_source_indices():
    originals = [
        {"index": 4, "text": "old line", "error": "TTS unavailable"},
        {"index": 1, "text": "keep line", "audio_path": "keep.wav"},
    ]
    scenes = [
        {"_source_scene_index": 1, "voiceover_text": "keep line"},
        {"_source_scene_index": 4, "voiceover_text": "new line"},
    ]
    assert scene_narration.narration_text_changes_for_edits(scenes, originals) == [4]

def test_edited_subtitles_follow_successful_scene_audio_and_edited_order():
    scenes = [
        {"_source_scene_index": 2, "voiceover_text": "third", "duration": 2.0},
        {"_source_scene_index": 0, "voiceover_text": "new first", "duration": 1.5},
        {"_source_scene_index": 1, "voiceover_text": "failed second", "duration": 3.0},
    ]
    clips = [
        {"index": 2, "text": "third", "audio_path": "third.wav"},
        {"index": 0, "text": "new first", "audio_path": "new-first.wav"},
        {"index": 1, "text": "failed second", "error": "tts unavailable"},
    ]
    subtitles = scene_narration.build_edited_subtitle_scenes(
        scenes, clips, fps=24, per_scene_narration=True,
    )
    assert [item["text"] for item in subtitles] == ["third", "new first"]
    assert [item["start_offset"] for item in subtitles] == [0.0, 2.0]
    assert [item["duration"] for item in subtitles] == [2.0, 1.5]


def test_edited_subtitles_keep_scene_text_without_per_scene_voiceover():
    scenes = [
        {"voiceover_text": "first caption", "duration": 1.0},
        {"voiceover_text": "second caption", "duration": 2.0},
    ]
    subtitles = scene_narration.build_edited_subtitle_scenes(
        scenes, None, fps=30, per_scene_narration=False,
    )
    assert [item["text"] for item in subtitles] == ["first caption", "second caption"]
    assert [item["start_offset"] for item in subtitles] == [0.0, 1.0]

    
def test_crossfade_trims_outgoing_narration_and_subtitle_slots():
    scenes = [
        {"_source_scene_index": 0, "voiceover_text": "first", "duration": 2.0,
         "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"_source_scene_index": 1, "voiceover_text": "second", "duration": 3.0},
    ]
    originals = [
        {"text": "first", "audio_path": "first.wav"},
        {"text": "second", "audio_path": "second.wav"},
    ]
    clips = scene_narration.remap_narration_clips_for_edits(scenes, originals, fps=24)
    assert [(clip["start"], clip["end"]) for clip in clips] == [
        (0.0, 1.5), (1.5, 4.5),
    ]
    subtitles = scene_narration.build_edited_subtitle_scenes(
        scenes, clips, fps=24, per_scene_narration=True,
    )
    assert [(cue["start_offset"], cue["duration"]) for cue in subtitles] == [
        (0.0, 1.5), (1.5, 3.0),
    ]


@pytest.mark.asyncio(loop_scope="function")
async def test_scene_narration_reuses_valid_checkpoint_audio_without_calling_tts(monkeypatch, tmp_path):
    from modules.ai_video_studio.ai_voice_studio import voice_engine as ve

    voice_root = tmp_path / "voice"
    voice_root.mkdir()
    saved_audio = voice_root / "saved.wav"
    dsp.write_audio(str(saved_audio), dsp.sine(330.0, 0.5) * 0.5)

    class MustNotSynthesize:
        async def synthesize_async(self, *args, **kwargs):
            raise AssertionError("saved narration should be reused, not synthesized")

    monkeypatch.setattr("modules.ai_video_studio.ai_voice_studio.get_voice_engine", lambda: MustNotSynthesize())
    monkeypatch.setattr(scene_narration, "get_subsystem_dir", lambda name: voice_root if name == "voice" else tmp_path)
    monkeypatch.setattr(
        "modules.ai_video_studio.ai_dubbing.export_dubbing.export_audio_track",
        lambda tracks, output_path, *, total_duration: {"duration": total_duration, "track_count": len(tracks)},
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        lambda video, audio, output: {"muxed": True, "output_path": output, "bytes": 123},
    )
    video = tmp_path / "source.mp4"
    video.write_bytes(b"video")
    callbacks = []

    result = await scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "voiceover_text": "Saved spoken line", "duration": 2.0}],
        video_path=str(video),
        params={},
        output_dir=str(tmp_path),
        checkpoint_clips=[{
            "index": 0, "text": "Saved spoken line", "audio_path": str(saved_audio),
            "tts_engine": "existing-engine", "audio_duration": 0.5,
        }],
        clip_callback=callbacks.append,
    )

    assert result["muxed"] is True
    assert result["clips"][0]["audio_path"] == str(saved_audio)
    assert result["clips"][0]["tts_engine"] == "existing-engine"
    assert callbacks[0]["audio_path"] == str(saved_audio)


@pytest.mark.asyncio(loop_scope="function")
async def test_scene_narration_does_not_reuse_checkpoint_audio_when_text_changed(monkeypatch, tmp_path):
    from modules.ai_video_studio.ai_voice_studio import voice_engine as ve

    voice_root = tmp_path / "voice"
    voice_root.mkdir()
    saved_audio = voice_root / "saved.wav"
    dsp.write_audio(str(saved_audio), dsp.sine(330.0, 0.5) * 0.5)
    synthesized = []

    class FakeVoiceEngine:
        async def synthesize_async(self, text, **kwargs):
            synthesized.append(text)
            output = voice_root / "fresh.wav"
            dsp.write_audio(str(output), dsp.sine(440.0, 0.5) * 0.5)
            return {"output_path": str(output), "engine": "fresh-engine", "duration": 0.5}

    monkeypatch.setattr("modules.ai_video_studio.ai_voice_studio.get_voice_engine", lambda: FakeVoiceEngine())
    monkeypatch.setattr(scene_narration, "get_subsystem_dir", lambda name: voice_root if name == "voice" else tmp_path)
    monkeypatch.setattr(
        "modules.ai_video_studio.ai_dubbing.export_dubbing.export_audio_track",
        lambda tracks, output_path, *, total_duration: {"duration": total_duration},
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        lambda video, audio, output: {"muxed": True, "output_path": output, "bytes": 123},
    )
    video = tmp_path / "source.mp4"
    video.write_bytes(b"video")

    result = await scene_narration.synthesize_scene_narration_async(
        [{"index": 0, "voiceover_text": "Updated line", "duration": 2.0}],
        video_path=str(video),
        params={},
        output_dir=str(tmp_path),
        checkpoint_clips=[{
            "index": 0, "text": "Old line", "audio_path": str(saved_audio),
        }],
    )

    assert synthesized == ["Updated line"]
    assert result["clips"][0]["audio_path"] == str(voice_root / "fresh.wav")


@pytest.mark.asyncio(loop_scope="function")
async def test_scene_narration_does_not_mux_partial_audio_and_checkpoints_failure(monkeypatch, tmp_path):
    callbacks = []
    voice_root = tmp_path / "voice"
    voice_root.mkdir()
    valid_audio = voice_root / "scene-2.wav"
    dsp.write_audio(str(valid_audio), dsp.sine(440.0, 0.4) * 0.25)

    class OneSceneFails:
        async def synthesize_async(self, text, **kwargs):
            if text == "failed line":
                raise RuntimeError("local pt-BR voice unavailable")
            return {
                "output_path": str(valid_audio),
                "engine": "test-tts",
                "duration": 0.4,
            }

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_voice_studio.get_voice_engine",
        lambda: OneSceneFails(),
    )
    monkeypatch.setattr(
        scene_narration, "get_subsystem_dir",
        lambda name: voice_root if name == "voice" else tmp_path,
    )

    def unexpected_export(*args, **kwargs):
        raise AssertionError("partial narration must not be exported")

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_dubbing.export_dubbing.export_audio_track",
        unexpected_export,
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.media.audio.mux_audio_into_video",
        unexpected_export,
    )

    result = await scene_narration.synthesize_scene_narration_async(
        [
            {"index": 0, "voiceover_text": "failed line", "duration": 10.0},
            {"index": 1, "voiceover_text": "working line", "duration": 10.0},
        ],
        video_path=str(tmp_path / "source.mp4"),
        params={"voice_language": "pt-BR", "fps": 1},
        output_dir=str(tmp_path),
        clip_callback=callbacks.append,
    )

    assert result["muxed"] is False
    assert result["narration_complete"] is False
    assert result["failed_scene_indices"] == [0]
    assert result["clips"][0]["status"] == "failed"
    assert result["clips"][1]["status"] == "completed"
    assert [item["index"] for item in callbacks] == [0, 1]
    assert callbacks[0]["error"] == "local pt-BR voice unavailable"
