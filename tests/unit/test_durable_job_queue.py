"""Tests for the SQLite-backed durable task queue."""
from __future__ import annotations

from modules.ai_video_studio.media import job_store


def test_durable_task_claim_is_exclusive_and_completes(tmp_path, monkeypatch):
    database = tmp_path / "queue.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)

    job_store.enqueue_task("task-1", "dependency_rebuild", {"job_id": "job-1"})
    assert job_store.has_active_task_for_job("job-1", "dependency_rebuild")
    first = job_store.claim_next_task("worker-a", lease_seconds=60)
    second = job_store.claim_next_task("worker-b", lease_seconds=60)

    assert first is not None
    assert first["payload"]["job_id"] == "job-1"
    assert first["attempts"] == 1
    assert second is None
    assert job_store.renew_task_lease("task-1", "worker-a", lease_seconds=60)
    assert job_store.complete_task("task-1", "worker-a")
    assert not job_store.has_active_task_for_job("job-1", "dependency_rebuild")
    assert job_store.claim_next_task("worker-b") is None
    assert job_store.list_tasks("dependency_rebuild")[0]["status"] == "completed"


def test_durable_task_retries_are_bounded(tmp_path, monkeypatch):
    database = tmp_path / "queue.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)

    job_store.enqueue_task("task-retry", "dependency_rebuild", {"job_id": "job-retry"})
    first = job_store.claim_next_task("worker-a")
    assert first["attempts"] == 1
    assert job_store.fail_task("task-retry", "worker-a", "temporary failure", retry_delay=0, max_attempts=2)

    second = job_store.claim_next_task("worker-b")
    assert second["attempts"] == 2
    assert job_store.fail_task("task-retry", "worker-b", "permanent failure", retry_delay=0, max_attempts=2)
    assert job_store.claim_next_task("worker-c") is None
    task = job_store.list_tasks("dependency_rebuild")[0]
    assert task["status"] == "failed"
    assert task["attempts"] == 2
    assert task["last_error"] == "permanent failure"


def test_expired_worker_leases_are_reclaimed_and_crashes_are_bounded(tmp_path, monkeypatch):
    database = tmp_path / "lease-recovery.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    clock = {"now": 1000.0}
    monkeypatch.setattr("time.time", lambda: clock["now"])

    job_store.enqueue_task("task-crash", "dependency_rebuild", {"job_id": "job-crash"})
    first = job_store.claim_next_task("worker-a", lease_seconds=30)
    assert first["attempts"] == 1

    clock["now"] = 1031.0
    second = job_store.claim_next_task("worker-b", lease_seconds=30)
    assert second["attempts"] == 2

    clock["now"] = 1062.0
    third = job_store.claim_next_task("worker-c", lease_seconds=30)
    assert third["attempts"] == 3

    clock["now"] = 1093.0
    assert job_store.claim_next_task("worker-d", lease_seconds=30) is None
    task = job_store.list_tasks("dependency_rebuild")[0]
    assert task["status"] == "failed"
    assert task["attempts"] == 3


def test_unique_task_enqueue_is_atomic_per_job_and_task_type(tmp_path, monkeypatch):
    database = tmp_path / "unique-queue.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)

    assert job_store.enqueue_unique_task_for_job(
        "scene-task-1", "scene_clip_rebuild", "job-unique",
        {"job_id": "job-unique", "queue_id": "queue-1"},
    )
    assert not job_store.enqueue_unique_task_for_job(
        "scene-task-2", "scene_clip_rebuild", "job-unique",
        {"job_id": "job-unique", "queue_id": "queue-2"},
    )
    # A different task type remains independent for the same job.
    assert job_store.enqueue_unique_task_for_job(
        "dependency-task-1", "dependency_rebuild", "job-unique",
        {"job_id": "job-unique"},
    )
    active = job_store.list_tasks()
    assert len(active) == 2
    assert {item["task_id"] for item in active} == {
        "scene-task-1", "dependency-task-1",
    }
