"""Tests for the VidGrid stream-copy assembly fast path."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from modules.ai_video_studio.media import output_paths
from modules.ai_video_studio.media.render import concat_vidgrid_scene_clips


def test_concat_uses_stream_copy_and_strips_per_clip_audio(tmp_path, monkeypatch):
    video_root = tmp_path / "videos"
    video_root.mkdir()
    clips = [video_root / "scene_01.mp4", video_root / "scene_02.mp4"]
    for clip in clips:
        clip.write_bytes(b"fake-mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _kind: video_root)

    import shutil
    import subprocess

    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")

    def fake_run(command, **_kwargs):
        if command[0].endswith("ffprobe"):
            payload = {
                "streams": [{
                    "codec_type": "video", "codec_name": "h264", "width": 1280,
                    "height": 720, "avg_frame_rate": "30/1", "pix_fmt": "yuv420p",
                }],
                "format": {"duration": "10.000000"},
            }
            return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")
        assert "-an" in command
        assert command[command.index("-c:v") + 1] == "copy"
        manifest = Path(command[command.index("-i") + 1]).read_text(encoding="utf-8")
        assert manifest.startswith("ffconcat version 1.0\\n")
        assert manifest.count("\\nfile '") == 2
        output = Path(command[-1])
        output.write_bytes(b"joined-mp4")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = concat_vidgrid_scene_clips(
        clips, video_root / "final.mp4", fps=30, width=1280, height=720,
    )

    assert result["used"] is True
    assert result["frames"] == 600
    assert result["engine"] == "ffmpeg_vidgrid_stream_copy"
    assert (video_root / "final.mp4").read_bytes() == b"joined-mp4"


def test_concat_rejects_clips_outside_video_asset_root(tmp_path, monkeypatch):
    video_root = tmp_path / "videos"
    video_root.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"fake-mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _kind: video_root)

    result = concat_vidgrid_scene_clips(
        [outside], video_root / "final.mp4", fps=30, width=1280, height=720,
    )

    assert result == {"used": False, "reason": "clip_outside_video_asset_root"}
