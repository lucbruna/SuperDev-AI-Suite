"""Embedding subsystem engine — Text embedding and similarity computation."""
import uuid
import math
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Embedding:
    embedding_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    vector: List[float] = field(default_factory=list)
    model: str = "hash"
    dimensions: int = 0
    created_at: datetime = field(default_factory=datetime.now)


class EmbeddingSubEngine:
    def __init__(self, dimensions: int = 128, model: str = "hash"):
        self._embeddings: Dict[str, Embedding] = {}
        self._dimensions = dimensions
        self._model = model

    def embed(self, text: str) -> Embedding:
        vector = self._compute_embedding(text)
        emb = Embedding(text=text, vector=vector, model=self._model, dimensions=self._dimensions)
        self._embeddings[emb.embedding_id] = emb
        return emb

    def batch_embed(self, texts: List[str]) -> List[Embedding]:
        return [self.embed(text) for text in texts]

    def get_embedding(self, embedding_id: str) -> Optional[Embedding]:
        return self._embeddings.get(embedding_id)

    def similarity(self, text_a: str, text_b: str) -> float:
        vec_a = self._compute_embedding(text_a)
        vec_b = self._compute_embedding(text_b)
        return self._cosine_similarity(vec_a, vec_b)

    def similarity_by_id(self, id_a: str, id_b: str) -> float:
        emb_a = self._embeddings.get(id_a)
        emb_b = self._embeddings.get(id_b)
        if not emb_a or not emb_b:
            return 0.0
        return self._cosine_similarity(emb_a.vector, emb_b.vector)

    def find_similar(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vec = self._compute_embedding(text)
        scored = []
        for emb in self._embeddings.values():
            score = self._cosine_similarity(query_vec, emb.vector)
            scored.append({"id": emb.embedding_id, "text": emb.text, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def delete(self, embedding_id: str) -> bool:
        return self._embeddings.pop(embedding_id, None) is not None

    def _compute_embedding(self, text: str) -> List[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        vector = []
        for i in range(0, min(len(h), self._dimensions * 2), 2):
            val = int(h[i:i+2], 16) / 255.0
            vector.append(val)
        while len(vector) < self._dimensions:
            vector.append(0.0)
        return vector[:self._dimensions]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def get_stats(self) -> dict:
        return {
            "total_embeddings": len(self._embeddings),
            "dimensions": self._dimensions,
            "model": self._model,
        }
