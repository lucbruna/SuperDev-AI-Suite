"""RAG package — retrieval and question answering over the knowledge base."""
from __future__ import annotations

from modules.ai_code_knowledge_graph.rag.context import build_context
from modules.ai_code_knowledge_graph.rag.retriever import RagRetriever

__all__ = ["RagRetriever", "build_context"]
