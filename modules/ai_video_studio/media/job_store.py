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
