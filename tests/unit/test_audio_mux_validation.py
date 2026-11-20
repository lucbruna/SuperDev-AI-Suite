from __future__ import annotations

import shutil
import subprocess

from modules.ai_video_studio.media import audio


def test_mux_rejects_missing_video_input(tmp_path, monkeypatch):
    audio_file = tmp_path / "voice.wav"
    audio_file.write_bytes(b"audio")
    monkeypatch.setattr(shutil, "which", lambda _name: "ffmpeg")
    result = audio.mux_audio_into_video(tmp_path / "missing.mp4", audio_file, tmp_path / "out.mp4")
    assert result["muxed"] is False
    assert result["reason"] == "video input missing or empty"


def test_mux_rejects_empty_audio_input(tmp_path, monkeypatch):
    video_file = tmp_path / "video.mp4"
    audio_file = tmp_path / "voice.wav"
    video_file.write_bytes(b"video")
    audio_file.write_bytes(b"")
    monkeypatch.setattr(shutil, "which", lambda _name: "ffmpeg")
    result = audio.mux_audio_into_video(video_file, audio_file, tmp_path / "out.mp4")
    assert result["muxed"] is False
    assert result["reason"] == "audio input missing or empty"


def test_mux_rejects_success_without_output_file(tmp_path, monkeypatch):
    video_file = tmp_path / "video.mp4"
    audio_file = tmp_path / "voice.wav"
    video_file.write_bytes(b"video")
    audio_file.write_bytes(b"audio")
    monkeypatch.setattr(shutil, "which", lambda _name: "ffmpeg")
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, "", ""))
    result = audio.mux_audio_into_video(video_file, audio_file, tmp_path / "missing-output.mp4")
    assert result["muxed"] is False
    assert result["reason"] == "mux output missing or empty"


def test_mux_reports_nonempty_output(tmp_path, monkeypatch):
    video_file = tmp_path / "video.mp4"
    audio_file = tmp_path / "voice.wav"
    output_file = tmp_path / "out.mp4"
    video_file.write_bytes(b"video")
    audio_file.write_bytes(b"audio")
    monkeypatch.setattr(shutil, "which", lambda _name: "ffmpeg")
    def fake_run(*args, **kwargs):
        output_file.write_bytes(b"muxed-video")
        return subprocess.CompletedProcess(args[0], 0, "", "")
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = audio.mux_audio_into_video(video_file, audio_file, output_file)
    assert result == {"output_path": str(output_file), "muxed": True, "bytes": len(b"muxed-video")}
