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


def mark_interrupted_edit_renders(jobs: dict[str, dict[str, Any]]) -> list[str]:
    """Mark an edit export interrupted when the API restarts mid-render.

    The final FFmpeg process is not checkpointed, so it cannot be resumed at
    the exact frame. Clear the process-local render lock so a fresh export can
    be requested; source assets are validated separately before retry.
    """
    recovered: list[str] = []
    for job_id, record in jobs.items():
        if record.get("edit_render_status") != "rendering":
            continue
        record["edit_render_status"] = "interrupted"
        # This flag belongs to the previous API process. If it remains True in
        # the persisted job, the render endpoint rejects every retry with 409.
        record["_rendering_edits"] = False
        record["edit_render_interrupted_at"] = datetime.now(timezone.utc).isoformat()
        scenes = record.get("_edited_scenes")
        has_scene_records = isinstance(scenes, list) and bool(scenes)
        can_retry_export = has_scene_records
        if record.get("vidgrid_compatible") and has_scene_records:
            # VidGrid needs one existing, non-empty clip for every edited scene.
            try:
                from pathlib import Path
                from modules.ai_video_studio.media.output_paths import get_subsystem_dir
                video_root = Path(get_subsystem_dir("videos")).resolve()
                clips = {
                    int(item.get("scene_index")): item
                    for item in (record.get("scene_clips") or [])
                    if isinstance(item, dict) and str(item.get("scene_index", "")).isdigit()
                }
                for position, scene in enumerate(scenes):
                    source_index = scene.get("_source_scene_index", position)
                    clip = clips.get(int(source_index)) if str(source_index).isdigit() else None
                    value = clip.get("output_path") if clip else None
                    path = Path(str(value)).resolve() if value else None
                    if path is None or video_root not in path.parents or not path.is_file() or path.stat().st_size <= 0:
                        can_retry_export = False
                        break
            except (OSError, TypeError, ValueError):
                can_retry_export = False
        record["edit_render_recovery"] = {
            "kind": "server_restart",
            "can_retry_export": can_retry_export,
            "scene_records_preserved": has_scene_records,
            "scene_assets_preserved": False,
            "automatic_resume_supported": False,
            "message": (
                "A exportação foi interrompida. O rascunho das cenas foi preservado; "
                "os arquivos serão verificados durante a exportação. O MP4 parcial não pode ser retomado."
                if can_retry_export else
                "A exportação foi interrompida. O rascunho foi preservado, mas os clipes necessários "
                "não foram encontrados ou não passaram na verificação. Reconstrua-os antes de exportar."
            ),
        }
        try:
            save_job(record)
        except Exception:
            # Keep in-memory recovery state even if persistence is temporarily unavailable.
            pass
        recovered.append(str(job_id))
    return recovered


