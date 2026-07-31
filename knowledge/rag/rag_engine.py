from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import RetrievalContext, SearchResult
from .citation_manager import CitationManager
from .context_builder import ContextBuilder
from .prompt_builder import PromptBuilder
from .reranker import Reranker
from .response_generator import ResponseGenerator
from .retriever import Retriever


class RagEngine:
    """Orchestrates the retrieval-augmented generation pipeline."""

    def __init__(
        self,
        retriever: Retriever | None = None,
        reranker: Reranker | None = None,
        context_builder: ContextBuilder | None = None,
        prompt_builder: PromptBuilder | None = None,
        citation_manager: CitationManager | None = None,
        response_generator: ResponseGenerator | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.rag_engine")
        self.retriever = retriever or Retriever()
        self.reranker = reranker or Reranker()
        self.context_builder = context_builder or ContextBuilder()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.citation_manager = citation_manager or CitationManager()
        self.response_generator = response_generator or ResponseGenerator()

    def pipeline(self, query: str, top_k: int = 5) -> tuple[list[SearchResult], RetrievalContext, dict[str, str], dict[str, Any]]:
        results = self.retriever.retrieve(query, top_k)
        reranked = self.reranker.rerank(query, results, top_k=top_k)
        self.citation_manager.register(reranked)
        context = self.context_builder.build(query, reranked)
        prompt = self.prompt_builder.build(query, context)
        response = self.response_generator.generate(query, context, prompt)
        return reranked, context, prompt, response

    def answer(self, query: str, top_k: int = 5) -> dict[str, Any]:
        reranked, context, _prompt, response = self.pipeline(query, top_k)
        return {
            "query": query,
            "answer": response["answer"],
            "context": [result.to_dict() for result in context.results],
            "citations": self.citation_manager.format_sources(),
            "scores": [result.score for result in context.results],
        }

    def register_with_manager(self, manager: Any) -> None:
        if manager is not None and not hasattr(manager, "rag"):
            manager.rag = self
            self._log.debug("registered rag engine on manager")
