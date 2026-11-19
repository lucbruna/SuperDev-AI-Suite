"""SQLite persistence for DARKSTUDIO video jobs and editable scene drafts.

Uses only the Python standard library. Job payloads are JSON documents stored
inside a local SQLite database under modules/downloads/jobs.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from modules.ai_video_studio.media.output_paths import get_subsystem_dir


def _database_path():
    return get_subsystem_dir("jobs") / "darkstudio_jobs.sqlite3"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(_database_path(), timeout=15)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS video_jobs (
            job_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            status TEXT NOT NULL,
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    return connection


def save_job(record: dict[str, Any]) -> None:
    """Persist a serializable snapshot; transient lock flags are excluded."""
    job_id = str(record.get("job_id") or "")
    project_id = str(record.get("project_id") or "")
    if not job_id or not project_id:
        raise ValueError("job_id and project_id are required for persistence")
    payload = {key: value for key, value in record.items() if key != "_rendering_edits"}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    updated_at = datetime.now(timezone.utc).isoformat()
    connection = _connect()
    try:
        connection.execute(
            """
            INSERT INTO video_jobs(job_id, project_id, status, payload, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                project_id=excluded.project_id,
                status=excluded.status,
                payload=excluded.payload,
                updated_at=excluded.updated_at
            """,
            (job_id, project_id, str(record.get("status") or "unknown"), encoded, updated_at),
        )
        connection.commit()
    finally:
        connection.close()


def load_jobs(project_id: str | None = None) -> dict[str, dict[str, Any]]:
    """Load persisted jobs, optionally filtered by project."""
    connection = _connect()
    try:
        if project_id:
            rows = connection.execute(
                "SELECT job_id, payload FROM video_jobs WHERE project_id=? ORDER BY updated_at DESC",
                (project_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT job_id, payload FROM video_jobs ORDER BY updated_at DESC"
            ).fetchall()
    finally:
        connection.close()
    result: dict[str, dict[str, Any]] = {}
    for job_id, payload in rows:
        try:
            record = json.loads(payload)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(record, dict):
            result[str(job_id)] = record
    return result


def mark_interrupted_jobs(jobs: dict[str, dict[str, Any]]) -> list[str]:
    """Mark queued/processing jobs as interrupted after an API process restart.

    Rendering is not resumed automatically because FFmpeg/provider subprocess
    state is not checkpointed. This prevents stale jobs from appearing active
    forever and preserves their last durable progress for inspection.
    """
    recovered: list[str] = []
    for job_id, record in jobs.items():
        if record.get("status") not in {"queued", "processing"}:
            continue
        record.update(
            status="failed",
            current_step="Interrupted",
            error="A geração foi interrompida por reinicialização do servidor. Inicie um novo job; o progresso salvo foi preservado.",
            interrupted=True,
        )
        try:
            save_job(record)
        except Exception:
            # Keep the in-memory record truthful even if the database is
            # temporarily unavailable during startup recovery.
            pass
        recovered.append(str(job_id))
    return recovered


def _ensure_task_queue(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS durable_tasks (
            task_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            available_at REAL NOT NULL,
            lease_owner TEXT,
            lease_expires_at REAL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            last_error TEXT
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_durable_tasks_claim "
        "ON durable_tasks(status, available_at, lease_expires_at, created_at)"
    )


def enqueue_task(task_id: str, task_type: str, payload: dict[str, Any]) -> None:
    """Persist a durable task before acknowledging it to the API client."""
    import time

    now = time.time()
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        connection.execute(
            """
            INSERT INTO durable_tasks(task_id, task_type, payload, status, attempts,
                                       available_at, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', 0, ?, ?, ?)
            ON CONFLICT(task_id) DO NOTHING
            """,
            (task_id, task_type, encoded, now, now, now),
        )
        connection.commit()
    finally:
        connection.close()


def claim_next_task(worker_id: str, lease_seconds: int = 300) -> dict[str, Any] | None:
    """Atomically claim one queued task or reclaim a task with an expired lease."""
    import time

    now = time.time()
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            UPDATE durable_tasks SET status='failed', lease_owner=NULL,
                lease_expires_at=NULL, last_error=COALESCE(last_error, 'Worker lease expired after maximum attempts'),
                updated_at=?
            WHERE status='processing' AND lease_expires_at IS NOT NULL
              AND lease_expires_at<=? AND attempts>=3
            """,
            (now, now),
        )
        row = connection.execute(
            """
            SELECT task_id, task_type, payload, attempts
            FROM durable_tasks
            WHERE attempts < 3 AND (
                (status='queued' AND available_at<=?)
                OR (status='processing' AND lease_expires_at IS NOT NULL AND lease_expires_at<=?)
            )
            ORDER BY created_at ASC LIMIT 1
            """,
            (now, now),
        ).fetchone()
        if row is None:
            connection.commit()
            return None
        task_id, task_type, encoded, attempts = row
        connection.execute(
            """
            UPDATE durable_tasks
            SET status='processing', attempts=?, lease_owner=?, lease_expires_at=?, updated_at=?
            WHERE task_id=?
            """,
            (int(attempts or 0) + 1, worker_id, now + max(30, int(lease_seconds)), now, task_id),
        )
        connection.commit()
        try:
            payload = json.loads(encoded)
        except (TypeError, json.JSONDecodeError):
            payload = {}
        return {"task_id": task_id, "task_type": task_type, "payload": payload,
                "attempts": int(attempts or 0) + 1, "lease_owner": worker_id}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def complete_task(task_id: str, worker_id: str) -> bool:
    """Complete only when the caller still owns the task lease."""
    import time

    connection = _connect()
    try:
        _ensure_task_queue(connection)
        cursor = connection.execute(
            """
            UPDATE durable_tasks
            SET status='completed', lease_owner=NULL, lease_expires_at=NULL, updated_at=?
            WHERE task_id=? AND status='processing' AND lease_owner=?
            """,
            (time.time(), task_id, worker_id),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def fail_task(task_id: str, worker_id: str, error: str, retry_delay: int = 30,
              max_attempts: int = 3) -> bool:
    """Schedule bounded retries; exhausted tasks become terminally failed."""
    import time

    now = time.time()
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        row = connection.execute(
            "SELECT attempts FROM durable_tasks WHERE task_id=? AND lease_owner=?",
            (task_id, worker_id),
        ).fetchone()
        if row is None:
            return False
        attempts = int(row[0] or 0)
        status = "failed" if attempts >= max_attempts else "queued"
        cursor = connection.execute(
            """
            UPDATE durable_tasks
            SET status=?, available_at=?, lease_owner=NULL, lease_expires_at=NULL,
                last_error=?, updated_at=?
            WHERE task_id=? AND lease_owner=?
            """,
            (status, now + max(0, retry_delay), str(error)[:1000], now, task_id, worker_id),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def list_tasks(task_type: str | None = None) -> list[dict[str, Any]]:
    """Return task metadata for diagnostics and operational dashboards."""
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        if task_type:
            rows = connection.execute(
                "SELECT task_id, task_type, status, attempts, available_at, lease_expires_at, last_error "
                "FROM durable_tasks WHERE task_type=? ORDER BY created_at DESC",
                (task_type,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT task_id, task_type, status, attempts, available_at, lease_expires_at, last_error "
                "FROM durable_tasks ORDER BY created_at DESC"
            ).fetchall()
    finally:
        connection.close()
    keys = ("task_id", "task_type", "status", "attempts", "available_at", "lease_expires_at", "last_error")
    return [dict(zip(keys, row)) for row in rows]


def renew_task_lease(task_id: str, worker_id: str, lease_seconds: int = 300) -> bool:
    """Extend a task lease while its worker is actively processing it."""
    import time

    now = time.time()
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        cursor = connection.execute(
            """
            UPDATE durable_tasks SET lease_expires_at=?, updated_at=?
            WHERE task_id=? AND status='processing' AND lease_owner=?
            """,
            (now + max(30, int(lease_seconds)), now, task_id, worker_id),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def has_active_task_for_job(job_id: str, task_type: str | None = None) -> bool:
    """Check whether a persisted queued/leased task still owns this job."""
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        if task_type:
            rows = connection.execute(
                "SELECT payload FROM durable_tasks WHERE status IN ('queued','processing') AND task_type=?",
                (task_type,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT payload FROM durable_tasks WHERE status IN ('queued','processing')"
            ).fetchall()
    finally:
        connection.close()
    for (encoded,) in rows:
        try:
            payload = json.loads(encoded)
        except (TypeError, json.JSONDecodeError):
            continue
        if str(payload.get("job_id") or "") == str(job_id):
            return True
    return False
