from __future__ import annotations

import re
from typing import Any


STOP_WORDS = {"a", "an", "the", "is", "are", "was", "were", "in", "on", "at", "to", "for",
              "of", "by", "with", "and", "or", "but", "it", "its", "that", "this", "from"}


class QueryOptimizer:
    async def optimize_query(self, query: str) -> dict[str, Any]:
        original = query.strip()
        keywords = await self.extract_keywords(original)
        expanded = await self.expand_query(original)
        return {
            "original": original,
            "optimized_query": " ".join(keywords),
            "keywords": keywords,
            "expanded": expanded,
            "relevance_score": await self.calculate_relevance(original, original),
        }

    async def expand_query(self, query: str) -> list[str]:
        expansions = {
            "machine learning": ["deep learning", "neural networks", "AI", "ML algorithms"],
            "nlp": ["natural language processing", "text mining", "language models"],
            "quantum": ["quantum computing", "qubits", "quantum algorithms"],
        }
        normalized = query.lower().strip()
        for key, values in expansions.items():
            if key in normalized:
                return [query] + values
        return [query]

    async def suggest_related(self, query: str) -> list[str]:
        suggestions = {
            "machine learning": ["supervised learning", "unsupervised learning", "reinforcement learning", "deep learning"],
            "deep learning": ["CNNs", "RNNs", "transformers", "GANs"],
            "nlp": ["tokenization", "sentiment analysis", "named entity recognition", "machine translation"],
            "quantum": ["quantum error correction", "quantum supremacy", "quantum cryptography"],
        }
        normalized = query.lower().strip()
        for key, values in suggestions.items():
            if key in normalized:
                return values
        return [f"related to {query}"]

    async def extract_keywords(self, query: str) -> list[str]:
        tokens = re.findall(r"\b[a-zA-Z]\w+\b", query.lower())
        keywords = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
        return keywords if keywords else tokens

    async def calculate_relevance(self, query: str, target: str) -> float:
        query_kw = set(await self.extract_keywords(query))
        target_kw = set(await self.extract_keywords(target))
        if not query_kw or not target_kw:
            return 0.0
        intersection = query_kw & target_kw
        union = query_kw | target_kw
        return round(len(intersection) / len(union), 4)