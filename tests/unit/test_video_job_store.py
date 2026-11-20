"""SQLite persistence tests for DARKSTUDIO job records."""
from __future__ import annotations

from modules.ai_video_studio.media import job_store


def test_job_store_round_trips_editable_scene_draft(tmp_path, monkeypatch) -> None:
    database = tmp_path / "jobs.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    record = {
        "job_id": "job-123",
        "project_id": "project-abc",
        "status": "completed",
        "params": {"frame_rate": 24},
        "_source_scenes": [{"index": 0, "duration": 2.0}],
        "_edited_scenes": [{"index": 0, "duration": 3.0}],
        "edit_timeline": {"duration_frames": 72, "tracks": []},
        "_rendering_edits": True,
    }

    job_store.save_job(record)
    loaded = job_store.load_jobs()

    assert loaded["job-123"]["project_id"] == "project-abc"
    assert loaded["job-123"]["_edited_scenes"][0]["duration"] == 3.0
    assert loaded["job-123"]["edit_timeline"]["duration_frames"] == 72
    assert "_rendering_edits" not in loaded["job-123"]
    assert job_store.load_jobs(project_id="other-project") == {}


def test_job_store_updates_existing_job_instead_of_duplicating(tmp_path, monkeypatch) -> None:
    database = tmp_path / "jobs.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    job_store.save_job({
        "job_id": "job-123", "project_id": "project-abc",
        "status": "processing", "progress": 0.5,
    })
    job_store.save_job({
        "job_id": "job-123", "project_id": "project-abc",
        "status": "completed", "progress": 1.0,
    })

    loaded = job_store.load_jobs()
    assert len(loaded) == 1
    assert loaded["job-123"]["status"] == "completed"
    assert loaded["job-123"]["progress"] == 1.0


def test_job_store_marks_only_in_flight_jobs_interrupted(tmp_path, monkeypatch) -> None:
    database = tmp_path / "jobs.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    jobs = {
        "queued-job": {"job_id": "queued-job", "project_id": "p1", "status": "queued", "progress": 0.0},
        "running-job": {"job_id": "running-job", "project_id": "p1", "status": "processing", "progress": 0.42},
        "done-job": {"job_id": "done-job", "project_id": "p1", "status": "completed", "progress": 1.0},
    }
    recovered = job_store.mark_interrupted_jobs(jobs)

    assert recovered == ["queued-job", "running-job"]
    assert jobs["queued-job"]["status"] == "failed"
    assert jobs["running-job"]["interrupted"] is True
    assert jobs["running-job"]["progress"] == 0.42
    assert jobs["done-job"]["status"] == "completed"
    loaded = job_store.load_jobs()
    assert loaded["running-job"]["status"] == "failed"
    assert "reinicialização" in loaded["running-job"]["error"]

def test_interrupted_job_reports_only_existing_assets_inside_asset_roots(tmp_path, monkeypatch):
    database = tmp_path / "jobs.sqlite3"
    roots = {name: tmp_path / name for name in ("jobs", "images", "videos", "voice")}
    for root in roots.values():
        root.mkdir()
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    monkeypatch.setattr(job_store, "get_subsystem_dir", lambda name: roots[name])

    image = roots["images"] / "scene-0.png"
    clip = roots["videos"] / "scene-0.mp4"
    narration = roots["voice"] / "scene-0.wav"
    outside = tmp_path / "outside.png"
    for path in (image, clip, narration, outside):
        path.write_bytes(b"asset")

    jobs = {
        "recoverable": {
            "job_id": "recoverable", "project_id": "p1", "status": "processing",
            "scene_progress": [{"scene_index": 0, "status": "completed"}],
            "scene_assets": [{"scene_index": 0, "image_path": str(image)}],
            "scene_clips": [
                {"scene_index": 0, "output_path": str(clip), "audio_path": str(narration)},
                {"scene_index": 1, "output_path": str(outside)},
            ],
            "voiceover": {"clips": [{"audio_path": str(narration)}]},
        }
    }

    assert job_store.mark_interrupted_jobs(jobs) == ["recoverable"]
    recovery = jobs["recoverable"]["failure_info"]
    assert recovery["preserved_image_count"] == 1
    assert recovery["preserved_clip_count"] == 1
    assert recovery["preserved_narration_count"] == 2
    assert recovery["recoverable_scene_indices"] == [0]
    assert recovery["scene_assets_preserved"] is True
    assert recovery["automatic_resume_supported"] is False
    persisted = job_store.load_jobs()["recoverable"]["failure_info"]
    assert persisted["preserved_clip_count"] == 1
