"""API tests for DARKSTUDIO timeline draft and edited MP4 rendering."""
from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from modules.ai_video_studio.api.routes import video


@pytest.fixture
def completed_job():
    job_id = "timeline-test-job"
    video._jobs[job_id] = {
        "job_id": job_id,
        "project_id": "test-project",
        "status": "completed",
        "output_url": "/downloads/original.mp4",
        "resolution": "1280x720",
        "frame_rate": 24,
        "params": {
            "resolution": "1280x720",
            "frame_rate": 24,
            "studio_id": "whymentary",
        },
        "_source_scenes": [
            {"index": 0, "duration": 2.0, "shot_type": "wide"},
            {"index": 1, "duration": 2.0, "shot_type": "close_up"},
        ],
        "_edited_scenes": [
            {"index": 0, "duration": 2.0, "shot_type": "wide"},
            {"index": 1, "duration": 2.0, "shot_type": "close_up"},
        ],
        "edit_timeline": {
            "tracks": [
                {"id": "video-main", "type": "video", "clips": []},
                {"id": "audio-narration", "type": "audio", "role": "narration", "clips": []},
            ]
        },
    }
    yield job_id
    video._jobs.pop(job_id, None)


def test_update_timeline_draft_keeps_non_video_tracks(completed_job, monkeypatch) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    request = video.TimelineEditRequest(
        scene_order=[1, 0],
        scene_edits=[
            video.SceneEdit(scene_index=0, duration_frames=72, transition_type="cut"),
            video.SceneEdit(scene_index=1, duration_frames=48, transition_type="cut"),
        ],
    )
    result = asyncio.run(video.update_video_job_timeline(completed_job, request))
    record = video._jobs[completed_job]
    assert result["edit_draft_status"] == "persisted_local_sqlite"
    assert [scene["index"] for scene in record["_edited_scenes"]] == [1, 0]
    assert [track["type"] for track in result["edit_timeline"]["tracks"]] == ["video", "audio"]



@pytest.mark.parametrize("field,value", [
    ("target_lufs", -40),
    ("true_peak_db", -12),
    ("loudness_range", 25),
])


@pytest.mark.parametrize("pan", [-1.1, 1.1])
def test_audio_timeline_rejects_pan_outside_stereo_range(pan):
    with pytest.raises(ValueError):
        video.AudioTimelineClip(asset="music/theme.wav", start=0, end=2, pan=pan)


@pytest.mark.parametrize("field,value", [
    ("compressor_ratio", 21),
    ("compressor_threshold_db", -61),
    ("eq_low_db", 13),
    ("eq_mid_db", -13),
])
def test_audio_timeline_rejects_invalid_mastering_controls(field, value):
    with pytest.raises(Exception):
        video.AudioTimelineEditRequest(**{field: value})


def test_audio_timeline_rejects_invalid_loudness_controls(field, value):
    with pytest.raises(ValueError):
        video.AudioTimelineEditRequest(**{field: value})

