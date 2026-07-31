from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


class EmbeddingService:
    _instance: EmbeddingService | None = None
    _model_name: str = "text-embedding-ada-002"
    _embedding_dim: int = 1536
    _local_model = None

    def __new__(cls) -> EmbeddingService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # NOTE: model loading is deferred to first use (lazy) so importing this
        # module (and therefore backend.app) does not pull in torch / download
        # model weights at import time.
        pass

    def _try_load_local(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self._local_model = SentenceTransformer(model_name)
            self._model_name = model_name
            dim = self._local_model.get_sentence_embedding_dimension()
            if dim is not None:
                self._embedding_dim = dim
        except ImportError:
            pass

    @property
    def embedding_dim(self) -> int:
        return self._embedding_dim

    def _embed_via_api(self, texts: list[str]) -> list[list[float]]:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return [[0.0] * self._embedding_dim for _ in texts]
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"input": texts, "model": "text-embedding-ada-002"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        ordered = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in ordered]

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self._embedding_dim
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._local_model is None:
            self._try_load_local()
        if self._local_model is not None:
            valid = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
            if not valid:
                return [[0.0] * self._embedding_dim for _ in texts]
            indices, clean = zip(*valid)
            embeddings = self._local_model.encode(list(clean), normalize_embeddings=True)
            results = [[0.0] * self._embedding_dim for _ in texts]
            for idx, emb in zip(indices, embeddings):
                results[idx] = emb.tolist()
            return results
        return self._embed_via_api(texts)

    async def aembed_text(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.embed_text, text)

    async def aembed_texts(self, texts: list[str]) -> list[list[float]]:
        return await asyncio.to_thread(self.embed_texts, texts)

    def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self._model_name,
            "embedding_dim": self._embedding_dim,
            "local_model_loaded": self._local_model is not None,
        }


embedding_service = EmbeddingService()