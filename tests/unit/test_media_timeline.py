"""Tests for the frame-accurate DARKSTUDIO edit timeline."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.media.timeline import build_edit_timeline


def test_video_timeline_uses_integer_frames_and_crossfade_overlap() -> None:
    scenes = [
        {"index": 0, "duration": 2.0, "shot_type": "wide",
         "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"index": 1, "duration": 3.0, "shot_type": "close_up"},
    ]
    timeline = build_edit_timeline(scenes, fps=24, width=1080, height=1920)
    video = timeline["tracks"][0]["clips"]
    assert video[0]["start_frame"] == 0
    assert video[0]["end_frame"] == 48
    assert video[1]["start_frame"] == 36
    assert video[1]["end_frame"] == 108
    assert timeline["duration_frames"] == 108
    assert timeline["duration_seconds"] == 4.5
    assert scenes[1].get("start_frame") is None


def test_timeline_adds_only_tracks_with_real_assets() -> None:
    timeline = build_edit_timeline(
        [{"duration": 4}],
        fps=30,
        narration={"clips": [{"start": 0.5, "end": 2.5, "audio_path": "voice.wav", "text": "Olá"}]},
        music_clips=[{"start": 0, "end": 4, "asset": "music.mp3"}],
        sfx_clips=[{"start": 1, "end": 1.5, "path": "whoosh.wav"}],
        subtitle_cues=[{"index": 1, "start": 0.5, "end": 2.0, "text": "Olá"}],
    )
    assert [track["role"] for track in timeline["tracks"][1:4]] == [
        "narration", "music", "sound_effect"
    ]
    assert timeline["tracks"][1]["clips"][0]["start_frame"] == 15
    assert timeline["tracks"][1]["clips"][0]["end_frame"] == 75
    assert timeline["tracks"][4]["clips"][0]["duration_frames"] == 45


def test_timeline_omits_missing_narration_and_optional_tracks() -> None:
    timeline = build_edit_timeline(
        [{"duration": 1}, {"duration": 1, "transition_out": {"type": "cut"}}],
        fps=24,
        narration={"clips": [{"start": 0, "end": 1, "text": "sem áudio"}]},
    )
    assert [track["type"] for track in timeline["tracks"]] == ["video"]


@pytest.mark.parametrize("scenes,kwargs", [
    ([], {}),
    ([{"duration": 0}], {}),
    ([{"duration": 1, "transition_out": {"type": "crossfade", "duration_frames": 8}}], {}),
    ([{"duration": 1}], {"fps": 0}),
    ([{"duration": 1}], {"width": 0}),
])
def test_timeline_rejects_invalid_video_spec(scenes, kwargs) -> None:
    with pytest.raises(ValueError):
        build_edit_timeline(scenes, **kwargs)


def test_timeline_rejects_invalid_audio_and_subtitle_ranges() -> None:
    with pytest.raises(ValueError, match="positive duration"):
        build_edit_timeline([{"duration": 1}], narration=[{"start": 2, "end": 1, "asset": "bad.wav"}])
    with pytest.raises(ValueError, match="requires text"):
        build_edit_timeline([{"duration": 1}], subtitle_cues=[{"start": 0, "end": 0.5, "text": " "}])
