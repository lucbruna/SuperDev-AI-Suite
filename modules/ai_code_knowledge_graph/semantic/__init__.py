"""Semantic analysis package — symbol index and file classification.

Kept dependency-free of ``core`` (no imports of the core package at module
level) so it can be imported safely from anywhere, including the runtime
wiring. Analyzer registration happens in ``core.knowledge_runtime``.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.semantic.engine import SemanticEngine, classify_file
from modules.ai_code_knowledge_graph.semantic.symbols import SymbolIndex

__all__ = ["SemanticEngine", "SymbolIndex", "classify_file"]
