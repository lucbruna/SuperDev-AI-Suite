"""Semantic engine — cross-file analysis: symbols, categories, summary stats.

Lighter than the graph builder: produces a symbol index and per-file role
classification (test/config/database/service/...) consumed by the dashboard,
agents and the dependency analyzer. Registered as an ``analyzer`` so the
pipeline index stage runs it automatically.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.semantic.symbols import SymbolIndex

_TEST_MARKERS = ("test", "spec")
_CONFIG_DIRS = ("config", "conf", "settings", ".github", ".gitlab")
_CONFIG_EXTS = (".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".cfg", ".env")
_DB_DIRS = ("migrations", "migration", "db", "database", "schema", "sql")
_ROLE_MARKERS = (
    "repository",
    "model",
    "service",
    "controller",
    "api",
    "route",
    "agent",
    "plugin",
    "workflow",
    "view",
    "component",
    "hook",
    "util",
    "helper",
    "middleware",
)


def classify_file(rel_path: str) -> str:
    """Infer the file's role from its path and name."""
    parts = rel_path.replace("\\", "/").split("/")
    name = parts[-1].lower()
    path_lower = rel_path.lower()
    if any(marker in name for marker in _TEST_MARKERS):
        return "test"
    if name.startswith(".") or any(part in _CONFIG_DIRS for part in parts) or name.endswith(_CONFIG_EXTS):
        return "config"
    if any(part in _DB_DIRS for part in parts) or name.endswith(".sql"):
        return "database"
    for role in _ROLE_MARKERS:
        if role in path_lower:
            return role
    return "source"


class SemanticEngine:
    """Cross-file analysis over a scan result."""

    # ── Analyzer interface (invoked by the pipeline index stage) ──────────
    def index(self, ctx) -> dict[str, Any]:
        """Analyzer hook: build the semantic index and store it on the context."""
        result = ctx.memory.get("scan_result")
        if not result:
            return {"symbols": 0, "detail": "no scan result"}
        analysis = self.analyze(result)
        ctx.memory.put("semantic_index", analysis["symbols"])
        ctx.memory.put("semantic_analysis", analysis["summary"])
        ctx.record("semantic_symbols", analysis["summary"]["symbols"])
        return {
            "symbols": analysis["summary"]["symbols"],
            "categories": len(analysis["summary"]["categories"]),
        }

    # ── Analysis ──────────────────────────────────────────────────────────
    def analyze(self, scan_result: dict[str, Any]) -> dict[str, Any]:
        """Return ``{symbols: SymbolIndex, summary: {...}}`` for a scan."""
        symbols = SymbolIndex.from_scan(scan_result)
        language_counts: dict[str, int] = {}
        category_paths: dict[str, list[str]] = {}
        for entry in scan_result.get("files", []):
            rel_path = entry.get("rel_path", "")
            category_paths.setdefault(classify_file(rel_path), []).append(rel_path)
            language = entry.get("language")
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        summary: dict[str, Any] = {
            "files": len(scan_result.get("files", [])),
            "symbols": symbols.count(),
            "languages": language_counts,
            "categories": {category: len(paths) for category, paths in category_paths.items()},
            "top_symbols": symbols.top(20),
        }
        return {"symbols": symbols, "summary": summary}
