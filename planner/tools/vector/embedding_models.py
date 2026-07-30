from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class EmbeddingModel(BaseModel):
    name: str
    provider: str
    dimension: int
    max_input_tokens: int = 8192


EMBEDDING_MODELS: dict[str, EmbeddingModel] = {
    "text-embedding-3-small": EmbeddingModel(name="text-embedding-3-small", provider="openai", dimension=1536),
    "text-embedding-3-large": EmbeddingModel(name="text-embedding-3-large", provider="openai", dimension=3072),
    "text-embedding-ada-002": EmbeddingModel(name="text-embedding-ada-002", provider="openai", dimension=1536),
}


def get_embedding_model(name: str) -> EmbeddingModel | None:
    return EMBEDDING_MODELS.get(name)
