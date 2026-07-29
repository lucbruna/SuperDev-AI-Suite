from __future__ import annotations

import re
from typing import Any

SAMPLE_DATA: dict[str, list[dict[str, Any]]] = {
    "machine learning": [
        {"title": "Deep Learning Overview", "source": "ArXiv", "relevance": 0.95, "content": "Deep learning uses neural networks with multiple layers."},
        {"title": "ML Best Practices", "source": "Google Scholar", "relevance": 0.88, "content": "Cross-validation and regularization are essential."},
        {"title": "Supervised vs Unsupervised", "source": "Wikipedia", "relevance": 0.72, "content": "Supervised learning uses labeled data."},
    ],
    "quantum computing": [
        {"title": "Quantum Algorithms", "source": "IEEE Xplore", "relevance": 0.91, "content": "Shor's algorithm factors integers exponentially faster."},
        {"title": "Qubit Technologies", "source": "ArXiv", "relevance": 0.87, "content": "Superconducting qubits are the leading technology."},
    ],
    "natural language processing": [
        {"title": "Transformer Architecture", "source": "ArXiv", "relevance": 0.94, "content": "Attention is all you need."},
        {"title": "BERT Explained", "source": "Google Scholar", "relevance": 0.9, "content": "Bidirectional encoding captures context from both directions."},
        {"title": "GPT Models", "source": "Medium", "relevance": 0.78, "content": "Autoregressive language models for text generation."},
    ],
}


class InformationCollector:
    def __init__(self) -> None:
        self._data: dict[str, list[dict[str, Any]]] = {k: list(v) for k, v in SAMPLE_DATA.items()}

    async def collect(self, query: str) -> dict[str, Any]:
        normalized = query.lower().strip()
        results = self._data.get(normalized, [])
        if not results:
            for key, items in self._data.items():
                if any(word in normalized for word in key.split()):
                    results = items
                    break
        if not results:
            results = [
                {"title": f"Result for '{query}'", "source": "Web", "relevance": 0.5, "content": f"Simulated content for: {query}"}
            ]
        return {
            "query": query,
            "results": results,
            "total": len(results),
        }

    async def collect_from_source(self, query: str, source_id: str) -> dict[str, Any]:
        result = await self.collect(query)
        filtered = [r for r in result["results"] if r.get("source", "").lower() == source_id.lower()]
        return {
            "query": query,
            "source": source_id,
            "results": filtered,
            "total": len(filtered),
        }

    def filter_results(self, results: list[dict[str, Any]], min_relevance: float = 0.5) -> list[dict[str, Any]]:
        return [r for r in results if r.get("relevance", 0) >= min_relevance]

    def rank_results(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(results, key=lambda r: r.get("relevance", 0), reverse=True)

    def extract_relevant(self, results: list[dict[str, Any]], top_n: int = 3) -> list[dict[str, Any]]:
        ranked = self.rank_results(results)
        return ranked[:top_n]