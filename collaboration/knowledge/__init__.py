"""Knowledge subsystem (Volume 26, Fase 7): wiki colaborativa.

KnowledgeEngine gerencia páginas wiki com categorias, histórico de
versões e busca (humanos e agentes de IA contribuem).
"""
from __future__ import annotations

from .knowledge_categories import KnowledgeCategories
from .knowledge_engine import KnowledgeEngine
from .knowledge_history import VersionEntry, VersionHistory
from .knowledge_manager import KnowledgeManager
from .knowledge_pages import KnowledgePage
from .knowledge_search import KnowledgeSearch

__all__ = [
    "KnowledgeCategories",
    "KnowledgeEngine",
    "KnowledgeManager",
    "KnowledgePage",
    "KnowledgeSearch",
    "VersionEntry",
    "VersionHistory",
]