def test_update_audio_timeline_persists_music_and_sfx_controls(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import audio_timeline

    monkeypatch.setattr(audio_timeline, "validate_audio_asset", lambda value: tmp_path / "validated.wav")
    request = video.AudioTimelineEditRequest(
        music_clips=[video.AudioTimelineClip(
            asset=str(tmp_path / "music.wav"), start=0.5, end=3.0,
            volume=0.25, fade_in=0.5, fade_out=0.75,
        )],
        sfx_clips=[video.AudioTimelineClip(
            asset=str(tmp_path / "impact.wav"), start=1.0, end=1.5, volume=0.8,
        )],
        ducking_enabled=True, ducking_db=12, ducking_threshold_db=-38,
        ducking_attack=0.06, ducking_release=0.4,
    )
    result = asyncio.run(video.update_video_job_audio(completed_job, request))
    record = video._jobs[completed_job]
    assert result["audio_draft_status"] == "saved"
    assert record["_audio_clips"]["music"][0]["volume"] == 0.25
    assert record["_audio_clips"]["sfx"][0]["start"] == 1.0
    assert record["_audio_settings"]["ducking_db"] == 12
    assert record["audio_settings"]["ducking_threshold_db"] == -38
    assert record["_audio_settings"]["normalization_enabled"] is True
    assert record["_audio_settings"]["normalization_target_dbfs"] == -18
    assert record["_audio_settings"]["loudness_normalization_enabled"] is False
    assert record["_audio_settings"]["target_lufs"] == -14
    music_track = next(track for track in result["edit_timeline"]["tracks"] if track.get("role") == "music")
    assert music_track["clips"][0]["fade_in"] == 0.5


def test_update_audio_timeline_rejects_looping_sound_effect(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import audio_timeline
    monkeypatch.setattr(audio_timeline, "validate_audio_asset", lambda value: tmp_path / "validated.wav")
    request = video.AudioTimelineEditRequest(sfx_clips=[video.AudioTimelineClip(
        asset="effects/hit.wav", start=0, end=1, loop=True,
    )])
    with pytest.raises(HTTPException) as error:
        asyncio.run(video.update_video_job_audio(completed_job, request))
    assert error.value.status_code == 422
    assert "music only" in str(error.value.detail)

def test_update_timeline_draft_rejects_unknown_job() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(video.update_video_job_timeline("missing-job", video.TimelineEditRequest()))
    assert error.value.status_code == 404


def test_render_edits_returns_new_mp4_and_regenerates_subtitle_sidecar(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import output_paths, render

    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda *_: tmp_path)
    monkeypatch.setattr(output_paths, "unique_filename", lambda *_: tmp_path / "edited.mp4")
    monkeypatch.setattr(video, "to_download_url", lambda path: "/downloads/edited.mp4")

    def fake_render(scenes, output_path, **kwargs):
        assert [scene["index"] for scene in scenes] == [0, 1]
        assert kwargs["require_mp4"] is True
        from pathlib import Path
        Path(output_path).write_bytes(b"fake-edited-mp4")
        return {"output_path": str(output_path), "frames": 96, "bytes": 1234, "engine": "ffmpeg"}

    monkeypatch.setattr(render, "render_multi_scene_video", fake_render)
    result = asyncio.run(video.render_video_job_edits(completed_job))
    assert result["status"] == "completed"
    assert result["output_url"] == "/downloads/edited.mp4"
    assert result["audio_status"] == "silent"
    assert result["subtitle_status"] == "regenerated"
    assert result["subtitles"]["format"] == "srt"
    assert video._jobs[completed_job]["edit_render_subtitles"] == "regenerated"
    assert video._jobs[completed_job]["edit_render_status"] == "completed"
    assert video._jobs[completed_job]["output_url"] == "/downloads/original.mp4"
    assert video._jobs[completed_job]["edited_output_url"] == "/downloads/edited.mp4"


def test_render_edits_mixes_saved_audio_tracks(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import audio, audio_timeline, output_paths, render

    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda *_: tmp_path)
    monkeypatch.setattr(output_paths, "unique_filename", lambda directory, prefix, extension: tmp_path / f"{prefix}.{extension}")
    monkeypatch.setattr(video, "to_download_url", lambda path: "/downloads/edited-final.mp4")

    def fake_render(scenes, output_path, **kwargs):
        from pathlib import Path
        Path(output_path).write_bytes(b"visual-mp4")
        return {"output_path": str(output_path), "frames": 96, "bytes": 1234, "engine": "ffmpeg"}

    def fake_mix(clips, output_path, *, total_duration, **settings):
        assert clips[0]["asset"].endswith("bed.wav")
        assert settings["ducking_db"] == 11
        assert settings["normalization_target_dbfs"] == -18
        assert settings["target_lufs"] == -14
        assert settings["loudness_normalization_enabled"] is True
        assert total_duration == 4
        from pathlib import Path
        Path(output_path).write_bytes(b"mixed-wav")
        return {"output_path": str(output_path), "duration": total_duration, "ducking": {"enabled": True, "reduction_db": 11, "speech_detected": True}, "normalization": {"enabled": True, "target_dbfs": -18, "gain_db": -2.5, "pre_rms": 0.13}, "loudness": {"enabled": True, "target_lufs": -14, "true_peak_db": -1, "output_i": -14.1, "output_tp": -1.2, "output_lra": 6.1, "passes": 2, "verified": True}}

    def fake_mux(video_path, audio_path, output_path):
        from pathlib import Path
        Path(output_path).write_bytes(b"final-mp4")
        return {"output_path": str(output_path), "muxed": True}

    monkeypatch.setattr(render, "render_multi_scene_video", fake_render)
    monkeypatch.setattr(audio_timeline, "mix_audio_timeline", fake_mix)
    monkeypatch.setattr(audio, "mux_audio_into_video", fake_mux)
    video._jobs[completed_job]["_audio_clips"] = {
        "music": [{"asset": str(tmp_path / "music" / "bed.wav"), "start": 0, "end": 4, "volume": 0.3}],
        "sfx": [],
    }
    video._jobs[completed_job]["_audio_settings"] = {"ducking_enabled": True, "ducking_db": 11, "ducking_threshold_db": -36, "ducking_attack": 0.08, "ducking_release": 0.35, "normalization_enabled": True, "normalization_target_dbfs": -18, "normalization_max_gain_db": 6, "loudness_normalization_enabled": True, "target_lufs": -14, "true_peak_db": -1, "loudness_range": 11}

    result = asyncio.run(video.render_video_job_edits(completed_job))
    assert result["audio_status"] == "mixed_audio"
    assert result["ducking"]["reduction_db"] == 11
    assert result["normalization"]["gain_db"] == -2.5
    assert result["loudness"]["output_i"] == -14.1
    assert video._jobs[completed_job]["edit_render_loudness"]["verified"] is True
    assert result["output_url"] == "/downloads/edited-final.mp4"
    assert video._jobs[completed_job]["edit_render_audio"] == "mixed_audio"


def test_render_edits_rejects_job_without_saved_scene_draft() -> None:
    job_id = "no-draft-job"
    video._jobs[job_id] = {"job_id": job_id, "status": "processing"}
    try:
        with pytest.raises(HTTPException) as error:
            asyncio.run(video.render_video_job_edits(job_id))
        assert error.value.status_code == 409
    finally:
        video._jobs.pop(job_id, None)


def test_job_status_exposes_persisted_edit_render_metadata(completed_job) -> None:
    video._jobs[completed_job].update(
        edit_draft_status="saved",
        edit_render_status="completed",
        edited_output_url="/downloads/edited.mp4",
        edited_video_duration=4.0,
        edit_render_audio="mixed_audio",
        edit_render_ducking={"enabled": True, "reduction_db": 12, "speech_detected": True},
        edit_render_normalization={"enabled": True, "target_dbfs": -18, "gain_db": -2},
        edit_render_loudness={"enabled": True, "target_lufs": -14, "output_i": -14.1, "output_tp": -1.2, "verified": True},
        edit_render_subtitles="regenerated",
        edited_subtitles={"format": "srt", "download_url": "/downloads/edited.srt"},
    )
    result = asyncio.run(video.get_video_job_status(completed_job))
    assert result.edited_output_url == "/downloads/edited.mp4"
    assert result.edit_render_status == "completed"
    assert result.edit_render_audio == "mixed_audio"
    assert result.edit_render_ducking["reduction_db"] == 12
    assert result.edit_render_normalization["gain_db"] == -2
    assert result.edit_render_loudness["output_i"] == -14.1
    assert result.edit_render_loudness["verified"] is True
    assert result.edit_render_subtitles == "regenerated"
    assert result.edited_subtitles["download_url"] == "/downloads/edited.srt"
