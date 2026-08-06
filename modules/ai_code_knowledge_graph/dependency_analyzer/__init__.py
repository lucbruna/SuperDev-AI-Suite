"""Dependency analyzer package — file-level dependency reports."""
from __future__ import annotations

from modules.ai_code_knowledge_graph.dependency_analyzer.dependency_analyzer import DependencyAnalyzer
from modules.ai_code_knowledge_graph.dependency_analyzer.resolver import DependencyResolver

__all__ = ["DependencyAnalyzer", "DependencyResolver"]
