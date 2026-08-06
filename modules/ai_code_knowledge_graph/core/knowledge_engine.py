"""Knowledge engine — the public entry point of the AI Code Knowledge Graph.

Exposes a compact API used by the REST layer, CLI and agents: scan, status,
snapshot and simple queries over the last scan. The module-level singleton
is obtained with :func:`get_engine`.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_manager import KnowledgeManager
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime

logger = logging.getLogger(__name__)


class KnowledgeEngine:
    """Facade combining runtime + manager for the knowledge module."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.runtime = KnowledgeRuntime(config)
        self.manager = KnowledgeManager(self.runtime)

    # ── Lifecycle ───────────────────────────────────────────────────────

    def scan(self, project_root: str | None = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
        """Scan the repository and build the knowledge document."""
        return self.manager.scan(project_root=project_root, meta=meta)

    def status(self) -> dict[str, Any]:
        return self.manager.status()

    def snapshot(self) -> dict[str, Any]:
        return self.manager.snapshot()

    def load_snapshot(self, path: str | None = None) -> dict[str, Any]:
        return self.manager.load_snapshot(path)

    def reset(self) -> None:
        self.manager.reset()

    # ── Queries over the last scan ──────────────────────────────────────

    def files(self, language: str | None = None) -> list[dict[str, Any]]:
        """Return scanned files, optionally filtered by language."""
        document = self.runtime.context.memory.get("knowledge_document")
        if not document:
            return []
        files = document.get("files", [])
        if language:
            files = [f for f in files if f.get("language") == language]
        return files

    def entity_counts(self) -> dict[str, int]:
        """Aggregate entity kinds across the last scan."""
        document = self.runtime.context.memory.get("knowledge_document")
        if not document:
            return {}
        counts: dict[str, int] = {}
        for entry in document.get("files", []):
            for entity in entry.get("parsed", {}).get("entities", []) if isinstance(entry.get("parsed"), dict) else []:
                kind = entity.get("kind", "unknown")
                counts[kind] = counts.get(kind, 0) + 1
        return counts

    def languages(self) -> dict[str, int]:
        """Count files per language in the last scan."""
        counts: dict[str, int] = {}
        for entry in self.files():
            lang = entry.get("language")
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
        return counts

    @property
    def state(self):
        return self.runtime.context.state.state.value

    @property
    def last_build(self) -> float | None:
        return self.runtime.context.state.finished_at


_ENGINE: KnowledgeEngine | None = None


def get_engine(config: KnowledgeConfig | None = None) -> KnowledgeEngine:
    """Return the shared KnowledgeEngine singleton."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = KnowledgeEngine(config)
    return _ENGINE
