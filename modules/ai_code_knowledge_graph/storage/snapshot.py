"""Snapshot manager — durable captures of the built knowledge base.

A snapshot persists the context artifacts (scan, graph, semantic analysis,
embeddings, dependency analysis, search index) as one JSON-serializable
document so a build can be restored, exported or diffed later. Snapshots are
rotated to ``max_snapshots`` and stored through the configured ``Store``.
"""
from __future__ import annotations

import dataclasses
import json
import time
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    MODULE_DATA_DIR,
)
from modules.ai_code_knowledge_graph.storage.json_store import JsonFileStore
from modules.ai_code_knowledge_graph.storage.sqlite_store import SqliteStore
from modules.ai_code_knowledge_graph.storage.store import Store

SNAPSHOT_PREFIX = "snapshot"


def build_store(config) -> Store:
    """Create the store matching ``config.storage_backend``.

    SQLite uses ``data_dir/db_file``; every other backend (including
    ``memory`` and the external ones, which are not wired yet) falls back to
    a JSON file store under ``data_dir`` so persistence always works.
    """
    data_dir = Path(config.data_dir or Path(config.scanner.project_root) / DATA_DIR_NAME / MODULE_DATA_DIR)
    if config.storage_backend == "sqlite":
        return SqliteStore(data_dir / (config.db_file or DEFAULT_DB_FILE))
    return JsonFileStore(data_dir)


class SnapshotManager:
    """Creates, lists, loads and rotates knowledge snapshots."""

    def __init__(self, store: Store, *, max_snapshots: int = 20) -> None:
        self.store = store
        self.max_snapshots = max(1, max_snapshots)

    # ── Persistence ──────────────────────────────────────────────────────
    def save(self, payload: dict[str, Any], *, tag: str = "") -> str:
        """Persist ``payload`` and return the generated snapshot id."""
        snapshot_id = f"{SNAPSHOT_PREFIX}_{int(time.time() * 1000)}_{tag or 'default'}"
        self.store.save(
            snapshot_id,
            {"meta": {"id": snapshot_id, "tag": tag or "default", "created_at": time.time()},
             "payload": payload},
        )
        self._rotate()
        return snapshot_id

    def load(self, snapshot_id: str) -> dict[str, Any] | None:
        """Return the snapshot document (``{"meta", "payload"}``) or ``None``."""
        return self.store.load(snapshot_id)

    def load_payload(self, snapshot_id: str) -> dict[str, Any] | None:
        document = self.store.load(snapshot_id)
        return document.get("payload") if document else None

    def delete(self, snapshot_id: str) -> bool:
        return self.store.delete(snapshot_id)

    def list(self) -> list[dict[str, Any]]:
        """Snapshot metadata, newest first."""
        items = []
        for snapshot_id in self.store.list_keys(prefix=f"{SNAPSHOT_PREFIX}_"):
            document = self.store.load(snapshot_id)
            if not document:
                continue
            meta = document.get("meta", {})
            items.append({
                "id": snapshot_id,
                "tag": meta.get("tag", ""),
                "created_at": meta.get("created_at", 0.0),
                "artifacts": len(document.get("payload", {})),
            })
        items.sort(key=lambda item: item["created_at"], reverse=True)
        return items

    def count(self) -> int:
        return len(self.store.list_keys(prefix=f"{SNAPSHOT_PREFIX}_"))

    def _rotate(self) -> None:
        """Drop oldest snapshots beyond ``max_snapshots``."""
        snapshots = self.list()
        while len(snapshots) > self.max_snapshots:
            self.store.delete(snapshots.pop()["id"])

    # ── Context helpers ──────────────────────────────────────────────────
    def capture(self, ctx) -> dict[str, Any]:
        """Collect every context artifact as a JSON-serializable payload."""
        return {key: self._to_jsonable(ctx.memory.get(key)) for key in ctx.memory.keys()}

    def restore(self, ctx, snapshot: dict[str, Any]) -> None:
        """Put a snapshot's payload back onto the context memory."""
        for key, value in snapshot.get("payload", {}).items():
            ctx.memory.put(key, value)

    @classmethod
    def _to_jsonable(cls, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return {str(key): cls._to_jsonable(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [cls._to_jsonable(item) for item in value]
        to_json = getattr(value, "to_json", None)
        if callable(to_json):
            return cls._to_jsonable(to_json())
        if dataclasses.is_dataclass(value):
            return cls._to_jsonable(dataclasses.asdict(value))
        dunder = getattr(value, "__dict__", None)
        if isinstance(dunder, dict):
            return cls._to_jsonable(dunder)
        return str(value)
