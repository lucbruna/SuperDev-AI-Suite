"""Scanner package for the AI Code Knowledge Graph module.

Provides the deterministic filesystem walk (:mod:`.filesystem_scanner`),
the top-level :class:`~.project_scanner.ProjectScanner` and per-language
content scanners that dispatch to the module's parsers. ``ProjectScanner``
is the entry point consumed by the knowledge pipeline.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.scanner.filesystem_scanner import FileInfo, language_for_file, scan_files
from modules.ai_code_knowledge_graph.scanner.project_scanner import ProjectScanner

__all__ = ["FileInfo", "ProjectScanner", "language_for_file", "scan_files"]
