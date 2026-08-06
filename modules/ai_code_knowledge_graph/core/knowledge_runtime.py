"""Knowledge runtime — wires configuration and shared components together.

Owns the resolved config, the context (bus, state, registry, memory,
sessions) and the pipeline/kernel used by managers, agents and the API.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_code_knowledge_graph.config import KnowledgeConfig, get_default_config
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_kernel import KnowledgeKernel
from modules.ai_code_knowledge_graph.core.knowledge_pipeline import KnowledgePipeline
from modules.ai_code_knowledge_graph.core.knowledge_state import KnowledgeState
from modules.ai_code_knowledge_graph.storage import SnapshotManager, build_store

logger = logging.getLogger(__name__)


class KnowledgeRuntime:
    """Bundle of config + context + executors for the knowledge module."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or get_default_config()
        self.config.resolve()
        self.context = KnowledgeContext(config=self.config)
        self.pipeline = KnowledgePipeline()
        self.kernel = KnowledgeKernel()
        self.snapshots = SnapshotManager(
            build_store(self.config), max_snapshots=self.config.max_snapshots
        )
        self.pipeline.add_stage("snapshot", KnowledgeState.SNAPSHOTTING, self._stage_snapshot)

    # Convenience accessors -------------------------------------------------
    @property
    def bus(self):
        return self.context.bus

    @property
    def state(self):
        return self.context.state

    @property
    def registry(self):
        return self.context.registry

    @property
    def memory(self):
        return self.context.memory

    @property
    def sessions(self):
        return self.context.sessions

    # ── Snapshot stage (registered on the pipeline by the runtime) ────────
    def _stage_snapshot(self, ctx) -> dict:
        """Persist the built knowledge base as a snapshot (autosave-gated)."""

        def _run(ctx):
            if not getattr(ctx.config, "autosave_snapshot", True):
                return {"name": "snapshot", "saved": 0, "detail": "autosave disabled"}
            snapshot_id = self.snapshots.save(self.snapshots.capture(ctx), tag="pipeline")
            ctx.record("snapshots_saved", 1)
            return {"name": "snapshot", "saved": 1, "snapshot_id": snapshot_id}

        return KnowledgePipeline._run_stage(ctx, "snapshot", KnowledgeState.SNAPSHOTTING, _run)

    def status(self) -> dict[str, Any]:
        """Current runtime status for dashboards and the API."""
        return {
            "state": self.context.state.to_dict(),
            "stats": dict(self.context.stats),
            "registry": self.context.registry.counts(),
            "memory": self.context.memory.stats(),
            "sessions_active": len(self.context.sessions.active()),
            "snapshots": self.snapshots.count(),
            "config": {
                "name": self.config.name,
                "version": self.config.version,
                "storage_backend": self.config.storage_backend,
                "project_root": self.config.scanner.project_root,
                "data_dir": self.config.data_dir,
            },
        }

    def reset(self, *, keep_config: bool = True) -> None:
        """Reset state, memory and sessions (config retained by default)."""
        self.context.state.reset()
        self.context.memory.clear()
        self.context.sessions.close_all()
        self.context.stats.clear()
        self.context.cancel_requested = False
        if not keep_config:
            self.config = get_default_config()
            self.config.resolve()
            self.context = KnowledgeContext(config=self.config)
        logger.info("Knowledge runtime reset")

    @classmethod
    def from_config(cls, config: KnowledgeConfig | None = None) -> "KnowledgeRuntime":
        """Factory kept for callers that prefer a classmethod style."""
        return cls(config)


def build_runtime(config: KnowledgeConfig | None = None) -> KnowledgeRuntime:
    """Build a runtime from an optional config (defaults to resolved config)."""
    return KnowledgeRuntime(config)


# Load phase components and register their analyzers with the shared default
# registry so the pipeline index stage runs them automatically. Kept at the
# bottom: the phase packages are core-free, and by this point the registry
# module is already initialized.
from modules.ai_code_knowledge_graph.core.knowledge_registry import default_registry  # noqa: E402
from modules.ai_code_knowledge_graph.dependency_analyzer import DependencyAnalyzer  # noqa: E402,F401
from modules.ai_code_knowledge_graph.embeddings.service import EmbeddingService  # noqa: E402,F401
from modules.ai_code_knowledge_graph.graph import KnowledgeGraphBuilder  # noqa: E402,F401
from modules.ai_code_knowledge_graph.indexing.indexer import KnowledgeIndexer  # noqa: E402,F401
from modules.ai_code_knowledge_graph.semantic import SemanticEngine  # noqa: E402,F401

default_registry().register("analyzer", "graph", KnowledgeGraphBuilder())
default_registry().register("analyzer", "semantic", SemanticEngine())
default_registry().register("analyzer", "embeddings", EmbeddingService())
default_registry().register("analyzer", "relations", DependencyAnalyzer())
default_registry().register("analyzer", "indexer", KnowledgeIndexer())
