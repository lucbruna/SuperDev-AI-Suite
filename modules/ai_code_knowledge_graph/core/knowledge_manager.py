"""Knowledge manager — high-level facade for the knowledge pipeline.

Presents a small, stable API (scan / status / snapshot / load / reset) used
by the engine, the REST API, the CLI and agents.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.core.exceptions import KnowledgeError, NotFoundError
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """Facade over a :class:`KnowledgeRuntime`."""

    def __init__(self, runtime: KnowledgeRuntime) -> None:
        self.runtime = runtime

    # ── Operations ──────────────────────────────────────────────────────

    def scan(self, project_root: str | None = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        """Run the full scan → parse → build → index pipeline."""
        session = self.runtime.context.create_session(meta=meta)
        try:
            summary = self.runtime.pipeline.run(self.runtime.context, project_root=project_root)
            session.meta = {"summary": summary}
            self.runtime.context.sessions.complete(session, success=True)
            if self.runtime.config.autosave_snapshot:
                self.snapshot()
            return summary
        except KnowledgeError as exc:
            self.runtime.context.sessions.complete(session, success=False)
            session.meta = {"error": exc.message}
            raise

    def status(self) -> dict[str, Any]:
        return self.runtime.status()

    def snapshot(self) -> dict[str, Any]:
        """Build a serializable snapshot and persist it (JSON)."""
        document = self.runtime.context.memory.get("knowledge_document")
        if document is None:
            raise KnowledgeError("No knowledge document available; run scan() first")
        snapshot = {
            "name": self.runtime.config.name,
            "version": self.runtime.config.version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project_root": document.get("project_root", ""),
            "files": document.get("files", []),
            "stats": dict(self.runtime.context.stats),
            "state": self.runtime.context.state.to_dict(),
        }
        self._write_snapshot(snapshot)
        self.runtime.context.memory.put("last_snapshot", snapshot)
        return snapshot

    def load_snapshot(self, path: str | None = None) -> dict[str, Any]:
        """Load a persisted snapshot (latest by default)."""
        snapshot_path = Path(path) if path else self._snapshot_path()
        if not snapshot_path.exists():
            raise NotFoundError("knowledge snapshot", snapshot_path.name)
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.runtime.context.memory.put("knowledge_document", data)
        self.runtime.context.memory.put("last_snapshot", data)
        return data

    def list_snapshots(self) -> list[str]:
        """List persisted snapshot files (newest first)."""
        data_dir = Path(self.runtime.config.data_dir)
        if not data_dir.exists():
            return []
        pattern = self.runtime.config.snapshot_file.replace(".json", "*.json")
        return sorted((p.name for p in data_dir.glob(pattern)), reverse=True)

    def reset(self) -> None:
        self.runtime.reset()

    # ── Helpers ─────────────────────────────────────────────────────────

    def _snapshot_path(self) -> Path:
        return Path(self.runtime.config.data_dir) / self.runtime.config.snapshot_file

    def _write_snapshot(self, snapshot: dict[str, Any]) -> Path:
        path = self._snapshot_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        stamped = path.with_name(f"{path.stem}_{stamp}.json")
        stamped.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        # Keep the max number of snapshots (prune oldest).
        pattern = f"{path.stem}_*.json"
        files = sorted(path.parent.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in files[self.runtime.config.max_snapshots:]:
            try:
                old.unlink()
            except OSError:
                pass
        # Always keep a stable "latest" copy.
        path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Knowledge snapshot written to %s", path)
        return path
