"""Graph assistant: graph-aware Q&A with LLM enrichment.

Builds a compact graph summary, retrieves relevant context via RAG, and — when
an LLM provider is configured — produces a natural-language answer. Without a
provider it returns a deterministic, structured answer.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_intelligence.llm.prompts import SYSTEM_ARCHITECT, qa_prompt
from modules.architecture_intelligence.rag.intelligence_rag import IntelligenceRAG


class GraphAssistant:
    """Answers questions about the architecture using RAG + optional LLM."""

    def __init__(self, rag: IntelligenceRAG | None = None) -> None:
        self.rag = rag or IntelligenceRAG()

    def ask(self, question: str, graph: Any) -> dict[str, Any]:
        self.rag.index_graph(graph)
        context = self.rag.context(question, limit=5)
        summary = self._summary(graph)

        llm_answer = self._llm(question, summary, context)
        answer = llm_answer or self._heuristic(question, summary, context)
        return {
            "question": question,
            "answer": answer,
            "generator": "llm" if llm_answer else "heuristic",
            "context": context,
            "stats": graph.stats(),
        }

    def _heuristic(self, question: str, summary: str, context: str) -> str:
        lines = [summary]
        if context:
            lines.append(f"Relevant files:\n{context}")
        lines.append("No LLM provider is configured; this answer is a heuristic summary.")
        return "\n".join(lines)

    def _llm(self, question: str, summary: str, context: str) -> str:
        try:
            from modules.architecture_intelligence.llm.provider import get_provider

            provider = get_provider()
            if not provider.available:
                return ""
            prompt = qa_prompt(f"{summary}\n\nRelevant context:\n{context}", question)
            return provider.complete(prompt, system=SYSTEM_ARCHITECT, max_tokens=400)
        except Exception:
            return ""

    @staticmethod
    def _summary(graph: Any) -> str:
        stats = graph.stats()
        kinds = ", ".join(f"{k}={v}" for k, v in sorted(stats.get("kinds", {}).items()))
        return (
            f"Architecture graph '{graph.name}' has {stats.get('nodes', 0)} nodes "
            f"and {stats.get('edges', 0)} edges. Node kinds: {kinds}."
        )


def ask(question: str, graph: Any) -> dict[str, Any]:
    return GraphAssistant().ask(question, graph)
