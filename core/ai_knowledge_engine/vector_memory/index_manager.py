from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class IndexInfo:
    index_id: str
    name: str
    index_type: str
    vector_count: int
    dimension: int
    created_at: float
    last_optimized: Optional[float] = None


class IndexManager:
    def __init__(self) -> None:
        self._indexes: dict[str, IndexInfo] = {}
        self._index_data: dict[str, dict[str, list[float]]] = {}

    def create_index(self, name: str, index_type: str = "flat", dimension: int = 128) -> IndexInfo:
        index_id = str(uuid.uuid4())
        info = IndexInfo(
            index_id=index_id,
            name=name,
            index_type=index_type,
            vector_count=0,
            dimension=dimension,
            created_at=time.time(),
        )
        self._indexes[index_id] = info
        self._index_data[index_id] = {}
        return info

    def rebuild_index(self, index_id: str, vectors: Optional[dict[str, list[float]]] = None) -> bool:
        if index_id not in self._indexes:
            return False
        info = self._indexes[index_id]
        if vectors is not None:
            self._index_data[index_id] = dict(vectors)
        info.vector_count = len(self._index_data[index_id])
        info.last_optimized = time.time()
        return True

    def optimize_index(self, index_id: str) -> bool:
        if index_id not in self._indexes:
            return False
        self._indexes[index_id].last_optimized = time.time()
        return True

    def get_index_info(self, index_id: str) -> Optional[IndexInfo]:
        return self._indexes.get(index_id)

    def list_indexes(self) -> list[IndexInfo]:
        return list(self._indexes.values())
