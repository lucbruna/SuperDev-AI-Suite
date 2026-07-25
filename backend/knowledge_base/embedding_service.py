from __future__ import annotations

import asyncio
import hashlib
from typing import Any

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _instance: EmbeddingService | None = None
    _model: SentenceTransformer | None = None
    _model_name: str = "all-MiniLM-L6-v2"
    _embedding_dim: int = 384

    def __new__(cls) -> EmbeddingService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self._load_model()

    def _load_model(self) -> None:
        try:
            self._model = SentenceTransformer(self._model_name)
            self._embedding_dim = self._model.get_sentence_embedding_dimension()
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self._embedding_dim
        
        hashlib.md5(text.encode()).hexdigest()
        
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not valid_texts:
            return [[0.0] * self._embedding_dim for _ in texts]
        
        indices, clean_texts = zip(*valid_texts, strict=False)
        embeddings = self._model.encode(list(clean_texts), normalize_embeddings=True)
        
        results = [[0.0] * self._embedding_dim for _ in texts]
        for idx, emb in zip(indices, embeddings, strict=False):
            results[idx] = emb.tolist()
        
        return results

    async def aembed_text(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_text, text)

    async def aembed_texts(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed_texts, texts)

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self._model_name,
            "embedding_dim": self._embedding_dim,
            "max_seq_length": self._model.get_max_seq_length() if self._model else 0,
        }


embedding_service = EmbeddingService()