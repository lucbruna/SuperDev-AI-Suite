"""Knowledge pipeline — orchestrates scan → parse → build → index → ready.

The pipeline is stage-driven and registry-aware: later phases (graph builder,
semantic engine, embeddings) register additional components and the pipeline
invokes them automatically when present, keeping this file stable.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_state import KnowledgeState
from modules.ai_code_knowledge_graph.core.exceptions import KnowledgeError, ParseError, ScanError

logger = logging.getLogger(__name__)

StageFn = Callable[[KnowledgeContext], dict[str, Any]]


class KnowledgePipeline:
    """Runs the knowledge building stages in order."""

    def __init__(self) -> None:
        self._extra_stages: list[tuple[str, KnowledgeState, StageFn]] = []

    def add_stage(self, name: str, state: KnowledgeState, fn: StageFn) -> None:
        """Register an extra pipeline stage (used by later phases)."""
        self._extra_stages.append((name, state, fn))

    def run(self, ctx: KnowledgeContext, project_root: str | None = None) -> dict[str, Any]:
        """Execute the full pipeline and return a summary."""
        started = time.time()
        ctx.started_at = started
        ctx.publish("pipeline.started", {"project_root": project_root or ctx.config.scanner.project_root})

        summary: dict[str, Any] = {"stages": []}
        try:
            summary["stages"].append(self._stage_scan(ctx, project_root))
            if ctx.cancelled:
                return self._cancelled(ctx, started, summary)
            summary["stages"].append(self._stage_parse(ctx))
            if ctx.cancelled:
                return self._cancelled(ctx, started, summary)
            summary["stages"].append(self._stage_build(ctx))
            if ctx.cancelled:
                return self._cancelled(ctx, started, summary)
            summary["stages"].append(self._stage_index(ctx))
            for name, state, fn in self._extra_stages:
                if ctx.cancelled:
                    break
                summary["stages"].append(self._run_stage(ctx, name, state, fn))
        except KnowledgeError as exc:
            ctx.state.mark_error(exc.message, exc.context)
            ctx.publish("pipeline.failed", {"error": exc.message})
            raise

        ctx.state.set_state(KnowledgeState.READY, context="pipeline")
        summary["elapsed_seconds"] = round(time.time() - started, 3)
        summary["state"] = ctx.state.to_dict()
        summary["stats"] = dict(ctx.stats)
        ctx.record("last_pipeline_elapsed", summary["elapsed_seconds"])
        ctx.publish("pipeline.completed", {"elapsed_seconds": summary["elapsed_seconds"]})
        return summary

    # ── Stages ────────────────────────────────────────────────────────

    def _stage_scan(self, ctx: KnowledgeContext, project_root: str | None) -> dict[str, Any]:
        def _run(ctx: KnowledgeContext) -> dict[str, Any]:
            scanner = self._resolve_component(ctx, "scanner", "project")
            if scanner is None:
                from modules.ai_code_knowledge_graph.scanner.project_scanner import ProjectScanner

                scanner = ProjectScanner(ctx.config.scanner)
            result = scanner.scan(project_root or ctx.config.scanner.project_root)
            ctx.record("files_scanned", len(result.get("files", [])))
            ctx.record("scan_errors", result.get("errors", []))
            ctx.memory.put("scan_result", result)
            return {"name": "scan", "files": len(result.get("files", [])), "detail": result.get("stats", {})}

        return self._run_stage(ctx, "scan", KnowledgeState.SCANNING, _run)

    def _stage_parse(self, ctx: KnowledgeContext) -> dict[str, Any]:
        def _run(ctx: KnowledgeContext) -> dict[str, Any]:
            result = ctx.memory.get("scan_result")
            if not result:
                raise ScanError("No scan result available to parse")
            parsed_files = 0
            parse_errors = 0
            entities: dict[str, int] = {}
            for entry in result.get("files", []):
                parsed = entry.get("parsed")
                if parsed is None:
                    continue
                parsed_files += 1
                for entity in parsed.get("entities", []):
                    kind = entity.get("kind", "unknown")
                    entities[kind] = entities.get(kind, 0) + 1
                if parsed.get("error"):
                    parse_errors += 1
            ctx.record("files_parsed", parsed_files)
            ctx.record("parse_errors", parse_errors)
            ctx.record("entity_counts", entities)
            return {"name": "parse", "files": parsed_files, "entities": entities, "errors": parse_errors}

        return self._run_stage(ctx, "parse", KnowledgeState.PARSING, _run)

    def _stage_build(self, ctx: KnowledgeContext) -> dict[str, Any]:
        def _run(ctx: KnowledgeContext) -> dict[str, Any]:
            result = ctx.memory.get("scan_result")
            document: dict[str, Any] = {
                "project_root": ctx.config.scanner.project_root,
                "built_at": time.time(),
                "files": result.get("files", []) if result else [],
                "stats": dict(ctx.stats),
            }
            ctx.memory.put("knowledge_document", document)
            ctx.record("knowledge_document_files", len(document["files"]))
            return {"name": "build", "files": len(document["files"])}

        return self._run_stage(ctx, "build", KnowledgeState.BUILDING, _run)

    def _stage_index(self, ctx: KnowledgeContext) -> dict[str, Any]:
        def _run(ctx: KnowledgeContext) -> dict[str, Any]:
            indexers = ctx.registry.all("analyzer")
            indexed = 0
            for name, indexer in indexers.items():
                if hasattr(indexer, "index") and callable(getattr(indexer, "index")):
                    indexer.index(ctx)
                    indexed += 1
            ctx.record("indexers_ran", indexed)
            return {"name": "index", "indexers": indexed}

        return self._run_stage(ctx, "index", KnowledgeState.INDEXING, _run)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _resolve_component(ctx: KnowledgeContext, kind: str, name: str):
        try:
            return ctx.registry.get(kind, name)
        except KnowledgeError:
            return None

    @staticmethod
    def _run_stage(ctx: KnowledgeContext, name: str, state: KnowledgeState, fn: StageFn) -> dict[str, Any]:
        ctx.state.set_state(state, context=f"stage:{name}")
        ctx.publish(f"stage.{name}.started", {})
        started = time.time()
        try:
            result = fn(ctx)
        except KnowledgeError as exc:
            ctx.state.mark_error(f"Stage '{name}' failed: {exc.message}", exc.context)
            ctx.publish(f"stage.{name}.failed", {"error": exc.message})
            raise
        except Exception as exc:  # noqa: BLE001 — wrap unexpected failures
            ctx.state.mark_error(f"Stage '{name}' failed: {exc}", {"exception": type(exc).__name__})
            ctx.publish(f"stage.{name}.failed", {"error": str(exc)})
            raise KnowledgeError(f"Stage '{name}' failed: {exc}", cause=exc) from exc
        result["elapsed_seconds"] = round(time.time() - started, 3)
        ctx.publish(f"stage.{name}.completed", result)
        return result

    @staticmethod
    def _cancelled(ctx: KnowledgeContext, started: float, summary: dict[str, Any]) -> dict[str, Any]:
        ctx.state.set_state(KnowledgeState.IDLE, context="cancelled")
        summary["cancelled"] = True
        summary["elapsed_seconds"] = round(time.time() - started, 3)
        ctx.publish("pipeline.cancelled", {})
        return summary