def _inspect_recoverable_scene_assets(record: dict[str, Any]) -> dict[str, Any]:
    """Count durable scene assets that still exist inside DARKSTUDIO asset roots."""
    from pathlib import Path

    roots = {
        name: Path(get_subsystem_dir(name)).resolve()
        for name in ("images", "videos", "voice")
    }

    def exists_inside(value: Any, root_name: str) -> bool:
        if not value:
            return False
        try:
            root = roots[root_name]
            path = Path(str(value)).resolve()
            return root in path.parents and path.is_file() and path.stat().st_size > 0
        except (OSError, TypeError, ValueError):
            return False

    image_indices: set[int] = set()
    clip_indices: set[int] = set()
    narration_count = 0

    for item in record.get("scene_assets") or []:
        if not isinstance(item, dict):
            continue
        index = item.get("scene_index")
        if exists_inside(item.get("image_path"), "images") and str(index).isdigit():
            image_indices.add(int(index))

    for position, scene in enumerate(record.get("_source_scenes") or []):
        if isinstance(scene, dict) and exists_inside(scene.get("background_image_path"), "images"):
            image_indices.add(int(scene.get("_source_scene_index", position)))

    for item in record.get("scene_clips") or []:
        if not isinstance(item, dict):
            continue
        index = item.get("scene_index")
        if exists_inside(item.get("output_path"), "videos") and str(index).isdigit():
            clip_indices.add(int(index))
        if exists_inside(item.get("audio_path"), "voice"):
            narration_count += 1

    voiceover = record.get("voiceover")
    if isinstance(voiceover, dict):
        for clip in voiceover.get("clips") or []:
            if isinstance(clip, dict) and exists_inside(clip.get("audio_path"), "voice"):
                narration_count += 1

    return {
        "preserved_image_count": len(image_indices),
        "preserved_clip_count": len(clip_indices),
        "preserved_narration_count": narration_count,
        "recoverable_scene_indices": sorted(image_indices | clip_indices),
        "scene_assets_preserved": bool(image_indices or clip_indices or narration_count),
    }


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
        progress_items = [
            item for item in (record.get("scene_progress") or [])
            if isinstance(item, dict)
        ]
        completed_indices = [
            int(item.get("scene_index", index))
            for index, item in enumerate(progress_items)
            if item.get("status") == "completed"
        ]
        active_scene = next(
            (item for item in reversed(progress_items) if item.get("status") == "processing"),
            None,
        )
        previous_step = str(record.get("current_step") or "unknown")
        message = (
            "A geração foi interrompida pela reinicialização do servidor. "
            "O progresso registrado foi preservado; a retomada automática integral ainda não está disponível."
        )
        record.update(
            status="failed",
            current_step="Interrupted",
            error=message,
            interrupted=True,
            failure_info={
                "kind": "server_restart",
                "failed_stage": previous_step,
                "failed_scene_index": active_scene.get("scene_index") if active_scene else None,
                "last_completed_scene_index": max(completed_indices) if completed_indices else None,
                "completed_scene_indices": completed_indices,
                **_inspect_recoverable_scene_assets(record),
                "automatic_resume_supported": False,
                "recovery_hint": (
                    "Os arquivos de imagem, clipes e narrações existentes foram verificados e listados. "
                    "Use as cenas recuperáveis para continuar a edição; o subprocesso interrompido não é retomado."
                ),
            },
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


def enqueue_unique_task_for_job(task_id: str, task_type: str, job_id: str,
                               payload: dict[str, Any]) -> bool:
    """Atomically enqueue at most one active task of this type for a job.

    The check and insert share a BEGIN IMMEDIATE transaction, so concurrent API
    requests cannot both pass a separate preflight check and create duplicates.
    Returns False when an active queued/leased task already owns the job.
    """
    import time

    now = time.time()
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        connection.execute("BEGIN IMMEDIATE")
        rows = connection.execute(
            "SELECT payload FROM durable_tasks WHERE task_type=? AND status IN ('queued','processing')",
            (task_type,),
        ).fetchall()
        for (active_payload,) in rows:
            try:
                active = json.loads(active_payload)
            except (TypeError, json.JSONDecodeError):
                continue
            if str(active.get("job_id") or "") == str(job_id):
                connection.rollback()
                return False
        connection.execute(
            """
            INSERT INTO durable_tasks(task_id, task_type, payload, status, attempts,
                                      available_at, created_at, updated_at)
            VALUES (?, ?, ?, 'queued', 0, ?, ?, ?)
            """,
            (task_id, task_type, encoded, now, now, now),
        )
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_queued_task(task_id: str) -> bool:
    """Remove a task only while it is still queued and unclaimed."""
    connection = _connect()
    try:
        _ensure_task_queue(connection)
        cursor = connection.execute(
            "DELETE FROM durable_tasks WHERE task_id=? AND status='queued'",
            (task_id,),
        )
        connection.commit()
        return cursor.rowcount == 1
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
                "SELECT task_id, task_type, status, attempts, available_at, lease_expires_at, last_error, payload "
                "FROM durable_tasks WHERE task_type=? ORDER BY created_at DESC",
                (task_type,),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT task_id, task_type, status, attempts, available_at, lease_expires_at, last_error, payload "
                "FROM durable_tasks ORDER BY created_at DESC"
            ).fetchall()
    finally:
        connection.close()
    keys = ("task_id", "task_type", "status", "attempts", "available_at", "lease_expires_at", "last_error", "payload")
    results = []
    for row in rows:
        item = dict(zip(keys, row))
        try:
            item["payload"] = json.loads(item["payload"])
        except (TypeError, json.JSONDecodeError):
            item["payload"] = {}
        results.append(item)
    return results


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
