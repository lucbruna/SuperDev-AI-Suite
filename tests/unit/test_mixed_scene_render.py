"""Mixed AI/procedural scene rendering and job-scoped motion integration tests."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.ai_video_studio.api.routes import video


def test_generate_scene_motion_persists_comfyui_clip_on_job(tmp_path, monkeypatch):
    from modules.ai_video_studio.media import output_paths
    from modules.ai_video_studio.ai_video_generator.image_to_video import image_to_video_engine

    images = tmp_path / "images"
    videos = tmp_path / "videos"
    images.mkdir()
    videos.mkdir()
    image = images / "scene.png"
    image.write_bytes(b"image")
    generated = videos / "scene_motion.mp4"
    generated.write_bytes(b"mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: images if name == "images" else videos)
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    monkeypatch.setattr(video, "to_download_url", lambda path: f"/downloads/{Path(path).name}")

    calls = {}
    def fake_generate(self, job):
        calls.update(job)
        return {
            "output_path": str(generated), "provider": "comfyui_workflow",
            "provider_prompt_id": "prompt-42", "duration": 10.0, "frames": 240, "fps": 24,
        }
    monkeypatch.setattr(image_to_video_engine.ImageToVideoEngine, "generate", fake_generate)

    job_id = "scene-motion-test"
    video._jobs[job_id] = {
        "job_id": job_id, "project_id": "test", "status": "completed",
        "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 24,
        "params": {"resolution": "1280x720", "frame_rate": 24},
        "_source_scenes": [{"index": 0}, {"index": 1, "background_image_path": str(image)}],
        "_edited_scenes": [{"index": 0}, {"index": 1, "background_image_path": str(image)}],
        "scene_clips": [],
    }
    try:
        result = asyncio.run(video.generate_video_job_scene_motion(
            job_id, 1, video.SceneMotionRequest(motion_prompt="Slow cinematic orbit"),
        ))
        scene = video._jobs[job_id]["_edited_scenes"][1]
        assert result["status"] == "ready"
        assert result["frames"] == 240
        assert scene["generative_video_path"] == str(generated)
        assert video._jobs[job_id]["scene_clips"][0]["generative_video_provider"] == "comfyui_workflow"
        assert calls["params"]["duration"] == 10.0
        assert calls["params"]["motion_provider"] == "comfyui"
    finally:
        video._jobs.pop(job_id, None)


def test_generate_scene_motion_rejects_image_outside_darkstudio_library(tmp_path, monkeypatch):
    from modules.ai_video_studio.media import output_paths

    images = tmp_path / "images"
    images.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"image")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: images)
    job_id = "scene-motion-invalid-image"
    video._jobs[job_id] = {
        "job_id": job_id, "project_id": "test", "status": "completed",
        "_edited_scenes": [{"background_image_path": str(outside)}],
    }
    try:
        with pytest.raises(Exception) as error:
            asyncio.run(video.generate_video_job_scene_motion(
                job_id, 0, video.SceneMotionRequest(motion_prompt="Animate"),
            ))
        assert getattr(error.value, "status_code", None) == 422
    finally:
        video._jobs.pop(job_id, None)


def test_mixed_renderer_normalizes_and_concatenates_ai_and_procedural_scenes(tmp_path, monkeypatch):
    from modules.ai_video_studio.media import output_paths, render

    video_root = tmp_path / "videos"
    video_root.mkdir()
    ai_clip = video_root / "ai_scene.mp4"
    ai_clip.write_bytes(b"ai-mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
    monkeypatch.setattr("shutil.which", lambda _name: "/usr/bin/ffmpeg")

    def fake_procedural(scene, output_path, **kwargs):
        Path(output_path).write_bytes(b"procedural-mp4")
        return {"output_path": str(output_path), "frames": 24}
    monkeypatch.setattr(render, "render_single_scene_clip", fake_procedural)

    commands = []
    def fake_run(command, **kwargs):
        commands.append(command)
        Path(command[-1]).write_bytes(b"encoded-mp4")
        return SimpleNamespace(returncode=0, stderr="")
    monkeypatch.setattr(subprocess, "run", fake_run)

    output = video_root / "mixed.mp4"
    result = render.render_mixed_scene_video(
        [{"index": 0, "duration": 1.0}, {"index": 1, "duration": 1.0}],
        output, generated_clips={1: str(ai_clip)}, fps=24, width=320, height=180,
    )
    assert output.read_bytes() == b"encoded-mp4"
    assert result["frames"] == 48
    assert result["generated_scene_indices"] == [1]
    assert result["engine"] == "ffmpeg_mixed_scene_transitions"
    assert result["transition_policy"] == "frame_accurate"
    assert len(commands) == 3  # normalize both sources, then assemble the timeline
    filter_graph = commands[-1][commands[-1].index("-filter_complex") + 1]
    assert "concat=n=2:v=1:a=0" in filter_graph
